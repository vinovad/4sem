"""
__init__.py - инициализация пакета model

Этот файл позволяет импортировать классы напрямую из пакета model:
from model import Pet, PetDatabase, XMLHandler
"""

from .pet import Pet
from .database import PetDatabase
from .xml_handler import XMLHandler

__all__ = ['Pet', 'PetDatabase', 'XMLHandler']