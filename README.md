# mp42pdf
## Extract Presentation Slides from MP4 Video (Non-AI Approach)

#### Requirements

`pip install -r requirements.txt`: To install the packages, you can use this command in your terminal

#### Usage
`python mp42pdf.py [-h] [--skip SKIP] [--num NUM] [--gray_threshold GRAY_THRESHOLD] input_mp4`

- positional arguments:
  `input_mp4`             Path to the input MP4 file

- optional arguments:
  `-h`, `--help` show this help message and exit
  `--skip` Number of frames to skip between extractions
  `--num` Number of frames to extract
  `--gray_threshold` Threshold for determining different frames (grayscale)
