import os
import argparse
import zipfile as zip
import calendar
import datetime
import xml.etree.ElementTree as ET

cur_path = "~"
permissions = {}
log_file = None


def log_action(user, action, details=""):
    global log_file
    if not log_file:
        return
    timestamp = datetime.datetime.now().isoformat()
    root = ET.Element("log") if not os.path.exists(log_file) else ET.parse(log_file).getroot()
    entry = ET.SubElement(root, "entry")
    ET.SubElement(entry, "timestamp").text = timestamp
    ET.SubElement(entry, "user").text = user
    ET.SubElement(entry, "action").text = action
    ET.SubElement(entry, "details").text = details
    tree = ET.ElementTree(root)
    tree.write(log_file, encoding="utf-8")


def cal(args=None):
    if not args:
        year, month = datetime.datetime.now().year, datetime.datetime.now().month
    else:
        try:
            year = int(args[0])
            month = int(args[1]) if len(args) > 1 else None
        except ValueError:
            print("Ошибка! Аргументы должны быть числами.")
            return
        if month and (month < 1 or month > 12):
            print("Ошибка! Месяц должен быть в диапазоне от 1 до 12.")
            return
    if month:
        print(calendar.TextCalendar().formatmonth(year, month))
    else:
        print(calendar.TextCalendar().formatyear(year))


def this_dir(zip_fs, cur_path="~"):
    with zip.ZipFile(zip_fs, "r") as zf:
        items = []
        # Определяем текущий путь
        base_path = "" if cur_path == "~" else cur_path.strip("/") + "/"
        for item in zf.namelist():
            # Учитываем только те элементы, которые принадлежат текущему каталогу
            if item.startswith(base_path):
                relative_path = item[len(base_path):].strip("/")
                # Добавляем только файлы и папки, находящиеся на одном уровне
                if "/" not in relative_path or relative_path.endswith("/"):
                    items.append(relative_path.rstrip("/"))
        return items



def cd(zip_fs, new_path):
    global cur_path
    with zip.ZipFile(zip_fs, "r") as zf:
        if new_path == "~":
            cur_path = "~"
            return
        next_path = "" if cur_path == "~" else cur_path.rstrip("/") + "/"
        full_path = next_path + new_path.strip("/") + "/"
        if full_path in zf.namelist():
            cur_path = full_path.rstrip("/")
        else:
            print("Ошибка! Путь не найден.")


def ls(zip_fs):
    for item in this_dir(zip_fs, cur_path):
        if item == "":
            continue
        perm = permissions.get(item, "default")
        print(f"{item}\t{perm}")


def tail(zip_fs, name, count):
    global cur_path
    with zip.ZipFile(zip_fs, "r") as zf:
        next_path = "" if cur_path == "~" else cur_path.rstrip("/") + "/"
        full_path = next_path + name.strip("/")
        if full_path in zf.namelist():
            with zf.open(full_path, "r") as f:
                lines = f.readlines()[-count:]
                for line in lines:
                    print(line.decode().strip())
        else:
            print("Ошибка! Файл не найден.")


def chmod(file, mode):
    if file in this_dir(zip_fs, cur_path):
        permissions[file] = mode
        print(f"Права для {file} установлены на {mode}.")
    else:
        print("Ошибка! Файл не найден.")


def run(username, zip_fs, script_path=None):
    global cur_path
    if script_path:
        if not os.path.exists(script_path):
            print(f"Ошибка! Скрипт {script_path} не найден.")
            return
        try:
            with open(script_path, "r", encoding="utf-8") as script:
                for line in script:
                    command = line.strip()
                    if command and not command.startswith("#"):
                        print(f"Выполнение команды из скрипта: {command}")
                        if not process_command(username, zip_fs, command):
                            return
        except Exception as e:
            print(f"Ошибка при выполнении скрипта: {e}")
            return

    while True:
        prompt_path = cur_path if cur_path != "~" else "~"
        command = input(f"{username}:{prompt_path}# ")
        if not process_command(username, zip_fs, command):
            break



def process_command(username, zip_fs, command):
    args = command.split()
    if not args:
        return True
    action, params = args[0], args[1:]
    log_action(username, action, " ".join(params))
    if action == "ls":
        if len(params) == 0:
            try:
                ls(zip_fs)
            except ValueError:
                print("Ошибка! Некорректное количество строк.")
        else:
            print("Ошибка! Комманда не принемает параметры!")
    elif action == "cd":
        if params:
            cd(zip_fs, params[0])
        else:
            print("Ошибка! Укажите путь.")
    elif action == "tail":
        if len(params) >= 2:
            try:
                tail(zip_fs, params[0], int(params[1]))
            except ValueError:
                print("Ошибка! Некорректное количество строк.")
        else:
            print("Ошибка! Укажите имя файла и количество строк.")
    elif action == "chmod":
        if len(params) == 2:
            chmod(params[0], params[1])
        else:
            print("Ошибка! Укажите файл и права.")
    elif action == "cal":
        cal(params)
    elif action == "exit":
        return False
    else:
        print("Неизвестная команда.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("username", type=str, help="Имя пользователя")
    parser.add_argument("zip_fs", type=str, help="Путь к виртуальной файловой системе (zip)")
    parser.add_argument("log_file", type=str, help="Путь к файлу логов")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту", default=None)
    args = parser.parse_args()

    username = args.username
    zip_fs = args.zip_fs
    log_file = args.log_file

    if not os.path.exists(zip_fs):
        print("Ошибка! ZIP-архив не найден.")
        exit(1)

    run(username, zip_fs, args.script)
