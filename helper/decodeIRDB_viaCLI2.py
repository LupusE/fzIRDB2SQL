#!/usr/bin/env python3
import sys
import subprocess
import importlib.util
import argparse
import os
import logging
from tqdm import tqdm
import serial
import time

# ----------------------------
# Dependency Management
# ----------------------------

def install_package(package_name):
    """
    Install a package using pip.
    """
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        print(f"Successfully installed package: {package_name}")
    except subprocess.CalledProcessError:
        print(f"Failed to install package: {package_name}. Please install it manually.")
        sys.exit(1)

def check_and_install_dependencies(required_packages):
    """
    Check for required packages and install any that are missing.
    """
    for package in required_packages:
        if not importlib.util.find_spec(package):
            print(f"Package '{package}' not found. Installing...")
            install_package(package)

# ----------------------------
# Flipper IR Decoder Class
# ----------------------------

class FlipperIRDecoder:
    def __init__(self, system_dir, flipper_dir, parsed_dir, port, log_level, log_file, close_apps_frequency=10):
        self.system_dir = system_dir
        self.flipper_dir = flipper_dir
        self.parsed_dir = parsed_dir
        self.port = port
        self.processed_count = 0
        self.failed_files = []
        self.setup_logging(log_level, log_file)
        self.serial_conn = None
        self.close_apps_frequency = close_apps_frequency

    def setup_logging(self, log_level, log_file):
        """
        Setup logging configuration.
        """
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            print(f"Invalid log level: {log_level}")
            sys.exit(1)
        
        logging.basicConfig(
            level=numeric_level,
            format='%(levelname)s: %(message)s',  # Simplified format
            handlers=[
                logging.FileHandler(log_file, mode='a'),  # Append mode
                logging.StreamHandler(sys.stdout)  # Console output
            ]
        )

    def connect_flipper(self):
        """
        Establish a serial connection to Flipper Zero.
        """
        try:
            self.serial_conn = serial.Serial(self.port, timeout=1)
            logging.info("Connected to Flipper Zero. Starting IR file processing.")
            self.check_cli_version()
        except serial.SerialException as e:
            logging.error(f"Error connecting to Flipper Zero on port {self.port}: {e}")
            sys.exit(1)

    def send_command(self, command, timeout=2):
        """
        Send a command to Flipper Zero and return the response with a shorter timeout.
        """
        try:
            self.serial_conn.write(f"{command}\r\n".encode('ascii'))
            
            start_time = time.time()
            response = ""
            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting).decode('ascii', errors='ignore')
                    response += chunk
                    if '\n' in chunk:  # Check for newline to indicate end of response
                        break
                time.sleep(0.05)  # Short sleep to prevent CPU hogging
            
            response = response.strip()
            
            # Filter out unwanted responses
            if any(unwanted in response for unwanted in ["Welcome to Flipper Zero", "Firmware version", ">:"]):
                return ""
            
            if "Error:" in response or "Failed:" in response:
                logging.error(f"Command '{command}' failed: {response}")
                return None
            
            return response
        except Exception as e:
            logging.error(f"Failed to send command '{command}': {e}")
            return None


    def send_command_with_retry(self, command, max_retries=3, timeout=2):
        """
        Send a command with retry mechanism and configurable timeout.
        """
        for attempt in range(max_retries):
            response = self.send_command(command, timeout=timeout)
            if response is not None:
                return response
            logging.warning(f"Retrying command '{command}' (attempt {attempt + 1}/{max_retries})")
            time.sleep(0.1)  # Reduced delay between retries
        logging.error(f"Command '{command}' failed after {max_retries} attempts")
        return None

    def create_directory(self, path):
        """
        Create a directory on Flipper Zero if it doesn't exist.
        """
        components = path.strip('/').split('/')
        for i in range(1, len(components) + 1):
            current_path = '/' + '/'.join(components[:i])
            response = self.send_command_with_retry(f"storage mkdir {current_path}")
            if response is None or ("Storage error:" in response and "already exists" not in response.lower()):
                logging.error(f"Error creating directory '{current_path}': {response}")
                return False
        return True

    def close_running_apps(self):
        """
        Close any running applications on Flipper Zero.
        """
        self.send_command_with_retry("loader list")
        self.send_command_with_retry("loader close infrared")
        self.send_command_with_retry("loader close ir_transmitter")

    def read_file_content(self, file_path):
        """
        Read file content with multiple encoding attempts.
        """
        encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        logging.error(f"Unable to read file '{file_path}' with any supported encoding.")
        return None

    def check_type_raw(self, irfile):
        """
        Check if the IR file is of type 'raw'.
        """
        content = self.read_file_content(irfile)
        if content is None:
            return False
        return 'type: raw' in content

    def gather_ir_files(self):
        """
        Gather all .ir files of type 'raw' from the system directory.
        """
        ir_files = []
        for subdir, _, files in os.walk(self.system_dir):
            for file in files:
                if file.lower().endswith(".ir"):
                    full_path = os.path.join(subdir, file)
                    if self.check_type_raw(full_path):
                        relative_path = os.path.relpath(subdir, self.system_dir).replace("\\", "/")
                        ir_files.append((relative_path, file))
        return ir_files

    def verify_file_exists(self, file_path, timeout=0.5):
        """
        Verify if a file exists on Flipper Zero with a shorter timeout.
        """
        response = self.send_command(f"storage info {file_path}", timeout=timeout)
        return response is not None and "File not found" not in response


    def decode_ir_file(self, relative_path, ir_file):
        """
        Decode a single IR file without closing apps each time.
        """
        input_file = f"{self.flipper_dir}{relative_path}/{ir_file}".replace("\\", "/")
        output_file = f"{self.parsed_dir}{relative_path}/{ir_file}".replace("\\", "/")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        if not self.create_directory(output_dir):
            logging.error(f"Failed to create directory for '{output_file}'")
            self.failed_files.append(input_file)
            return False

        # Decode the IR file with a shorter timeout
        decode_command = f"ir decode {input_file} {output_file}"
        response = self.send_command_with_retry(decode_command, timeout=1)

        if response is None or "Error" in response or "Failed" in response:
            logging.error(f"Failed to decode '{input_file}'. Response: {response}")
            self.failed_files.append(input_file)
            return False

        # Verify the file was created (with a short timeout)
        if self.verify_file_exists(output_file, timeout=0.5):
            self.processed_count += 1
            return True
        else:
            logging.error(f"Decoded file '{output_file}' not found after decoding.")
            self.failed_files.append(input_file)
            return False


    def process_ir_files(self, ir_files):
        """
        Process all gathered IR files with a progress bar and less frequent app closing.
        """
        total_files = len(ir_files)
        if total_files == 0:
            logging.info("No IR files to process.")
            return

        logging.info(f"{total_files} files to process. Starting...")
        with tqdm(total=total_files, desc="Decoding IR Files", unit="file") as pbar:
            for index, (relative_path, ir_file) in enumerate(ir_files, 1):
                if index % self.close_apps_frequency == 1:
                    self.close_running_apps()
                    logging.debug(f"Closed running apps before processing file {index}")
                
                self.decode_ir_file(relative_path, ir_file)
                pbar.update(1)

        logging.info(f"Finished. {self.processed_count} out of {total_files} files processed successfully.")
        if self.failed_files:
            logging.warning(f"{len(self.failed_files)} files failed to decode. Check the log for details.")

    def check_cli_version(self):
        """
        Check the CLI version of Flipper Zero.
        """
        response = self.send_command_with_retry("version")
        if response:
            logging.info(f"Flipper Zero Firmware Version: {response}")
        else:
            logging.warning("Unable to determine Flipper Zero firmware version")

    def capture_flipper_logs(self, duration=5):
        """
        Capture Flipper Zero logs for a specified duration.
        """
        self.send_command_with_retry("log debug")
        time.sleep(duration)
        logs = self.send_command_with_retry("log")
        self.send_command_with_retry("log default")
        return logs

    def run(self):
        """
        Run the IR decoding process.
        """
        self.connect_flipper()
        ir_files = self.gather_ir_files()
        self.process_ir_files(ir_files)
        self.serial_conn.close()

