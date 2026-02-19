from datetime import date, datetime
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .review import Review
    from .certificate import Certificate


class Product:
    _id_counter: int = 1
    PRODUCTION_STAGES: List[str] = ["dough", "baking", "cooling", "packaging"]
    
    def __init__(self, name: str) -> None:
        self.product_id: str = f"P{Product._id_counter:03}"
        self.name: str = name
        
        # Атрибуты по умолчанию не соответствуют стандартам
        self.attributes: Dict[str, str] = {
            "defects": "have",    # have, few, none
            "texture": "poor",     # poor, good, excellent
            "smell": "bad",        # bad, good, excellent
            "taste": "poor"        # poor, good, excellent
        }
        
        self.quality_checks: List[dict] = []  # Результаты проверок
        self.reviews: List['Review'] = []     # Отзывы
        self.certificates: List['Certificate'] = []  # Сертификаты
        self.status: str = "production"  # production, quality_check, approved, rejected
        self.current_stage: int = 0  # Индекс текущего этапа производства
        
        Product._id_counter += 1
    
    def get_current_stage(self) -> str:
        """Получить текущий этап производства"""
        if self.current_stage < len(self.PRODUCTION_STAGES):
            return self.PRODUCTION_STAGES[self.current_stage]
        return "completed"
    
    def update_attribute(self, attribute: str, value: str) -> None:
        """Обновить атрибут качества"""
        if attribute in self.attributes:
            self.attributes[attribute] = value
        else:
            raise ValueError(f"Атрибут {attribute} не существует")
    
    def add_review(self, review: 'Review') -> None:
        """Добавить отзыв к продукту"""
        self.reviews.append(review)
    
    def __str__(self) -> str:
        """Строковое представление продукта"""
        return (
            f"Product(ID={self.product_id}, Name={self.name}, "
            f"Status={self.status}, ProductionStage={self.get_current_stage()}, "
            f"Certificates={len(self.certificates)}, "
            f"Attributes={self.attributes})"
        )
