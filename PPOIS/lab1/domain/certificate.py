from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .quality_standard import QualityStandard


class Certificate:
    def __init__(self, product_id: str, standard: 'QualityStandard', stage: str) -> None:
        self.certificate_id: str = f"CERT-{product_id}-{datetime.now().strftime('%Y%m%d')}"
        self.product_id: str = product_id
        self.standard: 'QualityStandard' = standard
        self.stage: str = stage  # Этап производства, для которого выдан сертификат
        self.issue_date: datetime.date = datetime.now().date()
        self.expiration_date: datetime.date = self.issue_date + timedelta(days=365)
    
    def is_valid(self) -> bool:
        """Проверить, действителен ли сертификат"""
        return datetime.now().date() <= self.expiration_date

    def __str__(self) -> str:
        """Строковое представление сертификата"""
        return (
            f"Certificate(ID={self.certificate_id}, Product={self.product_id}, "
            f"Stage={self.stage}, Standard={self.standard.standard_name}, "
            f"Valid until={self.expiration_date})"
        )
