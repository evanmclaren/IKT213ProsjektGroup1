import os
import cv2
import tkinter as tk
from tkinter import filedialog, simpledialog, Button, Toplevel, Scale, HORIZONTAL, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from tools import ScaleTool, TranslateTool, DrawTool, HistoryTool, RotateTool
from layer import Layer
from filter import Filter
from facial_recognition import SunglassesFilter
from Planner import ImagePlannerApp


class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CDG")
        self.root.geometry("800x600")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side="right", fill="y")

        self.layers_frame = ttk.Frame(self.notebook)
        self.filters_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.layers_frame, text="Layers")
        self.notebook.add(self.filters_frame, text="Filters")

        layer_label = tk.Label(self.layers_frame, text="Layers", bg="lightgray", font=("Arial", 12, "bold"))
        layer_label.pack(pady=10)

        self.layer_listbox = tk.Listbox(self.layers_frame)
        self.layer_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.toggle_visibility_button = tk.Checkbutton(self.layers_frame, text="Toggle Visibility",
                                                       command=self.toggle_layer_visibility)
        self.toggle_visibility_button.pack(fill="x", padx=10, pady=5)

        self.add_layer_button = tk.Button(self.layers_frame, text="Add Layer", command=self.add_layer)
        self.add_layer_button.pack(fill="x", padx=10, pady=5)

        self.delete_layer_button = tk.Button(self.layers_frame, text="Delete Layer", command=self.delete_layer)
        self.delete_layer_button.pack(fill="x", padx=10, pady=5)

        self.resize_canvas_button = tk.Button(self.layers_frame, text="Resize Canvas", command=self.resize_canvas)
        self.resize_canvas_button.pack(fill="x", padx=10, pady=5)

        self.apply_blur_button = tk.Button(self.layers_frame, text="Apply Blur", command=self.apply_blur_filter_with_popup)
        self.apply_blur_button.pack(fill="x", padx=10, pady=5)

        self.image_planner_button = tk.Button(self.layers_frame, text="Open Image Planner", command=self.open_image_planner)
        self.image_planner_button.pack(fill="x", padx=10, pady=5)


# Sunglasses -------------
        filters_label = tk.Label(self.filters_frame, text="Filters", bg="lightgray", font=("Arial", 12, "bold"))
        filters_label.pack(pady=10)

        sunglasses_image = Image.open("sunglasses.png")
        sunglasses_image.thumbnail((100, 100))  # Resize to thumbnail
        sunglasses_photo = ImageTk.PhotoImage(sunglasses_image)

        filter_button = tk.Button(self.filters_frame, image=sunglasses_photo, command=self.apply_sunglasses_filter)
        filter_button.image = sunglasses_photo  # Keep reference to avoid garbage collection
        filter_button.pack(pady=5)
# Sunglasses --------------



        self.canvas = tk.Canvas(self.main_frame, bg="gray")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.button_panel = tk.Frame(root)
        self.button_panel.pack(side="bottom", fill="x")

# Buttons ----------------
        self.save_button = tk.Button(self.button_panel, text="Save Image", command=self.save_image)
        self.save_button.pack(side="left", padx=10, pady=10)

        self.load_button = tk.Button(self.button_panel, text="Load Image", command=self.load_image)
        self.load_button.pack(side="left", padx=10, pady=10)

        self.scale_button = tk.Button(self.button_panel, text="Scale Image", command=self.toggle_scaling)
        self.scale_button.pack(side="left", padx=10, pady=10)

        self.translate_button = tk.Button(self.button_panel, text="Translate Image", command=self.toggle_translation)
        self.translate_button.pack(side="left", padx=10, pady=10)

        self.draw_button = tk.Button(self.button_panel, text="Draw Mode: OFF", command=self.toggle_drawing)
        self.draw_button.pack(side="left", padx=10, pady=10)

        self.undo_button = tk.Button(self.button_panel, text="Undo", command=self.undo)
        self.undo_button.pack(side="left", padx=10, pady=10)

        self.redo_button = tk.Button(self.button_panel, text="Redo", command=self.redo)
        self.redo_button.pack(side="left", padx=10, pady=10)


