"""
pet.py - класс для представления данных о питомце

Вариант 8 требует следующую структуру:
- Имя питомца (строка)
- Дата рождения (тип date)
- Дата последнего приема (тип date)
- ФИО ветеринара (строка)
- Диагноз (строка)
"""

from datetime import date

class Pet:
    """Класс, представляющий питомца в ветеринарной клинике"""
    
    def __init__(self, name: str, birth_date: date, last_visit: date, 
                 vet_name: str, diagnosis: str):
        """
        Инициализация объекта Pet
        
        Args:
            name: Имя питомца
            birth_date: Дата рождения питомца
            last_visit: Дата последнего приема
            vet_name: ФИО ветеринара
            diagnosis: Диагноз
        """
        self.name = name
        self.birth_date = birth_date
        self.last_visit = last_visit
        self.vet_name = vet_name
        self.diagnosis = diagnosis
    
    def __str__(self):
        """Строковое представление питомца для отладки"""
        return (f"Pet(name={self.name}, "
                f"birth_date={self.birth_date.strftime('%d.%m.%Y')}, "
                f"last_visit={self.last_visit.strftime('%d.%m.%Y')}, "
                f"vet_name={self.vet_name}, "
                f"diagnosis={self.diagnosis})")
    
    def __repr__(self):
        """Представление объекта для интерпретатора"""
        return self.__str__()