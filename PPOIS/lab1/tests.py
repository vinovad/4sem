import pytest
from datetime import datetime, timedelta
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
    PackagingStage
)
from domain.quality_controller import QualityController
from unittest.mock import patch

def test_product_creation():
    #Проверка базового создания продукта#
    product = Product("Хлеб")
    
    assert product.name == "Хлеб"
    assert product.product_id == "1" or product.product_id.isdigit()  # ID теперь просто число
    
    # Проверка начальных атрибутов
    assert product.attributes["defects"] == "have"
    assert product.attributes["texture"] == "poor"
    assert product.attributes["smell"] == "bad"
    assert product.attributes["taste"] == "poor"
    
    # Проверка начального статуса и этапа
    assert product.status == "production"
    assert product.get_current_stage() == "dough"
    assert product.current_stage == 0

def test_product_id_uniqueness():
    #Проверка уникальности ID продуктов#
    product1 = Product("Хлеб")
    product2 = Product("Торт")
    
    assert product1.product_id != product2.product_id

def test_update_attribute():
    #Проверка обновления атрибутов качества#
    product = Product("Хлеб")
    
    # Обновляем атрибут
    product.update_attribute("defects", "none")
    assert product.attributes["defects"] == "none"
    
    # Попытка обновить несуществующий атрибут
    with pytest.raises(ValueError):
        product.update_attribute("invalid_attribute", "value")

def test_add_review():
    #Проверка добавления отзывов#
    product = Product("Хлеб")
    assert len(product.reviews) == 0
    
    # Добавляем отзыв
    review = Review(product.product_id, "Иван", "Хороший хлеб", 4)
    product.add_review(review)
    
    assert len(product.reviews) == 1
    assert product.reviews[0] == review

def test_certificate_validity():
    #Проверка валидности сертификата#
    product_id = "1"  # ID теперь просто число
    standard = GOSTStandard()
    stage = "dough"
    
    # Создаем действительный сертификат
    valid_certificate = Certificate(product_id, standard, stage)
    assert valid_certificate.is_valid() is True
    
    # Создаем сертификат и проверяем его валидность через год
    future_date = datetime.now() + timedelta(days=400)
    with patch('domain.certificate.datetime') as mock_datetime:
        mock_datetime.now.return_value = future_date
        mock_datetime.now.date.return_value = future_date.date()
        
        # Сертификат, созданный сейчас, должен быть невалидным через 400 дней
        assert valid_certificate.is_valid() is False

def test_gost_standard():
    #Проверка стандарта ГОСТ#
    standard = GOSTStandard()
    
    assert standard.standard_name == "ГОСТ СТ-1"
    assert standard.criteria == {
        "defects": "none",
        "texture": "good",
        "smell": "good",
        "taste": "good"
    }

def test_dough_stage():
    #Проверка этапа замеса теста#
    dough_stage = DoughStage()
    product = Product("Хлеб")
    
    # Продукт не соответствует требованиям
    assert dough_stage.check(product) == "Стадия замеса теста не пройдена."
    
    # Улучшаем продукт для прохождения этапа
    product.update_attribute("defects", "none")
    assert dough_stage.check(product) == "Стадия замеса теста пройдена."

def test_baking_stage():
    #Проверка этапа выпечки#
    baking_stage = BakingStage()
    product = Product("Хлеб")
    
    # Продукт не соответствует требованиям
    assert baking_stage.check(product) == "Стадия выпечки не пройдена."
    
    # Улучшаем продукт для прохождения этапа
    product.update_attribute("texture", "good")
    assert baking_stage.check(product) == "Стадия выпечки пройдена."

def test_cooling_stage():
    #Проверка этапа охлаждения#
    cooling_stage = CoolingStage()
    product = Product("Хлеб")
    
    # Продукт не соответствует требованиям
    assert cooling_stage.check(product) == "Стадия охлаждения не пройдена."
    
    # Улучшаем продукт для прохождения этапа
    product.update_attribute("smell", "good")
    assert cooling_stage.check(product) == "Стадия охлаждения пройдена."

def test_packaging_stage():
    #Проверка этапа упаковки#
    packaging_stage = PackagingStage()
    product = Product("Хлеб")
    
    # Продукт не соответствует требованиям
    assert packaging_stage.check(product) == "Стадия упаковки не пройдена."
    
    # Улучшаем продукт для прохождения этапа
    product.update_attribute("taste", "good")
    assert packaging_stage.check(product) == "Стадия упаковки пройдена."

