import json
from datetime import datetime, date
import os
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
        if standard_name == "ГОСТ СТ-1":
            return GOSTStandard()
        elif standard_name == "Собственный стандарт пекарни":
            return BakeryEnterpriseStandard()
        elif standard_name == "Органическая выпечка":
            return OrganicBakeryStandard()
        else:
            raise UnknownQualityStandardError(f"Неизвестный стандарт: {standard_name}")

    def add_product(self, name: str) -> Product:
        product = Product(name)
        self.products.append(product)
        return product

    def show_products(self) -> List[Tuple[str, str]]:
        return [(product.product_id, product.name) for product in self.products]

    def get_product(self, product_id: str) -> Product:
        product = next((p for p in self.products if p.product_id == product_id), None)
        if not product:
            raise ProductNotFoundError(f"Продукт с ID {product_id} не найден.")
        return product

    def has_certificate_for_current_stage(self, product_id: str) -> bool:
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
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError:
            return False
        
        if self.has_certificate_for_current_stage(product_id) and product.current_stage < len(product.PRODUCTION_STAGES) - 1:
            product.current_stage += 1
            return True
        return False

    def is_production_complete(self, product_id: str) -> bool:
        try:
            product = self.get_product(product_id)
            return product.current_stage >= len(product.PRODUCTION_STAGES)
        except ProductNotFoundError:
            return True  

    def add_quality_check(self, product_id: str, stage: str, result: dict) -> None:
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
        try:
            product = self.get_product(product_id)
            product.certificates.append(certificate)
        except ProductNotFoundError:
            pass

    def check_compliance(self, product_id: str, standard: QualityStandard) -> Tuple[bool, List[str]]:
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
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return False
        try:
            self.check_compliance(product_id, standard)
        except QualityCheckFailedError as e:
            print(f"\nОшибка: {e}")
            return False
        
        current_stage = product.get_current_stage()
        existing_cert = next(
            (cert for cert in product.certificates 
             if cert.stage == current_stage and cert.is_valid()), 
            None
        )
        
        if existing_cert:
            raise CertificateAlreadyExistsError(f"Продукт {product_id} уже имеет действующий сертификат для этапа {current_stage}.")
        certificate = Certificate(product_id, standard, current_stage)
        self.add_certificate(product_id, certificate)
        print(f"Сертификат успешно выдан для продукта {product_id} на этапе {current_stage}.")
        return True

    def improve_product(self, product_id: str, standard: QualityStandard) -> List[str]:
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return [f"Продукт с ID {product_id} не найден."]
        
        try:
            self.check_compliance(product_id, standard)
            return []
        except QualityCheckFailedError:
            _, failed_criteria = self._check_compliance_without_exception(product_id, standard)
            for criterion in failed_criteria:
                old_value = product.attributes[criterion]
                new_value = standard.criteria[criterion]
                product.update_attribute(criterion, new_value)
                print(f"  {criterion}: улучшено с '{old_value}' на '{new_value}'")
            return failed_criteria

    def _check_compliance_without_exception(self, product_id: str, standard: QualityStandard) -> Tuple[bool, List[str]]:
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
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            print(f"\nОшибка: {e}")
            return
        
        print(f"\nЗапуск производства для продукта {product_id}...")

        current_stage = product.get_current_stage()
        print(f"Текущий этап производства: {current_stage}")
        
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
        try:
            product = self.get_product(product_id)
            review = Review(product_id, author, comment, rating)
            product.add_review(review)
            return True
        except (ProductNotFoundError, InvalidReviewRatingError) as e:
            print(f"\nОшибка: {e}")
            return False

    def analyze_reviews(self, product_id: str) -> Tuple[Optional[float], List[str]]:
        try:
            product = self.get_product(product_id)
        except ProductNotFoundError as e:
            return None, [str(e)]
        
        if not product.reviews:
            return None, []
        avg_rating = sum(review.rating for review in product.reviews) / len(product.reviews)
        
        recommendations = []
        if avg_rating < 4:
            recommendations.append("Продукт требует улучшений: средний рейтинг ниже 4.")
        
        return avg_rating, recommendations

    def save_state(self, filename: str = "system_state.json") -> None:
        state = {
            "products": [],
            "next_product_id_counter": Product._id_counter,
            "system_metadata": {
                "saved_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        for product in self.products:
            product_data = {
                "product_id": product.product_id,
                "name": product.name,
                "attributes": product.attributes.copy(),
                "status": product.status,
                "current_stage": product.current_stage,
                "quality_checks": [],
                "reviews": [],
                "certificates": []
            }
            
            for check in product.quality_checks:
                check_data = {
                    "stage": check["stage"],
                    "result": check["result"],
                    "timestamp": check["timestamp"].isoformat() if hasattr(check["timestamp"], "isoformat") else str(check["timestamp"])
                }
                product_data["quality_checks"].append(check_data)
            
            for review in product.reviews:
                review_data = {
                    "author": review.author,
                    "comment": review.comment,
                    "rating": review.rating,
                    "date": review.date.isoformat()
                }
                product_data["reviews"].append(review_data)
            
            for certificate in product.certificates:
                certificate_data = {
                    "standard_name": certificate.standard.standard_name,
                    "stage": certificate.stage,
                    "issue_date": certificate.issue_date.isoformat(),
                    "expiration_date": certificate.expiration_date.isoformat()
                }
                product_data["certificates"].append(certificate_data)
            
            state["products"].append(product_data)
     
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
        
        print(f"Состояние системы сохранено в файл {filename}")

    def load_state(self, filename: str = "system_state.json") -> bool:
       
        if not os.path.exists(filename):
            print(f"Файл состояния {filename} не найден.")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.products = []
            Product._id_counter = 1 
            
            for product_data in state["products"]:
                product = Product(product_data["name"])
                product.product_id = product_data["product_id"]
                product.attributes = product_data["attributes"]
                product.status = product_data["status"]
                product.current_stage = product_data["current_stage"]
                
                for check_data in product_data["quality_checks"]:
                    try:
                        timestamp = datetime.fromisoformat(check_data["timestamp"])
                    except:
                        timestamp = datetime.now()
                    
                    product.quality_checks.append({
                        "stage": check_data["stage"],
                        "result": check_data["result"],
                        "timestamp": timestamp
                    })
                
                for review_data in product_data["reviews"]:
                    review = Review(
                        product_id=product.product_id,
                        author=review_data["author"],
                        comment=review_data["comment"],
                        rating=review_data["rating"]
                    )
                    review.date = datetime.fromisoformat(review_data["date"])
                    product.reviews.append(review)
                
                for cert_data in product_data["certificates"]:
                    standard = None
                    if cert_data["standard_name"] == "ГОСТ СТ-1":
                        standard = GOSTStandard()
                    elif cert_data["standard_name"] == "Собственный стандарт пекарни":
                        standard = BakeryEnterpriseStandard()
                    elif cert_data["standard_name"] == "Органическая выпечка":
                        standard = OrganicBakeryStandard()
                    
                    if standard:
                       
                        certificate = Certificate(
                            product_id=product.product_id,
                            standard=standard,
                            stage=cert_data["stage"]
                        )
                        certificate.issue_date = date.fromisoformat(cert_data["issue_date"])
                        certificate.expiration_date = date.fromisoformat(cert_data["expiration_date"])
                        product.certificates.append(certificate)
                
                self.products.append(product)
            
            if "next_product_id_counter" in state:
                Product._id_counter = state["next_product_id_counter"]
            
            print(f"Состояние системы успешно загружено из файла {filename}")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке состояния: {e}")
            return False