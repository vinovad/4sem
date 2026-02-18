from domain import (
    QualityController,
    Product,
    GOSTStandard,
    BakeryEnterpriseStandard,
    OrganicBakeryStandard,
    Review
)
from datetime import datetime

def main():
    controller = QualityController()
    
    while True:
        print("\nМеню:")
        print("1. Добавить продукт")
        
        # Показываем опции только если есть продукты
        if controller.products:
            print("2. Список продуктов")
            print("3. Запустить производство (перейти к следующему этапу)")
            print("4. Проверить продукт по стандарту качества")
            print("5. Внести улучшения в продукт")
            print("6. Выдать сертификат продукту")
            print("7. Добавить отзыв")
            print("8. Анализировать отзывы")
            print("9. Выход")
        else:
            print("2. Выход (список продуктов пуст)")
        
        choice = input("\nВыберите действие: ")
        
        if choice == '1':
            name = input("Введите название продукта: ")
            product = controller.add_product(name)
            print(f"\nПродукт с ID {product.product_id} добавлен.")
            print(product)
            
        elif choice == '2' and not controller.products:
            print("\nВыход из программы.")
            break
            
        elif choice == '2' and controller.products:
            products = controller.show_products()
            print("\nСписок продуктов:")
            for product_id, name in products:
                product = controller.get_product(product_id)
                print(f"ID: {product_id}, Название: {name}, Этап: {product.get_current_stage()}")
                    
        elif choice in ['3', '4', '5', '6', '7', '8'] and not controller.products:
            print("\nСписок продуктов пуст. Сначала добавьте продукт (пункт 1).")
                
        elif choice == '3':
            product_id = input("Введите ID продукта для запуска производства: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                controller.run_production(product_id)
                
        elif choice == '4':
            product_id = input("Введите ID продукта для проверки: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                print("\nВыберите стандарт качества:")
                print("1. ГОСТ СТ-1")
                print("2. Собственный стандарт пекарни")
                print("3. Органическая выпечка")
                standard_choice = input("Введите номер стандарта: ")
                
                if standard_choice in ["1", "2", "3"]:
                    try:
                        standard = controller.get_standard(
                            ["ГОСТ СТ-1", 
                             "Собственный стандарт пекарни", 
                             "Органическая выпечка"][int(standard_choice)-1]
                        )
                        print(f"\nПроверка на этапе: {product.get_current_stage()}")
                        is_compliant, failed_criteria = controller.check_compliance(
                            product_id, 
                            standard
                        )
                        
                        if is_compliant:
                            print(f"\nПродукт {product_id} соответствует стандарту для этапа {product.get_current_stage()}.")
                        else:
                            print(f"\nПродукт {product_id} НЕ соответствует стандарту для этапа {product.get_current_stage()}.")
                            print(f"Не соответствует по критериям: {', '.join(failed_criteria)}")
                    except ValueError as e:
                        print(f"\nОшибка: {e}")
                else:
                    print("\nНеверный выбор стандарта.")
                
        elif choice == '5':
            product_id = input("Введите ID продукта для улучшения: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                print("\nВыберите стандарт качества:")
                print("1. ГОСТ СТ-1")
                print("2. Собственный стандарт пекарни")
                print("3. Органическая выпечка")
                standard_choice = input("Введите номер стандарта: ")
                
                if standard_choice in ["1", "2", "3"]:
                    try:
                        standard = controller.get_standard(
                            ["ГОСТ СТ-1", 
                             "Собственный стандарт пекарни", 
                             "Органическая выпечка"][int(standard_choice)-1]
                        )
                        print(f"\nУлучшение продукта на этапе: {product.get_current_stage()}")
                        improved_criteria = controller.improve_product(
                            product_id, 
                            standard
                        )
                        
                        if not improved_criteria:
                            print(f"\nПродукт {product_id} уже соответствует стандарту для этапа {product.get_current_stage()}.")
                        else:
                            print(f"\nВнесены улучшения в продукт {product_id}:")
                            for criterion in improved_criteria:
                                print(f"- {criterion} улучшен до требуемого уровня")
                    except ValueError as e:
                        print(f"\nОшибка: {e}")
                else:
                    print("\nНеверный выбор стандарта.")
                
        elif choice == '6':
            product_id = input("Введите ID продукта для сертификации: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                print("\nВыберите стандарт качества:")
                print("1. ГОСТ СТ-1")
                print("2. Собственный стандарт пекарни")
                print("3. Органическая выпечка")
                standard_choice = input("Введите номер стандарта: ")
                
                if standard_choice in ["1", "2", "3"]:
                    try:
                        standard = controller.get_standard(
                            ["ГОСТ СТ-1", 
                             "Собственный стандарт пекарни", 
                             "Органическая выпечка"][int(standard_choice)-1]
                        )
                        print(f"\nВыдача сертификата для этапа: {product.get_current_stage()}")
                        success = controller.certify_product(
                            product_id, 
                            standard
                        )
                        if success:
                            print(f"\nСертификат успешно выдан для продукта {product_id} на этапе {product.get_current_stage()}.")
                        else:
                            print(f"\nНе удалось выдать сертификат для продукта {product_id} на этапе {product.get_current_stage()}.")
                    except ValueError as e:
                        print(f"\nОшибка: {e}")
                else:
                    print("\nНеверный выбор стандарта.")
                
        elif choice == '7':
            product_id = input("Введите ID продукта для добавления отзыва: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                author = input("Введите имя автора: ")
                comment = input("Введите комментарий: ")

                while True:
                    try:
                        rating = int(input("Введите рейтинг (1-5): "))
                        if 1 <= rating <= 5:
                            break
                        print("Рейтинг должен быть от 1 до 5.")
                    except ValueError:
                        print("Пожалуйста, введите число от 1 до 5.")

                success = controller.add_review(product_id, author, comment, rating)
                if success:
                    print(f"\nОтзыв успешно добавлен для продукта {product_id}.")
                else:
                    print(f"\nНе удалось добавить отзыв для продукта {product_id}.")
                
        elif choice == '8':
            product_id = input("Введите ID продукта для анализа отзывов: ")
            product = controller.get_product(product_id)
            
            if not product:
                print(f"\nПродукт с ID {product_id} не найден.")
            else:
                avg_rating, recommendations = controller.analyze_reviews(product_id)
                
                if avg_rating is None:
                    print(f"\nСредний рейтинг продукта {product_id}: нет отзывов")
                    print("Рекомендации: нет рекомендаций")
                else:
                    print(f"\nСредний рейтинг продукта {product_id}: {avg_rating:.2f}")
                    
                    if recommendations:
                        print("Рекомендации по улучшению:")
                        for rec in recommendations:
                            print(f"- {rec}")
                    else:
                        print("Рекомендации: продукт соответствует требованиям качества.")
                
        elif choice == '9' and controller.products:
            print("\nВыход из программы.")
            break
            
        else:
            print("\nНеверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()