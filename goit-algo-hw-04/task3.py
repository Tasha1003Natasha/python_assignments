import sys
from pathlib import Path
from colorama import Fore

# Функція, яка приймає шлях до директорії і візуалізує структуру цієї директорії, виводячи імена всіх піддиректорій та файлів.

def create_structure(base_path):
    files = sorted([f for f in base_path.iterdir() if f.is_file() and not f.name.startswith(".")], key=lambda x: x.name.lower())
    for f in files:
        print(Fore.GREEN + f.name)

    folders = sorted([d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith(".")], key=lambda x: x.name.lower())
    for folder in folders:
        print(Fore.BLUE + folder.name + "/")
        create_structure(folder)

def main():
      if len(sys.argv) < 2:
        print("Вкажіть шлях до директорії (наприклад: python task3.py picture)")
        return
      
      file_path = sys.argv[1]
      current_dir = Path(file_path)
      if not current_dir.exists() or not current_dir.is_dir():
           print(f"'{current_dir}' не існує або не є директорією.")
           return
      
      print(Fore.BLUE + current_dir.name + "/")
      create_structure(current_dir)
    
    
if __name__ == "__main__":
    main()
