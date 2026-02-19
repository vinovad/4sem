from typing import List, Dict, Tuple, Optional
from .product import Product
from .quality_standard import (
    QualityStandard, 
    GOSTStandard, 
    BakeryEnterpriseStandard, 
    OrganicBakeryStandard
)
from .certificate import Certificate
from .review import Review
from .production_stages import (
    DoughStage,
    BakingStage,
    CoolingStage,
    PackagingStage
)
from datetime import datetime


class QualityController:
    """Контроллер системы контроля качества"""
    
    def __init__(self) -> None:
        self.products: List[Product] = []
        self.quality_standards: Dict[str, QualityStandard] = {
            "1": GOSTStandard(),
            "2": BakeryEnterpriseStandard(),
            "3": OrganicBakeryStandard()
        }
        self.production_stages = [
            DoughStage(),
            BakingStage(),
            CoolingStage(),
            PackagingStage()
        ]

    def get_standard(self, standard_name: str) -> QualityStandard:
        """Получить стандарт по имени"""
        if standard_name == "ГОСТ СТ-1":
            return GOSTStandard()
        elif standard_name == "Собственный стандарт пекарни":
            return BakeryEnterpriseStandard()
        elif standard_name == "Органическая выпечка":
            return OrganicBakeryStandard()
        else:
            raise ValueError(f"Неизвестный стандарт: {standard_name}")

    def add_product(self, name: str) -> Product:
        """Добавить продукт в систему"""
        product = Product(name)
        self.products.append(product)
        return product

    def show_products(self) -> List[Tuple[str, str]]:
        """Показать список продуктов"""
        return [(product.product_id, product.name) for product in self.products]

    def get_product(self, product_id: str) -> Optional[Product]:
        """Получить продукт по ID"""
        return next((p for p in self.products if p.product_id == product_id), None)

    def has_certificate_for_current_stage(self, product_id: str) -> bool:
        """Проверить, есть ли действующий сертификат для текущего этапа продукта"""
        product = self.get_product(product_id)
        if not product:
            return False
        
        current_stage = product.get_current_stage()
        for cert in product.certificates:
            if cert.stage == current_stage and cert.is_valid():
                return True
        return False

    def advance_stage(self, product_id: str) -> bool:
        """Переводит продукт на следующий этап производства, если текущий этап пройден и сертифицирован"""
        product = self.get_product(product_id)
        if not product:
            return False
        
        if self.has_certificate_for_current_stage(product_id) and product.current_stage < len(product.PRODUCTION_STAGES) - 1:
            product.current_stage += 1
            return True
        return False

    def is_production_complete(self, product_id: str) -> bool:
        """Проверить, завершено ли производство"""
        product = self.get_product(product_id)
        if not product:
            return True  # Если продукт не найден, считаем производство завершенным
        
        return product.current_stage >= len(product.PRODUCTION_STAGES)

    def add_quality_check(self, product_id: str, stage: str, result: dict) -> None:
        """Добавляет запись о результате проверки качества"""
        product = self.get_product(product_id)
        if not product:
            return
        
        product.quality_checks.append({
            "stage": stage,
            "result": result,
            "timestamp": datetime.now()
        })

    def add_certificate(self, product_id: str, certificate: Certificate) -> None:
        """Добавляет сертификат продукту"""
        product = self.get_product(product_id)
        if product:
            product.certificates.append(certificate)

    def check_compliance(self, product_id: str, standard: QualityStandard) -> Tuple[bool, List[str]]:
        """Проверить соответствие продукта стандарту качества"""
        product = self.get_product(product_id)
        if not product:
            print(f"Продукт с ID {product_id} не найден.")
            return False, ["Продукт не найден"]
        
        current_stage = product.get_current_stage()
        failed_criteria = []
        for criterion, required_value in standard.criteria.items():
            actual_value = product.attributes[criterion]
            print(f"Проверка критерия '{criterion}': продукт имеет '{actual_value}', требуется '{required_value}'")
            if actual_value != required_value:
                failed_criteria.append(criterion)
        
        return len(failed_criteria) == 0, failed_criteria

    def certify_product(self, product_id: str, standard: QualityStandard) -> bool:
        """Выдать сертификат продукту"""
        product = self.get_product(product_id)
        if not product:
            print(f"Продукт с ID {product_id} не найден.")
            return False
        
        # Сначала проверяем соответствие стандарту
        is_compliant, _ = self.check_compliance(product_id, standard)
        if not is_compliant:
            print(f"Продукт {product_id} не соответствует стандарту и не может быть сертифицирован.")
            return False
        
        current_stage = product.get_current_stage()
        
        # Проверяем, не выдан ли уже действующий сертификат для текущего этапа
        existing_cert = next(
            (cert for cert in product.certificates 
             if cert.stage == current_stage and cert.is_valid()), 
            None
        )
        
        if existing_cert:
            print(f"Продукт {product_id} уже имеет действующий сертификат для этапа {current_stage}.")
            return False
        
        # Выдаем сертификат
        certificate = Certificate(product_id, standard, current_stage)
        self.add_certificate(product_id, certificate)
        print(f"Сертификат успешно выдан для продукта {product_id} на этапе {current_stage}.")
        return True

    def improve_product(self, product_id: str, standard: QualityStandard) -> List[str]:
        """Внести улучшения в продукт для соответствия стандарту"""
        product = self.get_product(product_id)
        if not product:
            print(f"Продукт с ID {product_id} не найден.")
            return [f"Продукт с ID {product_id} не найден."]
        
        _, failed_criteria = self.check_compliance(product_id, standard)
        if failed_criteria:
            for criterion in failed_criteria:
                old_value = product.attributes[criterion]
                new_value = standard.criteria[criterion]
                product.update_attribute(criterion, new_value)
                print(f"  {criterion}: улучшено с '{old_value}' на '{new_value}'")
        
        return failed_criteria

    def run_production(self, product_id: str) -> None:
        """Запустить производство продукта через все этапы"""
        product = self.get_product(product_id)
        if not product:
            print(f"Продукт с ID {product_id} не найден.")
            return
        
        print(f"\nЗапуск производства для продукта {product_id}...")
        
        # Проверяем текущий этап
        current_stage = product.get_current_stage()
        print(f"Текущий этап производства: {current_stage}")
        
        # Проверяем, пройден ли текущий этап
        if self.has_certificate_for_current_stage(product_id):
            print(f"Этап {current_stage} уже пройден.")
            if self.advance_stage(product_id):
                print(f"Переход к следующему этапу: {product.get_current_stage()}")
            else:
                print("Производство завершено успешно.")
        else:
            print(f"Необходимо пройти проверку и получить сертификат для этапа {current_stage}.")

    def add_review(self, product_id: str, author: str, comment: str, rating: int) -> bool:
        """Добавить отзыв к продукту"""
        product = self.get_product(product_id)
        if product:
            review = Review(product_id, author, comment, rating)
            product.add_review(review)
            return True
        return False

    def analyze_reviews(self, product_id: str) -> Tuple[Optional[float], List[str]]:
        """Анализировать отзывы и рекомендовать улучшения"""
        product = self.get_product(product_id)
        if not product:
            return None, ["Продукт не найден"]
        
        if not product.reviews:
            return None, []
        
        # Вычисляем средний рейтинг
        avg_rating = sum(review.rating for review in product.reviews) / len(product.reviews)
        
        # Анализируем, по каким критериям нужно улучшать
        recommendations = []
        if avg_rating < 4:
            recommendations.append("Продукт требует улучшений: средний рейтинг ниже 4.")
        
        return avg_rating, recommendations
