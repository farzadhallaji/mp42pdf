import argparse
import cv2
import os
import shutil
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def extract_frames(video_file, output_directory, gray_threshold, frame_skip_interval=None, frame_count_target=None):
    cap = cv2.VideoCapture(video_file)
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prev_frame = None
    frame_count = 0

    if frame_count_target:
        frame_skip_interval = max(total_frame_count // frame_count_target, 1)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip_interval == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            if prev_frame is not None:
                frame_diff = cv2.absdiff(gray_frame, prev_frame)
                _, threshold = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

                if cv2.countNonZero(threshold) > gray_threshold:
                    output_file = os.path.join(output_directory, f"frame_{frame_count:04d}.png")
                    cv2.imwrite(output_file, frame)

            prev_frame = gray_frame

        frame_count += 1

    cap.release()

def compile_frames_to_pdf(image_directory, output_pdf):
    image_files = sorted([os.path.join(image_directory, file) for file in os.listdir(image_directory)], key=natural_sort_key)
    if not image_files:
        print("No frames found.")
        return

    c = canvas.Canvas(output_pdf, pagesize=letter)

    for image_file in image_files:
        with Image.open(image_file) as img:
            width, height = img.size
            aspect_ratio = width / height

            if aspect_ratio >= 1:
                img_width = letter[0]
                img_height = letter[0] / aspect_ratio
            else:
                img_height = letter[1]
                img_width = letter[1] * aspect_ratio

            y_offset = letter[1] - img_height  # Adjust the y_offset to position the image at the top
            c.drawImage(image_file, 0, y_offset, img_width, img_height)
            c.showPage()

    c.save()

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Extract frames from an MP4 video and compile them into a PDF')
parser.add_argument('input_mp4', help='Path to the input MP4 file')
parser.add_argument('--skip', type=int, default=1, help='Number of frames to skip between extractions')
parser.add_argument('--num', type=int, default=None, help='Number of frames to extract')
parser.add_argument('--gray_threshold', type=int, default=500, help='Threshold for determine different frames (gray scale)')
args = parser.parse_args()

# Extract the base name of the input file
input_file_base = os.path.splitext(os.path.basename(args.input_mp4))[0]

# Create the output directory for frames
output_directory = f"{input_file_base}_frames"
os.makedirs(output_directory, exist_ok=True)

# Extract frames with significant changes
extract_frames(args.input_mp4, output_directory, gray_threshold=args.gray_threshold, frame_skip_interval=args.skip, frame_count_target=args.num)

# Generate the output PDF file path
output_pdf = f"{input_file_base}.pdf"

# Compile frames into a PDF
compile_frames_to_pdf(output_directory, output_pdf)

# Remove the frames directory
shutil.rmtree(output_directory)
