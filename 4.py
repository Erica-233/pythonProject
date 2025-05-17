import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import base64
from datetime import datetime
import webbrowser


class CIASurveillanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("CIA 棱镜计划管理系统")
        self.root.geometry("1280x800")
        self.root.configure(bg="#001933")

        # 初始化情报数据库
        self.agents = {}
        self.current_file = None
        self.encryption_key = "CIA-TOP-SECRET-2023"

        # 配置冷战风格界面
        self.configure_styles()
        self.create_interface()
        self.load_demo_data()

        # 绑定全局事件
        self.root.bind("<Control-n>", lambda e: self.new_db())
        self.root.bind("<Control-s>", lambda e: self.save_db())
        self.root.bind("<Control-o>", lambda e: self.open_db())

    def configure_styles(self):
        """配置冷战时期界面风格"""
        style = ttk.Style()
        style.theme_use('alt')

        # CIA 标准配色方案
        style.configure(".",
                        background="#001933",
                        foreground="#C0C0C0",
                        font=("Consolas", 10))

        style.configure("TEntry",
                        fieldbackground="#0A1A2F",
                        insertcolor="#C0C0C0")

        style.configure("TButton",
                        background="#003366",
                        foreground="white",
                        borderwidth=2,
                        relief="raised")
        style.map("TButton",
                  background=[("active", "#004080")],
                  relief=[("pressed", "sunken")])

        style.configure("Treeview",
                        background="#0A1A2F",
                        fieldbackground="#0A1A2F",
                        foreground="#C0C0C0")
        style.configure("Treeview.Heading",
                        background="#00234C",
                        foreground="white",
                        font=("Arial Black", 10))

        style.configure("Red.TButton",
                        background="#8B0000",
                        foreground="white")

    def create_interface(self):
        """构建情报系统界面"""
        self.create_toolbar()
        self.create_input_panel()
        self.create_data_view()
        self.create_status_bar()

    def create_toolbar(self):
        """创建顶部情报工具条"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)

        btn_data = [
            ("新建数据库", "icons/database_add.png", self.new_db),
            ("打开数据库", "icons/folder_open.png", self.open_db),
            ("保存数据库", "icons/disk.png", self.save_db),
            ("导出报告", "icons/report.png", self.export_report),
            ("卫星定位", "icons/satellite.png", self.show_geo_map),
            ("通讯监听", "icons/radio.png", self.monitor_comms),
            ("销毁证据", "icons/fire.png", self.wipe_data)
        ]

        for text, icon, cmd in btn_data:
            btn = ttk.Button(toolbar, text=text, command=cmd, style="Toolbutton")
            btn.pack(side=tk.LEFT, padx=2)

    def create_input_panel(self):
        """创建情报员信息输入面板"""
        input_frame = ttk.LabelFrame(self.root, text="特工档案管理", padding=(15, 10))
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # 核心信息输入区
        core_info = ttk.Frame(input_frame)
        core_info.grid(row=0, column=0, sticky=tk.W)

        fields = [
            ("agent_id", "特工编号:", 12),
            ("codename", "行动代号:", 15),
            ("age", "年龄:", 5),
            ("status", "当前状态:", 10),
            ("clearance", "密级:", 8),
            ("last_contact", "最后联络:", 15)
        ]

        self.entries = {}
        for row, (field, label, width) in enumerate(fields):
            ttk.Label(core_info, text=label).grid(row=row, column=0, sticky=tk.W)
            if field == "status":
                entry = ttk.Combobox(core_info,
                                     values=["活跃", "休眠", "被捕", "阵亡", "叛逃"],
                                     width=width)
            elif field == "clearance":
                entry = ttk.Combobox(core_info,
                                     values=["绝密", "机密", "秘密", "公开"],
                                     width=width)
            else:
                entry = ttk.Entry(core_info, width=width)
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.entries[field] = entry

        # 位置信息
        loc_frame = ttk.Frame(input_frame)
        loc_frame.grid(row=0, column=1, sticky=tk.EW, padx=20)

        ttk.Label(loc_frame, text="当前位置:").pack(side=tk.LEFT)
        self.entries["location"] = ttk.Entry(loc_frame, width=25)
        self.entries["location"].pack(side=tk.LEFT, padx=5)

        ttk.Button(loc_frame, text="地图标记",
                   command=self.mark_location).pack(side=tk.LEFT)

        # 任务记录系统
        ttk.Label(input_frame, text="任务记录:").grid(row=1, column=0, sticky=tk.W)
        self.mission_log = tk.Text(input_frame, height=5, wrap=tk.WORD,
                                   bg="#0A1A2F", fg="#C0C0C0",
                                   insertbackground="#C0C0C0")
        self.mission_log.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # 控制按钮
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(btn_frame, text="提交档案", command=self.update_agent).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="清除数据", command=self.clear_entries).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="删除特工", command=self.delete_agent, style="Red.TButton").pack(side=tk.LEFT,
                                                                                                    padx=3)
        ttk.Button(btn_frame, text="风险评估", command=self.risk_analysis).pack(side=tk.LEFT, padx=3)

        input_frame.grid_columnconfigure(1, weight=1)

    def create_data_view(self):
        """创建情报数据库视图"""
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = [
            ("agent_id", "编号", 100),
            ("codename", "代号", 120),
            ("age", "年龄", 60),
            ("status", "状态", 80),
            ("clearance", "密级", 80),
            ("location", "位置", 200),
            ("last_contact", "最后联络", 150)
        ]

        self.tree = ttk.Treeview(tree_frame, columns=[c[0] for c in columns],
                                 show="headings", selectmode="extended")

        for col_id, col_text, col_width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=col_width, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.show_full_profile)

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

    def create_status_bar(self):
        """创建情报系统状态栏"""
        self.status = ttk.Label(self.root, text="就绪 | 数据库: 未加载 | 特工总数: 0",
                                relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self):
        """更新状态栏信息"""
        db_status = self.current_file if self.current_file else "未加载"
        count = len(self.agents)
        self.status.config(text=f"就绪 | 数据库: {db_status} | 特工总数: {count}")

    def update_agent(self):
        """更新或添加特工档案"""
        agent_id = self.entries["agent_id"].get().strip()
        if not agent_id:
            messagebox.showerror("输入错误", "必须提供特工编号")
            return

        agent_data = {
            "codename": self.entries["codename"].get().strip(),
            "age": self.entries["age"].get().strip(),
            "status": self.entries["status"].get(),
            "clearance": self.entries["clearance"].get(),
            "location": self.entries["location"].get().strip(),
            "last_contact": self.entries["last_contact"].get().strip(),
            "missions": self.mission_log.get("1.0", tk.END).strip(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 数据验证
        if not agent_data["codename"]:
            messagebox.showerror("输入错误", "必须填写行动代号")
            return

        self.agents[agent_id] = agent_data
        self.update_treeview()
        self.update_status()
        messagebox.showinfo("操作成功", f"特工档案 {agent_id} 已更新")
        self.clear_entries()

    def delete_agent(self):
        """删除选定特工档案"""
        selected = self.tree.selection()
        if not selected:
            return

        agent_ids = [self.tree.item(i, "values")[0] for i in selected]
        confirm = messagebox.askyesno("确认删除",
                                      f"确定要永久删除选定的 {len(agent_ids)} 个特工档案？")
        if confirm:
            for agent_id in agent_ids:
                del self.agents[agent_id]
            self.update_treeview()
            self.update_status()

    def update_treeview(self):
        """更新情报数据库视图"""
        self.tree.delete(*self.tree.get_children())
        for agent_id, data in self.agents.items():
            self.tree.insert("", "end", values=(
                agent_id,
                data["codename"],
                data["age"],
                data["status"],
                data["clearance"],
                data["location"],
                data["last_contact"]
            ))

    def show_full_profile(self, event):
        """显示完整特工档案"""
        selected = self.tree.selection()
        if not selected:
            return

        agent_id = self.tree.item(selected[0], "values")[0]
        data = self.agents.get(agent_id)

        profile = tk.Toplevel(self.root)
        profile.title(f"绝密档案 - {agent_id}")
        profile.geometry("600x500")

        notebook = ttk.Notebook(profile)

        # 基本信息标签页
        basic_frame = ttk.Frame(notebook)
        self.create_profile_tab(basic_frame, data)
        notebook.add(basic_frame, text="基本信息")

        # 任务记录标签页
        mission_frame = ttk.Frame(notebook)
        mission_text = tk.Text(mission_frame, wrap=tk.WORD, bg="#0A1A2F", fg="#C0C0C0")
        mission_text.insert(tk.END, data.get("missions", "暂无记录"))
        mission_text.config(state=tk.DISABLED)
        mission_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(mission_frame, text="任务记录")

        notebook.pack(fill=tk.BOTH, expand=True)

    def create_profile_tab(self, frame, data):
        """创建档案信息标签页"""
        fields = [
            ("行动代号:", data["codename"]),
            ("年龄:", data["age"]),
            ("当前状态:", data["status"]),
            ("安全密级:", data["clearance"]),
            ("最后已知位置:", data["location"]),
            ("最后联络时间:", data["last_contact"]),
            ("建档时间:", data["created"]),
            ("最后修改:", data["modified"])
        ]

        for i, (label, value) in enumerate(fields):
            ttk.Label(frame, text=label, font=("Consolas", 10, "bold")).grid(row=i, column=0, sticky=tk.W, padx=10,
                                                                             pady=2)
            ttk.Label(frame, text=value).grid(row=i, column=1, sticky=tk.W, padx=10, pady=2)

    def risk_analysis(self):
        """执行风险评估分析"""
        analysis = {
            "active": 0,
            "captured": 0,
            "compromised": 0,
            "high_risk": 0
        }

        for agent in self.agents.values():
            if agent["status"] == "被捕":
                analysis["captured"] += 1
                analysis["high_risk"] += 1
            elif agent["status"] == "叛逃":
                analysis["compromised"] += 1
                analysis["high_risk"] += 1
            elif agent["status"] == "活跃":
                analysis["active"] += 1

        report = f"""▌ 风险评估报告 ▐

