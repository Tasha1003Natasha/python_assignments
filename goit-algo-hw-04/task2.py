
def get_cats_info(path):
# Функція, яка читає і повертає з файлу інформацію про котів.
    try:
        with open(path, "r") as fh:
            lines = [el.strip() for el in fh.readlines() if el.strip()]
       
            catsInfo = []
        
            for line in lines:
                try:
                    cat = line.split(",")
                    if len(cat) != 3: 
                        raise ValueError("Неправильна кількість даних")
                    catsInfo.append({"id": cat[0],"name": cat[1], "age": cat[2]})
                except ValueError:
                    print(f"{line} некоректні дані!")
                    continue

            return catsInfo
               

    except FileNotFoundError:
        print(f"Файл '{path}' не знайдено.")
        return []
    except Exception as e:
        print(f"Помилка при читанні або обробці файлу: {e}")
        return []


info = get_cats_info("cats_file.txt")
print(f"{info}")