import os
import sys
import subprocess
import importlib.util
import traceback
import time
import gc

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_package(package):
    if importlib.util.find_spec(package) is None:
        print(f"{package} not found. Installing...")
        install_package(package)

# Ensure required packages are installed
ensure_package("tqdm")

import difflib
import argparse
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(filename='ir_comparison_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read().splitlines()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(content))
        return True
    except Exception as e:
        logging.error(f"Error writing file {file_path}: {str(e)}")
        return False

def extract_button_info(content):
    buttons = []
    current_button = {}
    for line in content:
        line = line.strip()
        if line.startswith('name:'):
            if current_button:
                buttons.append(current_button)
            current_button = {'name': line.split(':')[1].strip(), 'lines': [line]}
        elif line.startswith(('type:', 'protocol:', 'address:', 'command:')):
            current_button[line.split(':')[0]] = line.split(':')[1].strip()
            current_button['lines'].append(line)
    if current_button:
        buttons.append(current_button)
    return buttons

def clean_and_deduplicate(original_content, decoded_content):
    # Extract initial comment block
    initial_comments = []
    for line in original_content:
        if line.strip().startswith('#') or line.startswith('Filetype:') or line.startswith('Version:'):
            initial_comments.append(line)
        else:
            break  # Stop when we hit the first non-comment line

    decoded_buttons = extract_button_info(decoded_content)
    
    # Remove duplicates
    unique_buttons = {}
    duplicates_removed = 0
    for button in decoded_buttons:
        if 'name' in button and 'protocol' in button and 'address' in button and 'command' in button:
            signature = (button['name'], button['protocol'], button['address'], button['command'])
            if signature not in unique_buttons:
                unique_buttons[signature] = button
            else:
                duplicates_removed += 1

    # Reconstruct the file content
    cleaned_content = initial_comments  # Start with the initial comments
    
    # Add buttons with single comment lines in between
    for i, button in enumerate(unique_buttons.values()):
        if i > 0:
            cleaned_content.append('#')
        cleaned_content.extend(button['lines'])

    return cleaned_content, duplicates_removed

def compare_files(original_file, decoded_file):
    try:
        original_content = read_file(original_file)
        decoded_content = read_file(decoded_file)
        
        if original_content is None or decoded_content is None:
            return None
        
        # Clean and deduplicate the decoded content
        cleaned_content, duplicates_removed = clean_and_deduplicate(original_content, decoded_content)
        
        # Write the cleaned content back to the decoded file
        if not write_file(decoded_file, cleaned_content):
            logging.error(f"Failed to write cleaned content to {decoded_file}")
            return None

        # Compare original content with cleaned content
        differ = difflib.Differ()
        diff = list(differ.compare(original_content, cleaned_content))
        
        # Calculate difference ratio
        similarity = difflib.SequenceMatcher(None, ''.join(original_content), ''.join(cleaned_content)).ratio()
        difference_ratio = 1 - similarity
        
        # Check for lost comments
        original_comments = [line for line in original_content if line.strip().startswith('#')]
        cleaned_comments = [line for line in cleaned_content if line.strip().startswith('#')]
        lost_comments = [comment for comment in original_comments if comment not in cleaned_comments]
        
        return {
            'difference_ratio': difference_ratio,
            'lost_comments': len(lost_comments),
            'duplicates_removed': duplicates_removed,
            'diff_summary': summarize_diff(diff)
        }
    except Exception as e:
        logging.error(f"Error comparing files {original_file} and {decoded_file}: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def summarize_diff(diff):
    added = sum(1 for line in diff if line.startswith('+ '))
    removed = sum(1 for line in diff if line.startswith('- '))
    changed = sum(1 for line in diff if line.startswith('? '))
    return f"Added: {added}, Removed: {removed}, Changed: {changed}"

def analyze_directories(original_dir, decoded_dir, threshold=0.1, file_limit=None):
    results = []
    skipped_files = []
    processed_files = 0
    
    # Get total number of .ir files for progress bar
    total_files = sum(1 for root, _, files in os.walk(original_dir) for file in files if file.endswith('.ir'))
    
    with tqdm(total=total_files, desc="Analyzing files", unit="file") as pbar:
        for root, _, files in os.walk(original_dir):
            for file in files:
                if file.endswith('.ir'):
                    try:
                        original_file = os.path.join(root, file)
                        relative_path = os.path.relpath(original_file, original_dir)
                        decoded_file = os.path.join(decoded_dir, relative_path)
                        
                        logging.debug(f"Processing file: {relative_path}")
                        
                        if os.path.exists(decoded_file):
                            comparison = compare_files(original_file, decoded_file)
                            if comparison is not None:
                                if comparison['difference_ratio'] > threshold or comparison['lost_comments']:
                                    results.append({
                                        'file': relative_path,
                                        'difference_ratio': comparison['difference_ratio'],
                                        'lost_comments': comparison['lost_comments'],
                                        'diff_summary': comparison['diff_summary']
                                    })
                        else:
                            skipped_files.append(relative_path)
                        
                        processed_files += 1
                        pbar.update(1)
                        
                        if file_limit and processed_files >= file_limit:
                            logging.info(f"Reached file limit of {file_limit}. Stopping analysis.")
                            return results, skipped_files
                        
                        # Force garbage collection every 1000 files
                        if processed_files % 1000 == 0:
                            gc.collect()
                            
                    except Exception as e:
                        logging.error(f"Error processing file {file}: {str(e)}")
                        logging.error(traceback.format_exc())
                        skipped_files.append(relative_path)
                        pbar.update(1)
    
    return results, skipped_files

def main(original_dir, decoded_dir, threshold=0.1, output_file=None, file_limit=None):
    print("Starting analysis...")
    logging.info("Starting analysis...")
    
    start_time = time.time()
    results, skipped_files = analyze_directories(original_dir, decoded_dir, threshold, file_limit)
    end_time = time.time()
    
    logging.info(f"Analysis completed in {end_time - start_time:.2f} seconds")
    
    # Sort results by difference ratio
    results.sort(key=lambda x: x['difference_ratio'], reverse=True)
    
    print(f"\nFound {len(results)} files with significant differences:")
    for result in results[:10]:  # Print only the top 10 results
        print(f"\nFile: {result['file']}")
        print(f"Difference Ratio: {result['difference_ratio']:.2f}")
        print(f"Lost Comments: {result['lost_comments']}")
        print(f"Diff Summary: {result['diff_summary']}")
    
    if len(results) > 10:
        print(f"... and {len(results) - 10} more files")
    
    print(f"\nSkipped {len(skipped_files)} files (not found in decoded directory or error in processing)")
    
    if output_file:
        print(f"\nWriting summarized results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write("Files with significant differences:\n")
            for result in results:
                out_file.write(f"\nFile: {result['file']}\n")
                out_file.write(f"Difference Ratio: {result['difference_ratio']:.2f}\n")
                out_file.write(f"Lost Comments: {result['lost_comments']}\n")
                out_file.write(f"Diff Summary: {result['diff_summary']}\n")
            
            out_file.write("\nSkipped files:\n")
            for skipped in skipped_files:
                out_file.write(f" - {skipped}\n")
        print(f"Summarized results written to {output_file}")
    
    logging.info("Analysis results written to output file")

if __name__ == "__main__":
    # Default values for IDE usage
    DEFAULT_ORIGINAL_DIR = r"Z:\scripts\ir files\Flipper-IRDB-main"
    DEFAULT_DECODED_DIR = r"Z:\scripts\ir files\DECODED-IRDB"
    DEFAULT_THRESHOLD = 0.1
    DEFAULT_OUTPUT_FILE = "ir_comparison_results.txt"
    DEFAULT_FILE_LIMIT = None  # Set to a number if you want to limit the files processed

    # Check if script is run from command line
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Compare original and decoded IR files.")
        parser.add_argument("original_dir", help="Path to the original IRDB directory")
        parser.add_argument("decoded_dir", help="Path to the decoded IRDB directory")
        parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Difference ratio threshold (default: 0.1)")
        parser.add_argument("--output", help="Output file for detailed results")
        parser.add_argument("--file-limit", type=int, help="Limit the number of files to process")
        args = parser.parse_args()

        main(args.original_dir, args.decoded_dir, args.threshold, args.output, args.file_limit)
    else:
        # Running in IDE
        main(DEFAULT_ORIGINAL_DIR, DEFAULT_DECODED_DIR, DEFAULT_THRESHOLD, DEFAULT_OUTPUT_FILE, DEFAULT_FILE_LIMIT)

print("\nAnalysis complete. Check 'ir_comparison_debug.log' for detailed logs.")