总特工人数: {len(self.agents)}
活跃特工: {analysis['active']}
被捕人员: {analysis['captured']}
叛逃特工: {analysis['compromised']}
高风险人员: {analysis['high_risk']}

评估建议:
"""
        if analysis['high_risk'] > 0:
            report += "! 检测到高风险人员，建议立即启动应急协议 !"
        else:
            report += "当前风险等级：绿色（安全）"

        messagebox.showinfo("风险评估", report)

    # 以下为数据持久化相关方法
    def new_db(self):
        if messagebox.askyesno("新建数据库", "这将清除当前所有未保存数据，是否继续？"):
            self.agents.clear()
            self.current_file = None
            self.update_treeview()
            self.update_status()

    def open_db(self):
        file_path = filedialog.askopenfilename(filetypes=[("CIA数据库", "*.ciadb")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    encrypted = f.read()
                    decoded = base64.b64decode(encrypted).decode()
                    self.agents = json.loads(decoded)
                self.current_file = file_path
                self.update_treeview()
                self.update_status()
                messagebox.showinfo("成功", "数据库解密加载完成")
            except Exception as e:
                messagebox.showerror("错误", f"数据库读取失败: {str(e)}")

    def save_db(self):
        if not self.current_file:
            self.save_db_as()
            return

        try:
            data = json.dumps(self.agents, indent=2)
            encrypted = base64.b64encode(data.encode()).decode()
            with open(self.current_file, "w") as f:
                f.write(encrypted)
            messagebox.showinfo("成功", "数据库加密保存完成")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def save_db_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".ciadb",
                                                 filetypes=[("CIA数据库", "*.ciadb")])
        if file_path:
            self.current_file = file_path
            self.save_db()

    def export_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("文本文件", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(f"▌ CIA 秘密行动报告 - {datetime.now().strftime('%Y-%m-%d')} ▐\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"数据库路径: {self.current_file or '内存数据库'}\n")
                    f.write("\n=== 活跃特工名单 ===\n")
                    for agent_id, data in self.agents.items():
                        if data["status"] == "活跃":
                            f.write(f"{agent_id} | {data['codename']} | {data['location']}\n")
                messagebox.showinfo("成功", "行动报告导出完成")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def show_context_menu(self, event):
        """显示右键上下文菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="快速定位", command=self.mark_location)
        menu.add_command(label="发送指令", command=self.send_order)
        menu.add_separator()
        menu.add_command(label="标记为叛逃", command=lambda: self.change_status("叛逃"))
        menu.add_command(label="标记为被捕", command=lambda: self.change_status("被捕"))
        menu.add_command(label="标记为休眠", command=lambda: self.change_status("休眠"))
        menu.tk_popup(event.x_root, event.y_root)

    def change_status(self, status):
        """快速修改特工状态"""
        selected = self.tree.selection()
        for item in selected:
            agent_id = self.tree.item(item, "values")[0]
            self.agents[agent_id]["status"] = status
        self.update_treeview()

    def mark_location(self):
        """地图标记功能（演示）"""
        webbrowser.open("https://www.openstreetmap.org/")

    def monitor_comms(self):
        """通讯监听模拟"""
        messagebox.showinfo("通讯监听", "正在扫描加密频道...\n检测到3条未解密信息")

    def wipe_data(self):
        """安全擦除数据"""
        if messagebox.askyesno("销毁证据", "将永久删除所有数据！"):
            self.agents.clear()
            self.current_file = None
            self.update_treeview()
            self.update_status()

    def clear_entries(self):
        """清空输入表单"""
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)
        self.mission_log.delete("1.0", tk.END)

    def load_demo_data(self):
        """加载演示数据"""
        self.agents["007"] = {
            "codename": "幽灵",
            "age": 35,
            "status": "活跃",
            "clearance": "绝密",
            "location": "莫斯科",
            "last_contact": "2023-10-15 23:45",
            "missions": "2023-09-01: 渗透克格勃总部\n2023-10-05: 获取核武计划",
            "created": "2023-01-01 09:00",
            "modified": "2023-10-15 23:45"
        }
        self.update_treeview()
        self.update_status()


if __name__ == "__main__":
    root = tk.Tk()
    app = CIASurveillanceSystem(root)
    root.mainloop()