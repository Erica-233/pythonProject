import json
import os
import random
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


class AddressBook:
    def __init__(self, filename='contacts.json'):
        self.filename = filename
        self.contacts = []
        self.load_contacts()

    def load_contacts(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.contacts = [Contact(**item) for item in data]

    def save_contacts(self):
        data = [vars(contact) for contact in self.contacts]
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def add_contact(self, contact):
        self.contacts.append(contact)
        self.save_contacts()

    def delete_contact(self, name):
        self.contacts = [c for c in self.contacts if c.name != name]
        self.save_contacts()

    def search_contacts(self, keyword):
        return [c for c in self.contacts
                if keyword.lower() in c.name.lower() or
                keyword in c.phone]


class Contact:
    def __init__(self, name, phone, email, address):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address


class CyberpunkContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("通讯录 v2.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a12')

        # 保存动画ID以便关闭时取消
        self.scan_lines_id = None
        self.binary_rain_id = None

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 风格配置
        self.colors = {
            'bg': '#0a0a12',
            'primary': '#00ff9d',
            'secondary': '#ff009d',
            'text': '#e0e0ff',
            'highlight': '#00f0ff',
            'panel': '#121220',
            'error': '#ff3c00'
        }

        self.setup_fonts()
        self.create_cyber_ui()
        self.address_book = AddressBook()
        self.update_contact_list()

    def on_close(self):
        """处理窗口关闭事件"""
        # 停止所有动画效果
        if self.scan_lines_id:
            self.root.after_cancel(self.scan_lines_id)
        if self.binary_rain_id:
            self.root.after_cancel(self.binary_rain_id)
        self.root.destroy()

    def setup_fonts(self):
        # 尝试加载赛博朋克风格字体
        default_fonts = ['OCR A Extended', 'Courier New', 'Agency FB', 'Consolas']
        available_fonts = set(tkfont.families())

        title_font = 'Courier New'
        main_font = 'Courier New'
        button_font = 'Courier New'

        for font in default_fonts:
            if font in available_fonts:
                if font == 'OCR A Extended':
                    title_font = font
                elif font == 'Agency FB':
                    button_font = font
                break

        self.title_font = tkfont.Font(family=title_font, size=24, weight="bold")
        self.main_font = tkfont.Font(family=main_font, size=12)
        self.button_font = tkfont.Font(family=button_font, size=14, weight="bold")

    def create_cyber_ui(self):
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(title_frame,
                 text=">_ EIRCA'S CONTACTS 2.0",
                 font=self.title_font,
                 fg=self.colors['primary'],
                 bg=self.colors['bg']).pack(side=tk.LEFT)

        # 状态指示器
        self.status_indicator = tk.Label(title_frame,
                                         text="■ SYSTEM ONLINE",
                                         font=self.button_font,
                                         fg=self.colors['primary'],
                                         bg=self.colors['bg'])
        self.status_indicator.pack(side=tk.RIGHT)

        # 搜索和操作面板
        control_frame = tk.Frame(self.root, bg=self.colors['panel'], bd=0)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(control_frame,
                                textvariable=self.search_var,
                                font=self.main_font,
                                bg='#1a1a2a',
                                fg=self.colors['text'],
                                insertbackground=self.colors['primary'],
                                relief=tk.FLAT,
                                highlightcolor=self.colors['highlight'],
                                highlightthickness=2)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search)

        button_style = {
            'font': self.button_font,
            'bg': self.colors['bg'],
            'fg': self.colors['primary'],
            'activebackground': self.colors['secondary'],
            'activeforeground': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 5,
            'highlightthickness': 0
        }

        tk.Button(control_frame,
                  text="[+] 新增",
                  command=self.show_add_dialog,
                  **button_style).pack(side=tk.LEFT)

        tk.Button(control_frame,
                  text="[i] 关于",
                  command=self.show_about,
                  **button_style).pack(side=tk.LEFT)

        # 联系人列表
        list_frame = tk.Frame(self.root, bg=self.colors['panel'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#1a1a2a",
                        foreground=self.colors['text'],
                        fieldbackground="#1a1a2a",
                        rowheight=30,
                        font=self.main_font,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#121220",
                        foreground=self.colors['primary'],
                        font=self.button_font,
                        relief=tk.FLAT)
        style.map("Treeview",
                  background=[('selected', self.colors['secondary'])],
                  foreground=[('selected', 'white')])

        self.tree = ttk.Treeview(list_frame,
                                 columns=('name', 'phone', 'email'),
                                 show='headings',
                                 style="Treeview")

        self.tree.heading('name', text='姓名')
        self.tree.heading('phone', text='电话')
        self.tree.heading('email', text='邮箱')

        self.tree.column('name', width=200, anchor='w')
        self.tree.column('phone', width=150, anchor='center')
        self.tree.column('email', width=250, anchor='w')

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # 右键菜单
        self.menu = tk.Menu(self.root,
                            tearoff=0,
                            bg='#1a1a2a',
                            fg=self.colors['text'],
                            activebackground=self.colors['secondary'],
                            activeforeground='white',
                            bd=0)
        self.menu.add_command(label="[编辑]",
                              font=self.button_font,
                              command=self.edit_contact)
        self.menu.add_command(label="[删除]",
                              font=self.button_font,
                              command=self.delete_contact)
        self.menu.add_command(label="[查看详情]",
                              font=self.button_font,
                              command=self.view_details)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 添加扫描线效果
        self.scan_lines = tk.Canvas(self.root,
                                    bg=self.colors['bg'],
                                    highlightthickness=0)
        self.scan_lines.place(x=0, y=0, relwidth=1, relheight=1)
        self.draw_scan_lines()

        # 添加二进制雨效果
        self.binary_rain = tk.Canvas(self.root,
                                     bg='black',
                                     highlightthickness=0)
        self.binary_rain.place(x=0, y=0, relwidth=1, relheight=1)
        self.binary_streams = []
        self.start_binary_rain()

        # 确保UI元素在最上层
        title_frame.lift()
        control_frame.lift()
        list_frame.lift()

    def draw_scan_lines(self):
        self.scan_lines.delete("all")
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 确保画布大小与窗口一致
        self.scan_lines.config(width=width, height=height)

        for i in range(0, height, 4):
            alpha = 0.1 + (i % 20) * 0.02
            color = self.blend_colors(self.colors['bg'], self.colors['primary'], alpha)
            self.scan_lines.create_line(0, i, width, i, fill=color, width=1)

        self.scan_lines_id = self.root.after(100, self.draw_scan_lines)

    def start_binary_rain(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 确保画布大小与窗口一致
        self.binary_rain.config(width=width, height=height)

        if not hasattr(self, 'binary_streams'):
            self.binary_streams = []

        # 创建新的二进制流
        if random.random() < 0.3 and len(self.binary_streams) < 15:
            x = random.randint(0, int(width))
            speed = random.uniform(2, 5)
            length = random.randint(5, 15)
            self.binary_streams.append({
                'x': x,
                'y': 0,
                'speed': speed,
                'length': length,
                'items': [random.choice(['0', '1']) for _ in range(length)]
            })

        # 更新现有流
        self.binary_rain.delete("all")
        for stream in self.binary_streams[:]:
            for i, char in enumerate(stream['items']):
                alpha = 1.0 - (i / stream['length'])
                color = self.blend_colors(self.colors['bg'], self.colors['primary'], alpha * 0.3)
                self.binary_rain.create_text(
                    stream['x'],
                    stream['y'] + i * 20,
                    text=char,
                    fill=color,
                    font=self.main_font
                )
            stream['y'] += stream['speed']

            # 移除超出屏幕的流
            if stream['y'] - stream['length'] * 20 > height:
                self.binary_streams.remove(stream)

        self.binary_rain_id = self.root.after(50, self.start_binary_rain)

    def blend_colors(self, color1, color2, alpha):
        """混合两种颜色"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        r = int(r1 + (r2 - r1) * alpha)
        g = int(g1 + (g2 - g1) * alpha)
        b = int(b1 + (b2 - b1) * alpha)

        return f"#{r:02x}{g:02x}{b:02x}"

    def update_contact_list(self, keyword=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        contacts = self.address_book.search_contacts(keyword or "")
        for contact in contacts:
            self.tree.insert('', 'end', values=(
                contact.name,
                contact.phone,
                contact.email
            ))

    def on_search(self, event):
        self.update_contact_list(self.search_var.get())

    def show_add_dialog(self, contact=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(">_ 添加新联系人" if not contact else ">_ 编辑联系人")
        dialog.configure(bg=self.colors['panel'])

        # 添加霓虹边框效果
        border_frame = tk.Frame(dialog,
                                bg=self.colors['primary'],
                                padx=1, pady=1)
        border_frame.pack(padx=10, pady=10)

        content_frame = tk.Frame(border_frame,
                                 bg=self.colors['panel'],
                                 padx=20, pady=20)
        content_frame.pack()

        fields = [
            ("姓名", 'name'),
            ("电话", 'phone'),
            ("邮箱", 'email'),
            ("地址", 'address')
        ]

        entries = {}
        for idx, (label, field) in enumerate(fields):
            tk.Label(content_frame,
                     text=f"> {label}:",
                     font=self.main_font,
                     fg=self.colors['text'],
                     bg=self.colors['panel']).grid(row=idx, column=0, sticky='e', pady=5)

            entry = tk.Entry(content_frame,
                             font=self.main_font,
                             bg='#1a1a2a',
                             fg=self.colors['text'],
                             insertbackground=self.colors['primary'],
                             relief=tk.FLAT)
            entry.grid(row=idx, column=1, pady=5, padx=10)

            if contact:
                entry.insert(0, getattr(contact, field))
            entries[field] = entry

        def save_contact():
            data = {field: entries[field].get() for field in entries}

            # 验证必填字段
            if not data['name'] or not data['phone']:
                self.show_cyber_message("错误", "姓名和电话是必填字段！", is_error=True)
                return

            try:
                if contact:
                    # 更新现有联系人
                    contact.__dict__.update(data)
                    self.address_book.save_contacts()
                    self.show_cyber_message("成功", f"{data['name']} 已更新！")
                else:
                    # 添加新联系人
                    self.address_book.add_contact(Contact(**data))
                    self.show_cyber_message("成功", f"{data['name']} 已添加！")

                self.update_contact_list()
                dialog.destroy()
            except Exception as e:
                self.show_cyber_message("错误", f"保存失败: {str(e)}", is_error=True)

        save_btn = tk.Button(content_frame,
                             text="[保存数据]",
                             command=save_contact,
                             font=self.button_font,
                             bg=self.colors['bg'],
                             fg=self.colors['primary'],
                             activebackground=self.colors['secondary'],
                             activeforeground='white',
                             bd=0)
        save_btn.grid(row=len(fields), columnspan=2, pady=(20, 0))

        # 使对话框模态化
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def edit_contact(self):
        selected = self.tree.selection()
        if selected:
            name = self.tree.item(selected[0], 'values')[0]
            contact = next((c for c in self.address_book.contacts if c.name == name), None)
            if contact:
                self.show_add_dialog(contact)

    def delete_contact(self):
        selected = self.tree.selection()
        if selected:
            name = self.tree.item(selected[0], 'values')[0]

            # 自定义确认对话框
            confirm_dialog = tk.Toplevel(self.root)
            confirm_dialog.title(">_ 确认删除")
            confirm_dialog.configure(bg=self.colors['panel'])

            border_frame = tk.Frame(confirm_dialog,
                                    bg=self.colors['secondary'],
                                    padx=1, pady=1)
            border_frame.pack(padx=10, pady=10)

            content_frame = tk.Frame(border_frame,
                                     bg=self.colors['panel'],
                                     padx=20, pady=20)
            content_frame.pack()

            tk.Label(content_frame,
                     text=f"确定要删除 {name} 吗？",
                     font=self.main_font,
                     fg=self.colors['text'],
                     bg=self.colors['panel']).pack(pady=10)

            btn_frame = tk.Frame(content_frame, bg=self.colors['panel'])
            btn_frame.pack()

            def do_delete():
                self.address_book.delete_contact(name)
                self.update_contact_list()
                confirm_dialog.destroy()
                self.show_cyber_message("成功", f"{name} 已删除！")

            tk.Button(btn_frame,
                      text="[确认删除]",
                      command=do_delete,
                      font=self.button_font,
                      bg=self.colors['bg'],
                      fg=self.colors['error'],
                      activebackground=self.colors['error'],
                      activeforeground='white',
                      bd=0).pack(side=tk.LEFT, padx=10)

            tk.Button(btn_frame,
                      text="[取消]",
                      command=confirm_dialog.destroy,
                      font=self.button_font,
                      bg=self.colors['bg'],
                      fg=self.colors['text'],
                      activebackground=self.colors['secondary'],
                      activeforeground='white',
                      bd=0).pack(side=tk.LEFT, padx=10)

            confirm_dialog.transient(self.root)
            confirm_dialog.grab_set()
            self.root.wait_window(confirm_dialog)

    def view_details(self):
        selected = self.tree.selection()
        if selected:
            name = self.tree.item(selected[0], 'values')[0]
            contact = next((c for c in self.address_book.contacts if c.name == name), None)

            if contact:
                detail_dialog = tk.Toplevel(self.root)
                detail_dialog.title(f">_ 详情: {name}")
                detail_dialog.configure(bg=self.colors['panel'])

                border_frame = tk.Frame(detail_dialog,
                                        bg=self.colors['primary'],
                                        padx=1, pady=1)
                border_frame.pack(padx=10, pady=10)

                content_frame = tk.Frame(border_frame,
                                         bg=self.colors['panel'],
                                         padx=20, pady=20)
                content_frame.pack()

                details = [
                    ("姓名", contact.name),
                    ("电话", contact.phone),
                    ("邮箱", contact.email),
                    ("地址", contact.address)
                ]

                for idx, (label, value) in enumerate(details):
                    tk.Label(content_frame,
                             text=f"{label}:",
                             font=self.button_font,
                             fg=self.colors['primary'],
                             bg=self.colors['panel'],
                             anchor='w').grid(row=idx, column=0, sticky='w', pady=5)

                    tk.Label(content_frame,
                             text=value,
                             font=self.main_font,
                             fg=self.colors['text'],
                             bg=self.colors['panel'],
                             anchor='w').grid(row=idx, column=1, sticky='w', pady=5, padx=10)

                detail_dialog.transient(self.root)
                detail_dialog.grab_set()
                self.root.wait_window(detail_dialog)

    def show_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title(">_ 关于")
        about_dialog.configure(bg=self.colors['panel'])

        border_frame = tk.Frame(about_dialog,
                                bg=self.colors['primary'],
                                padx=1, pady=1)
        border_frame.pack(padx=10, pady=10)

        content_frame = tk.Frame(border_frame,
                                 bg=self.colors['panel'],
                                 padx=20, pady=20)
        content_frame.pack()

        about_text = """
         
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣠⣾⣿⣿⣿⣿⠟⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠻⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠙⢿⣿⣿⣿⣿⣦⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⢀⣴⣿⣿⣿⣿⡟⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠻⣿⢿⣿⣿⡿⢆⠈⠻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢠⣾⣿⣿⣿⣿⠋⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⢃⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡈⢦⡈⠻⣿⠈⣷⡀⠹⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢠⣿⣿⣿⣿⡿⢃⣴⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⣴⣿⣿⣿⣿⣿⣿⣿⣿⡏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⢻⣦⣬⡀⢸⣷⠀⢻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⢠⣿⣿⣿⣿⡿⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢁⣿⣿⣿⣿⣿⢁⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠛⡙⠳⣾⡿⣄⠈⠻⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡿⠁⣠⠿⣿⡿⠛⡿⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⠏⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢸⣿⣿⣿⣿⡏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠻⣿⣿⣿⣿⡇⢽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⢹⣦⡈⠁⠟⣷⡄⠘⢿⣿
⣿⣿⣿⣿⣿⣿⣿⠃⢠⡟⢠⠟⢀⡾⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⠃⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⢿⣿⣿⣿⡇⢀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⢻⣿⣦⠀⢻⣿⡄⢸⣿
⣿⣿⣿⣿⣿⣿⡏⠀⣿⡇⠀⣠⣿⠃⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⡇⢸⣷⣄⠙⢿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⡘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⢀⠙⢇⢸⣿⠃⢸⣿
⣿⣿⣿⣿⣿⣿⡇⠀⣿⡇⣰⣿⡏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⢁⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⡟⢸⣿⣿⡟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠘⣿⣿⣿⡇⢸⣿⣿⣷⣄⠹⣿⣿⣿⣧⠹⣿⣿⣿⣿⣧⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠘⣷⣄⣸⣿⠀⠸⣿
⣿⣿⣿⣿⣿⣿⡇⠀⣿⣤⣿⣿⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠘⣿⣿⣿⣿⡇⢼⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠆⣿⣿⣿⡇⢸⣿⣿⣿⣿⣷⡈⠻⣿⣿⣷⡹⣿⣿⣿⣿⡆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠛⠛⣿⡟⢷⡄⠘
⣿⣿⣿⣿⣿⠏⢀⡄⢿⡟⢉⡁⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⢠⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⡿⢀⠀⣿⣿⣿⣿⠀⢸⣿⣿⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⡇⣸⣿⣿⣿⣿⣿⣿⣦⠙⢿⣿⣷⡜⢿⣿⣿⣷⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠰⣆⠙⢧⠈⣿⡄
⣿⣿⣿⣿⠏⢀⣾⣷⣾⢁⣿⠁⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣼⣿⣿⣿⣿⣿⣿⢠⣿⣿⣿⣿⡿⢁⣾⡆⢻⣿⣿⡏⢠⠸⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⣿⣿⡟⠀⣿⣿⣿⠀⣿⡿⠟⣋⣤⣾⣿⣿⣷⡌⠻⣿⣿⣎⠻⣿⣿⡆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⣿⣷⡀⠁⢸⣷
⣿⣿⣿⡿⠀⣼⣿⡇⠁⣾⡟⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣿⣿⣿⣿⣿⣿⠃⣾⡿⠿⣿⡿⢁⣾⣿⣧⠸⣿⣿⡇⢸⡀⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⣿⣿⡇⠀⠿⠟⠛⢀⣥⣶⣿⣿⣿⣿⣿⣿⣿⣿⣦⡘⢿⣿⣷⡝⢿⣇⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢻⣿⣷⡄⢸⡟
⣿⣿⣿⣇⠀⣿⣿⡇⠘⠁⡄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⠏⣼⣿⣷⣶⡄⢀⣘⡛⠻⠿⠆⢻⣿⡇⢸⣧⠸⣿⠀⢸⣿⣿⣿⣿⣿⣿⣿⠃⠀⣛⣉⠀⠀⣶⣾⠁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠻⣿⣿⣦⣽⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⠿⣿⣿⣿⡁
⣿⣿⣿⣿⡀⢹⣿⣿⠂⣸⡇⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⢸⣿⣿⣿⣿⠏⣸⣿⣿⣿⠋⣰⣿⣿⣿⣿⣷⣶⡀⢤⣄⢈⣿⣆⢹⠀⠈⣿⣿⣿⣿⣿⣿⡟⠀⢀⣿⠇⡄⢸⡿⠃⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡈⠻⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢰⣦⡾⠁⢠⠄
⣿⣿⣿⣿⣧⠀⢿⣿⣠⡿⠇⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⠋⣼⣿⣿⠟⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣄⠻⡀⢿⣿⣆⠀⢧⠘⣿⣿⣿⣿⠟⢠⠃⠼⠋⠜⠀⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡈⠻⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⠁⣠⠀⠀
⣿⣿⣿⣿⣿⡦⠈⠛⠻⣥⡄⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⡿⢃⣼⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⢈⣿⣿⣷⣌⣧⣈⣤⣤⣤⣴⣿⣤⣶⣾⣷⠶⠟⠛⠛⠋⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠙⠒⠄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⠇⢠⣿⠀⢀
⣿⣿⣿⡿⠋⠀⢀⡶⠀⠘⠇⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡟⣡⠾⠟⠁⠐⠛⠛⠛⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠙⠛⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⣿⣿⣿⣿⣿⣿⠘⠀⢼⣿⠀⠸
⣿⣿⡟⠁⣰⠇⠘⠀⣼⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⡍⣿⣿⡯⠀⠀⢹⣿⠀⠀
⣿⡟⠀⡼⠁⣰⡆⢀⣿⡇⠀⠘⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⡇⣿⣿⡇⠀⠰⣾⡟⠀⠀
⡏⠀⣼⠁⣰⣿⠁⢸⣿⡄⠀⠀⢿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡄⢸⣿⣿⣿⣿⢱⣿⣿⡇⠀⠀⣿⡇⠀⠀
⠀⣸⡇⢀⣿⡟⠀⢸⡿⡇⠀⠀⠸⣿⣿⢿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡇⢸⣿⣿⣿⣿⢸⣿⣿⠀⡄⠀⠻⠇⠀⠀
⡀⠙⠀⢸⣿⠃⠀⣿⡇⡗⠀⠇⠀⣿⣿⡘⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⡇⢸⣿⣿⣿⡟⣸⣿⣿⠀⠁⠀⣶⣶⡇⠀
⣷⡄⠀⣾⡿⠀⢀⣿⡇⡇⠀⠀⠀⢸⣿⡇⢿⣿⣿⣿⡇⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⣿⣿⣿⡇⢸⣿⣿⣿⢇⣿⣿⡇⠀⢠⠀⣿⣿⡇⢀
⣿⡇⠀⣿⣷⣄⡈⠛⠋⠃⠀⠄⠸⠀⣿⣿⠸⣿⣿⣿⣧⠸⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣤⣤⣄⣀⣀⣀⣤⣤⣤⣤⣴⣶⣾⣿⣿⣿⣿⣿⣿⣿⡇⣾⣿⣿⡿⣸⣿⣿⠃⣠⡏⠀⣿⣿⠇⢸
⣿⡇⠀⣿⣿⣿⣿⣿⠀⢸⣿⠇⠀⠀⢹⣿⣧⢻⣿⣿⣿⠀⣿⣿⣿⣶⣦⣤⣄⣀⣀⣀⣀⣀⣀⣀⣤⣤⣤⣶⣶⣿⣿⣿⣿⣿⡿⢿⣿⣿⣿⠿⠛⠛⠻⠿⠟⠛⢋⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⢣⣿⣿⣿⠀⣿⡇⠀⣿⣿⠀⢸
⣿⡇⠀⣿⣿⣿⣿⣿⡄⠈⣿⣔⠀⣆⠸⣿⣿⡌⢿⣿⣿⡆⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⣿⣿⠏⣾⣿⣿⡇⢸⣿⣧⣀⠀⣀⣠⣾
⣿⡇⠀⣿⣿⣿⣿⣿⡇⠀⣿⣇⠀⢸⠀⣿⣿⣿⡌⢿⣿⣇⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⢰⣿⡟⣼⣿⣿⣿⠁⣼⣿⣿⣿⠀⣿⣿⣿
⣿⡇⠀⣿⣿⣿⣿⣿⣿⠀⠘⠋⢁⣸⡇⠸⣿⣿⣿⡌⢿⣿⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⢀⣴⠁⣸⡟⣼⣿⣿⣿⡟⢀⣿⣿⣿⣿⠀⣿⣿⣿
⣿⣷⠀⢿⣿⣯⢹⣿⣿⣿⣦⠀⣿⣿⣿⠀⢿⣿⣿⣿⡌⢻⣇⠀⠀⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠉⢀⣠⣾⣿⡏⠀⡟⣵⣿⣿⣿⣿⠃⢸⣿⣿⣿⣿⠀⣿⣿⣿
⣿⣿⠀⢸⣿⣿⡄⢻⣿⣿⣿⠀⢹⣿⣿⡇⠘⣿⣿⣿⣿⣆⠹⡆⠹⣦⣀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠉⢀⣀⣤⣾⣿⣿⣿⣿⠁⠈⣼⣿⣿⣿⣿⡏⢀⣿⣿⣿⣿⣿⠀⢻⣿⣿
⣿⣿⡆⠘⣿⣿⣿⡄⢿⣿⣿⡇⠸⣿⣿⣿⡄⢹⣿⣿⣿⣿⣧⡀⠀⠹⣿⣿⣦⣤⣀⠈⠉⠛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠛⠋⠉⢀⣀⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⠇⢀⣾⣿⣿⣿⣿⡿⠀⣼⣿⣿⣿⣿⣿⠀⢸⣿⣿
⣿⣿⣧⠀⢿⣿⣿⣿⡄⢻⣿⣧⠀⣿⣿⡟⠳⡀⢻⣿⣿⣿⣿⣷⣄⠀⠹⣿⣿⣿⣿⣿⣷⣶⣤⣤⣀⣀⠈⠉⠉⠛⠛⠛⠻⠿⠿⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⡉⠉⣁⠀⠀⣄⣀⡀⠐⠛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣠⡿⢿⣿⣿⣿⡿⠁⣼⣿⣿⣿⣿⣿⣿⡆⢸⣿⣿
⣿⣿⣿⡀⠸⣿⣿⣿⣿⣆⠹⣿⡀⢸⣿⡇⢀⣧⠈⢿⣿⣿⣿⣿⣿⣷⣄⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡶⠖⠂⠀⣀⣠⣤⠀⢀⣠⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⣰⣿⣿⣿⣿⣷⣶⣦⡄⠀⣀⠉⠛⠿⢿⠟⢁⣼⣿⡇⢸⣿⣿⡿⠁⣼⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿
⣿⣿⣿⣧⠀⢻⣿⣿⣿⣿⣧⠘⠇⠀⣿⠁⢸⣿⣧⡈⠻⣿⣿⣿⣿⣿⣿⣦⣄⠙⢿⣿⣿⣿⣿⣿⣿⠟⠋⣁⠀⣤⣶⣾⣿⣿⣿⣿⡆⠹⣿⣿⣿⣿⣿⡿⠿⣿⣿⣿⡿⠃⣰⣿⣿⣿⣿⣿⣿⣿⣿⡇⣰⣿⠀⠀⠀⠀⢠⣾⣿⣿⡇⢸⡿⠋⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⠘⣿⣿
⣿⣿⣿⣿⣧⠀⠻⣿⣿⣿⣿⣷⡀⠀⡟⠀⣾⣿⣿⣷⣄⠈⠛⠛⢿⣿⣿⣿⣿⣧⡀⠻⣿⣿⠟⠋⠀⠀⢸⣿⡄⢻⣿⣿⣿⣿⣿⣿⣿⡄⠙⢉⣡⣤⣴⣶⣶⣦⣤⡄⢁⣼⣿⣿⣿⣿⣿⣿⣿⣿⡿⢀⣿⡏⠀⠀⠀⢀⣿⣿⣿⣿⣧⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿
⣿⣿⣿⣿⣿⣧⡀⠙⢿⣿⣿⣿⣿⡄⠁⢠⣿⣿⣿⣿⣿⣿⣶⠀⣄⠙⢿⣿⣿⣿⣷⠀⠛⠁⠀⠀⠀⠀⠀⣿⣇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣆⠙⣿⣿⣿⣿⣿⣿⠏⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣼⣿⠁⠀⠀⠀⢸⣿⣿⣿⣿⣿⣧⠈⠻⣿⣿⣿⣿⣿⣿⣿⠀⠙⢿⣿⡆⠸⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠈⢻⣿⣿⣿⣿⣆⠈⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣄⠻⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⠀⣿⣿⣿⣿⣿⣿⡿⠿⠛⠃⠈⠻⣿⣿⠟⠁⣀⣉⣉⡛⠛⠿⠿⣿⣿⣿⣿⠏⣰⣿⠇⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣷⣄⠉⠛⢿⣿⣿⣿⣿⣷⣄⠀⠙⣷⡄⠉
⣿⣿⣿⣿⣿⡟⠁⣠⣷⡄⠹⣿⣿⣿⣿⠀⠉⢹⣿⣿⣿⡿⠃⣰⣿⣿⣿⣧⠹⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣇⢸⣿⠿⠛⢉⣡⣴⣶⣿⠿⠟⠆⣸⣇⡠⠞⠛⠛⠻⠿⣿⣶⣶⣤⣤⣉⠉⠀⠿⠟⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⣦⡄⠙⣿⣿⣿⣿⣿⣷⡄⠈⠁⣠
⣿⣿⣿⡿⠋⢀⣴⣿⣿⣿⠀⣿⣿⣿⠏⠀⢠⣿⣿⣿⡿⠁⣴⣿⣿⣿⣿⣿⣤⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠋⡀⠠⣶⡿⠟⠛⠉⠁⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⠛⠀⠿⠶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢿⣿⣿⣿⣿⣿⡆⠈⠿⣿⣿⣿⣿⡟⠀⣴⣿
⣿⣿⡿⠁⣠⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⢀⣾⣿⣿⡿⠁⣼⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡈⠛⢿⣿⣿⡇⠀⠀⠈⠻⣿⡟⠀⣸⣿⣿
⣿⣿⡇⢀⣿⣿⣿⡿⠿⠟⠛⠉⡀⠀⠀⣼⣿⣿⣿⠃⢸⣿⣿⣿⠿⠋⣠⣴⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠿⣆⠈⣿⡿⠃⠀⠀⠀⠀⠙⠇⠀⣿⣿⣿
⣿⣿⣇⠀⠻⣿⣿⣦⣤⣴⣶⣿⣿⣶⣦⣄⠉⠻⣿⡄⠘⢿⣿⡏⢀⣾⣿⣿⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⡇⢰⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿
⣿⣿⣿⣷⣄⠈⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠙⣿⣦⠀⠉⠛⠿⠿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣇⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿
⣿⣿⣿⣿⣿⣿⣶⣤⣀⡈⠉⠙⠙⠻⢿⣿⣿⣿⠀⣿⠁⠀⠀⠀⠀⠀⣤⣄⣬⠻⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠆⠀⣄⠙⢿⡟⢀⡇⠀⠀⠀⠀⠀⠀⡿⠟⠁⠀⢹⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣿⣏⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠆
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⣀⣴⣿⠤⠊⢀⣾⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠄⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣷
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⢠⣾⣿⣏⣀⡠⠀⠙⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠟
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠈⠿⣿⣿⣿⣇⠀⠀⠘⠻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠟⠃⢀
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⡀⠉⠛⠛⠀⠀⣶⣄⡀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢴⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣶⣿                                      
                                              by leemabi
                                              2025-5-16
        
        """

        tk.Label(content_frame,
                 text=about_text,
                 font=self.main_font,
                 fg=self.colors['text'],
                 bg=self.colors['panel'],
                 justify=tk.LEFT).pack()

        about_dialog.transient(self.root)
        about_dialog.grab_set()
        self.root.wait_window(about_dialog)

    def show_cyber_message(self, title, message, is_error=False):
        msg_box = tk.Toplevel(self.root)
        msg_box.title(f">_ {title}")
        msg_box.configure(bg=self.colors['panel'])

        border_color = self.colors['error'] if is_error else self.colors['primary']
        border_frame = tk.Frame(msg_box,
                                bg=border_color,
                                padx=1, pady=1)
        border_frame.pack(padx=10, pady=10)

        content_frame = tk.Frame(border_frame,
                                 bg=self.colors['panel'],
                                 padx=20, pady=20)
        content_frame.pack()

        tk.Label(content_frame,
                 text=message,
                 font=self.main_font,
                 fg=self.colors['text'],
                 bg=self.colors['panel']).pack(pady=10)

        btn_frame = tk.Frame(content_frame, bg=self.colors['panel'])
        btn_frame.pack(pady=(10, 0))

        def close():
            msg_box.destroy()

        tk.Button(btn_frame,
                  text="[确认]",
                  command=close,
                  font=self.button_font,
                  bg=self.colors['bg'],
                  fg=border_color,
                  activebackground=border_color,
                  activeforeground='white',
                  bd=0).pack()

        msg_box.transient(self.root)
        msg_box.grab_set()
        self.root.wait_window(msg_box)


if __name__ == "__main__":
    root = tk.Tk()

    # 添加启动动画
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash_width = 400
    splash_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - splash_width) // 2
    y = (screen_height - splash_height) // 2
    splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
    splash.configure(bg='black')

    loading_text = tk.Label(splash,
                            text="Lounding...",
                            font=('Courier New', 16),
                            fg='#00ff9d',
                            bg='black')
    loading_text.pack(pady=50)

    progress = ttk.Progressbar(splash,
                               orient='horizontal',
                               length=300,
                               mode='determinate')
    progress.pack()


    def update_progress():
        for i in range(101):
            progress['value'] = i
            loading_text.config(text=f"Lounding... {i}%")
            splash.update_idletasks()
            root.after(30)
        splash.destroy()
        root.deiconify()  # 显示主窗口
        CyberpunkContactApp(root)  # 创建应用实例


    root.after(100, update_progress)
    root.withdraw()

    root.mainloop()