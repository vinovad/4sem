from datetime import datetime

class Review:
    def __init__(self, product_id: str, author: str, comment: str, rating: int) -> None:
        if not (1 <= rating <= 5):
            raise ValueError("Рейтинг должен быть от 1 до 5")
        
        self.product_id = product_id
        self.author = author
        self.comment = comment
        self.rating = rating
        self.date = datetime.now()
    
    def __str__(self) -> str:
        return (f"Review(ProductID={self.product_id}, Author={self.author}, "
                f"Rating={self.rating}/5, Date={self.date.strftime('%Y-%m-%d')})")