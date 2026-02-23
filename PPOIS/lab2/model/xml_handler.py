"""
xml_handler.py - класс для работы с XML

Содержит методы для:
- Сохранения данных в XML с использованием DOM
- Загрузки данных из XML с использованием SAX
"""

import xml.dom.minidom as dom
import xml.sax
from datetime import date
from .pet import Pet
from .database import PetDatabase

class XMLHandler:
    """Класс для обработки XML-файлов"""
    
    @staticmethod
    def save_to_xml(pets, filename):
        """
        Сохраняет данные в XML-файл с использованием DOM
        
        Args:
            pets: Список объектов Pet
            filename: Имя файла для сохранения
            
        Raises:
            RuntimeError: При ошибках ввода-вывода
        """
        try:
            # Создаем DOM-документ
            impl = dom.getDOMImplementation()
            doc = impl.createDocument(None, "pets", None)
            root = doc.documentElement
            
            # Добавляем каждого питомца как элемент
            for pet in pets:
                pet_elem = doc.createElement("pet")
                
                # Имя питомца
                name_elem = doc.createElement("name")
                name_elem.appendChild(doc.createTextNode(pet.name))
                pet_elem.appendChild(name_elem)
                
                # Дата рождения
                birth_date_elem = doc.createElement("birth_date")
                birth_date_elem.appendChild(doc.createTextNode(pet.birth_date.isoformat()))
                pet_elem.appendChild(birth_date_elem)
                
                # Дата последнего приема
                last_visit_elem = doc.createElement("last_visit")
                last_visit_elem.appendChild(doc.createTextNode(pet.last_visit.isoformat()))
                pet_elem.appendChild(last_visit_elem)
                
                # ФИО ветеринара
                vet_name_elem = doc.createElement("vet_name")
                vet_name_elem.appendChild(doc.createTextNode(pet.vet_name))
                pet_elem.appendChild(vet_name_elem)
                
                # Диагноз
                diagnosis_elem = doc.createElement("diagnosis")
                diagnosis_elem.appendChild(doc.createTextNode(pet.diagnosis))
                pet_elem.appendChild(diagnosis_elem)
                
                # Добавляем питомца в корневой элемент
                root.appendChild(pet_elem)
            
            # Сохраняем документ в файл
            with open(filename, "w", encoding="utf-8") as f:
                doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8")
                
        except (IOError, Exception) as e:
            raise RuntimeError(f"Ошибка сохранения в XML: {str(e)}")
    
    @staticmethod
    def load_from_xml(filename):
        """
        Загружает данные из XML-файла с использованием SAX
        
        Args:
            filename: Имя файла для загрузки
            
        Returns:
            Список объектов Pet
            
        Raises:
            RuntimeError: При ошибках ввода-вывода или парсинга
        """
        class PetHandler(xml.sax.ContentHandler):
            """Обработчик SAX для парсинга XML-файла"""
            
            def __init__(self):
                self.current_data = ""
                self.current_pet = None
                self.pets = []
                self.in_name = False
                self.in_birth_date = False
                self.in_last_visit = False
                self.in_vet_name = False
                self.in_diagnosis = False
            
            def startElement(self, name, attrs):
                """Обработка начала элемента"""
                if name == "pet":
                    self.current_pet = {
                        "name": "",
                        "birth_date": None,
                        "last_visit": None,
                        "vet_name": "",
                        "diagnosis": ""
                    }
                elif name == "name":
                    self.in_name = True
                elif name == "birth_date":
                    self.in_birth_date = True
                elif name == "last_visit":
                    self.in_last_visit = True
                elif name == "vet_name":
                    self.in_vet_name = True
                elif name == "diagnosis":
                    self.in_diagnosis = True
            
            def characters(self, content):
                """Обработка текстового содержимого"""
                self.current_data += content
            
            def endElement(self, name):
                """Обработка конца элемента"""
                # Сохраняем данные в текущего питомца
                if self.in_name and name == "name":
                    self.current_pet["name"] = self.current_data.strip()
                    self.in_name = False
                elif self.in_birth_date and name == "birth_date":
                    try:
                        year, month, day = map(int, self.current_data.strip().split('-'))
                        self.current_pet["birth_date"] = date(year, month, day)
                    except (ValueError, TypeError):
                        pass
                    self.in_birth_date = False
                elif self.in_last_visit and name == "last_visit":
                    try:
                        year, month, day = map(int, self.current_data.strip().split('-'))
                        self.current_pet["last_visit"] = date(year, month, day)
                    except (ValueError, TypeError):
                        pass
                    self.in_last_visit = False
                elif self.in_vet_name and name == "vet_name":
                    self.current_pet["vet_name"] = self.current_data.strip()
                    self.in_vet_name = False
                elif self.in_diagnosis and name == "diagnosis":
                    self.current_pet["diagnosis"] = self.current_data.strip()
                    self.in_diagnosis = False
                
                # Сохраняем питомца при завершении элемента pet
                if name == "pet" and self.current_pet:
                    # Проверяем, что все необходимые данные присутствуют
                    if (self.current_pet["name"] and 
                        self.current_pet["birth_date"] and 
                        self.current_pet["last_visit"]):
                        try:
                            pet = Pet(
                                self.current_pet["name"],
                                self.current_pet["birth_date"],
                                self.current_pet["last_visit"],
                                self.current_pet["vet_name"],
                                self.current_pet["diagnosis"]
                            )
                            self.pets.append(pet)
                        except Exception as e:
                            print(f"Ошибка создания объекта Pet: {e}")
                
                self.current_data = ""
        
        try:
            # Создаем и настраиваем SAX-парсер
            parser = xml.sax.make_parser()
            handler = PetHandler()
            parser.setContentHandler(handler)
            
            # Парсим файл
            parser.parse(filename)
            
            return handler.pets
        except (xml.sax.SAXException, IOError, Exception) as e:
            raise RuntimeError(f"Ошибка загрузки из XML: {str(e)}")