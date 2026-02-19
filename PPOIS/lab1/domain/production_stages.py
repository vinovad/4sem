from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product


class ProductionStage:
    """Базовый класс для этапов производства"""
    
    def __init__(self, stage_name: str) -> None:
        self.stage_name: str = stage_name
    
    def check(self, product: 'Product') -> str:
        """Проверить продукт на данном этапе"""
        raise NotImplementedError("Метод check должен быть реализован в подклассах")


class DoughStage(ProductionStage):
    """Этап замеса теста"""
    
    def __init__(self) -> None:
        super().__init__("dough")
    
    def check(self, product: 'Product') -> str:
        """Проверка качества теста"""
        if product.attributes["defects"] == "none":
            return "Стадия замеса теста пройдена."
        else:
            return "Стадия замеса теста не пройдена."


class BakingStage(ProductionStage):
    """Этап выпечки"""
    
    def __init__(self) -> None:
        super().__init__("baking")
    
    def check(self, product: 'Product') -> str:
        """Проверка качества выпечки"""
        if product.attributes["texture"] == "good" or product.attributes["texture"] == "excellent":
            return "Стадия выпечки пройдена."
        else:
            return "Стадия выпечки не пройдена."


class CoolingStage(ProductionStage):
    """Этап охлаждения"""
    
    def __init__(self) -> None:
        super().__init__("cooling")
    
    def check(self, product: 'Product') -> str:
        """Проверка качества охлаждения"""
        if product.attributes["smell"] == "good" or product.attributes["smell"] == "excellent":
            return "Стадия охлаждения пройдена."
        else:
            return "Стадия охлаждения не пройдена."


class PackagingStage(ProductionStage):
    """Этап упаковки"""
    
    def __init__(self) -> None:
        super().__init__("packaging")
    
    def check(self, product: 'Product') -> str:
        """Проверка качества упаковки"""
        if product.attributes["taste"] == "good" or product.attributes["taste"] == "excellent":
            return "Стадия упаковки пройдена."
        else:
            return "Стадия упаковки не пройдена."
