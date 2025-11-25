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
            return phone

    def remove_phone(self, phone: str):
        p = self.find_phone(phone)
        if p is None:
            return None

        self.phones.remove(p)
        return p

    def edit_phone(self, phone: str, new_phone: str):
        p = self.find_phone(phone)
        if p is None:
            raise ValueError(f"Old phone '{phone}' not found.")

        new_phone_obj = Phone(new_phone)
        p.value = new_phone_obj.value
        return p

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record
        return record

    def find(self, name: Name):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            return self.data.pop(name, None)

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
john.edit_phone("1234567890", "1111111111")
print(john)


found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("John")
print(book)