# Initialize tools ----------
        self.scale_tool = ScaleTool()
        self.translate_tool = TranslateTool()
        self.draw_tool = DrawTool()
        self.history_tool = HistoryTool()
        self.filter_tool = Filter()

# Variables -----------------
        self.layers = []
        self.image = None
        self.original_image = None
        self.scale_factor = 1.0
        self.scaling = False
        self.drawing = False
        self.translating = False
        self.brush_strokes = []
        self.offset = [0, 0]
        self.sunglasses_filter = SunglassesFilter()


        self.canvas.bind("<ButtonPress-1>", self.start_action)
        self.canvas.bind("<B1-Motion>", self.perform_action)
        self.canvas.bind("<ButtonRelease-1>", self.end_action)
        self.canvas.bind("<Configure>", self.on_resize)
        self.layer_listbox.bind("<<ListboxSelect>>", self.on_layer_select)


# ------- IMAGE PLANNER --------------------------------------#

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
            image_id = self.image_canvas.create_image(x, y, anchor="nw", image=photo, tags="thumbnail")
            self.thumbnails.append(photo)
            self.image_position_mapping[image_id] = image_path

            x += 110
            if x > self.root.winfo_width() - 110:
                x = 10
                y += 110

    def on_image_click(self, event):
        # Get the ID of the clicked item on the canvas
        clicked_item = self.image_canvas.find_withtag("current")

        # Check if the clicked item has the "thumbnail" tag
        if clicked_item and "thumbnail" in self.image_canvas.gettags(clicked_item[0]):
            # Retrieve the image path corresponding to the clicked thumbnail
            image_path = self.image_position_mapping.get(clicked_item[0])
            if image_path:
                # Call the main app's method to load the selected image
                self.main_app.load_image_from_path(image_path)
        else:
            print("Click ignored. Only thumbnails can load images.")


    def open_image_planner(self):
        planner_window = Toplevel(self.root)
        image_planner_app = ImagePlannerApp(planner_window, main_app=self)

    def load_image_from_path(self, image_path):
        if image_path:
            self.image = cv2.imread(image_path)
            if self.image is not None:
                self.original_image = self.image.copy()
                self.scale_factor = 1.0
                self.image_offset = [0, 0]
                self.brush_strokes.clear()

                image_height, image_width = self.image.shape[:2]

                # Add a white base layer
                if len(self.layers) == 0 or self.layers[0].name != "Base Layer":
                    base_layer = Layer(image_width, image_height, name="Base Layer")
                    base_image = Image.new("RGBA", (image_width, image_height), (255, 255, 255, 255))
                    base_layer.update_image(base_image)
                    self.layers.insert(0, base_layer)  # First layer as base.

                # Create new layer for the loaded image
                new_layer = Layer(image_width, image_height, name=f"Layer {len(self.layers) + 1}")
                new_layer.update_image(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGBA)))
                self.layers.append(new_layer)
                self.active_layer_index = len(self.layers) - 1  # Set the new layer as active


                self.canvas.config(width=image_width, height=image_height)
                self.canvas.config(scrollregion=(0, 0, image_width, image_height))
                self.root.geometry(f"{image_width}x{image_height + 100}")


                self.display_layers()
                self.update_layer_listbox()

