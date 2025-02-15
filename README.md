# interpolation

Проект использует python3.10

Для начала работы нужно установить библиотеки из requirement.txt:
```bash
pip install -r requirement.txt
```

Запуск 3_point.py:
```bash
python3.10 3_point.py
```

Преобразование в exe:
```bash
python3.10 3_point.py
```


## Как задать функцию и диапазон?


```python
def investigated_func(x):
    return x**2 / 20 - 0.654


investigated_func_str = 'x**2 / 20 - 0.654'
investigated_range = [-5, 5]
amount_iteration = 3
```

- investigated_func - задаёт функцию, которую минимизируем
- investigated_func_str - представление функции в виде строки
- investigated_range - промежуток, в котором происходит поиск минимума. Для корректного отображения, отрезок должен лежать в отрезке [-30, 30].
- amount_iteration - количество итераций, которые производит пользователь.



## Преобразование Python-кода в .exe

### Требования
- **Python** (установите с [официального сайта](https://www.python.org/downloads/))
- **pip** (устанавливается вместе с Python)
- **PyInstaller** (устанавливается через pip)

---

### Шаг 1: Установка PyInstaller
Откройте терминал или командную строку и выполните команду:

```bash
pip install pyinstaller
```

### Шаг 3: Компиляция в .exe

Выполните команду:
```bash
pyinstaller --onefile 3_point.py
```

    --onefile — собирает всё в один исполняемый файл.
    3_point.py — имя вашего скрипта.

Дополнительные параметры:

    --noconsole — скрывает консольное окно (для GUI приложений).

Пример:

```bash
pyinstaller --onefile --noconsole 3_point.py
```

### Шаг 4: Результат

После выполнения команды в папке проекта появится папка dist, где будет находиться скомпилированный .exe файл.
Путь к файлу: ./dist/main.exe
