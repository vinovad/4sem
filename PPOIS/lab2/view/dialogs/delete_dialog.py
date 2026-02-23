import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date

class DeleteDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Удаление питомца")
        self.geometry("700x450")
        self.resizable(True, True)
        
        # Центрируем окно
        self.transient(parent)
        self.grab_set()
        self._center_window()
        
        # Создаем интерфейс
        self._create_widgets()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (width // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Удаление по имени и дате рождения
        tab1 = ttk.Frame(notebook, padding="10")
        notebook.add(tab1, text="По имени и дате рождения")
        self._create_name_birth_tab(tab1)
        
        # Вкладка 2: Удаление по визиту и ветеринару
        tab2 = ttk.Frame(notebook, padding="10")
        notebook.add(tab2, text="По визиту и ветеринару")
        self._create_visit_vet_tab(tab2)
        
        # Вкладка 3: Удаление по диагнозу
        tab3 = ttk.Frame(notebook, padding="10")
        notebook.add(tab3, text="По диагнозу")
        self._create_diagnosis_tab(tab3)
    
    def _create_name_birth_tab(self, parent):
        # Форма поиска
        form_frame = ttk.LabelFrame(parent, text="Критерии удаления", padding="10")
        form_frame.pack(fill=tk.X, pady=5)
        
        # Имя питомца
        ttk.Label(form_frame, text="Имя питомца:").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Дата рождения
        ttk.Label(form_frame, text="Дата рождения:").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.birth_date_entry = DateEntry(
            form_frame, 
            width=12, 
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy'
        )
        self.birth_date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Кнопка поиска
        ttk.Button(
            form_frame,
            text="Найти",
            command=self._search_by_name_and_birth
        ).grid(row=0, column=2, rowspan=2, padx=10, sticky=tk.W)
        
        # Результаты поиска
        result_frame = ttk.LabelFrame(parent, text="Найденные записи", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создаем таблицу
        columns = ("name", "birth_date", "last_visit", "vet_name", "diagnosis")
        self.name_birth_tree = ttk.Treeview(
            result_frame, 
            columns=columns, 
            show="headings",
            selectmode="extended"  # Явно указываем множественный выбор
        )
        
        # Настройка заголовков
        self.name_birth_tree.heading("name", text="Имя питомца")
        self.name_birth_tree.heading("birth_date", text="Дата рождения")
        self.name_birth_tree.heading("last_visit", text="Дата последнего приема")
        self.name_birth_tree.heading("vet_name", text="ФИО ветеринара")
        self.name_birth_tree.heading("diagnosis", text="Диагноз")
        
        # Настройка колонок
        self.name_birth_tree.column("name", width=120, anchor=tk.W)
        self.name_birth_tree.column("birth_date", width=100, anchor=tk.CENTER)
        self.name_birth_tree.column("last_visit", width=120, anchor=tk.CENTER)
        self.name_birth_tree.column("vet_name", width=150, anchor=tk.W)
        self.name_birth_tree.column("diagnosis", width=200, anchor=tk.W)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.name_birth_tree.yview)
        self.name_birth_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.name_birth_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка удаления
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Удалить выбранные записи",
            command=self._delete_selected_name_birth
        ).pack(side=tk.RIGHT, padx=10)
    
    def _create_visit_vet_tab(self, parent):
        # Форма поиска
        form_frame = ttk.LabelFrame(parent, text="Критерии удаления", padding="10")
        form_frame.pack(fill=tk.X, pady=5)
        
        # Дата последнего визита
        ttk.Label(form_frame, text="Дата последнего визита:").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.visit_entry = DateEntry(
            form_frame, 
            width=12, 
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy'
        )
        self.visit_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # ФИО ветеринара
        ttk.Label(form_frame, text="ФИО ветеринара:").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.vet_name_entry = ttk.Entry(form_frame, width=30)
        self.vet_name_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Кнопка поиска
        ttk.Button(
            form_frame,
            text="Найти",
            command=self._search_by_visit_and_vet
        ).grid(row=0, column=2, rowspan=2, padx=10, sticky=tk.W)
        
        # Результаты поиска
        result_frame = ttk.LabelFrame(parent, text="Найденные записи", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создаем таблицу
        columns = ("name", "birth_date", "last_visit", "vet_name", "diagnosis")
        self.visit_vet_tree = ttk.Treeview(
            result_frame, 
            columns=columns, 
            show="headings",
            selectmode="extended"
        )
        
        # Настройка заголовков
        self.visit_vet_tree.heading("name", text="Имя питомца")
        self.visit_vet_tree.heading("birth_date", text="Дата рождения")
        self.visit_vet_tree.heading("last_visit", text="Дата последнего приема")
        self.visit_vet_tree.heading("vet_name", text="ФИО ветеринара")
        self.visit_vet_tree.heading("diagnosis", text="Диагноз")
        
        # Настройка колонок
        self.visit_vet_tree.column("name", width=120, anchor=tk.W)
        self.visit_vet_tree.column("birth_date", width=100, anchor=tk.CENTER)
        self.visit_vet_tree.column("last_visit", width=120, anchor=tk.CENTER)
        self.visit_vet_tree.column("vet_name", width=150, anchor=tk.W)
        self.visit_vet_tree.column("diagnosis", width=200, anchor=tk.W)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.visit_vet_tree.yview)
        self.visit_vet_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.visit_vet_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка удаления
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Удалить выбранные записи",
            command=self._delete_selected_visit_vet
        ).pack(side=tk.RIGHT, padx=10)
    
    def _create_diagnosis_tab(self, parent):
        # Форма поиска
        form_frame = ttk.LabelFrame(parent, text="Критерии удаления", padding="10")
        form_frame.pack(fill=tk.X, pady=5)
        
        # Фраза для поиска в диагнозе
        ttk.Label(form_frame, text="Фраза для поиска:").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.diagnosis_entry = ttk.Entry(form_frame, width=30)
        self.diagnosis_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text="(поиск будет регистронезависимым)").grid(row=1, column=1, sticky=tk.W)
        
        # Кнопка поиска
        ttk.Button(
            form_frame,
            text="Найти",
            command=self._search_by_diagnosis
        ).grid(row=0, column=2, rowspan=2, padx=10, sticky=tk.W)
        
        # Результаты поиска
        result_frame = ttk.LabelFrame(parent, text="Найденные записи", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создаем таблицу
        columns = ("name", "birth_date", "last_visit", "vet_name", "diagnosis")
        self.diagnosis_tree = ttk.Treeview(
            result_frame, 
            columns=columns, 
            show="headings",
            selectmode="extended"
        )
        
        # Настройка заголовков
        self.diagnosis_tree.heading("name", text="Имя питомца")
        self.diagnosis_tree.heading("birth_date", text="Дата рождения")
        self.diagnosis_tree.heading("last_visit", text="Дата последнего приема")
        self.diagnosis_tree.heading("vet_name", text="ФИО ветеринара")
        self.diagnosis_tree.heading("diagnosis", text="Диагноз")
        
        # Настройка колонок
        self.diagnosis_tree.column("name", width=120, anchor=tk.W)
        self.diagnosis_tree.column("birth_date", width=100, anchor=tk.CENTER)
        self.diagnosis_tree.column("last_visit", width=120, anchor=tk.CENTER)
        self.diagnosis_tree.column("vet_name", width=150, anchor=tk.W)
        self.diagnosis_tree.column("diagnosis", width=200, anchor=tk.W)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.diagnosis_tree.yview)
        self.diagnosis_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.diagnosis_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка удаления
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Удалить выбранные записи",
            command=self._delete_selected_diagnosis
        ).pack(side=tk.RIGHT, padx=10)
    
    
    def _search_by_name_and_birth(self):
        """Поиск по имени и дате рождения"""
        name = self.name_entry.get().strip()
        birth_date = self.birth_date_entry.get()  # Это строка в формате ДД.ММ.ГГГГ
        
        if not name:
            messagebox.showerror("Ошибка", "Введите имя питомца")
            return
        
        if not birth_date:
            messagebox.showerror("Ошибка", "Выберите дату рождения")
            return
        
        try:
            # Передаем строку, контроллер сам распарсит
            results = self.controller.search_by_name_and_birth(name, birth_date)
            
            # Отображаем результаты
            self._display_results(self.name_birth_tree, results)
            
            if not results:
                messagebox.showinfo("Поиск", "Записи не найдены")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
    
    def _search_by_visit_and_vet(self):
        """Поиск по дате визита и ветеринару"""
        last_visit = self.visit_entry.get()  # Строка
        vet_name = self.vet_name_entry.get().strip()
        
        if not last_visit:
            messagebox.showerror("Ошибка", "Выберите дату последнего визита")
            return
        
        if not vet_name:
            messagebox.showerror("Ошибка", "Введите ФИО ветеринара")
            return
        
        try:
            results = self.controller.search_by_visit_and_vet(last_visit, vet_name)
            self._display_results(self.visit_vet_tree, results)
            
            if not results:
                messagebox.showinfo("Поиск", "Записи не найдены")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
    
    def _search_by_diagnosis(self):
        """Поиск по фразе в диагнозе"""
        phrase = self.diagnosis_entry.get().strip()
        
        if not phrase:
            messagebox.showerror("Ошибка", "Введите фразу для поиска")
            return
        
        try:
            results = self.controller.search_by_diagnosis_phrase(phrase)
            self._display_results(self.diagnosis_tree, results)
            
            if not results:
                messagebox.showinfo("Поиск", "Записи не найдены")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
    
    def _display_results(self, tree, results):
        """Отображает результаты поиска в таблице"""
        # Очищаем таблицу
        for item in tree.get_children():
            tree.delete(item)
        
        # Заполняем таблицу результатами
        for pet in results:
            tree.insert("", tk.END, values=(
                pet.name,
                pet.birth_date.strftime("%d.%m.%Y"),
                pet.last_visit.strftime("%d.%m.%Y"),
                pet.vet_name,
                pet.diagnosis
            ))
    
   
    def _delete_selected_name_birth(self):
        """Удаляет выбранные записи из вкладки по имени и дате рождения"""
        selected_items = self.name_birth_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("Информация", "Нет выбранных записей для удаления")
            return
        
        # Получаем объекты Pet для удаления
        pets_to_delete = []
        found_pets = []  # Для отслеживания уникальности
        
        for item in selected_items:
            values = self.name_birth_tree.item(item)["values"]
            if not values:
                continue
                
            name = values[0]
            birth_date_str = values[1]  # Строка в формате ДД.ММ.ГГГГ
            
            try:
                # Ищем соответствующие объекты в базе
                # Важно: передаем name и birth_date_str как есть
                results = self.controller.search_by_name_and_birth(name, birth_date_str)
                
                # Добавляем найденных питомцев, избегая дубликатов
                for pet in results:
                    # Создаем уникальный ключ для проверки дубликатов
                    pet_key = (pet.name, pet.birth_date.isoformat())
                    if pet_key not in found_pets:
                        found_pets.append(pet_key)
                        pets_to_delete.append(pet)
                        
            except Exception as e:
                print(f"Ошибка при поиске для удаления: {e}")
                continue
        
        # *** ИСПРАВЛЕНО: Удаляем, даже если одна запись ***
        if pets_to_delete:
            count = len(pets_to_delete)
            if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить {count} запис(ь/и)?"):
                self.controller.delete_pets(pets_to_delete)
                # Обновляем результаты поиска
                self._search_by_name_and_birth()
        else:
            messagebox.showerror("Ошибка", "Не удалось найти соответствующие записи в базе")
    
    def _delete_selected_visit_vet(self):
        """Удаляет выбранные записи из вкладки по визиту и ветеринару"""
        selected_items = self.visit_vet_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("Информация", "Нет выбранных записей для удаления")
            return
        
        pets_to_delete = []
        found_pets = []
        
        for item in selected_items:
            values = self.visit_vet_tree.item(item)["values"]
            if not values:
                continue
                
            last_visit_str = values[2]  # Дата последнего визита
            vet_name = values[3]         # ФИО ветеринара
            
            try:
                results = self.controller.search_by_visit_and_vet(last_visit_str, vet_name)
                
                for pet in results:
                    pet_key = (pet.name, pet.birth_date.isoformat())
                    if pet_key not in found_pets:
                        found_pets.append(pet_key)
                        pets_to_delete.append(pet)
                        
            except Exception as e:
                print(f"Ошибка при поиске для удаления: {e}")
                continue
        
        if pets_to_delete:
            count = len(pets_to_delete)
            if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить {count} запис(ь/и)?"):
                self.controller.delete_pets(pets_to_delete)
                self._search_by_visit_and_vet()
        else:
            messagebox.showerror("Ошибка", "Не удалось найти соответствующие записи в базе")
    
    def _delete_selected_diagnosis(self):
        """Удаляет выбранные записи из вкладки по диагнозу"""
        selected_items = self.diagnosis_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("Информация", "Нет выбранных записей для удаления")
            return
        
        phrase = self.diagnosis_entry.get().strip()
        if not phrase:
            messagebox.showerror("Ошибка", "Не найдена фраза для поиска")
            return
        
        pets_to_delete = []
        found_pets = []
        
        # Получаем все записи, соответствующие фразе
        try:
            all_results = self.controller.search_by_diagnosis_phrase(phrase)
            # Создаем словарь для быстрого поиска по имени и дате
            results_dict = {}
            for pet in all_results:
                key = (pet.name, pet.birth_date.strftime("%d.%m.%Y"))
                results_dict[key] = pet
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
            return
        
        # Для каждого выбранного элемента находим соответствующего питомца
        for item in selected_items:
            values = self.diagnosis_tree.item(item)["values"]
            if not values:
                continue
                
            name = values[0]
            birth_date_str = values[1]
            key = (name, birth_date_str)
            
            if key in results_dict and key not in found_pets:
                found_pets.append(key)
                pets_to_delete.append(results_dict[key])
        
        if pets_to_delete:
            count = len(pets_to_delete)
            if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить {count} запис(ь/и)?"):
                self.controller.delete_pets(pets_to_delete)
                self._search_by_diagnosis()  # Обновляем результаты
        else:
            messagebox.showerror("Ошибка", "Не удалось найти соответствующие записи в базе")