#---------------------------------------------------------------------------

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is not None:
                self.original_image = self.image.copy()
                self.scale_factor = 1.0
                self.image_offset = [0, 0]
                self.brush_strokes.clear()

                image_height, image_width = self.image.shape[:2]
                if len(self.layers) == 0 or self.layers[0].name != "Base Layer":
                    base_layer = Layer(image_width, image_height, name="Base Layer")
                    base_image = Image.new("RGBA", (image_width, image_height), (255, 255, 255, 255))
                    base_layer.update_image(base_image)
                    self.layers.insert(0, base_layer)

                new_layer = Layer(image_width, image_height, name=f"Layer {len(self.layers) + 1}")
                new_layer.update_image(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGBA)))
                self.layers.append(new_layer)
                self.active_layer_index = len(self.layers) - 1


                self.canvas.config(width=image_width, height=image_height)
                self.canvas.config(scrollregion=(0, 0, image_width, image_height))
                self.root.geometry(f"{image_width}x{image_height + 100}")

                self.display_layers()
                self.update_layer_listbox()


    def add_layer(self):
        if len(self.layers) > 0:
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        else:
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        new_layer = Layer(width, height, name=f"Layer {len(self.layers) + 1}")
        transparent_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        new_layer.update_image(transparent_image)

        self.layers.append(new_layer)
        self.active_layer_index = len(self.layers) - 1
        self.display_layers()


        action_type = "add_layer"
        params = {
            "layer_index": self.active_layer_index
        }
        self.history_tool.record_action(action_type, params)


        self.update_layer_listbox()

    def delete_layer(self):
        selection = self.layer_listbox.curselection()
        if selection:
            self.active_layer_index = selection[0]
            deleted_layer = self.layers[self.active_layer_index]

            action_type = "delete_layer"
            params = {
                "layer_index": self.active_layer_index,
                "layer_data": deleted_layer
            }
            self.history_tool.record_action(action_type, params)
            del self.layers[self.active_layer_index]

            if len(self.layers) > 0:
                self.active_layer_index = min(self.active_layer_index, len(self.layers) - 1)
            else:
                self.active_layer_index = -1

            self.update_layer_listbox()
            self.display_layers()

            print(f"Deleted Layer: {deleted_layer.name}")
        else:
            print("No layer selected to delete.")

    def toggle_layer_visibility(self):
        if self.active_layer_index != -1:
            layer = self.layers[self.active_layer_index]
            layer.visible = not layer.visible
            self.display_layers()
            self.update_toggle_visibility_button()

    def update_toggle_visibility_button(self):
        if self.active_layer_index != -1:
            layer = self.layers[self.active_layer_index]
            if layer.visible:
                self.toggle_visibility_button.select()
            else:
                self.toggle_visibility_button.deselect()
        else:
            self.toggle_visibility_button.deselect()

    def update_layer_listbox(self):
        self.layer_listbox.delete(0, tk.END)

        # Populate the listbox with current layers
        for index, layer in enumerate(self.layers):
            self.layer_listbox.insert(tk.END, f"Layer {index + 1}")

        # Update the toggle visibility button state
        self.update_toggle_visibility_button()



    def resize_canvas(self):
        new_width = simpledialog.askinteger("Resize Canvas", "Enter new canvas width:")
        new_height = simpledialog.askinteger("Resize Canvas", "Enter new canvas height:")
        if new_width and new_height:
            previous_width = self.canvas.winfo_width()
            previous_height = self.canvas.winfo_height()

            base_layer = None
            if len(self.layers) > 0 and self.layers[0].name == "Base Layer":
                base_layer = self.layers[0]
                previous_base_layer_size = base_layer.get_image().size
            else:
                previous_base_layer_size = (previous_width, previous_height)

            self.canvas.config(width=new_width, height=new_height)
            self.canvas.config(scrollregion=(0, 0, new_width, new_height))
            self.root.geometry(f"{new_width}x{new_height + 100}")  # +100 for buttons space

            if base_layer:
                base_image = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
                base_layer.update_image(base_image)

            action_type = "resize_canvas"
            params = {
                "previous_width": previous_width,
                "previous_height": previous_height,
                "new_width": new_width,
                "new_height": new_height,
                "previous_base_layer_size": previous_base_layer_size
            }
            self.history_tool.record_action(action_type, params)
            self.display_layers()

    def display_layers(self):
        self.canvas.delete("all")
        for layer in self.layers:
            if layer.visible and layer.image is not None:
                layer_image = ImageTk.PhotoImage(layer.get_image())
                x_offset, y_offset = layer.get_offset()
                self.canvas.create_image(x_offset, y_offset, anchor="nw", image=layer_image)
                layer.tk_image = layer_image  # Store the image reference to prevent garbage collection
        self.draw_brush_strokes()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_layer_select(self, event):
        selection = self.layer_listbox.curselection()
        if selection:
            self.active_layer_index = selection[0]  # Update the active layer index
            print(f"Active layer updated to: {self.active_layer_index}")
        else:
            self.active_layer_index = -1  # No selection

    def save_image(self):
        if len(self.layers) == 0:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        final_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))

        for layer in self.layers:
            if layer.visible and layer.image is not None:
                x_offset, y_offset = layer.offset
                final_image.alpha_composite(layer.get_image(), dest=(x_offset, y_offset))


        final_image_draw = ImageDraw.Draw(final_image)
        for layer in self.layers:
            if layer.visible:
                for stroke in layer.brush_strokes:
                    if len(stroke.points) > 1:
                        for i in range(1, len(stroke.points)):
                            x1, y1 = stroke.points[i - 1]
                            x2, y2 = stroke.points[i]
                            final_image_draw.line([(x1, y1), (x2, y2)], fill=stroke.color, width=stroke.width)


        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("BMP files", "*.bmp")])
        if file_path:
            final_image.save(file_path)
            print(f"Image saved to {file_path}")

    def draw_brush_strokes(self):
        """Draw all brush strokes on the canvas from all layers."""
        self.canvas.delete("strokes")

        # Get scroll offsets in pixels
        x_scroll_offset = self.canvas.xview()[0] * self.canvas.winfo_width()
        y_scroll_offset = self.canvas.yview()[0] * self.canvas.winfo_height()

        for layer in self.layers:
            if layer.visible:
                for stroke in layer.brush_strokes:
                    if len(stroke.points) > 1:
                        for i in range(1, len(stroke.points)):
                            x1 = stroke.points[i - 1][0] * self.scale_factor + layer.offset[0] - x_scroll_offset
                            y1 = stroke.points[i - 1][1] * self.scale_factor + layer.offset[1] - y_scroll_offset
                            x2 = stroke.points[i][0] * self.scale_factor + layer.offset[0] - x_scroll_offset
                            y2 = stroke.points[i][1] * self.scale_factor + layer.offset[1] - y_scroll_offset
                            self.canvas.create_line(
                                x1, y1, x2, y2, fill=stroke.color, width=stroke.width, tags="strokes"
                            )

    def on_resize(self, event):
        if len(self.layers) > 0:
            self.display_layers()


    def toggle_scaling(self):
        self.scaling = not self.scaling
        self.drawing = False
        self.translating = False
        self.update_button_texts()

    def toggle_drawing(self):
        self.drawing = not self.drawing
        self.scaling = False
        self.translating = False
        self.update_button_texts()

    def toggle_translation(self):
        self.translating = not self.translating
        self.drawing = False
        self.scaling = False
        self.update_button_texts()

    def update_button_texts(self):
        self.scale_button.config(text="Scaling Mode: ON" if self.scaling else "Scaling Mode: OFF")
        self.draw_button.config(text="Draw Mode: ON" if self.drawing else "Draw Mode: OFF")
        self.translate_button.config(text="Translate Mode: ON" if self.translating else "Translate Mode: OFF")




