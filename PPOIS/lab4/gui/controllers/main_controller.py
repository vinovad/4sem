from tkinter import messagebox
from domain import (
    QualityController,
    GOSTStandard,
    BakeryEnterpriseStandard,
    OrganicBakeryStandard
)
from domain.domain_errors import (
    ProductNotFoundError,
    UnknownQualityStandardError,
    QualityCheckFailedError,
    CertificateAlreadyExistsError,
    InvalidReviewRatingError
)


class MainController:
    def __init__(self, model: QualityController):
        self.model = model
        self.view = None 
        
    def set_view(self, view):
        self.view = view

    def get_products(self):
        return self.model.products

    def add_product(self, name: str):
        try:
            product = self.model.add_product(name)
            if self.view:
                self.view.show_info(f"Продукт '{name}' с ID {product.product_id} успешно добавлен")
                self.view.refresh_product_list()
            return product
        except Exception as e:
            if self.view:
                self.view.show_error(f"Ошибка при добавлении продукта: {e}")
            return None

    def get_product(self, product_id: str):
        try:
            return self.model.get_product(product_id)
        except ProductNotFoundError as e:
            if self.view:
                self.view.show_error(str(e))
            return None

    def get_standards(self):
        return [
            {"id": "1", "name": "ГОСТ СТ-1", "class": GOSTStandard},
            {"id": "2", "name": "Собственный стандарт пекарни", "class": BakeryEnterpriseStandard},
            {"id": "3", "name": "Органическая выпечка", "class": OrganicBakeryStandard}
        ]

    def get_standard_by_name(self, name: str):
        try:
            return self.model.get_standard(name)
        except UnknownQualityStandardError as e:
            if self.view:
                self.view.show_error(str(e))
            return None

    def check_compliance(self, product_id: str, standard_name: str):
        try:
            standard = self.model.get_standard(standard_name)
            product = self.model.get_product(product_id)

            try:
                self.model.check_compliance(product_id, standard)
                return True, f"Продукт соответствует стандарту '{standard_name}' на этапе {product.get_current_stage()}"
            except QualityCheckFailedError as e:
                return False, str(e)

        except (ProductNotFoundError, UnknownQualityStandardError) as e:
            return False, str(e)

    def improve_product(self, product_id: str, standard_name: str):
        try:
            standard = self.model.get_standard(standard_name)
            product = self.model.get_product(product_id)

            try:
                self.model.check_compliance(product_id, standard)
                return True, f"Продукт уже соответствует стандарту '{standard_name}'", []
            except QualityCheckFailedError:
                improved_criteria = self.model.improve_product(product_id, standard)
                return True, f"Продукт улучшен до стандарта '{standard_name}'", improved_criteria

        except (ProductNotFoundError, UnknownQualityStandardError) as e:
            return False, str(e), []

    def certify_product(self, product_id: str, standard_name: str):
        try:
            standard = self.model.get_standard(standard_name)
            product = self.model.get_product(product_id)

            try:
                success = self.model.certify_product(product_id, standard)
                if success:
                    return True, f"Сертификат успешно выдан для продукта {product_id} на этапе {product.get_current_stage()}"
                else:
                    return False, "Не удалось выдать сертификат"
            except (CertificateAlreadyExistsError, QualityCheckFailedError) as e:
                return False, str(e)

        except (ProductNotFoundError, UnknownQualityStandardError) as e:
            return False, str(e)

    def advance_stage(self, product_id: str):
        try:
            product = self.model.get_product(product_id)
            current_stage = product.get_current_stage()

            if self.model.has_certificate_for_current_stage(product_id):
                if self.model.advance_stage(product_id):
                    new_stage = product.get_current_stage()
                    return True, f"Продукт переведен с этапа '{current_stage}' на этап '{new_stage}'"
                else:
                    if product.current_stage >= len(product.PRODUCTION_STAGES):
                        return True, "Производство продукта завершено!"
                    else:
                        return False, "Не удалось перейти на следующий этап"
            else:
                return False, f"Нет действующего сертификата для этапа '{current_stage}'. Сначала получите сертификат."

        except ProductNotFoundError as e:
            return False, str(e)

    def get_production_status(self, product_id: str):
        try:
            product = self.model.get_product(product_id)
            current_stage = product.get_current_stage()
            has_certificate = self.model.has_certificate_for_current_stage(product_id)

            return {
                "product_id": product_id,
                "product_name": product.name,
                "current_stage": current_stage,
                "has_certificate": has_certificate,
                "is_completed": product.current_stage >= len(product.PRODUCTION_STAGES),
                "attributes": product.attributes,
                "certificates_count": len(product.certificates),
                "reviews_count": len(product.reviews)
            }
        except ProductNotFoundError as e:
            return None

    def add_review(self, product_id: str, author: str, comment: str, rating: int):
        try:
            success = self.model.add_review(product_id, author, comment, rating)
            if success:
                return True, "Отзыв успешно добавлен"
            else:
                return False, "Не удалось добавить отзыв"
        except (ProductNotFoundError, InvalidReviewRatingError) as e:
            return False, str(e)

    def analyze_reviews(self, product_id: str):
        try:
            product = self.model.get_product(product_id)
            avg_rating, recommendations = self.model.analyze_reviews(product_id)

            if avg_rating is None:
                return {
                    "has_reviews": False,
                    "avg_rating": None,
                    "recommendations": []
                }
            else:
                return {
                    "has_reviews": True,
                    "avg_rating": avg_rating,
                    "recommendations": recommendations,
                    "reviews_count": len(product.reviews)
                }
        except ProductNotFoundError as e:
            return {"error": str(e)}

    def save_state(self, filename="system_state.json"):
        try:
            self.model.save_state(filename)
            return True, f"Состояние сохранено в файл {filename}"
        except Exception as e:
            return False, f"Ошибка при сохранении: {e}"

    def load_state(self, filename="system_state.json"):
        try:
            success = self.model.load_state(filename)
            if success:
                return True, f"Состояние загружено из файла {filename}"
            else:
                return False, f"Не удалось загрузить состояние из файла {filename}"
        except Exception as e:
            return False, f"Ошибка при загрузке: {e}"
