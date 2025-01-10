#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime

# Получить каталог, в котором находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def read_number():
    """Прочитать текущее число из файла."""
    try:
        with open("number.txt", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        # Создать файл с начальным числом, если он не существует
        write_number(0)
        return 0

def write_number(num):
    """Записать новое число в файл."""
    with open("number.txt", "w") as f:
        f.write(str(num))

def generate_commit_message():
    """Создать сообщение коммита с текущей датой и числом."""
    date = datetime.now().strftime("%Y-%m-%d")
    number = read_number()
    return f"feat(counter): update number to {number} on {date}"

def git_commit():
    """Добавить и зафиксировать изменения."""
    try:
        # Проверить, находимся ли мы в git-репозитории
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                      check=True, capture_output=True)
        
        # Добавить изменения
        subprocess.run(["git", "add", "number.txt"], check=True)
        
        # Создать коммит
        commit_message = generate_commit_message()
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Ошибка: не git-репозиторий или команда git не удалась")
        return False

def git_push():
    """Отправить зафиксированные изменения в удаленный репозиторий."""
    try:
        result = subprocess.run(["git", "push"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print("Изменения успешно отправлены.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отправке в репозиторий: {e.stderr}")
        return False

def update_cron_with_random_time():
    """Обновить crontab с случайным временем для следующего запуска."""
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    
    # Создать временный файл для crontab
    cron_file = "/tmp/current_cron"
    
    try:
        # Получить текущий crontab
        subprocess.run(f"crontab -l > {cron_file} 2>/dev/null || true", 
                      shell=True, check=True)
        
        # Прочитать существующие записи crontab
        with open(cron_file, "r") as file:
            lines = [line for line in file.readlines() 
                    if "update_number.py" not in line]
        
        # Добавить новую запись cron
        new_cron = (f"{random_minute} {random_hour} * * * "
                   f"cd {script_dir} && "
                   f"python3 {os.path.join(script_dir, 'update_number.py')}\n")
        lines.append(new_cron)
        
        # Записать обновленный crontab
        with open(cron_file, "w") as file:
            file.writelines(lines)
        
        # Установить новый crontab
        subprocess.run(["crontab", cron_file], check=True)
        print(f"Задание cron запланировано на {random_hour:02d}:{random_minute:02d}")
        
    except Exception as e:
        print(f"Ошибка при обновлении crontab: {str(e)}")
    finally:
        # Очистить временный файл
        if os.path.exists(cron_file):
            os.remove(cron_file)

def main():
    """Основная функция выполнения."""
    try:
        # Прочитать и увеличить число
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)
        
        # Зафиксировать и отправить изменения
        if git_commit() and git_push():
            # Обновить cron только если операции git прошли успешно
            update_cron_with_random_time()
        
    except Exception as e:
        print(f"Ошибка в основном выполнении: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
