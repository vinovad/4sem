"""
database.py - класс для управления коллекцией питомцев

Содержит методы для:
- Добавления питомцев
- Поиска по различным критериям (вариант 8)
- Удаления питомцев
- Постраничного отображения данных
"""

from datetime import date
from .pet import Pet

class PetDatabase:
    """Класс для управления коллекцией питомцев"""
    
    def __init__(self, records_per_page=10):
        """
        Инициализация базы данных питомцев
        
        Args:
            records_per_page: Количество записей на странице
        """
        self.pets = []  # Список всех питомцев
        self.current_page = 1  # Текущая страница
        self.records_per_page = records_per_page  # Записей на странице
    
    def add_pet(self, pet: Pet):
        """Добавляет питомца в базу данных"""
        self.pets.append(pet)
    
    def get_all_pets(self):
        """Возвращает все записи о питомцах"""
        return self.pets
    
    # Методы поиска согласно варианту 
    
    def find_by_name_and_birth(self, name: str, birth_date: date):
        """
        Поиск по имени питомца и дате рождения (условие 1)
        
        Args:
            name: Имя питомца
            birth_date: Дата рождения
            
        Returns:
            Список найденных питомцев
        """
        return [pet for pet in self.pets 
                if pet.name.lower() == name.lower() and pet.birth_date == birth_date]
    
    def find_by_visit_and_vet(self, last_visit: date, vet_name: str):
        """
        Поиск по дате последнего приема и ФИО ветеринара (условие 2)
        
        Args:
            last_visit: Дата последнего приема
            vet_name: ФИО ветеринара
            
        Returns:
            Список найденных питомцев
        """
        return [pet for pet in self.pets 
                if pet.last_visit == last_visit and pet.vet_name.lower() == vet_name.lower()]
    
    def find_by_diagnosis_phrase(self, phrase: str):
        """
        Поиск по фразе из диагноза (условие 3)
        
        Args:
            phrase: Фраза для поиска в диагнозе
            
        Returns:
            Список найденных питомцев
        """
        phrase = phrase.lower()
        return [pet for pet in self.pets if phrase in pet.diagnosis.lower()]
    
    # Методы удаления 
    
    def delete_pets(self, pets_to_delete):
        """
        Удаляет указанных питомцев из базы данных
        
        Args:
            pets_to_delete: Список питомцев для удаления
            
        Returns:
            Количество удаленных записей
        """
        initial_count = len(self.pets)
        self.pets = [pet for pet in self.pets if pet not in pets_to_delete]
        return initial_count - len(self.pets)
    
    # Методы для постраничной навигации 
    
    def get_page(self, page_num):
        """
        Возвращает питомцев для указанной страницы
        
        Args:
            page_num: Номер страницы
            
        Returns:
            Список питомцев для отображения на странице
        """
        start_idx = (page_num - 1) * self.records_per_page
        end_idx = start_idx + self.records_per_page
        return self.pets[start_idx:end_idx]
    
    def get_total_pages(self):
        """Возвращает общее количество страниц"""
        return (len(self.pets) + self.records_per_page - 1) // self.records_per_page
    
    def set_page_size(self, page_size):
        """
        Устанавливает количество записей на странице
        
        Args:
            page_size: Новое количество записей на странице
        """
        if page_size > 0:
            self.records_per_page = page_size
            # Корректируем текущую страницу, если нужно
            if self.current_page > self.get_total_pages():
                self.current_page = max(1, self.get_total_pages())
    
    def get_current_page(self):
        """Возвращает текущую страницу"""
        return self.current_page
    
    def set_current_page(self, page_num):
        """
        Устанавливает текущую страницу
        
        Args:
            page_num: Номер страницы
            
        Returns:
            True, если страница установлена успешно, иначе False
        """
        total_pages = self.get_total_pages()
        if 1 <= page_num <= total_pages or (total_pages == 0 and page_num == 1):
            self.current_page = page_num
            return True
        return False