#--------- PERFORM ACTION ------------------------------------------------#
    def start_action(self, event):
        if self.active_layer_index == -1:
            return

        active_layer = self.layers[self.active_layer_index]

        if self.scaling:
            self.previous_scale = self.scale_factor
            self.scale_tool.start_action(event)
        elif self.translating:
            self.previous_offset = active_layer.offset[:]
            self.translate_tool.start_action(event, active_layer.offset)
        elif self.drawing:
            self.current_stroke = self.draw_tool.start_action(event, active_layer.offset, self.scale_factor)
            active_layer.brush_strokes.append(self.current_stroke)

        elif self.rotating:
            self.rotate_tool.start_action(event)
            self.previous_angle = self.angle


    def perform_action(self, event):
        if self.active_layer_index == -1:
            return  # No active layer to perform actions on

        active_layer = self.layers[self.active_layer_index]

        if self.scaling and self.original_image is not None:
            # Perform scaling for the active layer
            self.image, self.scale_factor = self.scale_tool.perform_action(event, self.original_image,
                                                                           self.scale_factor)
            active_layer.update_image(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGBA)))
            self.display_layers()

        elif self.translating:
            # Perform the translation for the active layer
            self.translate_tool.perform_action(event, active_layer.offset)
            self.display_layers()  # Redraw the entire canvas to reflect changes in positions

        elif self.drawing:
            # Get scroll offsets in pixels
            x_scroll_offset = self.canvas.xview()[0] * self.canvas.winfo_width()
            y_scroll_offset = self.canvas.yview()[0] * self.canvas.winfo_height()

            # Adjust the drawing logic to account for the scroll offsets
            self.draw_tool.perform_action(
                event,
                active_layer.offset,
                self.scale_factor,
                x_scroll_offset,
                y_scroll_offset,
            )
            self.display_layers()  # Redraw the canvas to reflect changes



    def end_action(self, event):
        if self.active_layer_index == -1:
            return  # No active layer to perform actions on

        active_layer = self.layers[self.active_layer_index]

        if self.scaling:
            # Record the scaling action for undo/redo
            action_type = "scale"
            params = {
                "previous_scale": self.previous_scale,  # The original scale factor before scaling
                "new_scale": self.scale_factor,  # The new scale factor after scaling
                "layer_index": self.active_layer_index
            }
            self.history_tool.record_action(action_type, params)

        elif self.translating:
            # Record the translation action for undo/redo
            action_type = "translate"
            params = {
                "previous_offset": self.previous_offset,  # The original position before translation
                "new_offset": active_layer.offset[:],  # The new position after translation
                "layer_index": self.active_layer_index
            }
            self.history_tool.record_action(action_type, params)

        elif self.drawing:
            # Record the drawing action for undo/redo
            action_type = "draw"
            params = {
                "stroke": self.current_stroke,  # The current stroke that was added during drawing
                "layer_index": self.active_layer_index
            }
            self.history_tool.record_action(action_type, params)

