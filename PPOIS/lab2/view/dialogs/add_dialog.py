import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class AddPetDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Добавить питомца")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Центрируем окно
        self.transient(parent)
        self.grab_set()
        self._center_window()
        
        # Создаем форму
        self._create_form()
        
        # Фокус на поле имени
        self.name_entry.focus_set()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (width // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_form(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Дата последнего приема
        ttk.Label(form_frame, text="Дата последнего приема:").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.last_visit_entry = DateEntry(
            form_frame, 
            width=12, 
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy'
        )
        self.last_visit_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # ФИО ветеринара
        ttk.Label(form_frame, text="ФИО ветеринара:").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.vet_name_entry = ttk.Entry(form_frame, width=30)
        self.vet_name_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Диагноз
        ttk.Label(form_frame, text="Диагноз:").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.diagnosis_entry = ttk.Entry(form_frame, width=30)
        self.diagnosis_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Добавить", 
            command=self._add_pet
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Отмена", 
            command=self.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _add_pet(self):
        name = self.name_entry.get().strip()
        birth_date = self.birth_date_entry.get()
        last_visit = self.last_visit_entry.get()
        vet_name = self.vet_name_entry.get().strip()
        diagnosis = self.diagnosis_entry.get().strip()
        
        if not all([name, birth_date, last_visit, vet_name, diagnosis]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return
        
        self.controller.add_pet((name, birth_date, last_visit, vet_name, diagnosis))
        self.destroy()