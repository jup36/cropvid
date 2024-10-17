import os
import ffmpeg
import cv2
import re
import numpy as np


class VideoCropper:
    def __init__(self, directory, suffix="cropped", search_string="cropped", x=80, y=110, width=108, height=100):
        self.directory = directory
        self.suffix = suffix
        self.search_string = search_string
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def create_directory_to_save_cropped(self):
        parent_dir, dir_name = os.path.split(self.directory)

        # Create the new directory name by adding the suffix, e.g., cropped
        new_dir_name = dir_name + '_' + self.suffix

        # Create the new directory path
        new_dir_path = os.path.join(parent_dir, new_dir_name)

        if not os.path.exists(new_dir_path):
            try:
                os.mkdir(new_dir_path)
                print(f"Directory '{new_dir_path}' created.")
            except OSError as e:
                print(f"Error creating directory: {e}")
            else:
                print(f"Directory '{new_dir_path}' already exists.")
        return new_dir_path

    def select_uncropped_files(self):
        matching_files = []
        for filename in os.listdir(self.directory):
            if self.search_string not in filename:
                matching_files.append(filename)
        return matching_files

    def get_first_file_with_order(self):
        files = [f for f in os.listdir(self.directory) if f.endswith('.mp4')]
        files.sort(key=lambda x: int(re.search(r'_(\d{1,3})\.mp4', x).group(1)))
        #files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

        if files:
            return os.path.join(self.directory, files[0])
        else:
            return None

    def get_frame_size(self):
        # List and sort .mp4 files using regex
        mp4_files = [f for f in os.listdir(self.directory) if f.endswith('.mp4')]
        mp4_files.sort(key=lambda x: int(re.search(r'_(\d{1,3})\.mp4', x).group(1)))

        # Process only the first file
        if mp4_files:
            first_file = mp4_files[0]
            filepath = os.path.join(self.directory, first_file)
            cap = cv2.VideoCapture(filepath)

            if cap.isOpened():
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                print(f"{first_file}: Width = {int(width)}px, Height = {int(height)}px")
            else:
                print(f"Failed to open {first_file}")

            cap.release()
        else:
            print("No MP4 files found in the directory.")

    def crop_videos(self):
        matching_files = self.select_uncropped_files()
        cropped_path = self.create_directory_to_save_cropped()

        for filename in matching_files:
            input_file = os.path.join(self.directory, filename)
            output_file = os.path.join(cropped_path, filename[:-4] + "_cropped" + ".mp4")
            (
                ffmpeg.input(input_file)
                .crop(self.x, self.y, self.width, self.height)
                .output(output_file)
                .run(overwrite_output=True)
            )

    def display_and_confirm_cropping(self, input_file):
        cap = cv2.VideoCapture(input_file)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error reading video frame.")
            return False

        cropped_frame = frame[self.y:self.y + self.height, self.x:self.x + self.width]

        # Create a larger display window
        enlarged_frame = cv2.resize(cropped_frame, None, fx=2, fy=2)

        # Create a resizable window in the foreground
        cv2.namedWindow("Cropped Frame", cv2.WINDOW_NORMAL)

        should_continue = True  # Flag to control loop
        while should_continue:
            display_frame = enlarged_frame.copy()

            # Draw 'Yes' and 'No' buttons
            cv2.putText(display_frame, "Y", (40, enlarged_frame.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, "N", (enlarged_frame.shape[1] - 100, enlarged_frame.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Cropped Frame", display_frame)
            key = cv2.waitKey(0)

            if key == ord('y'):
                cv2.destroyAllWindows()
                should_continue = False
                return True
            elif key == ord('n'):
                cv2.destroyAllWindows()
                should_continue = False
                return False

    def interactive_cropping(self):
        input_file = self.get_first_file_with_order()
        while True:
            if not self.display_and_confirm_cropping(input_file):
                new_x = int(input(f"Enter new value for x ({self.x}): ") or self.x)
                new_y = int(input(f"Enter new value for y ({self.y}): ") or self.y)
                new_width = int(input(f"Enter new value for width ({self.width}): ") or self.width)
                new_height = int(input(f"Enter new value for height ({self.height}): ") or self.height)

                self.x, self.y, self.width, self.height = new_x, new_y, new_width, new_height
            else:
                break


"""
# Example usage
video_directory = '/path/to/directory'
cropper = VideoCropper(directory)
search_string = 'example'
x = 1000
y = 1000
width = 1000
height = 1000

cropper.crop_videos(search_string, x, y, width, height)
"""