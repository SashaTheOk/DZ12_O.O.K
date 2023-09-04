import pickle
from datetime import datetime
from collections import UserDict
import re

class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

class Phone(Field):
    def __eq__(self, other):
        return isinstance(other, Phone) and self.value == other.value

    @staticmethod
    def is_valid_phone(value):
        return re.match(r'^\+\d{2}-\d{3}-\d{3}-\d{3}$', value) is not None

    @Field.value.setter
    def value(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Invalid phone number format. Please use the format +xx-xxx-xxx-xxx.")
        self._value = value

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid_birthday(value):
            raise ValueError("Invalid birthday format. Please use YYYY-MM-DD.")
        self._year, self._month, self._day = map(int, value.split('-'))

    @staticmethod
    def is_valid_birthday(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def __eq__(self, other):
        return isinstance(other, Birthday) and self.value == other.value

    @Field.value.setter
    def value(self, value):
        if not self.is_valid_birthday(value):
            raise ValueError("Invalid birthday format. Please use YYYY-MM-DD.")
        self._value = value

class Record:
    def __init__(self, name: Name, phones: list, emails: list, birthday: Birthday = None):
        self.name = name
        self.phones = [Phone(phone) for phone in phones]
        self.emails = emails
        self.birthday = birthday

    def add_phone(self, phone):
        phone_number = Phone(phone)
        if phone_number not in self.phones:
            self.phones.append(phone_number)

    def find_phone(self, value):
        for phone in self.phones:
            if phone.value == value:
                return phone
        return None

    def delete_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        index = self.phones.index(old_phone)
        self.phones[index] = Phone(new_phone)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today()
            next_birthday = datetime(today.year, self.birthday._month, self.birthday._day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday._month, self.birthday._day)
            days_remaining = (next_birthday - today).days
            return days_remaining
        else:
            return None

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 5

    def iterator(self):
        keys = list(self.data.keys())
        current_index = 0

        while current_index < len(keys):
            yield [self.data[key] for key in keys[current_index:current_index + self.page_size]]
            current_index += self.page_size

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find_record(self, value):
        return self.data.get(value)

    def edit_record(self, name, new_phones, new_emails, new_birthday=None):
        if name in self.data:
            record = self.data[name]
            record.phones = [Phone(phone) for phone in new_phones]
            record.emails = new_emails
            if new_birthday:
                record.birthday = Birthday(new_birthday)
            self.data[name] = record
            print(f"Contact {name} edited successfully.")
        else:
            print(f"Contact with Name '{name}' not found.")

def save_address_book(address_book, file_name):
    with open(file_name, 'wb') as file:
        pickle.dump(address_book, file)

def load_address_book(file_name):
    try:
        with open(file_name, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()

def main():
    file_name = 'address_book.pickle'  # Вкажіть ім'я файлу, в якому буде збережено адресну книгу

    address_book = load_address_book(file_name)

    while True:
        print("\nOptions:")
        print("1. Add Contact")
        print("2. Find Contact")
        print("3. Edit Contact")
        print("4. Delete Contact")
        print("5. Exit")
        print("6. Search by Phone Number or Name")  # Доданий новий варіант вибору для пошуку

        choice = input("Select an option: ")

        if choice == "1":
            name = input("Enter Name: ")
            phone_numbers = input("Enter Phone Numbers (+xx-xxx-xxx-xxx, separate with commas): ").split(',')
            emails = input("Enter Emails (separate with commas): ").split(',')
            birthday = input("Enter Birthday (optional, YYYY-MM-DD): ")
            if birthday:
                birthday = Birthday(birthday.strip())
            name_field = Name(name.strip())
            record = Record(name_field, phone_numbers, emails, birthday)
            address_book.add_record(record)
            print(f"Contact {name} added to the address book.")

        elif choice == "2":
            search_term = input("Enter Name to search for: ")
            record = address_book.find_record(search_term)
            if record:
                print(f"Name: {record.name.value}")
                print("Phone Numbers:")
                for phone in record.phones:
                    print(phone.value)
                print("Emails:")
                for email in record.emails:
                    print(email)
                if record.birthday:
                    print(f"Birthday: {record.birthday.value}")
                    days_remaining = record.days_to_birthday()
                    if days_remaining is not None:
                        print(f"Days to next birthday: {days_remaining}")
                    else:
                        print("No birthday date provided.")
                else:
                    print("No birthday date provided.")
            else:
                print(f"Contact with Name '{search_term}' not found.")

        elif choice == "3":
            edit_name = input("Enter Name to edit: ")
            new_phone_numbers = input("Enter New Phone Numbers (+xx-xxx-xxx-xxx, separate with commas): ").split(',')
            new_emails = input("Enter New Emails (separate with commas): ").split(',')
            new_birthday = input("Enter New Birthday (optional, YYYY-MM-DD): ")
            address_book.edit_record(edit_name.strip(), new_phone_numbers, new_emails, new_birthday)

        elif choice == "4":
            delete_term = input("Enter Name to delete: ")
            record = address_book.find_record(delete_term)
            if record:
                del address_book.data[delete_term]
                print(f"Contact {delete_term} deleted from the address book.")
            else:
                print(f"Contact with Name '{delete_term}' not found.")

        elif choice == "5":
            save_address_book(address_book, file_name)  # Збереження адресної книги перед виходом
            print("Goodbye!")
            break

        elif choice == "6":
            search_term = input("Enter Phone Number or Name to search for: ")
            matching_records = []
            for record in address_book.values():
                if any(search_term in record.name.value or search_term in phone.value for phone in record.phones):
                    matching_records.append(record)

            if matching_records:
                print("Matching Contacts:")
                for record in matching_records:
                    print(f"Name: {record.name.value}")
                    print("Phone Numbers:")
                    for phone in record.phones:
                        print(phone.value)
                    print("Emails:")
                    for email in record.emails:
                        print(email)
                    if record.birthday:
                        print(f"Birthday: {record.birthday.value}")
                        days_remaining = record.days_to_birthday()
                        if days_remaining is not None:
                            print(f"Days to next birthday: {days_remaining}")
                        else:
                            print("No birthday date provided.")
                    else:
                        print("No birthday date provided.")
            else:
                print(f"No contacts found for '{search_term}'.")

        else:
            print("Invalid option. Please select a valid option.")

if __name__ == "__main__":
    main()
