from datetime import datetime
from typing import TYPE_CHECKING
from .domain_errors import InvalidReviewRatingError

if TYPE_CHECKING:
    from .product import Product


class Review:
    def __init__(self, product_id: str, author: str, comment: str, rating: int) -> None:
        if not (1 <= rating <= 5):
            raise InvalidReviewRatingError("Рейтинг должен быть от 1 до 5")
        
        self.product_id: str = product_id
        self.author: str = author
        self.comment: str = comment
        self.rating: int = rating
        self.date: datetime = datetime.now()
    
    def __str__(self) -> str:
        """Строковое представление отзыва"""
        return (
            f"Review(ProductID={self.product_id}, Author={self.author}, "
            f"Rating={self.rating}/5, Date={self.date.strftime('%Y-%m-%d')})"
        )