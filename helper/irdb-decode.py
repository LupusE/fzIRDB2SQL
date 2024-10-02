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
    def __init__(self, system_dir, flipper_dir, parsed_dir, port, log_level, log_file):
        self.system_dir = system_dir
        self.flipper_dir = flipper_dir
        self.parsed_dir = parsed_dir
        self.port = port
        self.processed_count = 0
        self.failed_files = []
        self.setup_logging(log_level, log_file)
        self.serial_conn = None

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
            format='%(asctime)s - %(levelname)s - %(message)s',
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
        except serial.SerialException as e:
            logging.error(f"Error connecting to Flipper Zero on port {self.port}: {e}")
            sys.exit(1)

    def send_command(self, command):
        """
        Send a command to Flipper Zero and return the response.
        Filters out unwanted CLI responses like ASCII art.
        """
        try:
            logging.debug(f"Sending command: {command}")
            self.serial_conn.write(f"{command}\r\n".encode('ascii'))
            time.sleep(0.5)  # Adjust as needed based on device responsiveness
            response = self.serial_conn.read(self.serial_conn.in_waiting).decode('ascii', errors='ignore').strip()
            
            # Filter out ASCII art or unwanted messages
            if "Welcome to Flipper Zero" in response:
                return ""
            if "Firmware version" in response:
                return ""
            if response.startswith(">:"):
                return ""
            if not response:
                return ""
            
            return response
        except Exception as e:
            logging.error(f"Failed to send command '{command}': {e}")
            return ""

    def create_directory(self, path):
        """
        Create a directory on Flipper Zero if it doesn't exist.
        """
        # Split the path into components to create nested directories
        directories = path.strip('/').split('/')
        current_path = ''
        for directory in directories:
            current_path += f'/{directory}'
            response = self.send_command(f"storage mkdir {current_path}")
            if "file/dir already exist" in response or "already exists" in response:
                # Directory already exists, no action needed
                continue
            elif "Storage error:" in response:
                # Log the error but continue attempting to create other directories
                logging.error(f"Error creating directory '{current_path}': {response}")
                continue
            else:
                logging.info(f"Created directory '{current_path}'.")

    def close_running_apps(self):
        """
        Close any running applications on Flipper Zero.
        """
        self.send_command("loader list")
        self.send_command("loader close infrared")
        self.send_command("loader close ir_transmitter")

    def check_type_raw(self, irfile):
        """
        Check if the IR file is of type 'raw'.
        """
        try:
            with open(irfile, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'type: raw' in content
        except UnicodeDecodeError:
            try:
                with open(irfile, 'r', encoding='cp1252') as f:
                    content = f.read()
                    return 'type: raw' in content
            except UnicodeDecodeError:
                logging.warning(f"Unable to read file '{irfile}' with UTF-8 or cp1252 encoding. Skipping.")
                return False
        except Exception as e:
            logging.error(f"Error reading file '{irfile}': {e}")
            return False

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

    def decode_ir_file(self, relative_path, ir_file):
        """
        Decode a single IR file.
        """
        input_file = f"{self.flipper_dir}{relative_path}/{ir_file}".replace("\\", "/")
        output_file = f"{self.parsed_dir}{relative_path}/{ir_file}".replace("\\", "/")

        logging.info(f"Decoding file: '{input_file}' to '{output_file}'.")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        self.create_directory(output_dir)

        # Close any running applications
        self.close_running_apps()

        # Decode the IR file
        decode_command = f"ir decode {input_file} {output_file}"
        response = self.send_command(decode_command)

        # Check response for success or failure
        if "Error" in response or "Failed" in response:
            logging.error(f"Failed to decode '{input_file}'. Response: {response}")
            self.failed_files.append(input_file)
            return False

        # Verify the file was created
        list_command = f"storage list {output_dir}"
        list_response = self.send_command(list_command)

        if ir_file in list_response:
            logging.info(f"Successfully decoded '{input_file}' to '{output_file}'.")
            return True
        else:
            logging.error(f"Decoded file '{output_file}' not found after decoding.")
            self.failed_files.append(input_file)
            return False

    def process_ir_files(self, ir_files):
        """
        Process all gathered IR files with a progress bar.
        """
        total_files = len(ir_files)
        if total_files == 0:
            logging.info("No IR files to process.")
            return

        logging.info(f"{total_files} files to process. Starting...")
        with tqdm(total=total_files, desc="Decoding IR Files", unit="file") as pbar:
            for relative_path, ir_file in ir_files:
                success = self.decode_ir_file(relative_path, ir_file)
                if success:
                    self.processed_count += 1
                pbar.update(1)

        logging.info(f"Finished. {self.processed_count} out of {total_files} files processed successfully.")
        if self.failed_files:
            logging.warning(f"{len(self.failed_files)} files failed to decode. Check the log for details.")

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
        default='Z:/scripts/ir files/Flipper-IRDB',
        help='Path to the IRDB on the system.'
    )
    parser.add_argument(
        '--flipper-dir',
        type=str,
        default='/ext/infrared/Flipper-IRDB/',
        help='Path to the IRDB on Flipper Zero.'
    )
    parser.add_argument(
        '--parsed-dir',
        type=str,
        default='/ext/infrared/parsed/',
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
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level.'
    )
    args = parser.parse_args()

    # Initialize and run the decoder
    decoder = FlipperIRDecoder(
        system_dir=args.system_dir,
        flipper_dir=args.flipper_dir,
        parsed_dir=args.parsed_dir,
        port=args.port,
        log_level=args.log_level,
        log_file=args.log_file
    )
    decoder.run()

    # Summary of failed decodings
    if decoder.failed_files:
        print("\nSummary of Failed Decodings:")
        for failed_file in decoder.failed_files:
            print(f" - {failed_file}")

if __name__ == "__main__":
    main()
