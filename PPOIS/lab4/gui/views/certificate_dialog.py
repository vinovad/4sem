import tkinter as tk
from tkinter import ttk, messagebox

class CertificateDialog(tk.Toplevel):
    def __init__(self, parent, controller, product_id):
        super().__init__(parent)
        self.controller = controller
        self.product_id = product_id
        self.product_info = self.controller.get_production_status(product_id)
        self.title(f"Выдача сертификата - Продукт {product_id}")
        self.geometry("500x450")
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
        title_label = ttk.Label(main_frame, text=f"Выдача сертификата для продукта {self.product_id}", 
                                 font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        if self.product_info:
            info_text = f"Продукт: {self.product_info['product_name']}\n"
            info_text += f"Текущий этап: {self.product_info['current_stage']}"
            info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
            info_label.pack(pady=(0, 10))
        cert_frame = ttk.LabelFrame(main_frame, text="Существующие сертификаты", padding="10")
        cert_frame.pack(fill=tk.X, pady=10)
        product = self.controller.get_product(self.product_id)
        if product and product.certificates:
            cert_text = ""
            for cert in product.certificates:
                cert_text += f"• {cert.standard.standard_name} - {cert.stage}\n"
                cert_text += f"  Действителен до: {cert.expiration_date}\n"
                cert_text += f"  Статус: {'✓ Действителен' if cert.is_valid() else '✗ Истек'}\n\n"
            cert_label = ttk.Label(cert_frame, text=cert_text, justify=tk.LEFT)
            cert_label.pack()
        else:
            ttk.Label(cert_frame, text="Нет сертификатов").pack()
        new_cert_frame = ttk.LabelFrame(main_frame, text="Выдать новый сертификат", padding="10")
        new_cert_frame.pack(fill=tk.X, pady=10)
        standards = self.controller.get_standards()
        self.standard_var = tk.StringVar()
        for std in standards:
            ttk.Radiobutton(new_cert_frame, text=std["name"], 
                           variable=self.standard_var, 
                           value=std["name"]).pack(anchor=tk.W, pady=2)
        ttk.Button(new_cert_frame, text="Выдать сертификат", 
                  command=self.issue_certificate).pack(pady=10)
        result_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(result_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(main_frame, text="Закрыть", command=self.destroy).pack(pady=(10, 0))
    
    def issue_certificate(self):
        standard = self.standard_var.get()
        if not standard:
            messagebox.showwarning("Предупреждение", "Выберите стандарт качества")
            return
        success, message = self.controller.certify_product(self.product_id, standard)
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