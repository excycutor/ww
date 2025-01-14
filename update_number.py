#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
import logging
from colorama import Fore, Style, init
import sys
import io

# Настройка кодировки UTF-8 для стандартного вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Инициализация colorama
init(autoreset=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_number.log", encoding='utf-8'),  # Логи в файл с UTF-8
        logging.StreamHandler(sys.stdout)  # Логи в консоль с UTF-8
    ]
)

# Цвета для уровней логирования
LOG_COLORS = {
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT
}

class ColoredFormatter(logging.Formatter):
    """Форматирование логов с цветами."""
    def format(self, record):
        log_message = super().format(record)
        return LOG_COLORS.get(record.levelno, Fore.WHITE) + log_message

# Применяем цветной форматтер к консольному логгеру
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def read_number():
    """Чтение числа из файла number.txt."""
    try:
        with open("number.txt", "r", encoding='utf-8') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        logging.error("Файл number.txt не найден.")
        raise
    except ValueError:
        logging.error("Файл number.txt содержит недопустимое значение.")
        raise

def write_number(num):
    """Запись числа в файл number.txt."""
    try:
        with open("number.txt", "w", encoding='utf-8') as f:
            f.write(str(num))
        logging.info(f"Число успешно обновлено на {num}.")
    except Exception as e:
        logging.error(f"Ошибка при записи числа в файл: {e}")
        raise

def generate_random_commit_message():
    """Генерация случайного сообщения для коммита."""
    try:
        from transformers import pipeline

        generator = pipeline(
            "text-generation",
            model="openai-community/gpt2",
        )
        prompt = """
            Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject. Please keep it short. Here are some examples:

            - feat(auth): add user authentication module
            - fix(api): resolve null pointer exception in user endpoint
            - docs(readme): update installation instructions
            - chore(deps): upgrade lodash to version 4.17.21
            - refactor(utils): simplify date formatting logic

            Now, generate a new commit message:
        """
        generated = generator(
            prompt,
            max_new_tokens=50,
            num_return_sequences=1,
            temperature=0.9,
            top_k=50,
            top_p=0.9,
            truncation=True,
        )
        text = generated[0]["generated_text"]

        if "- " in text:
            return text.rsplit("- ", 1)[-1].strip()
        else:
            raise ValueError(f"Unexpected generated text {text}")
    except Exception as e:
        logging.error(f"Ошибка при генерации сообщения коммита: {e}")
        raise

def git_commit():
    """Выполнение коммита изменений."""
    try:
        # Добавляем изменения в индекс Git
        subprocess.run(["git", "add", "number.txt"], check=True)
        
        # Генерация сообщения коммита
        if "FANCY_JOB_USE_LLM" in os.environ:
            commit_message = generate_random_commit_message()
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            commit_message = f"Update number: {date}"
        
        # Создание коммита
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        logging.info(f"Коммит успешно создан с сообщением: {commit_message}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении git-команды: {e}")
        raise
    except Exception as e:
        logging.error(f"Ошибка при создании коммита: {e}")
        raise

def git_push():
    """Отправка изменений в удаленный репозиторий."""
    try:
        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Изменения успешно отправлены в GitHub.")
        else:
            error_message = result.stderr.strip()
            logging.error(f"Ошибка при отправке изменений в GitHub: {error_message}")
            raise Exception(f"Ошибка Git: {error_message}")
    except Exception as e:
        logging.error(f"Ошибка при отправке изменений: {e}")
        raise

def check_remote_repository():
    """Проверка существования удаленного репозитория."""
    try:
        result = subprocess.run(["git", "ls-remote", "https://github.com/excycutor/fancy_job.git"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Репозиторий не найден или недоступен.")
        logging.info("Репозиторий доступен.")
    except Exception as e:
        logging.error(f"Ошибка при проверке репозитория: {e}")
        raise

def main():
    """Основная функция скрипта."""
    try:
        logging.info("Запуск скрипта...")
        
        # Проверка доступности репозитория
        check_remote_repository()
        
        # Чтение текущего числа
        current_number = read_number()
        logging.info(f"Текущее число: {current_number}")
        
        # Увеличение числа на 1
        new_number = current_number + 1
        logging.info(f"Новое число: {new_number}")
        
        # Запись нового числа в файл
        write_number(new_number)
        
        # Создание коммита
        git_commit()
        
        # Отправка изменений в GitHub
        git_push()
        
        logging.info("Скрипт успешно завершен.")
    except Exception as e:
        logging.error(f"Ошибка в основном потоке: {e}")
        exit(1)

if __name__ == "__main__":
    main()