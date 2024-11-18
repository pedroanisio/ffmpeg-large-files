# Video Processor

A Python script to process large `.mkv` files using `ffmpeg`, applying specific transformations and replacing the original files.

## Features
- Processes `.mkv` files larger than a configurable size limit (default: 15GB).
- Uses `ffmpeg` to re-encode video and audio streams.
- Optionally replaces the original files after successful processing.
- Generates detailed logs for tracking.

## Requirements
- Python 3.8+
- `ffmpeg` installed and accessible in the system path.

## Installation
Clone the repository:
```bash
git clone https://github.com/pedroanisio/ffmpeg-large-files
cd ffmpeg-large-files
```

## Usage
Run the script with:
```bash
python process_files.py --source /path/to/source --output /path/to/output --log /path/to/log.log
```

Optional arguments:
- `--size`: Set file size limit in GB (default: 15).
- `--auto-confirm`: Automatically confirm file processing without user prompts.

```
python process_files.py --source /mnt/prod --output /mnt/stage/movies --log /tmp/process_files.log
```