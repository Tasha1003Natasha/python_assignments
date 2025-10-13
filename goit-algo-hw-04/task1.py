
def total_salary(path):
    # Функція обчислює загальну та середню суми заробітних плат.
    try:
        with open(path, "r") as fh:
            lines = [el.strip() for el in fh.readlines() if el.strip()]
            salaries = []
          
            for line in lines:
                try:
                    salary = int(line.split(",")[1])
                    salaries.append(salary)
                except ValueError:
                    print(f"{line} заробітня плата не вказана!")
                    salaries.clear()

            if not salaries:
                return [0, 0]

            total = sum(salaries)
            average = total / len(salaries)
            return [total, average]

    except FileNotFoundError:
        print(f"Файл '{path}' не знайдено.")
        return [0,0]
    except Exception as e:
        print(f"Помилка при читанні або обробці файлу: {e}")
        return [0, 0]


total, average = total_salary("salary_file.txt")
print(f"Загальна сума заробітної плати: {total}, Середня заробітна плата: {average}")