def test_check_compliance():
    #Проверка соответствия продукта стандарту#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    gost_standard = GOSTStandard()
    
    # Проверка несоответствия
    is_compliant, failed_criteria = controller.check_compliance(product.product_id, gost_standard)
    assert is_compliant is False
    assert set(failed_criteria) == {"defects", "texture", "smell", "taste"}
    
    # Улучшаем продукт
    product.update_attribute("defects", "none")
    product.update_attribute("texture", "good")
    product.update_attribute("smell", "good")
    product.update_attribute("taste", "good")
    
    # Проверка соответствия
    is_compliant, failed_criteria = controller.check_compliance(product.product_id, gost_standard)
    assert is_compliant is True
    assert len(failed_criteria) == 0

def test_improve_product():
    #Проверка улучшения продукта#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    gost_standard = GOSTStandard()
    
    # Проверяем улучшение
    improved_criteria = controller.improve_product(product.product_id, gost_standard)
    assert len(improved_criteria) == 4
    assert set(improved_criteria) == {"defects", "texture", "smell", "taste"}
    
    # Проверяем, что атрибуты обновились
    for criterion in gost_standard.criteria:
        assert product.attributes[criterion] == gost_standard.criteria[criterion]
    
    # Проверяем улучшение уже соответствующего продукта
    improved_criteria = controller.improve_product(product.product_id, gost_standard)
    assert len(improved_criteria) == 0

def test_certify_product():
    #Проверка выдачи сертификата#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    gost_standard = GOSTStandard()
    
    # Попытка выдать сертификат без соответствия стандарту
    success = controller.certify_product(product.product_id, gost_standard)
    assert success is False
    assert len(product.certificates) == 0
    
    # Улучшаем продукт
    controller.improve_product(product.product_id, gost_standard)
    
    # Выдаем сертификат
    success = controller.certify_product(product.product_id, gost_standard)
    assert success is True
    assert len(product.certificates) == 1
    assert product.certificates[0].standard == gost_standard
    assert product.certificates[0].stage == "dough"
    
    # Попытка выдать сертификат повторно
    success = controller.certify_product(product.product_id, gost_standard)
    assert success is False
    assert len(product.certificates) == 1  # Количество не изменилось

def test_run_production():
    #Проверка запуска производства#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Проверяем начальный этап
    assert product.get_current_stage() == "dough"
    
    # Улучшаем и сертифицируем для первого этапа
    gost_standard = GOSTStandard()
    controller.improve_product(product.product_id, gost_standard)
    controller.certify_product(product.product_id, gost_standard)
    
    # Переходим к следующему этапу
    assert controller.has_certificate_for_current_stage(product.product_id) is True
    controller.run_production(product.product_id)
    assert product.get_current_stage() == "baking"
    
    # Сертифицируем для второго этапа
    controller.certify_product(product.product_id, gost_standard)
    controller.run_production(product.product_id)
    assert product.get_current_stage() == "cooling"
    
    # Сертифицируем для третьего этапа
    controller.certify_product(product.product_id, gost_standard)
    controller.run_production(product.product_id)
    assert product.get_current_stage() == "packaging"

def test_add_review_controller():
    #Проверка добавления отзыва через контроллер#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Добавляем отзыв
    success = controller.add_review(
        product.product_id,
        "Иван Петров",
        "Хороший хлеб!",
        4
    )
    
    assert success is True
    assert len(product.reviews) == 1
    assert product.reviews[0].author == "Иван Петров"
    assert product.reviews[0].rating == 4

def test_analyze_reviews():
    #Проверка анализа отзывов#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Добавляем отзывы
    controller.add_review(product.product_id, "Иван", "Хороший хлеб", 4)
    controller.add_review(product.product_id, "Мария", "Вкусный хлеб", 5)
    
    # Анализируем отзывы
    avg_rating, recommendations = controller.analyze_reviews(product.product_id)
    
    # Проверяем средний рейтинг
    assert avg_rating == 4.5
    
    # Проверяем рекомендации
    assert len(recommendations) == 0

def test_analyze_reviews_negative():
    #Проверка анализа отзывов с негативной оценкой#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Добавляем отзывы
    controller.add_review(product.product_id, "Иван", "Хороший хлеб", 4)
    controller.add_review(product.product_id, "Мария", "Вкусный хлеб", 5)
    controller.add_review(product.product_id, "Сергей", "Плохой хлеб", 2)
    
    # Анализируем отзывы
    avg_rating, recommendations = controller.analyze_reviews(product.product_id)
    
    # Проверяем средний рейтинг
    assert avg_rating == (4 + 5 + 2) / 3
    assert 3.66 <= avg_rating <= 3.67
    
    # Проверяем рекомендации
    assert len(recommendations) == 1
    assert "ниже 4" in recommendations[0]

