import tkinter as tk
from tkinter import ttk, messagebox

class ReviewDialog(tk.Toplevel):
    def __init__(self, parent, controller, product_id):
        super().__init__(parent)
        self.controller = controller
        self.product_id = product_id
        self.product_info = self.controller.get_production_status(product_id)
        self.title(f"Добавление отзыва - Продукт {product_id}")
        self.geometry("450x400")
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
        title_label = ttk.Label(main_frame, text=f"Добавление отзыва для продукта {self.product_id}", 
                                 font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        if self.product_info:
            info_label = ttk.Label(main_frame, 
                                   text=f"Продукт: {self.product_info['product_name']}",
                                   justify=tk.LEFT)
            info_label.pack(pady=(0, 20))
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        author_frame = ttk.Frame(form_frame)
        author_frame.pack(fill=tk.X, pady=5)
        ttk.Label(author_frame, text="Автор:", width=10).pack(side=tk.LEFT)
        self.author_var = tk.StringVar()
        self.author_entry = ttk.Entry(author_frame, textvariable=self.author_var, width=30)
        self.author_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        rating_frame = ttk.Frame(form_frame)
        rating_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rating_frame, text="Рейтинг (1-5):", width=10).pack(side=tk.LEFT)
        self.rating_var = tk.IntVar(value=5)
        rating_spinbox = ttk.Spinbox(rating_frame, from_=1, to=5, textvariable=self.rating_var, width=5)
        rating_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        comment_frame = ttk.Frame(form_frame)
        comment_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(comment_frame, text="Комментарий:", width=10).pack(anchor=tk.NW)
        self.comment_text = tk.Text(comment_frame, height=8, width=40, wrap=tk.WORD)
        self.comment_text.pack(side=tk.LEFT, padx=(5, 0), fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(comment_frame, orient=tk.VERTICAL, command=self.comment_text.yview)
        self.comment_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(button_frame, text="Добавить отзыв", command=self.add_review).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT)
    
    def add_review(self):
        author = self.author_var.get().strip()
        rating = self.rating_var.get()
        comment = self.comment_text.get(1.0, tk.END).strip()
        if not author:
            messagebox.showwarning("Предупреждение", "Введите имя автора")
            return
        if not comment:
            messagebox.showwarning("Предупреждение", "Введите комментарий")
            return
        success, message = self.controller.add_review(self.product_id, author, comment, rating)
        if success:
            messagebox.showinfo("Успех", message)
            self.destroy()
        else:
            messagebox.showerror("Ошибка", message)