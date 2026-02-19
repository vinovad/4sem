from .domain_errors import UnknownQualityStandardError

class QualityStandard:
    def __init__(self, standard_name: str, criteria: dict) -> None:
        self.standard_name: str = standard_name
        self.criteria: dict = criteria  # Требуемые значения атрибутов


class GOSTStandard(QualityStandard):
    def __init__(self) -> None:
        criteria = {
            "defects": "none",
            "texture": "good",
            "smell": "good",
            "taste": "good"
        }
        super().__init__("ГОСТ СТ-1", criteria)


class BakeryEnterpriseStandard(QualityStandard):
    def __init__(self) -> None:
        criteria = {
            "defects": "none",
            "texture": "excellent",
            "smell": "excellent",
            "taste": "excellent"
        }
        super().__init__("Собственный стандарт пекарни", criteria)


class OrganicBakeryStandard(QualityStandard):
    def __init__(self) -> None:
        criteria = {
            "defects": "none",
            "texture": "good",
            "smell": "good",
            "taste": "excellent"
        }
        super().__init__("Органическая выпечка", criteria)