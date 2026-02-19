class ProductError(Exception):
    """Базовый класс для исключений, связанных с продуктами."""
    pass

class ProductNotFoundError(ProductError):
    """Исключение, возникающее при отсутствии продукта с указанным ID."""
    pass

class InvalidProductAttributeError(ProductError):
    """Исключение, возникающее при попытке обновить несуществующий атрибут продукта."""
    pass

class QualityStandardError(Exception):
    """Базовый класс для исключений, связанных со стандартами качества."""
    pass

class UnknownQualityStandardError(QualityStandardError):
    """Исключение, возникающее при попытке использовать неизвестный стандарт качества."""
    pass

class QualityCheckFailedError(QualityStandardError):
    """Исключение, возникающее когда продукт не соответствует стандарту качества."""
    pass

class CertificateError(Exception):
    """Базовый класс для исключений, связанных с сертификатами."""
    pass

class CertificateAlreadyExistsError(CertificateError):
    """Исключение, возникающее при попытке выдать уже существующий сертификат."""
    pass

class ReviewError(Exception):
    """Базовый класс для исключений, связанных с отзывами."""
    pass

class InvalidReviewRatingError(ReviewError):
    """Исключение, возникающее при некорректном рейтинге отзыва."""
    pass