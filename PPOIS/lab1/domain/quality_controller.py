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
from .domain_errors import (
    ProductNotFoundError,
    UnknownQualityStandardError,
    QualityCheckFailedError,
    CertificateAlreadyExistsError,
    InvalidProductAttributeError,
    InvalidReviewRatingError
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
            raise UnknownQualityStandardError(f"Неизвестный стандарт: {standard_name}")

    def add_product(self, name: str) -> Product:
        """Добавить продукт в систему"""
        product = Product(name)
        self.products.append(product)
        return product

    def show_products(self) -> List[Tuple[str, str]]:
        """Показать список продуктов"""
        return [(product.product_id, product.name) for product in self.products]

    def get_product(self, product_id: str) -> Product:
        """Получить продукт по ID. Выбрасывает исключение, если продукт не найден."""
        product = next((p for p in self.products if p.product_id == product_id), None)
        if not product:
            raise ProductNotFoundError(f"Продукт с ID {product_id} не найден.")
        return product

    def has_certificate_for_current_stage(self, product_id: str) -> bool:
        """Проверить, есть ли действующий сертификат для текущего этапа продукта"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError:
            return False
        
        current_stage = product.get_current_stage()
        for cert in product.certificates:
            if cert.stage == current_stage and cert.is_valid():
                return True
        return False

    def advance_stage(self, product_id: str) -> bool:
        """Переводит продукт на следующий этап производства, если текущий этап пройден и сертифицирован"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError:
            return False
        
        if self.has_certificate_for_current_stage(product_id) and product.current_stage < len(product.PRODUCTION_STAGES) - 1:
            product.current_stage += 1
            return True
        return False

    def is_production_complete(self, product_id: str) -> bool:
        """Проверить, завершено ли производство"""
        try:
            product = self.get_product(product_id)
            return product.current_stage >= len(product.PRODUCTION_STAGES)
        except ProductNotFoundError:
            return True  # Если продукт не найден, считаем производство завершенным

    def add_quality_check(self, product_id: str, stage: str, result: dict) -> None:
        """Добавляет запись о результате проверки качества"""
        try:
            product = self.get_product(product_id)
            product.quality_checks.append({
                "stage": stage,
                "result": result,
                "timestamp": datetime.now()
            })
        except ProductNotFoundError:
            pass

    def add_certificate(self, product_id: str, certificate: Certificate) -> None:
        """Добавляет сертификат продукту"""
        try:
            product = self.get_product(product_id)
            product.certificates.append(certificate)
        except ProductNotFoundError:
            pass

    def check_compliance(self, product_id: str, standard: QualityStandard) -> Tuple[bool, List[str]]:
        """Проверить соответствие продукта стандарту качества"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            raise ProductNotFoundError(str(e))
        
        current_stage = product.get_current_stage()
        failed_criteria = []
        for criterion, required_value in standard.criteria.items():
            actual_value = product.attributes[criterion]
            print(f"Проверка критерия '{criterion}': продукт имеет '{actual_value}', требуется '{required_value}'")
            if actual_value != required_value:
                failed_criteria.append(criterion)
        
        if failed_criteria:
            raise QualityCheckFailedError(f"Продукт не соответствует стандарту. Не соответствует по критериям: {', '.join(failed_criteria)}")
        
        return True, []

    def certify_product(self, product_id: str, standard: QualityStandard) -> bool:
        """Выдать сертификат продукту"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return False
        
        # Сначала проверяем соответствие стандарту
        try:
            self.check_compliance(product_id, standard)
        except QualityCheckFailedError as e:
            print(f"\nОшибка: {e}")
            return False
        
        current_stage = product.get_current_stage()
        
        # Проверяем, не выдан ли уже действующий сертификат для текущего этапа
        existing_cert = next(
            (cert for cert in product.certificates 
             if cert.stage == current_stage and cert.is_valid()), 
            None
        )
        
        if existing_cert:
            raise CertificateAlreadyExistsError(f"Продукт {product_id} уже имеет действующий сертификат для этапа {current_stage}.")
        
        # Выдаем сертификат
        certificate = Certificate(product_id, standard, current_stage)
        self.add_certificate(product_id, certificate)
        print(f"Сертификат успешно выдан для продукта {product_id} на этапе {current_stage}.")
        return True

    def improve_product(self, product_id: str, standard: QualityStandard) -> List[str]:
        """Внести улучшения в продукт для соответствия стандарту"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return [f"Продукт с ID {product_id} не найден."]
        
        try:
            self.check_compliance(product_id, standard)
            # Если проверка прошла успешно, продукт уже соответствует стандарту
            return []
        except QualityCheckFailedError:
            # Если проверка не прошла, улучшаем продукт
            _, failed_criteria = self._check_compliance_without_exception(product_id, standard)
            for criterion in failed_criteria:
                old_value = product.attributes[criterion]
                new_value = standard.criteria[criterion]
                product.update_attribute(criterion, new_value)
                print(f"  {criterion}: улучшено с '{old_value}' на '{new_value}'")
            return failed_criteria

    def _check_compliance_without_exception(self, product_id: str, standard: QualityStandard) -> Tuple[bool, List[str]]:
        """Проверить соответствие продукта стандарту качества без выбрасывания исключений"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError:
            return False, ["Продукт не найден"]
        
        current_stage = product.get_current_stage()
        failed_criteria = []
        for criterion, required_value in standard.criteria.items():
            actual_value = product.attributes[criterion]
            if actual_value != required_value:
                failed_criteria.append(criterion)
        
        return len(failed_criteria) == 0, failed_criteria

    def run_production(self, product_id: str) -> None:
        """Запустить производство продукта через все этапы"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return
        
        print(f"\nЗапуск производства для продукта {product_id}...")
        
        # Проверяем текущий этап
        current_stage = product.get_current_stage()
        print(f"Текущий этап производства: {current_stage}")
        
        # Проверяем, пройден ли текущий этап
        if self.has_certificate_for_current_stage(product_id):
            print(f"Этап {current_stage} уже пройден.")
            try:
                if self.advance_stage(product_id):
                    print(f"Переход к следующему этапу: {product.get_current_stage()}")
                else:
                    print("Производство завершено успешно.")
            except Exception as e:
                print(f"\nОшибка при переходе к следующему этапу: {e}")
        else:
            print(f"Необходимо пройти проверку и получить сертификат для этапа {current_stage}.")

    def add_review(self, product_id: str, author: str, comment: str, rating: int) -> bool:
        """Добавить отзыв к продукту"""
        try:
            product = self.get_product(product_id)
            review = Review(product_id, author, comment, rating)
            product.add_review(review)
            return True
        except (ProductNotFoundError, InvalidReviewRatingError) as e:
            print(f"\nОшибка: {e}")
            return False

    def analyze_reviews(self, product_id: str) -> Tuple[Optional[float], List[str]]:
        """Анализировать отзывы и рекомендовать улучшения"""
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            return None, [str(e)]
        
        if not product.reviews:
            return None, []
        
        # Вычисляем средний рейтинг
        avg_rating = sum(review.rating for review in product.reviews) / len(product.reviews)
        
        # Анализируем, по каким критериям нужно улучшать
        recommendations = []
        if avg_rating < 4:
            recommendations.append("Продукт требует улучшений: средний рейтинг ниже 4.")
        
        return avg_rating, recommendations