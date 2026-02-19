import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from domain.product import Product
from domain.quality_standard import (
    GOSTStandard, 
    BakeryEnterpriseStandard, 
    OrganicBakeryStandard
)
from domain.review import Review
from domain.certificate import Certificate
from domain.production_stages import (
    DoughStage,
    BakingStage,
    CoolingStage,
    PackagingStage,
    ProductionStage
)
from domain.quality_controller import QualityController
from domain.domain_errors import (
    ProductNotFoundError,
    UnknownQualityStandardError,
    QualityCheckFailedError,
    CertificateAlreadyExistsError,
    InvalidProductAttributeError,
    InvalidReviewRatingError
)

# ==================== ТЕСТЫ PRODUCT ====================

def test_product_creation():
    """Проверка создания продукта"""
    product = Product("Хлеб")
    assert product.name == "Хлеб"
    assert product.product_id.isdigit()
    assert product.attributes == {
        "defects": "have",
        "texture": "poor",
        "smell": "bad",
        "taste": "poor"
    }
    assert product.status == "production"
    assert product.current_stage == 0
    assert product.get_current_stage() == "dough"
    assert len(product.reviews) == 0
    assert len(product.certificates) == 0
    assert len(product.quality_checks) == 0


def test_product_id_uniqueness():
    """Проверка уникальности ID продуктов"""
    product1 = Product("Хлеб")
    product2 = Product("Торт")
    assert product1.product_id != product2.product_id


def test_update_attribute():
    """Проверка обновления атрибутов"""
    product = Product("Хлеб")
    product.update_attribute("defects", "none")
    assert product.attributes["defects"] == "none"
    
    with pytest.raises(InvalidProductAttributeError):
        product.update_attribute("invalid", "value")


def test_add_review_to_product():
    """Проверка добавления отзыва к продукту"""
    product = Product("Хлеб")
    review = Review(product.product_id, "Иван", "Хороший хлеб", 5)
    product.add_review(review)
    assert len(product.reviews) == 1
    assert product.reviews[0] == review


def test_product_str():
    """Проверка строкового представления продукта"""
    product = Product("Хлеб")
    str_repr = str(product)
    assert "Product(ID=" in str_repr
    assert "Name=Хлеб" in str_repr
    assert "Stage=dough" in str_repr


def test_product_get_current_stage():
    """Проверка получения текущего этапа"""
    product = Product("Хлеб")
    assert product.get_current_stage() == "dough"
    product.current_stage = 1
    assert product.get_current_stage() == "baking"
    product.current_stage = 2
    assert product.get_current_stage() == "cooling"
    product.current_stage = 3
    assert product.get_current_stage() == "packaging"
    product.current_stage = 4
    assert product.get_current_stage() == "completed"


# ==================== ТЕСТЫ REVIEW ====================

def test_review_creation():
    """Проверка создания отзыва"""
    review = Review("1", "Иван", "Отличный хлеб!", 5)
    assert review.product_id == "1"
    assert review.author == "Иван"
    assert review.comment == "Отличный хлеб!"
    assert review.rating == 5
    assert isinstance(review.date, datetime)


def test_review_invalid_rating():
    """Проверка создания отзыва с некорректным рейтингом"""
    with pytest.raises(InvalidReviewRatingError, match="Рейтинг должен быть от 1 до 5"):
        Review("1", "Иван", "Комментарий", 0)
    with pytest.raises(InvalidReviewRatingError, match="Рейтинг должен быть от 1 до 5"):
        Review("1", "Иван", "Комментарий", 6)


def test_review_str():
    """Проверка строкового представления отзыва"""
    review = Review("1", "Иван", "Комментарий", 5)
    str_repr = str(review)
    assert "Review(ProductID=1" in str_repr
    assert "Author=Иван" in str_repr
    assert "Rating=5/5" in str_repr


# ==================== ТЕСТЫ CERTIFICATE ====================

def test_certificate_creation():
    """Проверка создания сертификата"""
    standard = GOSTStandard()
    cert = Certificate("1", standard, "dough")
    assert cert.product_id == "1"
    assert cert.standard == standard
    assert cert.stage == "dough"
    assert cert.certificate_id.startswith("CERT-1-")
    assert cert.issue_date == datetime.now().date()
    assert cert.expiration_date == datetime.now().date() + timedelta(days=365)


def test_certificate_validity():
    """Проверка валидности сертификата"""
    cert = Certificate("1", GOSTStandard(), "dough")
    assert cert.is_valid() is True
    
    # Проверка через 366 дней
    future_date = datetime.now() + timedelta(days=366)
    with patch('domain.certificate.datetime') as mock_datetime:
        mock_datetime.now.return_value = future_date
        mock_datetime.now.date.return_value = future_date.date()
        assert cert.is_valid() is False


def test_certificate_str():
    """Проверка строкового представления сертификата"""
    cert = Certificate("1", GOSTStandard(), "dough")
    str_repr = str(cert)
    assert "Certificate(ID=" in str_repr
    assert "Product=1" in str_repr
    assert "Stage=dough" in str_repr
    assert "Standard=ГОСТ СТ-1" in str_repr


