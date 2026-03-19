import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any

class MainWindow:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.root.title("Система контроля качества выпечки")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.root.configure(bg="#ffe4f0")
        self._apply_theme()
        self.center_window()
        self.create_menu()
        self.create_widgets()
        self.refresh_product_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        BG = "#ffb4d6"
        BG2 = "#c25f92"
        ACCENT = "#c04789"
        ACCENT2 = "#f48fb1"
        FG = "#5a0039"
        BTN_FG = "#060101"
        style.configure("TFrame", background=BG)
        style.configure("TLabelframe", background=BG, foreground=ACCENT, bordercolor=ACCENT2)
        style.configure("TLabelframe.Label", background=BG, foreground=ACCENT, font=("Arial", 9, "bold"))
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TButton", background=ACCENT, foreground=BTN_FG, bordercolor=ACCENT, focuscolor=ACCENT2, font=("Arial", 9, "bold"), padding=4)
        style.map("TButton", background=[("active", ACCENT2), ("disabled", BG2)], foreground=[("disabled", "#45172c")])
        style.configure("TSeparator", background=ACCENT2)
        style.configure("Treeview", background=BG, fieldbackground=BG, foreground=FG, bordercolor=ACCENT2, rowheight=22)
        style.configure("Treeview.Heading", background=ACCENT, foreground=BTN_FG, font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BTN_FG)])
        style.configure("Vertical.TScrollbar", background=ACCENT2, troughcolor=BG, bordercolor=BG2, arrowcolor=ACCENT)
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить состояние", command=self.save_state)
        file_menu.add_command(label="Загрузить состояние", command=self.load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        product_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Продукт", menu=product_menu)
        product_menu.add_command(label="Добавить продукт", command=self.add_product)
        product_menu.add_command(label="Обновить список", command=self.refresh_product_list)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        title_label = ttk.Label(header_frame, text="Система контроля качества выпечки", 
                                 font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="Добавить продукт", command=self.add_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Обновить", command=self.refresh_product_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Сохранить", command=self.save_state).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Загрузить", command=self.load_state).pack(side=tk.LEFT)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        self.count_label = ttk.Label(toolbar, text="Продуктов: 0")
        self.count_label.pack(side=tk.LEFT, padx=(5, 0))
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="Список продуктов", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        columns = ("id", "name", "stage", "certificates", "reviews")
        self.product_tree = ttk.Treeview(left_frame, columns=columns, show="tree headings", height=15)
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Название")
        self.product_tree.heading("stage", text="Этап")
        self.product_tree.heading("certificates", text="Сертификаты")
        self.product_tree.heading("reviews", text="Отзывы")
        self.product_tree.column("#0", width=0, stretch=False)
        self.product_tree.column("id", width=50)
        self.product_tree.column("name", width=150)
        self.product_tree.column("stage", width=100)
        self.product_tree.column("certificates", width=80, anchor=tk.CENTER)
        self.product_tree.column("reviews", width=60, anchor=tk.CENTER)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        ttk.Label(right_frame, text="Информация о продукте", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        info_frame = ttk.LabelFrame(right_frame, text="Детали", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.info_text = tk.Text(info_frame, height=10, width=40, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        actions_frame = ttk.LabelFrame(right_frame, text="Действия", padding="10")
        actions_frame.pack(fill=tk.X)
        button_frame = ttk.Frame(actions_frame)
        button_frame.pack(fill=tk.X)
        row1 = ttk.Frame(button_frame)
        row1.pack(fill=tk.X, pady=2)
        self.btn_check = ttk.Button(row1, text="Проверить качество", command=self.check_quality, state=tk.DISABLED)
        self.btn_check.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.btn_improve = ttk.Button(row1, text="Улучшить", command=self.improve_product, state=tk.DISABLED)
        self.btn_improve.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        row2 = ttk.Frame(button_frame)
        row2.pack(fill=tk.X, pady=2)
        self.btn_certify = ttk.Button(row2, text="Выдать сертификат", command=self.certify_product, state=tk.DISABLED)
        self.btn_certify.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.btn_advance = ttk.Button(row2, text="Следующий этап", command=self.advance_stage, state=tk.DISABLED)
        self.btn_advance.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        row3 = ttk.Frame(button_frame)
        row3.pack(fill=tk.X, pady=2)
        self.btn_review = ttk.Button(row3, text="Добавить отзыв", command=self.add_review, state=tk.DISABLED)
        self.btn_review.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.btn_analyze = ttk.Button(row3, text="Анализ отзывов", command=self.analyze_reviews, state=tk.DISABLED)
        self.btn_analyze.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.status_bar = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh_product_list(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        products = self.controller.get_products()
        self.count_label.config(text=f"Продуктов: {len(products)}")
        for product in products:
            self.product_tree.insert("", tk.END, 
                                     values=(product.product_id, 
                                            product.name, 
                                            product.get_current_stage(),
                                            len(product.certificates),
                                            len(product.reviews)),
                                     tags=(product.product_id,))
        self.update_status(f"Загружено {len(products)} продуктов")
    
    def on_product_select(self, event):
        selected = self.product_tree.selection()
        if selected:
            item = self.product_tree.item(selected[0])
            product_id = str(item['values'][0])
            product_info = self.controller.get_production_status(product_id)
            if product_info:
                self.btn_check.config(state=tk.NORMAL)
                self.btn_improve.config(state=tk.NORMAL)
                self.btn_certify.config(state=tk.NORMAL)
                self.btn_advance.config(state=tk.NORMAL)
                self.btn_review.config(state=tk.NORMAL)
                self.btn_analyze.config(state=tk.NORMAL)
                self.display_product_info(product_info)
            else:
                self.clear_product_info()
        else:
            self.btn_check.config(state=tk.DISABLED)
            self.btn_improve.config(state=tk.DISABLED)
            self.btn_certify.config(state=tk.DISABLED)
            self.btn_advance.config(state=tk.DISABLED)
            self.btn_review.config(state=tk.DISABLED)
            self.btn_analyze.config(state=tk.DISABLED)
            self.clear_product_info()
    
    def display_product_info(self, info: Dict[str, Any]):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        text = f"ID: {info['product_id']}\n"
        text += f"Название: {info['product_name']}\n"
        text += f"Текущий этап: {info['current_stage']}\n"
        text += f"Статус: {'Завершено' if info['is_completed'] else 'В производстве'}\n"
        text += f"Сертификат на этапе: {'Есть' if info['has_certificate'] else 'Нет'}\n"
        text += f"Количество сертификатов: {info['certificates_count']}\n"
        text += f"Количество отзывов: {info['reviews_count']}\n\n"
        text += "Атрибуты качества:\n"
        for attr, value in info['attributes'].items():
            text += f"  {attr}: {value}\n"
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)
    
    def clear_product_info(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def get_selected_product_id(self) -> Optional[str]:
        selected = self.product_tree.selection()
        if selected:
            item = self.product_tree.item(selected[0])
            return str(item['values'][0])
        return None
    
    def add_product(self):
        from .product_dialog import ProductDialog
        dialog = ProductDialog(self.root, self.controller)
        self.root.wait_window(dialog)
        self.refresh_product_list()
    
    def check_quality(self):
        from .quality_check_dialog import QualityCheckDialog
        product_id = self.get_selected_product_id()
        if product_id:
            dialog = QualityCheckDialog(self.root, self.controller, product_id)
            self.root.wait_window(dialog)
    
    def improve_product(self):
        product_id = self.get_selected_product_id()
        if not product_id:
            return
        standards = self.controller.get_standards()
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор стандарта")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="Выберите стандарт качества:").pack(pady=10)
        standard_var = tk.StringVar()
        for std in standards:
            ttk.Radiobutton(dialog, text=std["name"], variable=standard_var, 
                           value=std["name"]).pack(anchor=tk.W, padx=20)
        def on_improve():
            if not standard_var.get():
                messagebox.showwarning("Предупреждение", "Выберите стандарт")
                return
            success, message, criteria = self.controller.improve_product(product_id, standard_var.get())
            if success:
                if criteria:
                    msg = f"{message}\n\nУлучшенные критерии:\n" + "\n".join([f"- {c}" for c in criteria])
                else:
                    msg = message
                messagebox.showinfo("Успех", msg)
                self.refresh_product_list()
            else:
                messagebox.showerror("Ошибка", message)
            dialog.destroy()
        ttk.Button(dialog, text="Улучшить", command=on_improve).pack(pady=10)
    
    def certify_product(self):
        from .certificate_dialog import CertificateDialog
        product_id = self.get_selected_product_id()
        if product_id:
            dialog = CertificateDialog(self.root, self.controller, product_id)
            self.root.wait_window(dialog)
            self.refresh_product_list()
    
    def advance_stage(self):
        product_id = self.get_selected_product_id()
        if product_id:
            success, message = self.controller.advance_stage(product_id)
            if success:
                messagebox.showinfo("Успех", message)
                self.refresh_product_list()
            else:
                messagebox.showerror("Ошибка", message)
    
    def add_review(self):
        from .review_dialog import ReviewDialog
        product_id = self.get_selected_product_id()
        if product_id:
            dialog = ReviewDialog(self.root, self.controller, product_id)
            self.root.wait_window(dialog)
            self.refresh_product_list()
    
    def analyze_reviews(self):
        from .analysis_dialog import AnalysisDialog
        product_id = self.get_selected_product_id()
        if product_id:
            dialog = AnalysisDialog(self.root, self.controller, product_id)
            self.root.wait_window(dialog)
    
    def save_state(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="system_state.json"
        )
        if filename:
            success, message = self.controller.save_state(filename)
            if success:
                messagebox.showinfo("Успех", message)
                self.update_status(message)
            else:
                messagebox.showerror("Ошибка", message)
    
    def load_state(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            success, message = self.controller.load_state(filename)
            if success:
                messagebox.showinfo("Успех", message)
                self.refresh_product_list()
                self.update_status(message)
            else:
                messagebox.showerror("Ошибка", message)
    
    def show_info(self, message: str):
        messagebox.showinfo("Информация", message)
        self.update_status(message)
    
    def show_error(self, message: str):
        messagebox.showerror("Ошибка", message)
        self.update_status(f"Ошибка: {message}")
    
    def update_status(self, message: str):
        self.status_bar.config(text=message)
    
    def show_about(self):
        about_text = "Система контроля качества выпечки"
        messagebox.showinfo("О программе", about_text)
    
    def on_closing(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
            self.controller.save_state()
            self.root.destroy()