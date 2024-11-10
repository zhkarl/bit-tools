import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk, Menu
import json

class ScriptManager:
    def __init__(self):
        self.scripts = []

    def add_command(self, command, params=None, index=None):
        """添加指令和参数"""
        if index is not None:
            self.scripts.insert(index, {'command': command, 'params': params})  # 在指定位置插入
        else:
            self.scripts.append({'command': command, 'params': params})  # 默认添加到末尾

    def remove_command(self, index):
        """删除指定索引的指令"""
        if 0 <= index < len(self.scripts):
            self.scripts.pop(index)

    def modify_command(self, index, command, params):
        """修改指定索引的指令"""
        if 0 <= index < len(self.scripts):
            self.scripts[index] = {'command': command, 'params': params}

    def save_script(self, filename):
        """将指令保存为文件，确保中文可读"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scripts, f, indent=4, ensure_ascii=False)

    def load_script(self, filename):
        """从文件加载指令"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.scripts = json.load(f)

class App:
    def __init__(self, root):
        self.manager = ScriptManager()
        self.root = root
        self.root.title("脚本管理器 v1.0")
        self.root.iconbitmap(".\\resource\\actor.ico")

        # 创建顶部按钮框架
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))

        # 添加保存、加载和清空按钮到顶部
        save_button = tk.Button(top_frame, text="保存脚本", command=self.save_script)
        save_button.pack(side=tk.LEFT, padx=(5, 0))

        load_button = tk.Button(top_frame, text="加载脚本", command=self.load_script)
        load_button.pack(side=tk.LEFT, padx=(0, 5))

        clear_button = tk.Button(top_frame, text="清空列表", command=self.clear_scripts)
        clear_button.pack(side=tk.LEFT, padx=5)

        # 创建主框架
        main_frame = tk.Frame(root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建左侧框架
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 创建浏览器指令按钮
        browser_frame = tk.LabelFrame(left_frame, text="浏览器指令")
        browser_frame.pack(pady=5, padx=5, fill="both", expand=True)

        browser_commands = [
            "创建比特窗口", "打开比特窗口", "关闭比特窗口", "删除比特窗口", "重置关闭状态",
            "清理窗口缓存", "一键排列窗口", "修改窗口代理", "窗口随机指纹", "窗口固定指纹", "Google搜索"
        ]

        for command in browser_commands:
            button = tk.Button(browser_frame, text=command, command=lambda cmd=command: self.handle_command(cmd))
            button.pack(side=tk.TOP, padx=5, pady=5)

        # 创建中间框架
        mid_frame = tk.Frame(main_frame)
        mid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(mid_frame, text="指令列表：").pack(side=tk.TOP, anchor=tk.W)
        # 创建中间列表框
        self.command_listbox = tk.Listbox(mid_frame, width=50)
        self.command_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))

        # 创建右侧框架
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建窗口指令按钮
        window_frame = tk.LabelFrame(right_frame, text="窗口指令")
        window_frame.pack(pady=5, padx=5, fill="both", expand=True)

        window_commands = [
            "访问URL", "滚动页面", "回到顶部", "鼠标悬停", "鼠标点击", "元素等待", "元素滚动", "输入文本", "时间等待", "循环起点", "循环终点"
        ]

        for command in window_commands:
            button = tk.Button(window_frame, text=command, command=lambda cmd=command: self.handle_command(cmd))
            button.pack(side=tk.TOP, padx=5, pady=5)

        # 绑定删除键事件
        self.command_listbox.bind('<Delete>', self.delete_command)
        # 绑定上下键事件
        self.command_listbox.bind('<Up>', self.move_up)
        self.command_listbox.bind('<Down>', self.move_down)

    def handle_command(self, command):
        """处理指令按钮点击事件"""
        if command == "创建比特窗口":
            self.create_bit_window()
        elif command == "修改窗口代理":
            self.modify_proxy()
        elif command == "Google搜索":
            self.get_google_search_input()
        elif command == "窗口固定指纹":
            self.get_browser_fingerprint_input()
        elif command in ["打开比特窗口", "关闭比特窗口", "删除比特窗口", "重置关闭状态",
                         "获取窗口详情", "清理窗口缓存", "一键排列窗口", "窗口随机指纹", "修改窗口代理"]:
            self.command_join(command)
        elif command in ["鼠标悬停", "鼠标点击", "元素等待", "元素滚动"]:
            self.get_element_input(command)
        elif command == "滚动页面":
            self.get_scroll_input()
        elif command == "访问URL":
            self.access_url()
        elif command == "输入文本":
            self.get_input_text()
        elif command == "时间等待":
            self.get_time_wait_input()
        elif command in ["循环起点", "循环终点", "回到顶部"]:
            self.command_join(command)
        else:
            params = simpledialog.askstring("输入参数", f"请输入参数 (指令: {command}):")
            if params is not None:
                param_list = [param.strip() for param in params.split(',')] if params else []
                self.command_join(command, param_list)

    def get_time_wait_input(self):
        """获取时间等待的秒数输入"""
        window = tk.Toplevel(self.root)
        window.title("时间等待 - 输入秒数")

        tk.Label(window, text="请输入等待的秒数:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        seconds_entry = tk.Entry(window)
        seconds_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 随机等待复选框
        random_wait_var = tk.BooleanVar(value=False)
        random_wait_check = tk.Checkbutton(window, text="随机等待", variable=random_wait_var)
        random_wait_check.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_time_wait_confirm(seconds_entry.get(), random_wait_var.get(), window))
        confirm_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_time_wait_confirm(self, seconds, is_random, window):
        """确认按钮的回调函数，用于处理时间等待的秒数输入"""
        if seconds.isdigit():
            # 根据 is_random 的值设置参数
            random_param = "是" if is_random else "否"
            self.command_join("时间等待", [seconds, random_param])
            window.destroy()
        else:
            messagebox.showwarning("输入错误", "请提供有效的秒数。")

    def get_input_text(self):
        """获取输入文本的元素和文本内容"""
        window = tk.Toplevel(self.root)
        window.title("输入文本 - 输入元素和内容")

        tk.Label(window, text="请输入元选择器:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        element_entry = tk.Entry(window)
        element_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        tk.Label(window, text="请输入文本内容:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        text_entry = tk.Entry(window)
        text_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)

        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_input_text_confirm(element_entry.get(), text_entry.get(), window))
        confirm_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_input_text_confirm(self, element, text, window):
        """确认按钮的回调函数，用于处理输入文本的元素和内容"""
        if element and text:
            self.command_join("输入文本", [element, text])
            window.destroy()
        else:
            messagebox.showwarning("输入错误", "请提供有效的元素选择器和文本内容。")

    def get_scroll_input(self):
        """获取滚动页面的像素输入"""
        window = tk.Toplevel(self.root)
        window.title("滚动页面 - 输入像素")

        # 滚动像素输入框
        tk.Label(window, text="请输入滚动的像素:").grid(row=0, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        pixel_entry = tk.Entry(window)
        pixel_entry.grid(row=0, column=1, padx=10, pady=(10, 5), sticky=tk.EW)
        tk.Label(window, text="正数向下滚动，负数向上滚动").grid(row=1, column=1, padx=10, pady=(0, 10), sticky=tk.W)

        # 随机滚动复选框
        random_scroll_var = tk.BooleanVar(value=False)
        random_scroll_check = tk.Checkbutton(window, text="随机滚动", variable=random_scroll_var)
        random_scroll_check.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # 确认按钮
        confirm_button = tk.Button(window, text="确认",
                                   command=lambda: self.on_scroll_confirm(pixel_entry.get(),
                                                                          random_scroll_var.get(),
                                                                          window))
        confirm_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_scroll_confirm(self, pixels, is_random, window):
        """确认按钮的回调函数，用于处理滚动输入"""
        try:
            # 尝试将输入转换为整数，允许负数
            pixel_value = int(pixels)
            params = [str(pixel_value), "是" if is_random else "否"]
            self.command_join("滚动页面", params)
            window.destroy()
        except ValueError:
            messagebox.showwarning("输入错误", "请提供有效的整数值（可以是负数）。")

    def get_element_input(self, command):
        """获取元素输入"""
        window = tk.Toplevel(self.root)
        window.title(f"{command} - 输入元素")

        tk.Label(window, text="请输入元素选择器:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        element_entry = tk.Entry(window)
        element_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_element_confirm(command, element_entry.get(), window))
        confirm_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_element_confirm(self, command, element, window):
        """确认按钮的回调函数，用于处理元素输入"""
        if element:
            self.command_join(command, [element])
            window.destroy()
        else:
            messagebox.showwarning("输入错误", "请提供有效的元素选择器。")

    def create_bit_window(self):
        """处理创建比特窗口令的参数输入"""
        # 创建一个新的窗口
        window = tk.Toplevel(self.root)
        window.title("创建比特窗口")

        # 服务址输入框
        tk.Label(window, text="服务地址:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        service_address_entry = tk.Entry(window)
        service_address_entry.insert(0, "http://127.0.0.1:54345")  # 默认值
        service_address_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 禁止加载图片复选框
        disable_images_var = tk.BooleanVar(value=True)
        disable_images_check = tk.Checkbutton(window, text="禁止加载图片", variable=disable_images_var)
        disable_images_check.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # 禁止视频自动播放复选框
        disable_autoplay_var = tk.BooleanVar(value=True)
        disable_autoplay_check = tk.Checkbutton(window, text="禁止视频自动播放", variable=disable_autoplay_var)
        disable_autoplay_check.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # 启用代理选框
        enable_proxy_var = tk.BooleanVar(value=True)
        enable_proxy_check = tk.Checkbutton(window, text="启用代理API", variable=enable_proxy_var)
        enable_proxy_check.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # 代理地入框
        tk.Label(window, text="代理地址:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        proxy_address_entry = tk.Entry(window)
        proxy_address_entry.grid(row=4, column=1, padx=10, pady=10)
        proxy_address_entry.insert(0, "http://127.0.0.1:5001/proxy")

        # 确认按钮
        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_confirm(service_address_entry, disable_images_var, disable_autoplay_var, enable_proxy_var, proxy_address_entry, window), padx=10)
        confirm_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def access_url(self):
        """处理访问URL的参数输入"""
        # 创建一个新的窗口
        window = tk.Toplevel(self.root)
        window.title("访问URL")

        # URL输入框
        tk.Label(window, text="请输入URL:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        url_entry = tk.Entry(window)
        url_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 确认按钮
        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_access_url_confirm(url_entry, window), padx=10)
        confirm_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_access_url_confirm(self, url_entry, window):
        """确认按钮的回调函数，用于访问URL"""
        url = url_entry.get()
        if url:
            self.command_join("访问URL", [url])
            window.destroy()
        else:
            messagebox.showwarning("输入错误", "请提供有效的URL。")

    def command_join(self, command, params=None):
        """处理新指令，插入到当前选中指令下方"""
        selected_index = self.command_listbox.curselection()
        if selected_index:
            index = selected_index[0] + 1  # 在当前选中指令下方插入
        else:
            index = len(self.manager.scripts)  # 如果没有选中指令，则放在末尾

        self.manager.add_command(command, params, index=index)
        self.update_command_listbox()
        self.command_listbox.selection_set(index)  # 选中插入后的指令

    def on_confirm(self, service_address_entry, disable_images_var, disable_autoplay_var, enable_proxy_var, proxy_address_entry, window):
        """确认按钮的回调函数"""
        service_address = service_address_entry.get()
        params = [
            service_address,
            "是" if disable_images_var.get() else "否",
            "是" if disable_autoplay_var.get() else "否",
            "是" if enable_proxy_var.get() else "否",
            proxy_address_entry.get()  # 代理地址
        ]
        self.command_join("创建比特窗口", params)
        window.destroy()

    def delete_command(self, event=None):
        """删除选中的指令"""
        selected_index = self.command_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.manager.remove_command(index)
            self.update_command_listbox()
            # messagebox.showinfo("删除成功", "指令已删除。")
        else:
            messagebox.showwarning("删除失败", "请先选择要删除的指令。")

    def move_up(self, event=None):
        """将选中的指令向上移动"""
        selected_index = self.command_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            if index > 0:  # 确保不是第一个元素
                # 交换指令
                self.manager.scripts[index], self.manager.scripts[index - 1] = self.manager.scripts[index - 1], self.manager.scripts[index]
                self.update_command_listbox()
                self.command_listbox.selection_clear(0, "end")
                self.command_listbox.selection_set(index)  # 选中上移后的元素
                self.command_listbox.activate(index)

    def move_down(self, event=None):
        """将选中的指令向下移动"""
        selected_index = self.command_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            if index < len(self.manager.scripts) - 1:  # 确保不是最后一个元素
                # 交换指令
                self.manager.scripts[index], self.manager.scripts[index + 1] = self.manager.scripts[index + 1], self.manager.scripts[index]
                self.update_command_listbox()
                self.command_listbox.selection_clear(0, "end")
                self.command_listbox.selection_set(index)  # 选中下移后的元素
                self.command_listbox.activate(index)

    def save_script(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.manager.save_script(filename)
            messagebox.showinfo("保存成功", "脚本已保存。")

    def load_script(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.manager.load_script(filename)
            self.update_command_listbox()
            messagebox.showinfo("加载成功", "脚本已加载。")

    def update_command_listbox(self):
        self.command_listbox.delete(0, tk.END)
        for script in self.manager.scripts:
            if script['params'] is None:
                self.command_listbox.insert(tk.END, f"{script['command']}")
            else:
                self.command_listbox.insert(tk.END, f"{script['command']}({', '.join(script['params'])})")

    def clear_scripts(self):
        """清空脚本列表"""
        if messagebox.askyesno("确认清空", "确定要清空所有指令吗？"):
            self.manager.scripts.clear()
            self.update_command_listbox()

    def get_google_search_input(self):
        """获取Google搜索的参数输入"""
        window = tk.Toplevel(self.root)
        window.title("Google搜索 - 输入参数")

        # 站点输入框
        tk.Label(window, text="站点:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        site_entry = tk.Entry(window)
        site_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # 关键词输入框
        tk.Label(window, text="关键词:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        keyword_entry = tk.Entry(window)
        keyword_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # 起始页输入框
        tk.Label(window, text="起始页:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        start_page_entry = tk.Entry(window)
        start_page_entry.insert(0, "1")  # 默认值
        start_page_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        
        # 结束页输入框
        tk.Label(window, text="结束页:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        end_page_entry = tk.Entry(window)
        end_page_entry.insert(0, "50")  # 默认值
        end_page_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.EW)

        # 是否循环复选框
        loop_var = tk.BooleanVar(value=True)  # 默认是
        loop_check = tk.Checkbutton(window, text="是否循环", variable=loop_var)
        loop_check.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        # 确认按钮
        confirm_button = tk.Button(window, text="确认",
                                   command=lambda: self.on_google_search_confirm(
                                       site_entry.get(),
                                       keyword_entry.get(),
                                       start_page_entry.get(),
                                       end_page_entry.get(),
                                       loop_var.get(),  # 获取是否循环的值
                                       window))
        confirm_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_google_search_confirm(self, site, keyword, start_page, end_page, is_loop, window):
        """确认按钮的回调函数，用于处理Google搜索参数"""
        if not site or not keyword:
            messagebox.showwarning("输入错误", "请提供站点和关键词。")
            return
            
        try:
            start = int(start_page)
            end = int(end_page)
            if start <= 0 or end < start:
                raise ValueError
            
            params = [site, keyword, str(start), str(end), "是" if is_loop else "否"]  # 添加循环参数
            self.command_join("Google搜索", params)
            window.destroy()
        except ValueError:
            messagebox.showwarning("输入错误", "请提供有效的页码范围（起始页必须大于0，结束页必须大于等于起始页）。")

    def modify_proxy(self):
        """处理修改窗口代理的参数输入"""
        window = tk.Toplevel(self.root)
        window.title("修改窗口代理")

        # 代理模式选择
        mode_frame = tk.LabelFrame(window, text="代理模式")
        mode_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky=tk.EW)
        
        proxy_mode_var = tk.StringVar(value="fixed")
        tk.Radiobutton(mode_frame, text="固定代理", variable=proxy_mode_var, 
                      value="fixed", command=lambda: self.toggle_proxy_fields(proxy_fields_frame, api_frame, proxy_mode_var.get())
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Radiobutton(mode_frame, text="接口代理", variable=proxy_mode_var, 
                      value="api", command=lambda: self.toggle_proxy_fields(proxy_fields_frame, api_frame, proxy_mode_var.get())
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # 代理类型选择（仅用于固定代理）
        type_frame = tk.LabelFrame(window, text="代理类型")
        type_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.EW)
        
        proxy_type_var = tk.StringVar(value="http")
        tk.Radiobutton(type_frame, text="HTTP", variable=proxy_type_var, value="http").pack(side=tk.LEFT, padx=10, pady=5)
        tk.Radiobutton(type_frame, text="HTTPS", variable=proxy_type_var, value="https").pack(side=tk.LEFT, padx=10, pady=5)
        tk.Radiobutton(type_frame, text="SOCKS5", variable=proxy_type_var, value="socks5").pack(side=tk.LEFT, padx=10, pady=5)

        # 代理参数输入框架
        proxy_fields_frame = tk.Frame(window)
        proxy_fields_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.EW)

        # 代理参数输入框
        tk.Label(proxy_fields_frame, text="代理参数:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        proxy_params_entry = tk.Entry(proxy_fields_frame)
        proxy_params_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # 提示标签
        tk.Label(proxy_fields_frame, text="格式: IP/端口/用户名/密码", fg="gray").grid(row=1, column=1, padx=10, pady=2, sticky=tk.W)

        # API地址输入框（初始隐藏）
        api_frame = tk.Frame(window)
        api_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.EW)
        tk.Label(api_frame, text="API地址:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        api_entry = tk.Entry(api_frame)
        api_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        api_frame.grid_remove()  # 初始隐藏

        # 确认按钮
        confirm_button = tk.Button(window, text="确认",
                                   command=lambda: self.on_modify_proxy_confirm(
                                       proxy_mode_var.get(),
                                       proxy_type_var.get(),
                                       proxy_params_entry.get(),
                                       api_entry.get(),
                                       window))
        confirm_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def toggle_proxy_fields(self, proxy_fields_frame, api_frame, proxy_mode):
        """切换代理输入字段的显示状态"""
        if proxy_mode == "fixed":
            proxy_fields_frame.grid()
            api_frame.grid_remove()
        else:  # api
            proxy_fields_frame.grid_remove()
            # api_frame.grid()

    def on_modify_proxy_confirm(self, proxy_mode, proxy_type, proxy_params, api_address, window):
        """确认按钮的回调函数，用于处理代理修改"""
        if proxy_mode == "fixed":
            # 验证代理参数格式
            if not proxy_params:
                messagebox.showwarning("输入错误", "请提供代理参数。")
                return
                
            # 解析代理参数
            parts = proxy_params.split('/')
            if len(parts) < 2:
                messagebox.showwarning("输入错误", "代理参数格式应为: IP/端口/用户名/密码")
                return
                
            ip, port = parts[0], parts[1]
            username = parts[2] if len(parts) > 2 else ""
            password = parts[3] if len(parts) > 3 else ""
            
            # 构造代理地址
            proxy_address = f"{ip}:{port}"
            if username and password:
                proxy_address = f"{username}:{password}@{proxy_address}"
                
            params = [proxy_mode, proxy_type, proxy_address]
        else:  # api

            params = [proxy_mode, proxy_type]

        self.command_join("修改窗口代理", params)
        window.destroy()

    def get_browser_fingerprint_input(self):
        """获取浏览器指纹的JSON字符串输入"""
        window = tk.Toplevel(self.root)
        window.title("窗口固定指纹 - 输入JSON")

        tk.Label(window, text="请输入浏览器指纹JSON:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        fingerprint_entry = tk.Text(window, height=15, width=50)  # 使用Text控件以便输入多行
        fingerprint_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # 确认按钮
        confirm_button = tk.Button(window, text="确认", command=lambda: self.on_browser_fingerprint_confirm(fingerprint_entry.get("1.0", tk.END), window))
        confirm_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def on_browser_fingerprint_confirm(self, fingerprint_json, window):
        """确认按钮的回调函数，用于处理浏览器指纹输入"""
        try:
            self.command_join("窗口固定指纹", [fingerprint_json])  # 将数据添加到命令中
            window.destroy()
        except json.JSONDecodeError:
            messagebox.showwarning("输入错误", "请提供有效的JSON字符串。")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
