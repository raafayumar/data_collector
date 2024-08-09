import cv2
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, font
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime
import json


class AnnotationTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Annotation Correction Tool")

        self.classes = {0: "FOCUSED", 1: "SLEEPY", 2: "DISTRACTED"}
        self.frame_files = []
        self.frames_dir = None
        self.current_frame_index = 0
        self.metadata_filename = None
        self.metadata = None
        self.count = 0
        self.corrected_count = 0
        self.progress_filename = "progress.json"

        # Create frames
        self.cv_frame = tk.Frame(self.master)
        self.cv_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.annotation_frame = tk.Frame(self.master)
        self.annotation_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Increase font size for labels
        label_font = font.Font(size=12)

        # Create image label
        self.image_label = tk.Label(self.cv_frame, font=label_font)
        self.image_label.pack(expand=True, anchor="center")

        # Create filename label
        self.filename_label = tk.Label(self.cv_frame, text="", font=label_font)
        self.filename_label.pack()

        self.annotation_label = tk.Label(self.annotation_frame, text="Annotations: ", font=label_font)
        self.annotation_label.pack()

        # Create total frames label
        self.total_frames_label = tk.Label(self.master, text="Total Frames: 0", font=("Helvetica", 10))
        self.total_frames_label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        self.progress_label = tk.Label(self.master, text="Current frame: 0", font=("Helvetica", 10))
        self.progress_label.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

        self.instructions_label = tk.Label(self.master,
                                           text="Instructions:\nPress '0' for class FOCUSED.\nPress '1' for class SLEEPY.\nPress '2' for class DISTRACTED.\nPress left/right arrow keys to navigate frames.\nClose the window to quit (press 'q').",
                                           font=label_font)
        self.instructions_label.grid(row=2, column=0)

        self.master.bind('<Key>', self.key_press)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

        self.master.focus_force()
        self.master.grab_set()
        self.initialize_metadata()

    def initialize_metadata(self):
        self.frames_dir = os.path.normpath(filedialog.askdirectory())
        if self.frames_dir:
            metadata_dir = os.path.join(self.frames_dir, 'metadata')
            if not os.path.exists(metadata_dir):
                os.makedirs(metadata_dir)

            self.frame_files = [f for f in os.listdir(self.frames_dir) if f.endswith(('.jpeg', '.jpg', '.png'))]
            self.total_frames_label.config(text=f"Total Frames: {len(self.frame_files)}")
            if self.frame_files:
                user_name = simpledialog.askstring('Enter User Name', 'Enter your name')
                self.metadata_filename = os.path.join(self.frames_dir, metadata_dir,
                                                      f"{user_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
                metadata_rows = []
                for count, frame_file in enumerate(self.frame_files):
                    annotations = self.read_annotation(
                        os.path.join(self.frames_dir, os.path.splitext(frame_file)[0] + '.txt'))
                    metadata_rows.append(
                        {'Filename': frame_file, 'Previous Annotations': annotations, 'New Annotations': None})
                self.metadata = pd.DataFrame(metadata_rows)
                self.metadata.to_csv(self.metadata_filename, index=False)

                # Load progress if exists
                if os.path.exists(self.progress_filename):
                    with open(self.progress_filename, 'r') as f:
                        progress_data = json.load(f)
                        self.current_frame_index = progress_data.get('current_frame_index', 0)
                        self.corrected_count = progress_data.get('corrected_count', 0)

                frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
                annotations = self.metadata.loc[self.current_frame_index, 'Previous Annotations']
                self.display_image(cv2.imread(frame_path), annotations, self.frame_files[self.current_frame_index],
                                   self.current_frame_index)

            else:
                messagebox.showwarning("Warning", "No frames found in the directory.")
        else:
            messagebox.showerror("Error", "Frames directory not selected.")

    def display_image(self, frame, annotations, filename, frames):
        self.count += 1
        for annotation in annotations:
            class_id = annotation[0]
            class_name = self.classes[class_id]
            bbox = annotation[1:]
            frame = self.draw_boxes(frame, [bbox], class_name)

        # Crop the image to show the left side containing the driver's face plus some background
        frame = self.crop_image(frame, annotations)

        max_width = 1920
        max_height = 1080
        height, width, _ = frame.shape
        if width > max_width or height > max_height:
            if width / max_width > height / max_height:
                ratio = max_width / width
            else:
                ratio = max_height / height
            frame = cv2.resize(frame, (int(width * ratio), int(height * ratio)))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.photo)
        self.progress_label.config(text=f"Current frame: {frames}")
        annotation_text = '\n'.join([f"Class: {self.classes[a[0]]}, BBox: {a[1:]}" for a in annotations])
        self.annotation_label.config(text=f"Annotations: {annotation_text}\nFrame: {filename}")

        self.filename_label.config(text=f"Frame: {filename}")

    def crop_image(self, frame, annotations):
        # Find the bounding box of the driver's face (assuming it's the first annotation)
        if annotations:
            bbox = annotations[0][1:]
            height, width, _ = frame.shape
            x, y, w, h = bbox
            left = int((x - w / 2) * width)
            right = int((x + w / 2) * width)
            top = int((y - h / 2) * height)
            bottom = int((y + h / 2) * height)

            # Extend the bounding box by 25% in all directions
            padding_x = int(0.25 * width)
            padding_y = int(0.25 * height)
            left = max(0, left - padding_x)
            right = min(width, right + padding_x)
            top = max(0, top - padding_y)
            bottom = min(height, bottom + padding_y)

            # Crop the image to the extended bounding box
            frame = frame[top:bottom, left:right]
        return frame

    def draw_boxes(self, image, boxes, class_name):
        for box in boxes:
            x, y, w, h = box
            height, width, _ = image.shape
            left = int((x - w / 2) * width)
            top = int((y - h / 2) * height)
            right = int((x + w / 2) * width)
            bottom = int((y + h / 2) * height)
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(image, class_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        return image

    def read_annotation(self, annotation_file):
        with open(annotation_file, 'r') as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            data = line.strip().split()
            class_id = int(data[0])
            x, y, h, w = map(float, data[1:])
            annotations.append([class_id, x, y, h, w])
        return annotations

    def change_class(self, annotation_file, new_class):
        with open(annotation_file, 'r') as f:
            lines = f.readlines()
        corrected_annotations = []
        for line in lines:
            line_split = line.strip().split()
            old_class = line_split[0]
            line_split[0] = str(new_class)
            line_split = [element.strip("'") for element in line_split]
            corrected_annotations.append(line_split)
        with open(annotation_file, 'w') as f:
            for line in corrected_annotations:
                f.write(' '.join(line) + '\n')
        new_list = [[float(x) if '.' in x else int(x) for x in sublist] for sublist in corrected_annotations]

        return new_list

    def change_class_handler(self, annotation_file, new_class):
        previous_annotations = self.read_annotation(annotation_file)
        corrected_annotations = self.change_class(annotation_file, new_class)
        self.metadata.at[self.current_frame_index, 'Previous Annotations'] = corrected_annotations
        self.metadata.to_csv(self.metadata_filename, index=False)
        self.display_annotation_change(previous_annotations, corrected_annotations)

        # Refresh the image display with updated annotations
        frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
        self.display_image(cv2.imread(frame_path), corrected_annotations, self.frame_files[self.current_frame_index],
                           self.current_frame_index)

    def display_annotation_change(self, previous_annotations, corrected_annotations):
        previous_text = '\n'.join(
            [f"Class: {self.classes.get(a[0], 'Unknown')}, BBox: {a[1:]}" for a in previous_annotations])
        corrected_text = '\n'.join(
            [f"Class: {self.classes.get(a[0], 'Unknown')}, BBox: {', '.join(map(str, a[1:]))}" for a in
             corrected_annotations])
        corrected_text = corrected_text.replace("'", "")
        self.annotation_label.config(
            text=f"Previous annotations:\n{previous_text}\nCorrected annotations:\n{corrected_text}")

    def key_press(self, event):
        if event.char == 'q':
            self.on_closing()
        elif event.char in ['0', '1', '2']:
            self.corrected_count += 1
            new_class = int(event.char)
            if new_class in self.classes.keys():
                annotation_file = os.path.join(self.frames_dir,
                                               os.path.splitext(self.frame_files[self.current_frame_index])[0] + '.txt')
                self.change_class_handler(annotation_file, new_class)
        elif event.keysym == 'Right':
            if self.current_frame_index < len(self.frame_files) - 1:
                self.current_frame_index += 1
                frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
                annotations = self.metadata.loc[self.current_frame_index, 'Previous Annotations']
                self.display_image(cv2.imread(frame_path), annotations, self.frame_files[self.current_frame_index],
                                   self.current_frame_index)
            else:
                messagebox.showinfo("Info", f"{self.corrected_count} files corrected")
                messagebox.showinfo("Info", "All frames processed.")
                self.master.quit()
        elif event.keysym == 'Left':
            if self.current_frame_index > 0:
                self.current_frame_index -= 1
                self.count -= 1
                frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
                annotations = self.metadata.loc[self.current_frame_index, 'Previous Annotations']
                self.display_image(cv2.imread(frame_path), annotations, self.frame_files[self.current_frame_index],
                                   self.current_frame_index)

    def on_closing(self):
        progress_data = {
            'current_frame_index': self.current_frame_index,
            'corrected_count': self.corrected_count
        }
        with open(self.progress_filename, 'w') as f:
            json.dump(progress_data, f)
        self.master.quit()


root = tk.Tk()
app = AnnotationTool(root)
root.mainloop()