# -------------------------------------------------------------





# --------------- FILTERS: BLUR + SUNGLASSES ------------------
    def apply_sunglasses_filter(self):
        if self.active_layer_index == -1:
            print("No active layer to apply the filter on.")
            return

        active_layer = self.layers[self.active_layer_index]
        active_image = active_layer.get_image()

        if active_image is None:
            print("No image loaded to apply the sunglasses filter.")
            return

        image_cv = cv2.cvtColor(np.array(active_image), cv2.COLOR_RGBA2BGR)
        sunglasses_layer_cv = self.sunglasses_filter.apply_filter(image_cv)
        sunglasses_layer_pil = Image.fromarray(sunglasses_layer_cv)

        new_layer = Layer(active_image.width, active_image.height, name="Sunglasses Layer")
        new_layer.update_image(sunglasses_layer_pil)
        new_layer.offset = [
            int(active_layer.offset[0] * self.scale_factor),
            int(active_layer.offset[1] * self.scale_factor),
        ]

        self.layers.append(new_layer)
        self.active_layer_index = len(self.layers) - 1

        action_type = "apply_sunglasses"
        params = {
            "layer_index": self.active_layer_index,
            "layer_data": new_layer
        }
        self.history_tool.record_action(action_type, params)

        self.update_layer_listbox()
        self.display_layers()


    def apply_blur_filter_with_popup(self):
        if self.active_layer_index == -1:
            return

        # Create a popup window
        popup = Toplevel(self.root)
        popup.title("Adjust Blur Strength")
        popup.geometry("300x150")

        # Add a slider to adjust the blur strength
        blur_slider = Scale(popup, from_=0, to=20, orient=HORIZONTAL, label="Blur Strength")
        blur_slider.set(0)  # Set initial value to 0 (no blur)
        blur_slider.pack(fill="x", padx=10, pady=10)

        def preview_blur():
            if self.active_layer_index != -1:
                active_layer = self.layers[self.active_layer_index]
                if active_layer.image is not None:
                    kernel_size = blur_slider.get()
                    if kernel_size > 0:
                        rgba_image = active_layer.get_image()
                        rgb_image = rgba_image.convert("RGB")  # Remove alpha temporarily for OpenCV
                        alpha_channel = rgba_image.split()[-1]  # Extract alpha channel

                        # Convert to OpenCV
                        cv_rgb = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)
                        cv_alpha = np.array(alpha_channel)

                        # Apply Gaussian blur to RGB and alpha channels
                        blurred_rgb = cv2.GaussianBlur(cv_rgb, (kernel_size * 2 + 1, kernel_size * 2 + 1), 0)
                        blurred_alpha = cv2.GaussianBlur(cv_alpha, (kernel_size * 2 + 1, kernel_size * 2 + 1), 0)

                        # Convert back to PIL and restore the alpha channel
                        blurred_image = Image.fromarray(cv2.cvtColor(blurred_rgb, cv2.COLOR_BGR2RGB))
                        blurred_alpha_channel = Image.fromarray(blurred_alpha).convert("L")
                        final_image = Image.merge("RGBA", (*blurred_image.split(), blurred_alpha_channel))

                        active_layer.update_image(final_image)
                    else:
                        active_layer.update_image(self.previous_image)
                    self.display_layers()

        def apply_blur():
            preview_blur()
            popup.destroy()

            action_type = "filter"
            params = {
                "layer_index": self.active_layer_index,
                "previous_image": self.previous_image,
                "new_image": self.layers[self.active_layer_index].get_image().copy()
            }
            self.history_tool.record_action(action_type, params)

        def cancel_blur():

            if self.active_layer_index != -1:
                self.layers[self.active_layer_index].update_image(self.previous_image)
                self.display_layers()
            popup.destroy()

        apply_button = Button(popup, text="Apply", command=apply_blur)
        apply_button.pack(side="left", padx=10, pady=10)

        cancel_button = Button(popup, text="Cancel", command=cancel_blur)
        cancel_button.pack(side="right", padx=10, pady=10)

        blur_slider.bind("<Motion>", lambda event: preview_blur())

        if self.active_layer_index != -1:
            active_layer = self.layers[self.active_layer_index]
            self.previous_image = active_layer.get_image().copy()