# ==================== ТЕСТЫ PRODUCTION STAGES ====================

def test_dough_stage():
    """Проверка этапа замеса теста"""
    stage = DoughStage()
    product = Product("Хлеб")
    assert stage.check(product) == "Стадия замеса теста не пройдена."
    product.update_attribute("defects", "none")
    assert stage.check(product) == "Стадия замеса теста пройдена."


def test_baking_stage():
    """Проверка этапа выпечки"""
    stage = BakingStage()
    product = Product("Хлеб")
    assert stage.check(product) == "Стадия выпечки не пройдена."
    product.update_attribute("texture", "good")
    assert stage.check(product) == "Стадия выпечки пройдена."
    product.update_attribute("texture", "excellent")
    assert stage.check(product) == "Стадия выпечки пройдена."


def test_cooling_stage():
    """Проверка этапа охлаждения"""
    stage = CoolingStage()
    product = Product("Хлеб")
    assert stage.check(product) == "Стадия охлаждения не пройдена."
    product.update_attribute("smell", "good")
    assert stage.check(product) == "Стадия охлаждения пройдена."
    product.update_attribute("smell", "excellent")
    assert stage.check(product) == "Стадия охлаждения пройдена."


def test_packaging_stage():
    """Проверка этапа упаковки"""
    stage = PackagingStage()
    product = Product("Хлеб")
    assert stage.check(product) == "Стадия упаковки не пройдена."
    product.update_attribute("taste", "good")
    assert stage.check(product) == "Стадия упаковки пройдена."
    product.update_attribute("taste", "excellent")
    assert stage.check(product) == "Стадия упаковки пройдена."


def test_production_stage_abstract():
    """Проверка абстрактного метода"""
    stage = ProductionStage("test")
    with pytest.raises(NotImplementedError):
        stage.check(None)


# ==================== ТЕСТЫ QUALITY STANDARDS ====================

def test_gost_standard():
    """Проверка стандарта ГОСТ"""
    standard = GOSTStandard()
    assert standard.standard_name == "ГОСТ СТ-1"
    assert standard.criteria == {
        "defects": "none",
        "texture": "good",
        "smell": "good",
        "taste": "good"
    }


def test_bakery_standard():
    """Проверка стандарта пекарни"""
    standard = BakeryEnterpriseStandard()
    assert standard.standard_name == "Собственный стандарт пекарни"
    assert standard.criteria == {
        "defects": "none",
        "texture": "excellent",
        "smell": "excellent",
        "taste": "excellent"
    }


def test_organic_standard():
    """Проверка органического стандарта"""
    standard = OrganicBakeryStandard()
    assert standard.standard_name == "Органическая выпечка"
    assert standard.criteria == {
        "defects": "none",
        "texture": "good",
        "smell": "good",
        "taste": "excellent"
    }


# ==================== ТЕСТЫ QUALITY CONTROLLER ====================

def test_add_product():
    """Проверка добавления продукта"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    assert product in controller.products
    assert len(controller.products) == 1


def test_show_products():
    """Проверка отображения продуктов"""
    controller = QualityController()
    controller.add_product("Хлеб")
    controller.add_product("Торт")
    products = controller.show_products()
    assert len(products) == 2
    assert products[0][1] == "Хлеб"
    assert products[1][1] == "Торт"


def test_get_product():
    """Проверка получения продукта по ID"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    assert controller.get_product(product.product_id) == product
    with pytest.raises(ProductNotFoundError):
        controller.get_product("999")


def test_has_certificate_for_current_stage():
    """Проверка наличия сертификата"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    assert controller.has_certificate_for_current_stage(product.product_id) is False
    
    cert = Certificate(product.product_id, GOSTStandard(), "dough")
    product.certificates.append(cert)
    assert controller.has_certificate_for_current_stage(product.product_id) is True


def test_advance_stage():
    """Проверка перехода на следующий этап"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Без сертификата
    assert controller.advance_stage(product.product_id) is False
    assert product.current_stage == 0
    
    # С сертификатом
    cert = Certificate(product.product_id, GOSTStandard(), "dough")
    product.certificates.append(cert)
    assert controller.advance_stage(product.product_id) is True
    assert product.current_stage == 1
    assert product.get_current_stage() == "baking"


def test_is_production_complete():
    """Проверка завершения производства"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    assert controller.is_production_complete(product.product_id) is False
    
    product.current_stage = 4
    assert controller.is_production_complete(product.product_id) is True
    
    # Несуществующий продукт
    assert controller.is_production_complete("999") is True


def test_add_quality_check():
    """Проверка добавления проверки качества"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    result = {"standard": "ГОСТ", "passed": True}
    controller.add_quality_check(product.product_id, "dough", result)
    
    assert len(product.quality_checks) == 1
    assert product.quality_checks[0]["stage"] == "dough"
    assert product.quality_checks[0]["result"] == result