def test_review_invalid_rating():
    #Проверка создания отзыва с некорректным рейтингом#
    product_id = "1"
    author = "Иван Петров"
    comment = "Хороший хлеб"
    
    # Рейтинг ниже допустимого
    with pytest.raises(ValueError, match="Рейтинг должен быть от 1 до 5"):
        Review(product_id, author, comment, 0)
    
    # Рейтинг выше допустимого
    with pytest.raises(ValueError, match="Рейтинг должен быть от 1 до 5"):
        Review(product_id, author, comment, 6)

def test_get_product():
    #Проверка получения продукта по ID#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Получаем продукт по ID
    retrieved_product = controller.get_product(product.product_id)
    assert retrieved_product == product
    
    # Проверка получения несуществующего продукта
    assert controller.get_product("999") is None

def test_has_certificate_for_current_stage():
    #Проверка наличия сертификата для текущего этапа#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Проверка отсутствия сертификата
    assert controller.has_certificate_for_current_stage(product.product_id) is False
    
    # Улучшаем и сертифицируем продукт
    gost_standard = GOSTStandard()
    controller.improve_product(product.product_id, gost_standard)
    controller.certify_product(product.product_id, gost_standard)
    
    # Проверка наличия сертификата
    assert controller.has_certificate_for_current_stage(product.product_id) is True

def test_advance_stage():
    #Проверка перехода на следующий этап#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Пытаемся перейти без сертификата
    assert controller.advance_stage(product.product_id) is False
    assert product.get_current_stage() == "dough"
    
    # Улучшаем и сертифицируем
    gost_standard = GOSTStandard()
    controller.improve_product(product.product_id, gost_standard)
    controller.certify_product(product.product_id, gost_standard)
    
    # Переходим на следующий этап
    assert controller.advance_stage(product.product_id) is True
    assert product.get_current_stage() == "baking"

def test_add_quality_check():
    #Проверка добавления проверки качества#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Добавляем проверку качества
    stage = "dough"
    result = {"standard": "ГОСТ", "passed": True}
    controller.add_quality_check(product.product_id, stage, result)
    
    # Проверяем, что проверка добавлена
    assert len(product.quality_checks) == 1
    assert product.quality_checks[0]["stage"] == stage
    assert product.quality_checks[0]["result"] == result
    assert "timestamp" in product.quality_checks[0]

def test_add_certificate():
    #Проверка добавления сертификата через контроллер#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    certificate = Certificate(product.product_id, GOSTStandard(), "dough")
    
    # Добавляем сертификат
    controller.add_certificate(product.product_id, certificate)
    
    assert len(product.certificates) == 1
    assert product.certificates[0] == certificate

def test_is_production_complete():
    #Проверка завершения производства#
    controller = QualityController()
    product = controller.add_product("Хлеб")
    
    # Производство не завершено
    assert controller.is_production_complete(product.product_id) is False
    
    # Переводим на последний этап
    product.current_stage = 3
    
    # Производство все еще не завершено (нужно пройти все этапы)
    assert controller.is_production_complete(product.product_id) is False
    
    # Переводим за пределы этапов
    product.current_stage = 4
    
    # Производство завершено
    assert controller.is_production_complete(product.product_id) is True

def test_review_str():
    #Проверка строкового представления отзыва#
    review = Review("1", "Иван", "Хороший хлеб", 5)
    str_review = str(review)
    
    assert "Review" in str_review
    assert "ProductID=1" in str_review
    assert "Author=Иван" in str_review
    assert "Rating=5/5" in str_review

def test_certificate_str():
    #Проверка строкового представления сертификата#
    certificate = Certificate("1", GOSTStandard(), "dough")
    str_cert = str(certificate)
    
    assert "Certificate" in str_cert
    assert "Product=1" in str_cert
    assert "Stage=dough" in str_cert
    assert "Standard=ГОСТ СТ-1" in str_cert

def test_product_str():
    #Проверка строкового представления продукта#
    product = Product("Хлеб")
    str_product = str(product)
    
    assert "Product" in str_product
    assert "Name=Хлеб" in str_product
    assert "Status=production" in str_product
    assert "Stage=dough" in str_product