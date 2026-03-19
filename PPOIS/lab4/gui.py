import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain.quality_controller import QualityController
from gui.controllers.main_controller import MainController
from gui.views.main_window import MainWindow


def main():
    root = tk.Tk()
    model = QualityController()
    try:
        model.load_state()
    except Exception as e:
        messagebox.showwarning("Предупреждение",
                               f"Не удалось загрузить сохраненное состояние: {e}")

    #  контроллер
    controller = MainController(model)
    app = MainWindow(root, controller)
    controller.set_view(app)  # <-- Вот этот вызов устанавливает связь
    # главный цикл
    root.mainloop()


if __name__ == "__main__":
    main()
