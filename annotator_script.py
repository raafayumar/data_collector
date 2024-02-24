import cv2
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, font
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime


class AnnotationTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Annotation Correction Tool")

        self.classes = {0: "FOCUSED", 1: "SLEEPY", 2: "DISTRACTED"}
        self.frame_files = []
        self.frames_dir = None  # Initialize frames_dir attribute
        self.current_frame_index = 0
        self.metadata_filename = None
        self.metadata = None

        # Create frames
        self.cv_frame = tk.Frame(self.master)
        self.cv_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Add padding

        self.annotation_frame = tk.Frame(self.master)
        self.annotation_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)  # Add padding

        # Increase font size for labels
        label_font = font.Font(size=12)

        # Create image label
        self.image_label = tk.Label(self.cv_frame, font=label_font)
        self.image_label.pack(expand=True)  # Expand the label to fill the frame

        # Create filename label
        self.filename_label = tk.Label(self.cv_frame, text="", font=label_font)
        self.filename_label.pack()

        self.annotation_label = tk.Label(self.annotation_frame, text="Annotations: ", font=label_font)
        self.annotation_label.pack()

        # Create total frames label
        self.total_frames_label = tk.Label(self.master, text="Total Frames: 0", font=("Helvetica", 10))
        self.total_frames_label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)  # Adjust grid position

        self.instructions_label = tk.Label(self.master,
                                           text="Instructions:\nPress '0' for next frame.\nPress 'c' to change class.\nClose the window to continue to the next frame or to quit (press 'q').\nPress left arrow key for previous frame.",
                                           font=label_font)
        self.instructions_label.grid(row=2, column=0)  # Adjust grid position

        self.master.bind('<Key>', self.key_press)

        self.master.focus_force()  # Set focus to the application window
        self.master.grab_set()
        self.initialize_metadata()

    def initialize_metadata(self):
        self.frames_dir = os.path.normpath(filedialog.askdirectory())
        if self.frames_dir:
            metadata_dir = os.path.join(self.frames_dir, 'metadata')
            if not os.path.exists(metadata_dir):
                os.makedirs(metadata_dir)

            self.frame_files = [f for f in os.listdir(self.frames_dir) if f.endswith('.jpg')]
            # Update the total frames label
            self.total_frames_label.config(text=f"Total Frames: {len(self.frame_files)}")
            if self.frame_files:
                user_name = simpledialog.askstring('Enter User Name', 'Enter your name')
                self.metadata_filename = os.path.join(self.frames_dir, metadata_dir,
                                                      f"{user_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
                metadata_rows = []
                for frame_file in self.frame_files:
                    annotations = self.read_annotation(
                        os.path.join(self.frames_dir, os.path.splitext(frame_file)[0] + '.txt'))
                    metadata_rows.append(
                        {'Filename': frame_file, 'Previous Annotations': annotations, 'New Annotations': None})
                self.metadata = pd.DataFrame(metadata_rows)
                self.metadata.to_csv(self.metadata_filename, index=False)

                frame_path = os.path.join(self.frames_dir, self.frame_files[0])
                annotations = self.metadata.loc[0, 'Previous Annotations']
                self.display_image(cv2.imread(frame_path), annotations, self.frame_files[0])
            else:
                messagebox.showwarning("Warning", "No frames found in the directory.")
        else:
            messagebox.showerror("Error", "Frames directory not selected.")

    def display_image(self, frame, annotations, filename):
        for annotation in annotations:
            class_id = annotation[0]
            class_name = self.classes[class_id]
            bbox = annotation[1:]
            frame = self.draw_boxes(frame, [bbox], class_name)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.photo)

        annotation_text = '\n'.join([f"Class: {self.classes[a[0]]}, BBox: {a[1:]}" for a in annotations])
        self.annotation_label.config(text=f"Annotations: {annotation_text}\nFrame: {filename}")

        self.filename_label.config(text=f"Frame: {filename}")

    def draw_boxes(self, image, boxes, class_name):
        for box in boxes:
            x, y, w, h = box
            # Convert normalized coordinates to pixel values
            height, width, _ = image.shape
            left = int((x - w / 2) * width)
            top = int((y - h / 2) * height)
            right = int((x + w / 2) * width)
            bottom = int((y + h / 2) * height)
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)  # Changed box color to red
            cv2.putText(image, class_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255),
                        2)  # Changed text color to red
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
            line_split = [element.strip("'") for element in line_split]  # Remove single quotes
            corrected_annotations.append(line_split)
        with open(annotation_file, 'w') as f:
            for line in corrected_annotations:
                f.write(' '.join(line) + '\n')
        new_list = [[float(x) if '.' in x else int(x) for x in sublist] for sublist in corrected_annotations]

        return new_list

    def change_class_handler(self, annotation_file, new_class):
        previous_annotations = self.read_annotation(annotation_file)
        corrected_annotations = self.change_class(annotation_file, new_class)
        self.metadata.at[self.current_frame_index, 'New Annotations'] = corrected_annotations
        self.metadata.to_csv(self.metadata_filename, index=False)
        self.display_annotation_change(previous_annotations, corrected_annotations)

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
            self.master.quit()
        elif event.char == 'c':
            new_class = simpledialog.askinteger("Change Class",
                                                "Enter new class (0: FOCUSED, 1: SLEEPY, 2: DISTRACTED): ")
            if new_class is not None and new_class in self.classes.keys():
                annotation_file = os.path.join(self.frames_dir,
                                               os.path.splitext(self.frame_files[self.current_frame_index])[0] + '.txt')
                self.change_class_handler(annotation_file, new_class)
        elif event.keysym == 'Right':
            self.current_frame_index += 1
            if self.current_frame_index < len(self.frame_files):
                frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
                annotations = self.metadata.loc[self.current_frame_index, 'Previous Annotations']
                self.display_image(cv2.imread(frame_path), annotations, self.frame_files[self.current_frame_index])
            else:
                messagebox.showinfo("Info", "All frames processed.")
                self.master.quit()
        elif event.keysym == 'Left' and self.current_frame_index > 0:
            self.current_frame_index -= 1
            frame_path = os.path.join(self.frames_dir, self.frame_files[self.current_frame_index])
            annotations = self.metadata.loc[self.current_frame_index, 'Previous Annotations']
            self.display_image(cv2.imread(frame_path), annotations, self.frame_files[self.current_frame_index])


root = tk.Tk()
app = AnnotationTool(root)
root.mainloop()
