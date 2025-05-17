import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import ImageGrab  # 需要安装 Pillow 库：pip install Pillow

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画板")

        # 初始化绘图参数
        self.pen_color = "black"
        self.pen_size = 2
        self.draw_shape = "line"  # 当前绘制形状：line/rectangle/oval
        self.start_x, self.start_y = None, None  # 记录起始坐标

        # 创建画布
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建右侧控制面板
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 颜色选择按钮
        color_btn = tk.Button(control_frame, text="选择颜色", command=self.choose_color)
        color_btn.pack(pady=5)

        # 显示当前颜色
        self.color_preview = tk.Label(control_frame, bg=self.pen_color, width=10, height=2)
        self.color_preview.pack(pady=5)

        # 画笔粗细滑动条
        tk.Label(control_frame, text="画笔粗细").pack()
        self.size_slider = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.change_size)
        self.size_slider.set(self.pen_size)
        self.size_slider.pack()

        # 形状选择
        shape_frame = tk.Frame(control_frame)
        shape_frame.pack(pady=10)
        self.shape_var = tk.StringVar(value="line")
        shapes = [("线条", "line"), ("矩形", "rectangle"), ("圆形", "oval")]
        for text, shape in shapes:
            rb = tk.Radiobutton(shape_frame, text=text, variable=self.shape_var, value=shape)
            rb.pack(anchor=tk.W)

        # 清空按钮
        clear_btn = tk.Button(control_frame, text="清空画布", command=self.clear_canvas)
        clear_btn.pack(pady=5)

        # 保存按钮
        save_btn = tk.Button(control_frame, text="保存图片", command=self.save_image)
        save_btn.pack(pady=5)

        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color
            self.color_preview.config(bg=color)

    def change_size(self, value):
        self.pen_size = int(value)

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_drawing(self, event):
        self.start_x, self.start_y = event.x, event.y

    def drawing(self, event):
        if self.start_x and self.start_y:
            # 绘制临时图形（跟随鼠标移动）
            self.canvas.delete("temp")  # 删除上一个临时图形
            shape = self.shape_var.get()
            if shape == "line":
                self.canvas.create_line(
                    self.start_x, self.start_y, event.x, event.y,
                    fill=self.pen_color, width=self.pen_size, tags="temp"
                )
            elif shape == "rectangle":
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.pen_color, width=self.pen_size, tags="temp"
                )
            elif shape == "oval":
                self.canvas.create_oval(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.pen_color, width=self.pen_size, tags="temp"
                )

    def stop_drawing(self, event):
        # 绘制最终图形
        if self.start_x and self.start_y:
            shape = self.shape_var.get()
            if shape == "line":
                self.canvas.create_line(
                    self.start_x, self.start_y, event.x, event.y,
                    fill=self.pen_color, width=self.pen_size
                )
            elif shape == "rectangle":
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.pen_color, width=self.pen_size
                )
            elif shape == "oval":
                self.canvas.create_oval(
                    self.start_x, self.start_y, event.x, event.y,
                    outline=self.pen_color, width=self.pen_size
                )
        self.start_x, self.start_y = None, None

    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")]
        )
        if file_path:
            # 获取画布区域坐标
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            # 截屏保存
            ImageGrab.grab().crop((x, y, x1, y1)).save(file_path)
            tk.messagebox.showinfo("保存成功", f"图片已保存至：{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()