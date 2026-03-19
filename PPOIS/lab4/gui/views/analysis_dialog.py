import tkinter as tk
from tkinter import ttk, messagebox

class AnalysisDialog(tk.Toplevel):
    def __init__(self, parent, controller, product_id):
        super().__init__(parent)
        self.controller = controller
        self.product_id = product_id
        self.product_info = self.controller.get_production_status(product_id)
        self.analysis_result = self.controller.analyze_reviews(product_id)
        self.title(f"Анализ отзывов - Продукт {product_id}")
        self.geometry("500x400")
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
        title_label = ttk.Label(main_frame, text=f"Анализ отзывов для продукта {self.product_id}", 
                                 font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        if self.product_info:
            info_label = ttk.Label(main_frame, 
                                   text=f"Продукт: {self.product_info['product_name']}",
                                   justify=tk.LEFT)
            info_label.pack(pady=(0, 20))
        if "error" in self.analysis_result:
            error_label = ttk.Label(main_frame, text=f"Ошибка: {self.analysis_result['error']}", 
                                    foreground="red")
            error_label.pack(pady=20)
            ttk.Button(main_frame, text="Закрыть", command=self.destroy).pack()
            return
        result_frame = ttk.LabelFrame(main_frame, text="Результаты анализа", padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True)
        if not self.analysis_result["has_reviews"]:
            ttk.Label(result_frame, text="Нет отзывов для анализа", 
                     font=("Arial", 10)).pack(pady=20)
        else:
            stats_frame = ttk.Frame(result_frame)
            stats_frame.pack(fill=tk.X, pady=(0, 15))
            avg_rating = self.analysis_result["avg_rating"]
            ttk.Label(stats_frame, text="Средний рейтинг:", 
                     font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
            rating_text = f"{avg_rating:.2f} / 5.00"
            if avg_rating >= 4.5:
                rating_text += " (Отлично)"
                rating_color = "green"
            elif avg_rating >= 3.5:
                rating_text += " (Хорошо)"
                rating_color = "blue"
            elif avg_rating >= 2.5:
                rating_text += " (Средне)"
                rating_color = "orange"
            else:
                rating_text += " (Плохо)"
                rating_color = "red"
            rating_label = ttk.Label(stats_frame, text=rating_text, foreground=rating_color)
            rating_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
            ttk.Label(stats_frame, text="Количество отзывов:", 
                     font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(stats_frame, text=str(self.analysis_result["reviews_count"])).grid(
                row=1, column=1, sticky=tk.W, padx=(10, 0))
            if self.analysis_result["recommendations"]:
                rec_frame = ttk.LabelFrame(result_frame, text="Рекомендации по улучшению", padding="10")
                rec_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
                for i, rec in enumerate(self.analysis_result["recommendations"], 1):
                    rec_label = ttk.Label(rec_frame, text=f"{i}. {rec}", wraplength=350, justify=tk.LEFT)
                    rec_label.pack(anchor=tk.W, pady=2)
            else:
                good_label = ttk.Label(result_frame, 
                                       text="✓ Продукт соответствует требованиям качества", 
                                       foreground="green", font=("Arial", 10))
                good_label.pack(pady=10)
        ttk.Button(main_frame, text="Закрыть", command=self.destroy).pack(pady=(20, 0))
