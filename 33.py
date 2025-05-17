import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime


class CIASurveillanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("CIA 战略情报管理系统")
        self.root.geometry("1200x800")
        self.root.configure(bg="#001933")

        # CIA风格配色（深蓝、金属灰、警报红）
        self.style_config = {
            "bg_color": "#001933",  # 深蓝色背景
            "fg_color": "#C0C0C0",  # 银色文字
            "accent_color": "#002366",  # CIA标志蓝
            "alert_color": "#8B0000",  # 警报红色
            "field_bg": "#0A1A2F",  # 输入框背景
            "button_color": "#003366"  # 按钮颜色
        }

        self.agents = {}
        self.current_file = None

        # 初始化样式
        self.configure_styles()
        self.create_widgets()
        self.load_initial_data()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # 全局样式配置
        style.configure(".",
                        background=self.style_config["bg_color"],
                        foreground=self.style_config["fg_color"],
                        font=("Consolas", 10))

        # 输入框样式
        style.configure("TEntry",
                        fieldbackground=self.style_config["field_bg"],
                        foreground=self.style_config["fg_color"],
                        insertcolor=self.style_config["fg_color"])

        # 按钮样式
        style.configure("TButton",
                        background=self.style_config["button_color"],
                        foreground=self.style_config["fg_color"],
                        borderwidth=1,
                        relief="raised")
        style.map("TButton",
                  background=[("active", self.style_config["accent_color"])])

        # 树状视图样式
        style.configure("Treeview",
                        background=self.style_config["field_bg"],
                        fieldbackground=self.style_config["field_bg"],
                        foreground=self.style_config["fg_color"])
        style.configure("Treeview.Heading",
                        background=self.style_config["accent_color"],
                        foreground="white",
                        font=("Arial", 10, "bold"))

    def create_widgets(self):
        # 顶部工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="新建数据库", command=self.new_db).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="打开数据库", command=self.open_db).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="保存数据库", command=self.save_db).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导出报告", command=self.export_report).pack(side=tk.LEFT, padx=2)

        # 情报员信息输入面板
        input_frame = ttk.LabelFrame(self.root, text="情报员档案管理", padding=(10, 5))
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # 输入字段
        fields = [
            ("agent_id", "特工编号:"),
            ("codename", "行动代号:"),
            ("age", "年龄:"),
            ("location", "当前位置:"),
            ("status", "当前状态:"),
            ("last_contact", "最后联络:")
        ]

        self.entries = {}
        for i, (field, label) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky=tk.W, pady=2)
            if field == "status":
                entry = ttk.Combobox(input_frame, values=["活跃", "休眠", "被捕", "阵亡"])
            else:
                entry = ttk.Entry(input_frame)
            entry.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky=tk.EW, padx=5, pady=2)
            self.entries[field] = entry

        # 任务记录
        ttk.Label(input_frame, text="最新任务记录:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.mission_log = tk.Text(input_frame, height=4,
                                   bg=self.style_config["field_bg"],
                                   fg=self.style_config["fg_color"],
                                   insertbackground=self.style_config["fg_color"])
        self.mission_log.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=2)

        # 控制按钮
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=5)

        ttk.Button(btn_frame, text="添加/更新档案", command=self.update_agent).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="清除记录", command=self.clear_entries).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="删除特工", command=self.delete_agent).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="深度分析", command=self.show_analysis).pack(side=tk.LEFT, padx=3)

        # 情报数据库视图
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("agent_id", "codename", "age", "location", "status", "last_contact")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        # 设置列参数
        col_widths = {
            "agent_id": 120,
            "codename": 150,
            "age": 80,
            "location": 200,
            "status": 100,
            "last_contact": 150
        }

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths[col], anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # 绑定事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.show_full_profile)

    def update_agent(self):
        agent_id = self.entries["agent_id"].get().strip()
        if not agent_id:
            messagebox.showerror("错误", "必须输入特工编号")
            return

        # 构建特工数据
        agent_data = {
            "codename": self.entries["codename"].get().strip(),
            "age": self.entries["age"].get().strip(),
            "location": self.entries["location"].get().strip(),
            "status": self.entries["status"].get(),
            "last_contact": self.entries["last_contact"].get().strip(),
            "missions": self.mission_log.get("1.0", tk.END).strip(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 验证必要字段
        if not all([agent_data["codename"], agent_data["location"]]):
            messagebox.showerror("错误", "必须填写行动代号和当前位置")
            return

        self.agents[agent_id] = agent_data
        self.update_treeview()
        messagebox.showinfo("成功", f"特工 {agent_data['codename']} 档案已更新")
        self.clear_entries()

    def delete_agent(self):
        selected = self.tree.selection()
        if not selected:
            return

        agent_id = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("确认", f"确定要删除特工 {agent_id} 的所有记录？"):
            del self.agents[agent_id]
            self.update_treeview()

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for agent_id, data in self.agents.items():
            self.tree.insert("", "end", values=(
                agent_id,
                data["codename"],
                data["age"],
                data["location"],
                data["status"],
                data["last_contact"]
            ))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        agent_id = self.tree.item(selected[0], "values")[0]
        agent_data = self.agents.get(agent_id)
        if agent_data:
            self.entries["agent_id"].delete(0, tk.END)
            self.entries["agent_id"].insert(0, agent_id)
            self.entries["codename"].delete(0, tk.END)
            self.entries["codename"].insert(0, agent_data["codename"])
            self.entries["age"].delete(0, tk.END)
            self.entries["age"].insert(0, agent_data["age"])
            self.entries["location"].delete(0, tk.END)
            self.entries["location"].insert(0, agent_data["location"])
            self.entries["status"].set(agent_data["status"])
            self.entries["last_contact"].delete(0, tk.END)
            self.entries["last_contact"].insert(0, agent_data["last_contact"])
            self.mission_log.delete("1.0", tk.END)
            self.mission_log.insert("1.0", agent_data.get("missions", ""))

    def show_full_profile(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        agent_id = self.tree.item(selected[0], "values")[0]
        agent_data = self.agents.get(agent_id)

        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"绝密档案 - {agent_id}")
        profile_window.geometry("600x400")

        txt = tk.Text(profile_window, bg=self.style_config["field_bg"],
                      fg=self.style_config["fg_color"], wrap=tk.WORD)
        vsb = ttk.Scrollbar(profile_window, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)

        profile_content = f"""▌ CIA 绝密档案 - {agent_data['codename']} ▐

编号: {agent_id}
年龄: {agent_data['age']}
状态: {agent_data['status']}
最后已知位置: {agent_data['location']}
最后联络时间: {agent_data['last_contact']}
建档时间: {agent_data['created']}

=== 任务记录 ===
{agent_data.get('missions', '暂无记录')}
"""
        txt.insert(tk.END, profile_content)
        txt.configure(state="disabled")

    def show_analysis(self):
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("战略态势分析")
        analysis_window.geometry("400x300")

        status_count = {}
        for agent in self.agents.values():
            status = agent["status"]
            status_count[status] = status_count.get(status, 0) + 1

        analysis_text = "▌ 当前行动态势分析 ▐\n\n"
        analysis_text += f"总特工人数: {len(self.agents)}\n"
        for status, count in status_count.items():
            analysis_text += f"{status}: {count}\n"

        lbl = ttk.Label(analysis_window, text=analysis_text, justify=tk.LEFT)
        lbl.pack(padx=10, pady=10)

    def new_db(self):
        if messagebox.askyesno("新建数据库", "这将清除当前所有数据，是否继续？"):
            self.agents.clear()
            self.update_treeview()
            self.current_file = None

    def open_db(self):
        file_path = filedialog.askopenfilename(filetypes=[("CIA数据库文件", "*.ciadb")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.agents = json.load(f)
                self.current_file = file_path
                self.update_treeview()
                messagebox.showinfo("成功", "数据库加载完成")
            except Exception as e:
                messagebox.showerror("错误", f"文件加载失败: {str(e)}")

    def save_db(self):
        if not self.current_file:
            self.save_db_as()
            return

        try:
            with open(self.current_file, "w") as f:
                json.dump(self.agents, f, indent=2)
            messagebox.showinfo("成功", "数据库保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def save_db_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".ciadb",
                                                 filetypes=[("CIA数据库文件", "*.ciadb")])
        if file_path:
            self.current_file = file_path
            self.save_db()

    def export_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("文本文件", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("▌ CIA 战略情报报告 ▐\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for agent_id, data in self.agents.items():
                        f.write(f"特工编号: {agent_id}\n")
                        f.write(f"行动代号: {data['codename']}\n")
                        f.write(f"当前状态: {data['status']}\n")
                        f.write("=" * 40 + "\n")
                messagebox.showinfo("成功", "报告导出完成")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)
        self.mission_log.delete("1.0", tk.END)

    def load_initial_data(self):
        # 示例数据加载（实际使用时可移除）
        self.agents["007"] = {
            "codename": "Ghost",
            "age": 35,
            "location": "莫斯科",
            "status": "活跃",
            "last_contact": "2023-10-05 22:00",
            "missions": "2023-09-15: 成功渗透克格勃网络\n2023-10-01: 获取核武计划情报",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.update_treeview()


if __name__ == "__main__":
    root = tk.Tk()
    app = CIASurveillanceSystem(root)
    root.mainloop()