from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if len(value) < 3:
            raise ValueError("Name is too short, need more than 2 symbols")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone: str):
        if phone not in self.phones:
            self.phones.append(Phone(phone))
            return f"Phone added: {self.phones}"

    def remove_phone(self, phone: str):
        self.phones = [p for p in self.phones if p.value != phone]
        return f"Phone removed: {self.phones}"

    def edit_phone(self, phone: str, new_phone: str):
        for p in self.phones:
            if p.value == phone:
                p.value = new_phone
                return p
        raise ValueError("Old {phone} number not found.")

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError(f"Phone number '{phone}' not found.")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.data = {}

    def add_record(self, record: Record):
        self.data[record.name.value] = record
        return f"Record added: {record.name.value}"

    def find(self, name: Name):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            value = self.data.pop(name)
            return f"Removed: {name}"

    def __str__(self):
        result = ["AddressBook:"]
        for record in self.data.values():
            result.append(str(record))
        return "\n".join(result)


book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")

book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

print(book)

john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john)

found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("John")
print(book)
