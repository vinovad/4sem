"""
__init__.py - инициализация пакета controller

Этот файл позволяет импортировать классы напрямую из пакета controller:
from controller import AppController
"""

from .app_controller import AppController

__all__ = ['AppController']