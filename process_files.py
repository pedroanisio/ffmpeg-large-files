import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import shutil
import argparse

# Dependency check
def check_ffmpeg():
    """Ensure ffmpeg is installed and accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Please install it to use this script.")

# Logging setup
def setup_logging(log_file):
    """Configure logging."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    with open(log_file, "w") as log:
        log.write("=== Video Processing Log ===\n")
        log.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("=" * 30 + "\n\n")

# Get file info
def get_file_info(file_path):
    """Extract useful information about the file."""
    try:
        size = os.path.getsize(file_path)
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        return {
            "size_gb": size / (1024 ** 3),
            "last_modified": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        logging.error(f"Error getting file info for {file_path}: {e}")
        return None

# Find large files
def find_large_files(directory, size_limit_gb=15):
    """Find all .mkv files larger than the specified size in GB."""
    size_limit_bytes = size_limit_gb * (1024 ** 3)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > size_limit_bytes:
                    yield file_path

# Process a single file
def process_file(input_file, output_dir):
    """Process the file with ffmpeg."""
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_dir, filename)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
        "-i", input_file,
        "-map", "0:0", "-filter:v", "fps=24000/1001", "-c:v", "libx264", "-b:v",
        "5000k", "-profile:v", "high", "-level:v", "4.1", "-coder", "cabac", "-map",
        "0:1", "-c:a", "aac", "-b:a", "320k", "-ac", "6", "-disposition:a:0", "default",
        output_file
    ]
    result = subprocess.run(command)
    return result.returncode == 0, output_file

# Main script
def main(source_dir, output_dir, log_file, size_limit_gb, auto_confirm):
    setup_logging(log_file)
    check_ffmpeg()
    
    logging.info("Script started.")
    os.makedirs(output_dir, exist_ok=True)

    skipped_log = os.path.join(output_dir, "skipped_files.log")
    with open(skipped_log, "w") as log:
        pass  # Clear previous log
    
    for input_file in find_large_files(source_dir, size_limit_gb):
        file_info = get_file_info(input_file)
        if file_info:
            logging.info(f"Found file: {input_file} (Size: {file_info['size_gb']:.2f} GB, Last Modified: {file_info['last_modified']})")
            print(f"Found file: {input_file} (Size: {file_info['size_gb']:.2f} GB, Last Modified: {file_info['last_modified']})")
        else:
            logging.warning(f"Skipping file due to error retrieving info: {input_file}")
            continue

        if not auto_confirm:
            confirm = input("Do you want to process this file? (y/n): ").strip().lower()
            if confirm != "y":
                logging.info(f"File skipped: {input_file}")
                with open(skipped_log, "a") as log:
                    log.write(f"{input_file}\n")
                continue

        logging.info(f"Processing file: {input_file}")
        print(f"Processing: {input_file}")
        success, output_file = process_file(input_file, output_dir)

        if success:
            logging.info(f"Processing complete for: {input_file}")
            print(f"Processing complete for: {input_file}")
            shutil.move(output_file, input_file)
            logging.info(f"Replaced original file: {input_file}")
        else:
            logging.error(f"Error processing file: {input_file}")
            with open(skipped_log, "a") as log:
                log.write(f"{input_file}\n")
            if os.path.exists(output_file):
                os.remove(output_file)
                logging.info(f"Removed failed output file: {output_file}")
    
    logging.info("Script finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process large .mkv files.")
    parser.add_argument("--source", required=True, help="Source directory containing .mkv files.")
    parser.add_argument("--output", required=True, help="Output directory for processed files.")
    parser.add_argument("--log", default="/tmp/process_files.log", help="Log file path.")
    parser.add_argument("--size", type=int, default=15, help="Size limit in GB for processing files.")
    parser.add_argument("--auto-confirm", action="store_true", help="Automatically confirm processing without prompts.")
    args = parser.parse_args()

    try:
        main(args.source, args.output, args.log, args.size, args.auto_confirm)
    except Exception as e:
        logging.error(f"Script failed: {e}")
        print(f"Error: {e}")
