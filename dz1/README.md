Задание №1
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
zip. Эмулятор должен работать в режиме CLI.

• Имя компьютера для показа в приглашении к вводу.

• Путь к архиву виртуальной файловой системы.

• Путь к лог-файлу.

Лог-файл имеет формат csv и содержит все действия во время последнего
сеанса работы с эмулятором. Для каждого действия указаны дата и время.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также
следующие команды:
1. chmod.
2. tail.
3. cal.
Все функции эмулятора должны быть покрыты тестами, а для каждой из
поддерживаемых команд необходимо написать 2 теста.
_____________________________________________________________________________________________________________________________
## 1. Запуск программы
```
cd D:\DZ1

python main.py edz пример.zip log.xml
```
_____________________________________________________________________________________________________________________________
## 2. Структура проекта

start_script.txt                  # Список команд которые последовательно выполняются при запуске эмулятора для проверки работоспособности эмулятора

log.xml                           # Лог файл, хранящий все прописанные в эмуляторе команды

main.py                          # Код эмулятора системы

пример.zip                       # Архив с виртуальной фаловой системой
_____________________________________________________________________________________________________________________________
## 3. Тест работоспособности

##Запуск тестирования 

```
python main.py edz пример.zip log.xml --script start_script.txt
```
Результат

![image](https://github.com/Edzzn0ler/config-management/blob/89fd52c8ac619721e02bf3cbea67757ea1217474/dz1/image.png)
