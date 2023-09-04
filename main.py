from collections import UserDict
from datetime import datetime
import re
import pickle

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Некоректний формат номера телефону. Використовуйте '+11-111-111-111'")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(value):
        return re.match(r'^\+\d{2}-\d{3}-\d{3}-\d{3}$', value) is not None

class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid_birthday(value):
            raise ValueError("Некоректний формат дня народження. Використовуйте 'yyyy-mm-dd'")
        super().__init__(value)

    @staticmethod
    def is_valid_birthday(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self._birthday = birthday

    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            index = self.phones.index(old_phone)
            self.phones[index] = new_phone

    def days_to_birthday(self):
        if self._birthday:
            birth_date = datetime.strptime(self._birthday, '%Y-%m-%d').date()
            today = datetime.now().date()
            next_birthday = birth_date.replace(year=today.year)

            if today > next_birthday:
                next_birthday = next_birthday.replace(year=today.year + 1)

            days_until_birthday = (next_birthday - today).days
            return days_until_birthday

    @property
    def birthday(self):
        return self._birthday.value if self._birthday else None

    @birthday.setter
    def birthday(self, value):
        if value is None:
            self._birthday = None
        else:
            if not Birthday.is_valid_birthday(value):
                raise ValueError("Використовуйте 'yyyy-mm-dd'")
            self._birthday = Birthday(value)

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 5
        self.filename = 'address_book.pkl'

    def add_record(self, record):
        self.data[record.name.value] = record

    def save_to_disk(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_disk(self):
        try:
            with open(self.filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            self.data = {}

    def search_contacts(self, query):
        results = []
        query = query.lower()  # Convert the query to lowercase for case-insensitive search

        for record in self.data.values():
            # Convert the name and phone numbers to lowercase for case-insensitive search
            name_value = record.name.value.lower()
            phone_values = [phone.value.lower() for phone in record.phones]

            if query in name_value or any(query in phone for phone in phone_values):
                results.append(record)

        return results

if __name__ == "__main__":
    address_book = AddressBook()
    address_book.load_from_disk()

    while True:
        print("Меню:")
        print("1. Додати контакт")
        print("2. Пошук контакту")
        print("3. Вихід")
        choice = input("Виберіть опцію: ")

        if choice == "1":
            name = input("Введіть ім'я: ")
            phone = input("Введіть номер телефону: ")
            birthday = input("Введіть день народження (yyyy-mm-dd): ")

            record = Record(Name(name), Phone(phone), Birthday(birthday))
            address_book.add_record(record)
            address_book.save_to_disk()
            print("Контакт додано.")

        elif choice == "2":
            query = input("Введіть ім'я або номер телефону для пошуку: ")
            results = address_book.search_contacts(query)
            if results:
                for result in results:
                    print(f"Ім'я: {result.name.value}")
                    print(f"Номер телефону: {', '.join(phone.value for phone in result.phones)}")
                    print(f"День народження: {result.birthday}")
                    print("-" * 20)
            else:
                print("Контактів не знайдено.")

        elif choice == "3":
            address_book.save_to_disk()
            break

        else:
            print("Невірний вибір. Спробуйте ще раз.")