#--------------------------------------------------------------------------------------



#------------------------- UNDO + REDO ------------------------------------------------

    def undo(self):
        action = self.history_tool.undo()
        if action is None:
            return


        if action["type"] == "resize_canvas":
            # Undo resizing the canvas
            previous_width = action["params"]["previous_width"]
            previous_height = action["params"]["previous_height"]
            self.canvas.config(width=previous_width, height=previous_height)
            self.canvas.config(scrollregion=(0, 0, previous_width, previous_height))
            self.root.geometry(f"{previous_width}x{previous_height + 100}")
            if len(self.layers) > 0 and self.layers[0].name == "Base Layer":
                self.layers[0].update_image(
                    Image.new("RGBA", action["params"]["previous_base_layer_size"], (255, 255, 255, 255))
                )
            self.display_layers()

        elif action["type"] == "filter" or action["type"] == "apply_filter":
            layer_index = action["params"]["layer_index"]
            previous_image = action["params"]["previous_image"]

            if layer_index < len(self.layers):
                self.layers[layer_index].update_image(previous_image)
                self.display_layers()

        elif action["type"] == "add_layer":
            layer_index = action["params"]["layer_index"]
            if layer_index < len(self.layers):
                del self.layers[layer_index]
                # Update active_layer_index to be consistent
                if layer_index == len(self.layers):
                    self.active_layer_index = len(self.layers) - 1
                else:
                    self.active_layer_index = layer_index
                self.update_layer_listbox()
                self.display_layers()

        elif action["type"] == "delete_layer":
            layer_index = action["params"]["layer_index"]
            layer_data = action["params"]["layer_data"]
            self.layers.insert(layer_index, layer_data)
            self.active_layer_index = layer_index
            self.update_layer_listbox()
            self.display_layers()

        elif action["type"] == "scale":
            layer_index = action["params"]["layer_index"]
            self.scale_factor = action["params"]["previous_scale"]
            self.layers[layer_index].update_image(
                Image.fromarray(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGBA))
            )
            self.display_layers()

        elif action["type"] == "translate":
            layer_index = action["params"]["layer_index"]
            self.layers[layer_index].offset = action["params"]["previous_offset"][:]
            self.display_layers()

        elif action["type"] == "draw":
            layer_index = action["params"]["layer_index"]
            self.layers[layer_index].brush_strokes.remove(action["params"]["stroke"])
            self.display_layers()

        # Handle the action
        elif action["type"] == "apply_sunglasses":
            # Undo applying the sunglasses filter by removing the layer
            layer_index = action["params"]["layer_index"]
            if layer_index < len(self.layers):
                del self.layers[layer_index]
                self.active_layer_index = -1 if len(self.layers) == 0 else min(layer_index, len(self.layers) - 1)
                self.update_layer_listbox()
                self.display_layers()
                print("Undo: Removed sunglasses layer.")

    def redo(self):
        action = self.history_tool.redo()
        if action is None:
            return


        if action["type"] == "resize_canvas":
            previous_width = action["params"]["previous_width"]
            previous_height = action["params"]["previous_height"]
            self.canvas.config(width=previous_width, height=previous_height)
            self.canvas.config(scrollregion=(0, 0, previous_width, previous_height))
            self.root.geometry(f"{previous_width}x{previous_height + 100}")
            if len(self.layers) > 0 and self.layers[0].name == "Base Layer":
                self.layers[0].update_image(
                    Image.new("RGBA", action["params"]["previous_base_layer_size"], (255, 255, 255, 255))
                )
            self.display_layers()

        elif action["type"] == "filter":
            layer_index = action["params"]["layer_index"]
            new_image = action["params"]["new_image"]
            if layer_index < len(self.layers):
                self.layers[layer_index].update_image(new_image)
                self.display_layers()

        elif action["type"] == "add_layer":
            self.add_layer()

        elif action["type"] == "delete_layer":
            layer_index = action["params"]["layer_index"]
            if layer_index < len(self.layers):
                del self.layers[layer_index]
                self.update_layer_listbox()
                self.display_layers()

        elif action["type"] == "scale":
            layer_index = action["params"]["layer_index"]
            new_scale = action["params"]["new_scale"]
            previous_scale = action["params"]["previous_scale"]

            active_layer = self.layers[layer_index]
            if active_layer.image is not None:
                scaled_width = int(active_layer.get_image().width * new_scale / previous_scale)
                scaled_height = int(active_layer.get_image().height * new_scale / previous_scale)

                scaled_image = active_layer.get_image().resize(
                    (scaled_width, scaled_height), Image.Resampling.LANCZOS
                )
                active_layer.update_image(scaled_image)

                active_layer.offset[0] = int(active_layer.offset[0] * new_scale / previous_scale)
                active_layer.offset[1] = int(active_layer.offset[1] * new_scale / previous_scale)

                self.scale_factor = new_scale
                self.display_layers()

        elif action["type"] == "translate":
            layer_index = action["params"]["layer_index"]
            self.layers[layer_index].offset = action["params"]["new_offset"][:]
            self.display_layers()

        elif action["type"] == "draw":
            layer_index = action["params"]["layer_index"]
            self.layers[layer_index].add_brush_stroke(action["params"]["stroke"])
            self.display_layers()

        elif action["type"] == "rotate":
            layer_index = action["params"]["layer_index"]
            new_angle = action["params"]["new_angle"]
            self.angle = new_angle
            rotated_image = self.rotate_tool.perform_action(None, self.original_image, self.angle)[0]
            self.layers[layer_index].update_image(Image.fromarray(cv2.cvtColor(rotated_image, cv2.COLOR_BGR2RGBA)))
            self.display_layers()

        elif action["type"] == "apply_sunglasses":
            layer_index = action["params"]["layer_index"]
            layer_data = action["params"]["layer_data"]
            self.layers.insert(layer_index, layer_data)
            self.active_layer_index = layer_index
            self.update_layer_listbox()
            self.display_layers()
            print("Redo: Restored sunglasses layer.")


root = tk.Tk()
app = ImageResizerApp(root)
root.mainloop()