def test_add_certificate():
    """Проверка добавления сертификата"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    cert = Certificate(product.product_id, GOSTStandard(), "dough")
    
    controller.add_certificate(product.product_id, cert)
    assert len(product.certificates) == 1
    assert product.certificates[0] == cert


def test_check_compliance_success():
    """Проверка успешного соответствия стандарту"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    product.update_attribute("defects", "none")
    product.update_attribute("texture", "good")
    product.update_attribute("smell", "good")
    product.update_attribute("taste", "good")
    
    result, failed = controller.check_compliance(product.product_id, GOSTStandard())
    assert result is True
    assert len(failed) == 0


def test_check_compliance_failure():
    """Проверка несоответствия стандарту"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    with pytest.raises(QualityCheckFailedError):
        controller.check_compliance(product.product_id, GOSTStandard())


def test_check_compliance_product_not_found():
    """Проверка соответствия для несуществующего продукта"""
    controller = QualityController()
    with pytest.raises(ProductNotFoundError):
        controller.check_compliance("999", GOSTStandard())


def test_certify_product_success():
    """Проверка успешной сертификации"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Улучшаем продукт
    for attr, value in GOSTStandard().criteria.items():
        product.update_attribute(attr, value)
    
    result = controller.certify_product(product.product_id, GOSTStandard())
    assert result is True
    assert len(product.certificates) == 1


def test_certify_product_failure_no_compliance():
    """Проверка сертификации без соответствия"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    result = controller.certify_product(product.product_id, GOSTStandard())
    assert result is False
    assert len(product.certificates) == 0


def test_certify_product_already_exists():
    """Проверка повторной сертификации"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Улучшаем и сертифицируем
    for attr, value in GOSTStandard().criteria.items():
        product.update_attribute(attr, value)
    controller.certify_product(product.product_id, GOSTStandard())
    
    # Пытаемся сертифицировать повторно
    with pytest.raises(CertificateAlreadyExistsError):
        controller.certify_product(product.product_id, GOSTStandard())


def test_improve_product():
    """Проверка улучшения продукта"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    improved = controller.improve_product(product.product_id, GOSTStandard())
    assert len(improved) == 4
    
    # Проверяем, что атрибуты обновились
    for criterion, value in GOSTStandard().criteria.items():
        assert product.attributes[criterion] == value


def test_improve_product_already_compliant():
    """Проверка улучшения уже соответствующего продукта"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Делаем продукт соответствующим
    for attr, value in GOSTStandard().criteria.items():
        product.update_attribute(attr, value)
    
    improved = controller.improve_product(product.product_id, GOSTStandard())
    assert len(improved) == 0


def test_run_production():
    """Проверка запуска производства"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Улучшаем и сертифицируем
    for attr, value in GOSTStandard().criteria.items():
        product.update_attribute(attr, value)
    controller.certify_product(product.product_id, GOSTStandard())
    
    # Запускаем производство
    controller.run_production(product.product_id)
    assert product.current_stage == 1
    assert product.get_current_stage() == "baking"


def test_add_review_success():
    """Проверка успешного добавления отзыва"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    result = controller.add_review(product.product_id, "Иван", "Отлично", 5)
    assert result is True
    assert len(product.reviews) == 1


def test_add_review_invalid_rating():
    """Проверка добавления отзыва с неверным рейтингом"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    result = controller.add_review(product.product_id, "Иван", "Отлично", 6)
    assert result is False
    assert len(product.reviews) == 0


def test_analyze_reviews():
    """Проверка анализа отзывов"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    controller.add_review(product.product_id, "Иван", "Норм", 4)
    controller.add_review(product.product_id, "Петр", "Отлично", 5)
    
    avg, recs = controller.analyze_reviews(product.product_id)
    assert avg == 4.5
    assert len(recs) == 0


def test_analyze_reviews_low_rating():
    """Проверка анализа низких оценок"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    controller.add_review(product.product_id, "Иван", "Плохо", 2)
    controller.add_review(product.product_id, "Петр", "Так себе", 3)
    
    avg, recs = controller.analyze_reviews(product.product_id)
    assert avg == 2.5
    assert len(recs) == 1
    assert "ниже 4" in recs[0]


def test_analyze_reviews_no_reviews():
    """Проверка анализа без отзывов"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    avg, recs = controller.analyze_reviews(product.product_id)
    assert avg is None
    assert len(recs) == 0


def test_get_standard():
    """Проверка получения стандарта по имени"""
    controller = QualityController()
    
    gost = controller.get_standard("ГОСТ СТ-1")
    assert isinstance(gost, GOSTStandard)
    
    bakery = controller.get_standard("Собственный стандарт пекарни")
    assert isinstance(bakery, BakeryEnterpriseStandard)
    
    organic = controller.get_standard("Органическая выпечка")
    assert isinstance(organic, OrganicBakeryStandard)
    
    with pytest.raises(UnknownQualityStandardError):
        controller.get_standard("Неизвестный")


def test_check_compliance_without_exception():
    """Проверка внутреннего метода без исключений"""
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    is_compliant, failed = controller._check_compliance_without_exception(
        product.product_id, GOSTStandard()
    )
    assert is_compliant is False
    assert len(failed) == 4
