import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import face_recognition
import shutil

class ImagePlannerApp:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.root.title("Image Planner")
        self.root.geometry("1000x600")

        self.left_frame = tk.Frame(root, width=200, bg='lightgray')
        self.left_frame.pack(side="left", fill="y")
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.load_folder_button = tk.Button(self.left_frame, text="Load Folder", command=self.load_folder)
        self.load_folder_button.pack(pady=10)

        self.sort_images_button = tk.Button(self.left_frame, text="Sort Images by Faces", command=self.sort_images)
        self.sort_images_button.pack(pady=10)

        self.download_folders_button = tk.Button(self.left_frame, text="Download Sorted Folders", command=self.download_sorted_folders)
        self.download_folders_button.pack(pady=10)

        self.group_listbox = tk.Listbox(self.left_frame)
        self.group_listbox.pack(fill="y", pady=10)
        self.group_listbox.bind("<<ListboxSelect>>", self.display_group_images)
        self.group_listbox.bind("<Double-1>", self.rename_group)

        self.image_canvas = tk.Canvas(self.right_frame, bg="white")
        self.image_canvas.pack(fill="both", expand=True)
        self.image_canvas.bind("<Button-1>", self.on_image_click)

        self.image_paths = []
        self.thumbnails = []
        self.known_face_encodings = []
        self.known_face_paths = []
        self.groups = {}
        self.image_position_mapping = {}

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths.clear()
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        self.image_paths.append(os.path.join(root, file))
            messagebox.showinfo("Success", f"Loaded {len(self.image_paths)} images from folder.")
            self.display_images()

    def display_images(self):
        self.image_canvas.delete("all")
        self.thumbnails.clear()
        self.image_position_mapping.clear()

        x, y = 10, 10
        for image_path in self.image_paths:
            image = Image.open(image_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            image_id = self.image_canvas.create_image(x, y, anchor="nw", image=photo)
            self.thumbnails.append(photo)
            self.image_position_mapping[image_id] = image_path

            x += 110
            if x > self.root.winfo_width() - 110:
                x = 10
                y += 110

    def on_image_click(self, event):
        clicked_image_id = self.image_canvas.find_closest(event.x, event.y)
        image_path = self.image_position_mapping.get(clicked_image_id[0])

        if image_path:
            self.main_app.load_image_from_path(image_path)

    def sort_images(self):
        if not self.image_paths:
            messagebox.showwarning("Warning", "No images loaded.")
            return

        self.known_face_encodings.clear()
        self.known_face_paths.clear()
        self.groups.clear()
        self.group_listbox.delete(0, tk.END)

        for image_path in self.image_paths:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                face_encoding = face_encodings[0]
                match_found = False

                for i, known_encoding in enumerate(self.known_face_encodings):
                    match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
                    if match[0]:
                        group_name = f"Person_{i+1}"
                        self.groups[group_name].append(image_path)
                        match_found = True
                        break

                if not match_found:
                    self.known_face_encodings.append(face_encoding)
                    new_group_index = len(self.known_face_encodings)
                    group_name = f"Person_{new_group_index}"
                    self.groups[group_name] = [image_path]
                    self.group_listbox.insert(tk.END, group_name)

        messagebox.showinfo("Success", "Images sorted into groups by faces.")

    def display_group_images(self, event):
        selection = self.group_listbox.curselection()
        if selection:
            group_name = self.group_listbox.get(selection[0])
            self.image_canvas.delete("all")
            self.thumbnails.clear()

            x, y = 10, 10
            for image_path in self.groups.get(group_name, []):
                image = Image.open(image_path)
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)
                image_id = self.image_canvas.create_image(x, y, anchor="nw", image=photo)
                self.thumbnails.append(photo)
                self.image_position_mapping[image_id] = image_path
                x += 110
                if x > self.root.winfo_width() - 110:
                    x = 10
                    y += 110

    def rename_group(self, event):
        selection = self.group_listbox.curselection()
        if selection:
            group_name = self.group_listbox.get(selection[0])
            new_name = simpledialog.askstring("Rename Group", f"Enter new name for {group_name}:")
            if new_name:
                self.groups[new_name] = self.groups.pop(group_name)
                self.group_listbox.delete(selection[0])
                self.group_listbox.insert(selection[0], new_name)
                messagebox.showinfo("Success", f"Group renamed to '{new_name}'.")

    def download_sorted_folders(self):
        output_folder = filedialog.askdirectory(title="Select Folder to Save Sorted Groups")
        if output_folder:
            for group_name, image_paths in self.groups.items():
                group_folder = os.path.join(output_folder, group_name)
                os.makedirs(group_folder, exist_ok=True)
                for image_path in image_paths:
                    shutil.copy(image_path, group_folder)
            messagebox.showinfo("Success", f"Sorted folders downloaded to '{output_folder}'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePlannerApp(root, main_app=None)
    root.mainloop()
