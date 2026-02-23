import tkinter as tk
from tkinter import ttk, messagebox
from view.widgets import Pagination

class MainWindow(tk.Tk):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = None  # Инициализируем как None
        self.title("Ветеринарная клиника")
        self.geometry("1000x600")
        
        # Создаем таблицу
        self._create_table()
        
        # Создаем пагинацию без контроллера (временно)
        self.pagination = Pagination(self, None)
        self.pagination.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Сохраняем контроллер, но не создаем меню и панель инструментов сейчас
        self._pending_controller = controller
        
        # Если контроллер уже передан, завершаем инициализацию
        if controller is not None:
            self.set_controller(controller)
    
    def set_controller(self, controller):
        """Устанавливает контроллер и завершает инициализацию интерфейса"""
        self.controller = controller
        # Обновляем пагинацию с новым контроллером
        self.pagination.controller = controller
        # Создаем меню и панель инструментов
        self._create_menu()
        self._create_toolbar()
        # Обновляем таблицу
        self.update_table([])
    
    def _create_table(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем таблицу с прокруткой
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Вертикальная прокрутка
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Горизонтальная прокрутка
        h_scroll = ttk.Scrollbar(frame, orient="horizontal")
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Определяем колонки
        columns = ("name", "birth_date", "last_visit", "vet_name", "diagnosis")
        
        # Создаем Treeview
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings",
            yscrollcommand=tree_scroll.set,
            xscrollcommand=h_scroll.set
        )
        
        # Настройка заголовков
        self.tree.heading("name", text="Имя питомца")
        self.tree.heading("birth_date", text="Дата рождения")
        self.tree.heading("last_visit", text="Дата последнего приема")
        self.tree.heading("vet_name", text="ФИО ветеринара")
        self.tree.heading("diagnosis", text="Диагноз")
        
        # Настройка колонок
        self.tree.column("name", width=150, anchor=tk.W)
        self.tree.column("birth_date", width=120, anchor=tk.CENTER)
        self.tree.column("last_visit", width=150, anchor=tk.CENTER)
        self.tree.column("vet_name", width=200, anchor=tk.W)
        self.tree.column("diagnosis", width=300, anchor=tk.W)
        
        # Привязка прокрутки к таблице
        tree_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Добавляем таблицу
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_menu(self):
        menu_bar = tk.Menu(self)
        
        # Меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Загрузить из XML", command=self.controller.load_from_xml)
        file_menu.add_command(label="Сохранить в XML", command=self.controller.save_to_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню "Операции"
        operations_menu = tk.Menu(menu_bar, tearoff=0)
        operations_menu.add_command(label="Добавить питомца", command=self.controller.show_add_dialog)
        operations_menu.add_command(label="Поиск питомца", command=self.controller.show_search_dialog)
        operations_menu.add_command(label="Удалить питомца", command=self.controller.show_delete_dialog)
        menu_bar.add_cascade(label="Операции", menu=operations_menu)
        
        self.config(menu=menu_bar)
    
    def _create_toolbar(self):
        toolbar = ttk.Frame(self, padding="5")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="Добавить", command=self.controller.show_add_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Поиск", command=self.controller.show_search_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=self.controller.show_delete_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Сохранить", command=self.controller.save_to_xml).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Загрузить", command=self.controller.load_from_xml).pack(side=tk.LEFT, padx=2)
    
    def update_table(self, pets):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем таблицу
        for pet in pets:
            self.tree.insert("", tk.END, values=(
                pet.name,
                pet.birth_date.strftime("%d.%m.%Y"),
                pet.last_visit.strftime("%d.%m.%Y"),
                pet.vet_name,
                pet.diagnosis
            ))