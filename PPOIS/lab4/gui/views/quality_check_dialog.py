import tkinter as tk
from tkinter import ttk, messagebox

class QualityCheckDialog(tk.Toplevel):
    def __init__(self, parent, controller, product_id):
        super().__init__(parent)
        self.controller = controller
        self.product_id = product_id
        self.product_info = self.controller.get_production_status(product_id)
        self.title(f"Проверка качества - Продукт {product_id}")
        self.geometry("500x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.create_widgets()
        
    def center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        title_label = ttk.Label(main_frame, text=f"Проверка качества продукта {self.product_id}", 
                                 font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        if self.product_info:
            info_text = f"Продукт: {self.product_info['product_name']}\n"
            info_text += f"Текущий этап: {self.product_info['current_stage']}"
            info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
            info_label.pack(pady=(0, 20))
        standard_frame = ttk.LabelFrame(main_frame, text="Выберите стандарт качества", padding="10")
        standard_frame.pack(fill=tk.X, pady=10)
        standards = self.controller.get_standards()
        self.standard_var = tk.StringVar()
        for std in standards:
            ttk.Radiobutton(standard_frame, text=std["name"], 
                           variable=self.standard_var, 
                           value=std["name"]).pack(anchor=tk.W, pady=2)
        ttk.Button(main_frame, text="Проверить соответствие", 
                  command=self.check_quality).pack(pady=20)
        result_frame = ttk.LabelFrame(main_frame, text="Результат проверки", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(main_frame, text="Закрыть", command=self.destroy).pack(pady=(10, 0))
    
    def check_quality(self):
        standard = self.standard_var.get()
        if not standard:
            messagebox.showwarning("Предупреждение", "Выберите стандарт качества")
            return
        success, message = self.controller.check_compliance(self.product_id, standard)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        if success:
            self.result_text.insert(1.0, "✓ " + message)
            self.result_text.tag_add("success", "1.0", tk.END)
            self.result_text.tag_config("success", foreground="green")
        else:
            self.result_text.insert(1.0, "✗ " + message)
            self.result_text.tag_add("error", "1.0", tk.END)
            self.result_text.tag_config("error", foreground="red")
        self.result_text.config(state=tk.DISABLED)