import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import requests
import json
import time
from threading import Thread, Event
from browser.bit import Bit
from browser.web import Web
import configparser
import os
import hashlib
import uuid
import datetime


class ScriptRunner:
    def __init__(self, root):
        self.bit_window = None
        self.bit_browser = None
        self.web_browser = None

        self.root = root
        self.root.title("脚本运行器 v1.0")
        self.root.iconbitmap(".\\resource\\run.ico")

        self.scripts = []
        self.running = False
        self.pause_event = Event()
        self.current_index = 0
        self.loop_start_index = None  # 添加循环起点索引变量
        self.loop_count = 0  # 添加循环计数器
        self.max_loops = 3  # 设置最大循环次数，防止无限循环

        self.abort_image = False
        self.abort_media = False
        self.proxy_use = False
        self.proxy_api = None

        self.waiting_time = 0

        self.config_file = "config.ini"
        
        # 创建配置解析器
        self.config = configparser.ConfigParser()
        
        # 加载配置文件
        self.load_config()

        # 配置根窗口的网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 创建主框架
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)  # 使用grid替代pack
        
        # 配置主框架的网格权重
        main_frame.grid_rowconfigure(1, weight=1)  # 脚本列表区域
        main_frame.grid_rowconfigure(2, weight=2)  # 文本框区域
        main_frame.grid_columnconfigure(0, weight=1)

        # 创建按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=0, column=0, sticky='ew', pady=10)

        # 左侧按钮
        left_button_frame = tk.Frame(button_frame)
        left_button_frame.pack(side=tk.LEFT)

        self.load_button = tk.Button(left_button_frame, text="加载脚本", command=self.load_script)
        self.load_button.pack(side=tk.LEFT, padx=0, pady=0)

        self.run_button = tk.Button(left_button_frame, text="运行脚本", command=self.start_running)
        self.run_button.pack(side=tk.LEFT, padx=0, pady=0)

        # 添加停止运行按钮
        self.stop_button = tk.Button(left_button_frame, text="停止运行", command=self.stop_running)
        self.stop_button.pack(side=tk.LEFT, padx=0, pady=0)

        self.step_button = tk.Button(left_button_frame, text="单步运行", command=self.step_running)
        self.step_button.pack(side=tk.LEFT, padx=0, pady=0)

        self.pause_button = tk.Button(left_button_frame, text="暂停脚本", command=self.pause_running, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=0, pady=0)

        # 添加保存记录按钮
        self.save_log_button = tk.Button(left_button_frame, text="保存记录", command=self.save_log)
        self.save_log_button.pack(side=tk.LEFT, padx=(10, 0))

        # 添加清空记录按钮
        self.clear_button = tk.Button(left_button_frame, text="清空记录", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=0)

        # 右侧循环次数控制
        right_control_frame = tk.Frame(button_frame)
        right_control_frame.pack(side=tk.RIGHT)

        tk.Label(right_control_frame, text="最大循环次数:").pack(side=tk.LEFT, padx=5)
        
        # 减少按钮
        self.decrease_button = tk.Button(right_control_frame, text="-", width=2, command=self.decrease_loops)
        self.decrease_button.pack(side=tk.LEFT)

        # 循环次数输入框 - 使用配置中的值
        self.max_loops_var = tk.StringVar(value=str(self.max_loops))
        self.max_loops_entry = tk.Entry(right_control_frame, textvariable=self.max_loops_var, width=5, justify=tk.CENTER)
        self.max_loops_entry.pack(side=tk.LEFT, padx=2)

        # 增加按钮
        self.increase_button = tk.Button(right_control_frame, text="+", width=2, command=self.increase_loops)
        self.increase_button.pack(side=tk.LEFT)

        # 绑定循环次数变更事件
        self.max_loops_var.trace_add("write", self.on_loops_change)

        # 创建脚本列表框架
        list_frame = tk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self.script_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.script_listbox.grid(row=0, column=0, sticky='nsew')

        # 添加滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # 配置滚动条和列表框
        self.script_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.script_listbox.yview)

        # 创建文本框框架
        footer_frame = tk.Frame(main_frame)
        footer_frame.grid(row=2, column=0, sticky='nsew', pady=(10, 0))
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_rowconfigure(0, weight=1)

        # 创建文本框和滚动条的容器
        text_frame = tk.Frame(footer_frame)
        text_frame.grid(row=0, column=0, sticky='nsew')
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # 创建文本框
        self.text_browser = tk.Text(text_frame, wrap="word")
        self.text_browser.grid(row=0, column=0, sticky='nsew')

        # 创建垂直滚动条
        text_scrollbar_y = tk.Scrollbar(text_frame, orient="vertical", command=self.text_browser.yview)
        text_scrollbar_y.grid(row=0, column=1, sticky='ns')

        # 配置文本框的滚动
        self.text_browser.configure(yscrollcommand=text_scrollbar_y.set)

        # 验证 license
        if not self.verify_license():
            self.show_license_dialog()
            return

    def load_script(self):
        """加载脚本文件"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.scripts = json.load(f)
                self.update_listbox()
                messagebox.showinfo("成功", "脚本加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"加载脚本失败: {str(e)}")

    def update_listbox(self):
        """更新列表框显示"""
        self.script_listbox.delete(0, tk.END)
        for script in self.scripts:
            if script.get('params'):
                display_text = f"{script['command']}({', '.join(map(str, script['params']))})"
            else:
                display_text = script['command']
            self.script_listbox.insert(tk.END, display_text)

    def start_running(self):
        """始运行脚本"""
        if not self.scripts:
            messagebox.showwarning("警告", "请先加载脚本")
            return

        # 获取并验证最大循环次数
        try:
            self.max_loops = int(self.max_loops_var.get())
            if self.max_loops <= 0:
                raise ValueError("循环次数必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的循环次数: {str(e)}")
            return

        if not self.running:
            self.running = True
            self.run_button.config(state=tk.DISABLED)
            self.load_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.max_loops_entry.config(state=tk.DISABLED)  # 运行时禁用输入框
            self.pause_event.set()
            Thread(target=self.run_script).start()

    def pause_running(self):
        """暂停运行脚本"""
        if self.running:
            if self.pause_event.is_set():
                self.pause_event.clear()
                self.pause_button.config(text="继续脚本")
            else:
                self.pause_event.set()
                self.pause_button.config(text="暂停脚本")
                self.stop_button.config(state=tk.NORMAL)  # 暂停时启用停止按钮

    def stop_running(self):
        """停止运行脚本"""
        self.running = False
        self.pause_event.set()  # 确保暂停事件被设置
        self.run_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)  # 停止时禁用停止按钮
        self.max_loops_entry.config(state=tk.NORMAL)  # 停止时启用输入框

    def run_script(self):
        """运行脚本的主逻辑"""
        try:
            i = self.current_index
            while i < len(self.scripts):
                if not self.running:
                    break

                self.pause_event.wait()  # 等待暂停事件
                if not self.running:
                    break

                if time.time() < self.waiting_time:
                    waiting = int(self.waiting_time-int(time.time()))
                    message = f"时间等待还有{waiting}秒"
                    if waiting % 5 == 0 or waiting <= 10:
                        self.show_message(f"{message}", level="info")
                    # 可选：仍然显示错误对话框
                    time.sleep(1)
                    continue
                else:
                    self.waiting_time = 0

                self.current_index = i
                script = self.scripts[i]
                
                # 在主线程中更新UI
                self.root.after(500, self.select_current_script)
                
                # 执行脚本命令
                try:
                    self.execute_command(script)
                    time.sleep(0.3)  # 添加短暂延迟，避免执行过快
                except Exception as e:
                    error_message = f"执行命令 '{script['command']}' 时发生错误: {str(e)}"
                    self.show_message(f"{error_message}", level="error")  # 添加错误标识符
                    # 可选：仍然显示错误对话框
                    self.root.after(0, lambda msg=error_message: messagebox.showerror("错误", msg))
                    break

                # 更新索引，考虑循环情况
                i = self.current_index + 1

        finally:
            self.current_index = 0
            self.loop_start_index = None  # 重置循环起点
            self.loop_count = 0  # 重置循环计数
            self.show_message("脚本执行结束", clear=False)
            self.root.after(0, self.stop_running)

    def select_current_script(self):
        """选中当前正在执行的脚本行"""
        self.script_listbox.selection_clear(0, tk.END)
        self.script_listbox.selection_set(self.current_index)
        self.script_listbox.see(self.current_index)

    def show_message(self, message, clear=False, level="info"):
        """显示信息到文本框
        Args:
            message: 要显示的信息
            clear: 是否清除之前的信息
            level: 信息级别 ("info", "warning", "error")
        """
        def _update():
            if clear:
                self.text_browser.delete(1.0, tk.END)
            
            # 根据不同级别添加不同的前缀标识
            prefix = {
                "info": "●",
                "warning": "◆",
                "error": "✘"
            }.get(level, "")
            
            timestamp = time.strftime('%H:%M:%S')
            formatted_message = f"[{timestamp}] {prefix} {message}\n"
            
            # # 检查最后一行是否包含“时间等待还有”
            # current_content = self.text_browser.get(1.0, tk.END)
            # lines = current_content.splitlines()
            # if lines and len(lines) > 2 and "时间等待还有" in lines[-2]:
            #     # 替换最后一行
            #     self.text_browser.delete(f"{len(lines)}.0", tk.END)  # 删除最后一行
            # elif lines and len(lines) > 2 and "时间等待还有" in lines[-1]:
            #     # 替换最后一行
            #     self.text_browser.delete(f"{len(lines)-1}.0", tk.END)  # 删除最后一行
            
            # 根据不同级别设置不同的标签
            self.text_browser.insert(tk.END, formatted_message)
            self.text_browser.see(tk.END)  # 自动滚动到最新信息
        
        self.root.after(0, _update)

    def get_proxy(self):
        try:
            response = requests.post(self.proxy_api)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    proxy_info = data['proxy']
                    return proxy_info
            else:
                data = response.json()
                self.show_message(f"获取代理失败:{data['message']}", level="error")
                return None
        except Exception as e:
            self.show_message(f"获取代理异常:{str(e)}", level="error")
            return None

    def execute_command(self, script):
        """执行单个脚本命令"""
        command = script['command']
        params = script.get('params', [])
        self.show_message(f"执行命令: {command}, 参数: {params}", level="info")

        try:
            if command == "创建比特窗口":
                if params[1] == '是':
                    self.abort_image = True
                if params[2] == '是':
                    self.abort_media = True
                if params[3] == '是':
                    self.proxy_use = True
                    self.proxy_api = params[4]
                self.bit_window = Bit(params[0], abortImage=self.abort_image, abortMedia=self.abort_media)
                self.show_message("比特窗口创建成功", level="info")
            elif command == "打开比特窗口":
                self.bit_browser = self.bit_window.create()
                self.web_browser = Web(self.bit_window, self.bit_browser)
                self.show_message("比特窗口打开成功", level="info")
            elif command == "关闭比特窗口":
                self.bit_window.close(self.bit_browser)
                self.show_message("比特窗口已关闭", level="info")
            elif command == "删除比特窗口":
                self.bit_window.delete(self.bit_browser)
                self.show_message("比特窗口已删除", level="info")
            elif command == "重置关闭状态":
                self.bit_window.reset(self.bit_browser)
                self.show_message("窗口状态已重置", level="info")
            elif command == "获取窗口详情":
                detail = self.bit_window.detail(self.bit_browser)
                self.show_message("窗口详情:", clear=True)
                self.show_message(detail, level="info")
            elif command == "清理窗口缓存":
                self.bit_window.clear([self.bit_browser])
                self.show_message("窗口缓存已清理", level="info")
            elif command == "一键排列窗口":
                self.bit_window.flexable()
                self.show_message("窗口已重新排列", level="info")
            elif command == "窗口随机指纹":
                if self.bit_window.finger(self.bit_browser):
                    self.show_message("窗口指纹已随机化", level="info")
                else:
                    raise Exception("窗口随机指纹失败")
            elif command == "窗口固定指纹":
                if self.bit_window.finger_fix(self.bit_browser, params[0]):
                    self.show_message("窗口指纹已修改", level="info")
                else:
                    raise Exception("窗口指纹修改失败")
            elif command == "修改窗口代理":
                if self.proxy_use:
                    proxy_mode = params[0]  # 获取代理模式
                    proxy_type = params[1]  # 获取代理类型
                    
                    if proxy_mode == "fixed":
                        proxy_params = params[2]  # 获取代理参数
                        # 解析代理参数
                        parts = proxy_params.split('@')
                        if len(parts) != 2:
                            raise Exception("代理参数格式应为: {username}:{password}@{ip}:{port}")
                        
                        user_pass, host_port = parts
                        user_pass_parts = user_pass.split(':')
                        if len(user_pass_parts) != 2:
                            raise Exception("代理用户名和密码格式应为: username:password")
                        
                        username, password = user_pass_parts
                        host_port_parts = host_port.split(':')
                        if len(host_port_parts) != 2:
                            raise Exception("代理IP和端口格式应为: ip:port")
                        
                        ip, port = host_port_parts

                        proxy_data = {
                            'ids': [self.bit_browser],
                            'proxyMethod': 2,
                            'proxyType': proxy_type,
                            'host': ip,
                            'port': port,
                            'proxyUserName': username,
                            'proxyPassword': password,
                        }
                        if self.bit_window.proxy(proxy_data):
                            self.show_message(f"窗口代理已修改（固定模式）: {proxy_type} {ip}:{port} {username}/{password}", level="info")
                        else:
                            raise Exception("窗口代理修改失败")
                    else:  # api
                        proxy = self.get_proxy()
                        if proxy:
                            proxy_data = {
                                'ids': [self.bit_browser],
                                'proxyMethod': 2,
                                'proxyType': proxy['type'],
                                'host': proxy['ip'],
                                'port': proxy['port'],
                                'proxyUserName': proxy['username'],
                                'proxyPassword': proxy['password'],
                            }
                            if self.bit_window.proxy(proxy_data):
                                self.show_message(f"窗口代理已修改（接口模式）: {proxy['type']} {proxy['ip']}:{proxy['port']} {proxy['username']}/{proxy['password']}", level="info")
                            else:
                                raise Exception("窗口代理修改失败")
                        else:
                            raise Exception("获取代理失败，无法修改窗口代理")
                else:
                    self.show_message("代理功能未启用", level="warning")
            elif command == "访问URL":
                self.web_browser.open(params[0])
                self.show_message(f"正在访问: {params[0]}", level="info")
            elif command == "滚动页面":
                scroll_pixels = int(params[0])
                is_random = False
                if len(params) > 1 and params[1] == "是":
                    is_random = True
                
                if is_random:
                    import random
                    # 根据滚动方向决定随机范围
                    if scroll_pixels > 0:
                        actual_pixels = random.randint(0, scroll_pixels)
                    else:
                        actual_pixels = random.randint(scroll_pixels, 0)
                    self.web_browser.scroll(str(actual_pixels))
                    self.show_message(f"随机滚动页面: {actual_pixels}像素", level="info")
                else:
                    self.web_browser.scroll(params[0])
                    self.show_message(f"滚动页面: {params[0]}像素", level="info")
            elif command == "回到顶部":
                self.web_browser.top()
                self.show_message(f"回到顶部", level="info")
            elif command == "鼠标悬停":
                self.web_browser.hover(params[0])
                self.show_message(f"鼠标悬停于元素: {params[0]}", level="info")
            elif command == "鼠标点击":
                if ',' in params[0]:
                    import random
                    selectors = [s.strip() for s in params[0].split(',')]
                    selected_selector = random.choice(selectors)
                    self.show_message(f"随机选择元素: {selected_selector}", level="info")
                    self.web_browser.click(selected_selector)
                else:
                    self.web_browser.click(params[0])
                    self.show_message(f"点击元素: {params[0]}", level="info")
            elif command == "元素等待":
                self.web_browser.wait_for_element(params[0])
                self.show_message(f"等待元素出现: {params[0]}", level="info")
            elif command == "元素滚动":
                self.web_browser.scroll_to_element(params[0])
                self.show_message(f"滚动到元素: {params[0]}", level="info")
            elif command == "输入文本":
                self.web_browser.input_text(params[0], params[1])
                self.show_message(f"在元素 {params[0]} 中输入文本", level="info")
            elif command == "时间等待":
                try:
                    import random
                    wait_time = int(params[0])  # 强制转换为整数
                    if len(params) > 1 and params[1] == '是':
                        wait_time = random.randint(1, wait_time)
                    self.show_message(f"时间等待共需{wait_time}秒", level="info")
                    # 使用 after 方法进行非阻塞等待
                    self.waiting_time = time.time() + wait_time
                except ValueError:
                    raise Exception(f"无效的等待时间: {params[0]}，必须为整数")
            elif command == "循环起点":
                if self.loop_start_index is None:
                    self.loop_start_index = self.current_index
                    self.loop_count = 0
                    self.show_message(f"设置循环起点: 第 {self.loop_start_index + 1} 行", level="info")
            elif command == "循环终点":
                if self.loop_start_index is not None:
                    self.loop_count += 1
                    if self.loop_count < self.max_loops:
                        self.show_message(f"第 {self.loop_count} 次循环完成，返回第 {self.loop_start_index + 1} 行", level="info")
                        self.current_index = self.loop_start_index - 1
                    else:
                        self.show_message(f"达到最大循环次数 {self.max_loops}，循环结束", level="info")
                        self.loop_start_index = None
                        self.loop_count = 0
            elif command == "Google搜索":
                while True:
                    find = False
                    for page in range(int(params[2])-1, int(params[3])):
                        search_page = self.web_browser.google(params[0], params[1], page)
                        if search_page > 0:
                            self.show_message(f"Google搜索: 在第 {search_page} 页找到关键词 {params[1]} 搜索结果", level="info")
                            find = True
                            break
                        else:
                            raise Exception(f"Google搜索: 在第 {page+1} 页未找到关键词 {params[1]} 搜索结果")
                    if find or len(params) < 5 or params[4] != '是':
                        break
        except Exception as e:
            self.show_message(f"执行命令 '{command}' 时出错: {str(e)}", level="error")
            raise  # 重新抛出异常，让上层处理

    def increase_loops(self):
        """增加最大循环次数"""
        try:
            current = int(self.max_loops_var.get())
            self.max_loops_var.set(str(current + 1))
            self.save_config()  # 保存更新后的值
        except ValueError:
            self.max_loops_var.set("1")
            self.save_config()

    def decrease_loops(self):
        """减少最大循环次数"""
        try:
            current = int(self.max_loops_var.get())
            if current > 1:
                self.max_loops_var.set(str(current - 1))
                self.save_config()  # 保存更新后的值
        except ValueError:
            self.max_loops_var.set("1")
            self.save_config()

    def load_config(self):
        """加载配置文件"""
        try:
            self.config.read(self.config_file, encoding='utf-8')
            self.max_loops = self.config.getint('Settings', 'max_loops', fallback=3)
        except Exception:
            self.max_loops = 3
            self.save_config()

    def save_config(self):
        """保存配置到文件"""
        if not self.config.has_section('Settings'):
            self.config.add_section('Settings')
        self.config.set('Settings', 'max_loops', str(self.max_loops))
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            self.show_message(f"保存配置失败: {str(e)}", level="error")

    def on_loops_change(self, *args):
        """循环次数变更时的处理函数"""
        try:
            current = int(self.max_loops_var.get())
            if current > 0:
                self.max_loops = current
                self.save_config()
        except ValueError:
            pass

    def clear_log(self):
        """清空记录"""
        try:
            self.text_browser.delete(1.0, tk.END)
            self.show_message("记录已清空", level="info")
        except Exception as e:
            messagebox.showerror("错误", f"清空记录失败: {str(e)}")

    def save_log(self):
        """保存记录到文件"""
        try:
            # 获取当前时间作为默认文件名
            default_filename = time.strftime("log_%Y%m%d_%H%M%S.txt")
            
            # 打开文件保存对话框
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if filename:
                # 获取文本框中的所有内容
                log_content = self.text_browser.get(1.0, tk.END)
                
                # 保存到文件
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.show_message(f"记录已保存到: {filename}", level="info")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存记录失败: {str(e)}")

    def verify_license(self):
        """验证 license"""
        try:
            # 检查 license 文件是否存在
            if not os.path.exists("license.json"):
                self.show_message(f"未找到 license 文件", level="warning")
                return False
                
            # 读取 license 文件
            with open("license.json", "r", encoding="utf-8") as f:
                license_data = json.load(f)
                
            # 验证 license 格式
            if "data" not in license_data or "signature" not in license_data:
                return False
                
            # 验证签名
            data_str = json.dumps(license_data["data"], sort_keys=True)
            current_signature = hashlib.sha256(data_str.encode()).hexdigest()
            if current_signature != license_data["signature"]:
                return False
                
            # 验证机器码
            current_machine_code = str(uuid.getnode())
            if current_machine_code != license_data["data"]["machine_code"]:
                return False
                
            # 验证过期时间
            expiry_date = datetime.datetime.strptime(
                license_data["data"]["expiry_date"], 
                "%Y-%m-%d %H:%M:%S"
            )
            if datetime.datetime.now() > expiry_date:
                self.show_message(f"License 已过期", level="warning")
                return False
                
            # 验证成功，更新窗口标题
            self.update_title(license_data["data"]["customer"], expiry_date)
            return True
                
        except Exception as e:
            self.show_message(f"License 验证失败: {str(e)}", level="warning")
            return False

    def update_title(self, customer, expiry_date):
        """更新窗口标题"""
        expiry_str = expiry_date.strftime("%Y-%m-%d")
        self.root.title(f"脚本运行器 v1.0 - {customer} (有效期至: {expiry_str})")

    def show_license_dialog(self):
        """显示 license 验证对话框"""
        # 创建顶层窗口
        dialog = tk.Toplevel(self.root, padx=10, pady=10)
        dialog.title("License 验证")
        dialog.geometry("380x220")
        dialog.resizable(False, False)
        
        # 使主窗口无法操作
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 禁用关闭按钮
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # 计居中位置
        def center_dialog():
            # 获取主窗口位置和大小
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            root_width = self.root.winfo_width()
            root_height = self.root.winfo_height()
            
            # 获取对话框大小
            dialog_width = 380
            dialog_height = 220
            
            # 计算居中位置
            x = root_x + (root_width - dialog_width) // 2
            y = root_y + (root_height - dialog_height) // 2
            
            # 设置对话框位置
            dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 等待主窗口更新完成后再居中显示
        self.root.update_idletasks()
        center_dialog()
        
        # 机器码显示
        ttk.Label(dialog, text="机器码:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # 创建机器码框架
        machine_code_frame = ttk.Frame(dialog)
        machine_code_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 机器码输入框
        machine_code = str(uuid.getnode())
        code_text = ttk.Entry(machine_code_frame)
        code_text.insert(0, machine_code)
        code_text.config(state='readonly')
        code_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 复制按钮
        def copy_machine_code():
            dialog.clipboard_clear()
            dialog.clipboard_append(machine_code)
            messagebox.showinfo("提示", "机器码已复制到剪贴板")
        
        ttk.Button(machine_code_frame, text="复制机器码", command=copy_machine_code).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 客户名称输入
        ttk.Label(dialog, text="户名称:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill=tk.X, pady=(0, 10), expand=True)
        
        # License 文件选择
        ttk.Label(dialog, text="License 文件:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        license_path = tk.StringVar()
        
        def select_license():
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                license_path.set(filename)
        
        license_frame = ttk.Frame(dialog)
        license_frame.pack(fill=tk.X, pady=(0, 10))
        license_entry = ttk.Entry(license_frame, textvariable=license_path, state='readonly')
        license_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(license_frame, text="选择", command=select_license).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 验证按钮
        def verify():
            if not name_entry.get().strip():
                messagebox.showerror("错误", "请输入客户名称")
                return
            
            if not license_path.get():
                messagebox.showerror("错误", "请选�� License 文件")
                return
                
            try:
                # 复制 license 文件到程序目录
                import shutil
                shutil.copy2(license_path.get(), "license.json")
                
                # 重新验证
                if self.verify_license():
                    messagebox.showinfo("成功", "License 验证通过")
                    dialog.destroy()
                    self.__init__(self.root)  # 重新初始化主窗口
                else:
                    messagebox.showerror("错误", "License 验证失败")
                    name_entry.delete(0, tk.END)
                    license_path.set("")
            except Exception as e:
                messagebox.showerror("错误", f"验证过程出错: {str(e)}")
        
        # 添加退出按钮
        def exit_app():
            if messagebox.askyesno("确认", "确定要退出程序吗？"):
                self.root.quit()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(10, 0), fill=tk.X)
        
        ttk.Button(button_frame, text="验证", command=verify).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="退出程序", command=exit_app).pack(side=tk.RIGHT)

    def step_running(self):
        """单步运行脚本"""
        if not self.scripts:
            messagebox.showwarning("警告", "请先加载脚本")
            return
  
        if not self.running:
            self.load_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.pause_event.set()

            selected_indices = self.script_listbox.curselection()
            if selected_indices:
                self.current_index = selected_indices[0]  # 赋值给 current_index
            else:
                self.current_index = 0  # 如果没有选中项，默认从第一个开始
            
            self.execute_next_command(True)  # 执行下一条命令

    def execute_next_command(self, step=False):
        """执行当前索引的命令"""
        if self.current_index < len(self.scripts):
            script = self.scripts[self.current_index]
            try:
                self.execute_command(script)
                self.select_current_script()  # 选中当前执行的脚本行
                self.current_index += 1  # 更新索引
                if step:  # 如果是单步运行，直接返回
                    self.script_listbox.selection_clear(0, "end")
                    self.script_listbox.selection_set(self.current_index)
                    return
                self.root.after(0, self.execute_next_command)  # 继续执行下一条命令
            except Exception as e:
                error_message = f"执行命令 '{script['command']}' 时发生错误: {str(e)}"
                self.show_message(f"☹ {error_message}", level="error")
                self.stop_running()  # 停止运行


if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptRunner(root)
    root.mainloop()

