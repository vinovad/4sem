"""
main.py - точка входа в приложение

Запускает приложение "Ветеринарная клиника"
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import PetDatabase, XMLHandler
from controller import AppController
from view import MainWindow
import config

def main():
    """Запускает приложение"""
    # Создаем контроллер без окна
    controller = AppController(None)
    
    # Создаем главное окно без контроллера
    app = MainWindow()
    
    # Устанавливаем контроллер в главное окно
    app.set_controller(controller)
    
    # Устанавливаем окно в контроллер и завершаем инициализацию
    controller.view = app
    
    # Загружаем демо-данные и обновляем интерфейс
    controller.load_demo_data()
    
    # Запускаем цикл обработки событий
    app.mainloop()
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Приложение не может быть запущено:\n{str(e)}")
        sys.exit(1)
