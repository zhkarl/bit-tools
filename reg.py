import tkinter as tk
from tkinter import ttk, messagebox
import json
import hashlib
import datetime
import os

class LicenseGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("License管理 v1.0")
        self.root.iconbitmap(".\\resource\\reg.ico")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 客户信息区域
        ttk.Label(main_frame, text="客户信息", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(main_frame, text="客户名称:").grid(row=1, column=0, sticky=tk.W)
        self.customer_name = ttk.Entry(main_frame, width=40)
        self.customer_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="机器码:").grid(row=2, column=0, sticky=tk.W)
        self.machine_code = ttk.Entry(main_frame, width=40)
        self.machine_code.grid(row=2, column=1, padx=5, pady=5)
        
        # License配置区域
        ttk.Label(main_frame, text="License配置", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        ttk.Label(main_frame, text="有效期:").grid(row=4, column=0, sticky=tk.W)
        self.expiry_frame = ttk.Frame(main_frame)
        self.expiry_frame.grid(row=4, column=1, sticky=tk.W)
        
        self.expiry_value = ttk.Entry(self.expiry_frame, width=10)
        self.expiry_value.pack(side=tk.LEFT, padx=(0, 5))
        
        self.expiry_unit = ttk.Combobox(self.expiry_frame, values=['天', '月', '年'], width=5)
        self.expiry_unit.set('天')
        self.expiry_unit.pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="生成License", command=self.generate_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
    def generate_license(self):
        """生成license"""
        try:
            # 验证输入
            if not self.customer_name.get().strip():
                messagebox.showerror("错误", "请输入客户名称")
                return
            
            if not self.machine_code.get().strip():
                messagebox.showerror("错误", "请输入机器码")
                return
            
            if not self.expiry_value.get().strip():
                messagebox.showerror("错误", "请输入有效期")
                return
            
            try:
                expiry_value = int(self.expiry_value.get())
                if expiry_value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "有效期必须是正整数")
                return
            
            # 计算过期时间
            today = datetime.datetime.now()
            if self.expiry_unit.get() == '天':
                expiry_date = today + datetime.timedelta(days=expiry_value)
            elif self.expiry_unit.get() == '月':
                expiry_date = today + datetime.timedelta(days=expiry_value * 30)
            else:  # 年
                expiry_date = today + datetime.timedelta(days=expiry_value * 365)
            
            # 生成license数据
            license_data = {
                "customer": self.customer_name.get().strip(),
                "machine_code": self.machine_code.get().strip(),
                "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 生成签名
            data_str = json.dumps(license_data, sort_keys=True)
            signature = hashlib.sha256(data_str.encode()).hexdigest()
            
            # 组合最终的license
            final_license = {
                "data": license_data,
                "signature": signature
            }
            
            # 保存到文件
            filename = f"license_{self.customer_name.get().strip()}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_license, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"License已生成: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成License失败: {str(e)}")
    
    def clear_form(self):
        """清空表单"""
        self.customer_name.delete(0, tk.END)
        self.machine_code.delete(0, tk.END)
        self.expiry_value.delete(0, tk.END)
        self.expiry_unit.set('天')

if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseGenerator(root)
    root.mainloop()