# ----------------------------
# Main Function
# ----------------------------

def main():
    # Define required packages
    required_packages = ['serial', 'tqdm', 'colorama']

    # Check and install dependencies
    check_and_install_dependencies(required_packages)

    # Import after ensuring dependencies are installed
    import serial
    import time
    import logging
    from tqdm import tqdm

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Decode IR files on Flipper Zero.")
    parser.add_argument(
        '--system-dir',
        type=str,
        default='Z:/scripts/ir files/Flipper-IRDB-main',
        help='Path to the IRDB on the system.'
    )
    parser.add_argument(
        '--flipper-dir',
        type=str,
        default='/ext/infrared/Flipper-IRDB-main/',
        help='Path to the IRDB on Flipper Zero.'
    )
    parser.add_argument(
        '--parsed-dir',
        type=str,
        default='/ext/infrared/DECODED-IRDB/',
        help='Path to the parsed files on Flipper Zero.'
    )
    parser.add_argument(
        '--port',
        type=str,
        default='COM14',
        help='Serial port for Flipper Zero.'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default='decodeIRDB.log',
        help='File to log the output.'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level.'
    )
    parser.add_argument(
    '--close-apps-frequency',
    type=int,
    default=10,
    help='Frequency of closing running apps (every N files).'
    )
    args = parser.parse_args()

    # Initialize and run the decoder
    decoder = FlipperIRDecoder(
        system_dir=args.system_dir,
        flipper_dir=args.flipper_dir,
        parsed_dir=args.parsed_dir,
        port=args.port,
        log_level=args.log_level,
        log_file=args.log_file,
        close_apps_frequency=args.close_apps_frequency
    )
    decoder.run()

    # Summary of failed decodings
    if decoder.failed_files:
        print("\nSummary of Failed Decodings:")
        for failed_file in decoder.failed_files:
            print(f" - {failed_file}")

if __name__ == "__main__":
    main()