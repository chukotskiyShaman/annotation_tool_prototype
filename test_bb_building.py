import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class YOLOAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Dataset Annotation Tool")

        self.image_folder = ""
        self.annotated_folder = "annotated_data"  # Папка для обработанных данных
        self.image_list = []
        self.current_image_index = 0
        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.bboxes = []
        self.current_bbox = None

        # Список классов
        self.classes = ["cat", "dog", "car", "person"]  # Пример классов
        self.class_var = tk.StringVar(value=self.classes[0])  # Текущий выбранный класс

        # Выпадающий список для выбора класса
        self.class_combobox = ttk.Combobox(root, textvariable=self.class_var, values=self.classes)
        self.class_combobox.pack()

        self.load_button = tk.Button(root, text="Load Images", command=self.load_images)
        self.load_button.pack()

        self.next_button = tk.Button(root, text="Next Image", command=self.next_image)
        self.next_button.pack()

        self.save_button = tk.Button(root, text="Save Annotations", command=self.save_annotations)
        self.save_button.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Создаем папку для аннотированных данных, если она не существует
        if not os.path.exists(self.annotated_folder):
            os.makedirs(self.annotated_folder)

    def load_images(self):
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            # Фильтруем изображения: исключаем те, которые уже в папке annotated_data
            annotated_images = set(os.listdir(self.annotated_folder))
            self.image_list = [
                os.path.join(self.image_folder, f)
                for f in os.listdir(self.image_folder)
                if f.endswith(('.png', '.jpg', '.jpeg')) and f not in annotated_images
            ]
            if self.image_list:
                self.show_image(0)

    def show_image(self, index):
        if 0 <= index < len(self.image_list):
            self.current_image_index = index
            image_path = self.image_list[index]
            self.image = Image.open(image_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            self.bboxes = []
            self.load_annotations(image_path)

    def load_annotations(self, image_path):
        annotation_path = image_path.replace(".jpg", ".txt").replace(".png", ".txt").replace(".jpeg", ".txt")
        if os.path.exists(annotation_path):
            with open(annotation_path, "r") as f:
                for line in f.readlines():
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    class_name = self.classes[int(class_id)]  # Преобразуем ID в имя класса
                    self.bboxes.append((class_name, x_center, y_center, width, height))
                    self.draw_bbox(x_center, y_center, width, height)

    def draw_bbox(self, x_center, y_center, width, height):
        img_width, img_height = self.image.size
        x1 = (x_center - width / 2) * img_width
        y1 = (y_center - height / 2) * img_height
        x2 = (x_center + width / 2) * img_width
        y2 = (y_center + height / 2) * img_height
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="bbox")

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_bbox = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.current_bbox, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        img_width, img_height = self.image.size
        x_center = ((self.start_x + end_x) / 2) / img_width
        y_center = ((self.start_y + end_y) / 2) / img_height
        width = abs(end_x - self.start_x) / img_width
        height = abs(end_y - self.start_y) / img_height
        class_name = self.class_var.get()  # Получаем выбранный класс
        self.bboxes.append((class_name, x_center, y_center, width, height))

    def save_annotations(self):
        if self.image_list:
            image_path = self.image_list[self.current_image_index]
            annotation_path = image_path.replace(".jpg", ".txt").replace(".png", ".txt").replace(".jpeg", ".txt")
            with open(annotation_path, "w") as f:
                for bbox in self.bboxes:
                    class_name, x_center, y_center, width, height = bbox
                    class_id = self.classes.index(class_name)  # Преобразуем имя класса в ID
                    f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

            # Перемещаем изображение и аннотацию в папку annotated_data
            self.move_to_annotated(image_path, annotation_path)

    def move_to_annotated(self, image_path, annotation_path):
        """Перемещает изображение и аннотацию в папку annotated_data."""
        image_name = os.path.basename(image_path)
        annotation_name = os.path.basename(annotation_path)

        # Перемещаем изображение
        shutil.move(image_path, os.path.join(self.annotated_folder, image_name))
        # Перемещаем аннотацию
        if os.path.exists(annotation_path):
            shutil.move(annotation_path, os.path.join(self.annotated_folder, annotation_name))

        # Удаляем изображение из списка
        self.image_list.pop(self.current_image_index)
        if self.image_list:
            self.show_image(min(self.current_image_index, len(self.image_list) - 1))
        else:
            self.canvas.delete("all")  # Очищаем холст, если изображений больше нет

    def next_image(self):
        # Сохраняем текущую аннотацию перед переходом к следующему изображению
        self.save_annotations()

        # Переходим к следующему изображению
        if self.current_image_index < len(self.image_list) - 1:
            self.show_image(self.current_image_index + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOAnnotationApp(root)
    root.mainloop()
