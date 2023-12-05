import cv2
import tkinter as tk
from tkinter import simpledialog


class ImageAnnotator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Annotator")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

        self.class_names = None
        self.current_class = None
        self.bbox = None

        self.is_capturing = False
        self.frame = None
        self.annotation_string = ''

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def set_class_names(self, class_names):
        self.class_names = class_names

    def annotate_frame(self, frame):
        self.frame = frame
        self.annotate_frame_internal()

    def annotate_frame_internal(self):
        self.bbox = cv2.selectROI('Annotation', self.frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow('Annotation')
        self.get_class_input()

    def get_class_input(self):
        choices = "\n".join([f'Enter {i} for {class_name}' for i, class_name in enumerate(self.class_names)])
        self.current_class = simpledialog.askstring('Class', choices)
        self.annotation_string = self.get_annotation_string()
        self.root.destroy()  # Close the Tkinter window after annotating

    def get_annotation_string(self):
        class_label = self.current_class
        x, y, w, h = self.bbox
        cx = (x + w / 2) / self.frame.shape[1]
        cy = (y + h / 2) / self.frame.shape[0]
        bw = w / self.frame.shape[1]
        bh = h / self.frame.shape[0]
        return f'{class_label} {cx} {cy} {bw} {bh}'

    def on_canvas_click(self, event):
        if not self.is_capturing:
            self.annotate_frame_internal()
