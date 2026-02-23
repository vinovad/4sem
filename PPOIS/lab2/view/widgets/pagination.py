"""
pagination.py - компонент постраничной навигации

Позволяет пользователю:
- Переходить на первую, последнюю, следующую и предыдущую страницы
- Изменять количество записей на странице
- Видеть текущую страницу и общее количество страниц
"""

import tkinter as tk
from tkinter import ttk, messagebox  # Добавляем импорт messagebox

class Pagination(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Текущая страница
        self.current_page = tk.IntVar(value=1)
        
        # Количество записей на странице
        self.page_size = tk.IntVar(value=10)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Кнопка "Первая"
        ttk.Button(
            self, 
            text="<< Первая", 
            command=lambda: self.controller.change_page(1)
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Предыдущая"
        ttk.Button(
            self, 
            text="< Предыдущая", 
            command=lambda: self.controller.change_page(self.current_page.get() - 1)
        ).pack(side=tk.LEFT, padx=5)
        
        # Текущая страница
        ttk.Label(self, text="Страница:").pack(side=tk.LEFT, padx=5)
        page_entry = ttk.Entry(self, textvariable=self.current_page, width=5)
        page_entry.pack(side=tk.LEFT, padx=5)
        page_entry.bind("<Return>", lambda event: self._go_to_page())
        
        # Общее количество страниц
        self.total_pages_label = ttk.Label(self, text="/ 0")
        self.total_pages_label.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Следующая"
        ttk.Button(
            self, 
            text="Следующая >", 
            command=lambda: self.controller.change_page(self.current_page.get() + 1)
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Последняя"
        ttk.Button(
            self, 
            text="Последняя >>", 
            command=lambda: self.controller.change_page(self.total_pages)
        ).pack(side=tk.LEFT, padx=5)
        
        # Размер страницы
        ttk.Label(self, text="Записей на странице:").pack(side=tk.LEFT, padx=5)
        page_size_entry = ttk.Entry(self, textvariable=self.page_size, width=5)
        page_size_entry.pack(side=tk.LEFT, padx=5)
        page_size_entry.bind("<Return>", lambda event: self._change_page_size())
        
        # Общее количество записей
        self.total_records_label = ttk.Label(self, text="Всего записей: 0")
        self.total_records_label.pack(side=tk.LEFT, padx=10)
    
    def update_pagination(self, current_page, total_pages, total_records):
        self.current_page.set(current_page)
        self.total_pages = total_pages
        self.total_pages_label.config(text=f"/ {total_pages}")
        self.total_records_label.config(text=f"Всего записей: {total_records}")
    
    def _go_to_page(self):
        try:
            page_num = self.current_page.get()
            self.controller.change_page(page_num)
        except tk.TclError:
            messagebox.showerror("Ошибка", "Введите корректный номер страницы")
    
    def _change_page_size(self):
        try:
            page_size = self.page_size.get()
            self.controller.change_page_size(page_size)
        except tk.TclError:
            messagebox.showerror("Ошибка", "Введите корректное количество записей на странице")