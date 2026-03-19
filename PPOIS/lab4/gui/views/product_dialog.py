import tkinter as tk
from tkinter import ttk, messagebox

class ProductDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Добавление продукта")
        self.geometry("400x200")
        self.resizable(False, False)
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
        title_label = ttk.Label(main_frame, text="Добавление нового продукта", 
                                 font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Название продукта:", font=("Arial", 10)).pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var, font=("Arial", 10))
        self.name_entry.pack(fill=tk.X, pady=(5, 0))
        self.name_entry.focus_set()
        self.name_entry.bind('<Return>', lambda e: self.add_product())
        info_label = ttk.Label(main_frame, text="Введите название продукта и нажмите 'Добавить'", 
                               foreground="gray")
        info_label.pack(pady=10)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(button_frame, text="Добавить", command=self.add_product).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT)
    
    def add_product(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Предупреждение", "Введите название продукта")
            return
        product = self.controller.add_product(name)
        if product:
            self.destroy()