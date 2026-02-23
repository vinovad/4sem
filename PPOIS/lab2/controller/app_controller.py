"""
app_controller.py - главный контроллер приложения

Контроллер реализует следующие функции:
- Обработка пользовательских действий (добавление, поиск, удаление, сохранение, загрузка)
- Управление постраничной навигацией
- Связь между моделью и представлением
"""

import os
from datetime import date
from tkinter import filedialog, messagebox

from model import Pet, PetDatabase, XMLHandler
from view.dialogs.add_dialog import AddPetDialog
from view.dialogs.search_dialog import SearchDialog
from view.dialogs.delete_dialog import DeleteDialog

class AppController:
    def __init__(self, view=None):
        """
        Инициализация контроллера
        
        Args:
            view: Объект представления (MainWindow)
        """
        self.view = view
        self.database = PetDatabase()
        self.current_file = None  # Текущий файл для сохранения/загрузки
    
    def initialize(self):
        """Завершает инициализацию контроллера после установки view"""
        # Обновляем интерфейс
        self.update_view()
    
    def load_demo_data(self):
        """Загружает демо-данные из XML-файлов"""
        try:
            # Загружаем данные из demo1.xml
            demo1_path = os.path.join("data", "demo1.xml")
            if os.path.exists(demo1_path):
                pets = XMLHandler.load_from_xml(demo1_path)
                for pet in pets:
                    self.database.add_pet(pet)
                print(f"Загружено {len(pets)} записей из {demo1_path}")
            
            # Загружаем данные из demo2.xml
            demo2_path = os.path.join("data", "demo2.xml")
            if os.path.exists(demo2_path):
                pets = XMLHandler.load_from_xml(demo2_path)
                for pet in pets:
                    self.database.add_pet(pet)
                print(f"Загружено {len(pets)} записей из {demo2_path}")
            
            # Обновляем интерфейс только один раз после загрузки всех данных
            self.update_view()
        except Exception as e:
            print(f"Демо-данные не загружены: {str(e)}")
    
    def update_view(self):
        """Обновляет таблицу и информацию о пагинации в представлении"""
        if self.view is None:
            return
            
        # Получаем данные для текущей страницы
        pets = self.database.get_page(self.database.get_current_page())
        
        # Обновляем таблицу
        self.view.update_table(pets)
        
        # Обновляем информацию о пагинации
        total_pages = self.database.get_total_pages()
        total_records = len(self.database.get_all_pets())
        self.view.pagination.update_pagination(
            self.database.get_current_page(),
            total_pages,
            total_records
        )
    
    #Методы для отображения диалоговых окон 
    
    def show_add_dialog(self):
        """Показывает диалог добавления питомца"""
        AddPetDialog(self.view, self)
    
    def show_search_dialog(self):
        """Показывает диалог поиска питомца"""
        SearchDialog(self.view, self)
    
    def show_delete_dialog(self):
        """Показывает диалог удаления питомца"""
        DeleteDialog(self.view, self)
    
    #Методы для работы с данными 
    
    def add_pet(self, pet_data):
        """
        Добавляет нового питомца в базу данных
        
        Args:
            pet_data: Кортеж с данными питомца (name, birth_date, last_visit, vet_name, diagnosis)
        """
        try:
            name, birth_date_str, last_visit_str, vet_name, diagnosis = pet_data
            
            # Преобразование строк в даты
            birth_date = self._parse_date(birth_date_str)
            last_visit = self._parse_date(last_visit_str)
            
            # Проверка логики дат (дата последнего визита не может быть раньше даты рождения)
            if last_visit < birth_date:
                messagebox.showerror(
                    "Ошибка", 
                    "Дата последнего приема не может быть раньше даты рождения питомца"
                )
                return
            
            # Создание и добавление питомца
            pet = Pet(name, birth_date, last_visit, vet_name, diagnosis)
            self.database.add_pet(pet)
            
            # Обновление интерфейса
            self.update_view()
            messagebox.showinfo("Успех", "Питомец успешно добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный формат данных: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить питомца: {str(e)}")
    
    #Методы поиска согласно варианту 8 
    
    def search_by_name_and_birth(self, name, birth_date_str):
        """
        Поиск по имени питомца и дате рождения (условие 1)
        
        Args:
            name: Имя питомца
            birth_date_str: Строка с датой рождения
            
        Returns:
            Список найденных питомцев
        """
        try:
            birth_date = self._parse_date(birth_date_str)
            return self.database.find_by_name_and_birth(name, birth_date)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты рождения")
            return []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
            return []
    
    def search_by_visit_and_vet(self, last_visit_str, vet_name):
        """
        Поиск по дате последнего приема и ФИО ветеринара (условие 2)
        
        Args:
            last_visit_str: Строка с датой последнего приема
            vet_name: ФИО ветеринара
            
        Returns:
            Список найденных питомцев
        """
        try:
            last_visit = self._parse_date(last_visit_str)
            return self.database.find_by_visit_and_vet(last_visit, vet_name)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты последнего приема")
            return []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
            return []
    
    def search_by_diagnosis_phrase(self, phrase):
        """
        Поиск по фразе из диагноза (условие 3)
        
        Args:
            phrase: Фраза для поиска в диагнозе
            
        Returns:
            Список найденных питомцев
        """
        try:
            return self.database.find_by_diagnosis_phrase(phrase)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")
            return []
    
    #Методы удаления 
    
    def delete_pets(self, pets_to_delete):
        """
        Удаляет указанных питомцев из базы данных
        
        Args:
            pets_to_delete: Список питомцев для удаления
        """
        try:
            if not pets_to_delete:
                messagebox.showinfo("Информация", "Нет записей для удаления")
                return
            
            count = self.database.delete_pets(pets_to_delete)
            self.update_view()
            messagebox.showinfo("Успех", f"Успешно удалено {count} записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить записи: {str(e)}")
    
    #Методы для работы с XML 
    
    def load_from_xml(self):
        """Загружает данные из XML-файла"""
        try:
            filename = filedialog.askopenfilename(
                title="Выберите XML-файл",
                filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")]
            )
            
            if filename:
                pets = XMLHandler.load_from_xml(filename)
                initial_count = len(self.database.get_all_pets())
                
                for pet in pets:
                    self.database.add_pet(pet)
                
                self.current_file = filename
                self.update_view()
                
                added_count = len(self.database.get_all_pets()) - initial_count
                messagebox.showinfo(
                    "Успех", 
                    f"Загружено {added_count} записей из {os.path.basename(filename)}"
                )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def save_to_xml(self):
        """Сохраняет данные в XML-файл"""
        try:
            # Если есть текущий файл, сохраняем в него
            if self.current_file and messagebox.askyesno("Сохранение", 
                    f"Сохранить данные в файл {os.path.basename(self.current_file)}?"):
                XMLHandler.save_to_xml(self.database.get_all_pets(), self.current_file)
                messagebox.showinfo("Успех", "Данные успешно сохранены")
                return
            
            # Иначе запрашиваем имя файла
            filename = filedialog.asksaveasfilename(
                title="Сохранить как",
                defaultextension=".xml",
                filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")]
            )
            
            if filename:
                XMLHandler.save_to_xml(self.database.get_all_pets(), filename)
                self.current_file = filename
                messagebox.showinfo("Успех", "Данные успешно сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    #Методы для постраничной навигации 
    
    def change_page(self, page_num):
        """
        Изменяет текущую страницу
        
        Args:
            page_num: Номер страницы
        """
        if self.database.set_current_page(page_num):
            self.update_view()
        else:
            total_pages = self.database.get_total_pages()
            if total_pages > 0:
                messagebox.showwarning("Внимание", f"Номер страницы должен быть от 1 до {total_pages}")
            else:
                messagebox.showinfo("Информация", "Нет данных для отображения")
    
    def change_page_size(self, page_size):
        """
        Изменяет количество записей на странице
        
        Args:
            page_size: Новое количество записей на странице
        """
        try:
            page_size = int(page_size)
            if page_size <= 0:
                raise ValueError("Количество записей на странице должно быть положительным")
            
            self.database.set_page_size(page_size)
            
            # Если текущая страница больше, чем общее количество страниц, перейти на последнюю
            if self.database.get_current_page() > self.database.get_total_pages():
                self.database.set_current_page(self.database.get_total_pages())
            
            self.update_view()
            messagebox.showinfo("Успех", f"Количество записей на странице изменено на {page_size}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить размер страницы: {str(e)}")
    
    #Вспомогательные методы 
    
    def _parse_date(self, date_str):
        """
        Парсит строку в объект date
        
        Поддерживаемые форматы:
        - ДД.ММ.ГГГГ
        - ГГГГ-ММ-ДД
        
        Args:
            date_str: Строка с датой
            
        Returns:
            Объект date
            
        Raises:
            ValueError: При некорректном формате даты
        """
        date_str = date_str.strip()
        
        try:
            # Попробуем формат ДД.ММ.ГГГГ
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) == 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    return date(year, month, day)
            
            # Попробуем формат ГГГГ-ММ-ДД
            if '-' in date_str:
                parts = date_str.split('-')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    return date(year, month, day)
            
            raise ValueError(f"Некорректный формат даты: {date_str}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Некорректный формат даты '{date_str}': {str(e)}")
