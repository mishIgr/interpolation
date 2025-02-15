from matplotlib.pyplot import figure, show
from matplotlib.widgets import TextBox, Button, Slider
from matplotlib.animation import FuncAnimation
import numpy as np
import tkinter as tk
from tkinter import messagebox


# Функция для исследования (парабола)
def investigated_func(x):
    """Исследуемая функция: квадратичная зависимость."""
    return x**2 / 20 - 0.654


investigated_func_str = 'x**2 / 20 - 0.654'  # Строковое представление функции
investigated_range = [-5, 5]  # Начальный диапазон x
amount_iteration = 3  # Количество итераций поиска минимума
counter_iteration = amount_iteration  # Счетчик итераций

# Класс для зума и панорамирования


class ZoomPan:
    """Класс для управления масштабированием и перемещением графика."""

    def __init__(self, min_scale=1.5, max_scale=60):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.enabled = True
        self.min_scale = min_scale  # Минимальный масштаб
        self.max_scale = max_scale  # Максимальный масштаб

    def zoom_factory(self, ax, base_scale=2.):
        """Функция для обработки событий прокрутки мыши (зум)."""
        def zoom(event):
            if not self.enabled:  # Отключает масштабирование, если запрещено
                return

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # Текущая координата x под курсором
            ydata = event.ydata  # Текущая координата y под курсором

            # Вычисляем масштабирование по направлению прокрутки
            scale_factor = 1 / base_scale if event.button == 'down' else base_scale

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            # Ограничение масштаба (не даем слишком сильно увеличить или уменьшить)
            if ((self.min_scale > cur_xlim[1] - cur_xlim[0]) * (event.button == 'down')) or \
                    ((self.max_scale < cur_xlim[1] - cur_xlim[0]) * (event.button == 'up')):
                return

            if ((self.min_scale > cur_ylim[1] - cur_ylim[0]) * (event.button == 'down')) or \
                    ((self.max_scale < cur_ylim[1] - cur_ylim[0]) * (event.button == 'up')):
                return

            # Считаем новую границу осей с учетом прокрутки
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1 - relx),
                        xdata + new_width * relx])
            ax.set_ylim([ydata - new_height * (1 - rely),
                        ydata + new_height * rely])
            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)
        return zoom

    def pan_factory(self, ax):
        """Функция для обработки перемещения графика (панорамирование)."""
        def onPress(event):
            if not self.enabled:  # Отключает панорамирование при перемещении параболы
                return
            if event.inaxes != ax:
                return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            """Перемещение графика при зажатой кнопке мыши."""
            if not self.enabled or self.press is None or event.inaxes != ax:
                return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)
            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)
        return onMotion


# Списки для хранения точек, маркеров и подписей
selected_points = []
point_markers = []
annotations = []


def add_point(x, y):
    """Добавление точки на график."""
    selected_points.append((x, y))
    marker, = ax.plot(x, y, 'ro', markersize=10)  # Красная точка
    annotation = ax.annotate(f"({x:.2f}, {y:.2f})", (x, y),
                             textcoords="offset points", xytext=(5, 5), ha='center')
    point_markers.append(marker)
    annotations.append(annotation)

    # Сортируем точки по x (чтобы всегда были в порядке)
    sorted_data = sorted(zip(selected_points, point_markers,
                         annotations), key=lambda t: t[0][0])
    selected_points[:], point_markers[:], annotations[:] = map(
        list, zip(*sorted_data))
    ax.figure.canvas.draw()


def del_point(ind):
    """Удаление точки по индексу."""
    selected_points.pop(ind)
    point_markers.pop(ind).remove()
    annotations.pop(ind).remove()
    ax.figure.canvas.draw()


def update_parabola(val=None):
    """Обновление отображения параболы при изменении параметров."""
    try:
        a = float(textbox_a.text)
        x0 = float(textbox_x0.text)
        y0 = float(textbox_y0.text)

        y_parabola = a * (x - x0) ** 2 + y0
        parabola.set_ydata(y_parabola)

        # Перемещение вершины параболы
        parabola_vertex.set_data([x0], [y0])

        ax.figure.canvas.draw_idle()
    except ValueError:
        print("Ошибка ввода! Введите числовые значения.")


def on_drag(event):
    '''Функция для перетаскивания параболы.

    Проверяет, находится ли курсор внутри области осей (ax) и нажата ли левая кнопка мыши. 
    При перемещении курсора обновляет координаты вершины параболы (x0, y0), 
    а также соответствующие текстовые поля.
    '''
    if event.inaxes != ax:  # Проверяем, находится ли курсор над осями
        return

    # Проверяем, нажата ли левая кнопка мыши и включен ли режим перетаскивания
    if event.button == 1 and parabola_dragging['drag']:
        new_x0 = event.xdata  # Новая координата x вершины параболы
        new_y0 = event.ydata  # Новая координата y вершины параболы

        # Обновляем значения в текстовых полях
        textbox_x0.set_val(str(round(new_x0, 3)))
        textbox_y0.set_val(str(round(new_y0, 3)))

        # Обновляем отрисовку параболы с новыми параметрами
        update_parabola()


def on_click_parabola(event):
    '''Функция для определения клика по вершине параболы.

    Проверяет, был ли клик в пределах области осей и 
    находится ли он вблизи вершины параболы с учетом текущего масштаба.
    При успешной проверке включает режим перетаскивания параболы.
    '''
    if event.inaxes != ax:  # Проверяем, находится ли клик в области осей
        return

    # Получаем текущий масштаб по осям
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]

    # Координаты вершины параболы
    x0 = float(textbox_x0.text)
    y0 = float(textbox_y0.text)

    # Допустимое расстояние для клика с учетом масштаба
    tolerance_x = 0.02 * x_range  # 2% от диапазона по X
    tolerance_y = 0.02 * y_range  # 2% от диапазона по Y

    # Проверяем, находится ли клик вблизи вершины параболы
    if abs(event.xdata - x0) < tolerance_x and abs(event.ydata - y0) < tolerance_y:
        parabola_dragging['drag'] = True  # Включаем режим перетаскивания
        zp.enabled = False  # Отключаем панорамирование при перетаскивании


def on_release(event):
    '''Функция для завершения перетаскивания параболы.

    Отключает режим перетаскивания и снова включает панорамирование.
    '''
    parabola_dragging['drag'] = False  # Завершаем перетаскивание
    zp.enabled = True  # Включаем панорамирование после перетаскивания


def show_info(event):
    '''Функция для отображения информационного окна.

    Открывает окно с сообщением, в котором отображается информация о задаче оптимизации.
    '''
    info_text = f'Нужно найти мин f = {investigated_func_str}'  # Текст сообщения
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно Tkinter
    messagebox.showinfo("Информация об интерфейсе",
                        info_text)  # Отображаем сообщение
    root.destroy()  # Закрываем окно после просмотра


def update_slider_a(val):
    '''Функция для обновления скорости изменения параметра 'a'.

    Задаёт скорость изменения параметра 'a' в зависимости от положения слайдера.
    Положительное значение слайдера увеличивает 'a', отрицательное — уменьшает.
    '''
    global a_change_rate  # Используем глобальную переменную скорости изменения 'a'
    step = 0.05  # Шаг изменения 'a'

    # Определяем скорость изменения 'a' в зависимости от положения слайдера
    if val > 0:
        a_change_rate = step * val
    elif val < 0:
        a_change_rate = step * val
    else:
        a_change_rate = 0  # При положении 0 скорость изменения равна 0


def update_a_over_time(frame):
    '''Функция для динамического изменения параметра 'a' с течением времени.

    Обновляет значение параметра 'a' в зависимости от скорости изменения (a_change_rate).
    После обновления пересчитывается и перерисовывается парабола.
    '''
    global a_current  # Используем текущее значение параметра 'a'
    if a_change_rate != 0:  # Если скорость изменения не равна 0
        a_current += a_change_rate  # Обновляем значение 'a'

        # Обновляем текстовое поле для отображения текущего значения 'a'
        textbox_a.set_val(str(round(a_current, 3)))

        # Обновляем отрисовку параболы с новым значением 'a'
        update_parabola()


def reset_slider(event):
    '''Функция для сброса слайдера при отпускании мыши.

    При отпускании мыши над слайдером устанавливает значение слайдера в 0.
    '''
    if event.inaxes == ax_slider_a:  # Проверяем, отпущена ли мышь на слайдере
        slider_a.set_val(0)  # Сброс слайдера в исходное положение


def calculate_minimum_x(event):
    '''Функция для вычисления координаты минимума параболы.

    Проверяет, выбрано ли три точки, и вычисляет координату минимума по оси X,
    используя формулы для апроксимации параболой. 
    Если минимум находится в пределах выбранных точек, запрашивает у пользователя интервал.
    '''
    if len(selected_points) != 3:  # Проверяем, выбрано ли 3 точки
        root = tk.Tk()
        root.withdraw()
        # Сообщение об ошибке
        messagebox.showinfo("Ошибка", "Необходимо 3 точки.")
        root.destroy()
        return

    # Получаем координаты выбранных точек
    x1, y1 = selected_points[0]
    x2, y2 = selected_points[1]
    x3, y3 = selected_points[2]

    # Вычисляем коэффициенты по формулам для апроксимации
    Delta_a = -x1 * y2 + x1 * y3 + x2 * y1 - x2 * y3 - x3 * y1 + x3 * y2
    Delta_b = x1**2 * y2 - x1**2 * y3 - x2**2 * \
        y1 + x2**2 * y3 + x3**2 * y1 - x3**2 * y2

    try:
        # Вычисляем координату минимума по оси X
        x_min = -Delta_b / (2 * Delta_a)

        # Проверяем, находится ли минимум в диапазоне выбранных точек
        x_min_range = sorted([x1, x2, x3])
        if x_min_range[0] <= x_min <= x_min_range[2]:
            # Запрос интервала у пользователя
            ask_user_interval(x_min, x_min_range)
        else:
            raise ZeroDivisionError  # Если минимум вне диапазона

    except ZeroDivisionError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Ошибка вычислений", "Минимум апроксимируемой функции находится за пределами отрезка.")
        root.destroy()
    except ValueError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Ошибка вычислений", str(e))
        root.destroy()


def search_new_point(x_min):
    '''Функция для поиска новой точки для апроксимации.

    Определяет новую точку в зависимости от положения минимума (x_min).
    Если новая точка слишком близко к минимуму, то она корректируется.
    Возвращает координаты новой точки (x, y).
    '''
    # Определяем новую точку как середину между первыми двумя выбранными точками
    new_x = (selected_points[0][0] + selected_points[1][0]) / 2

    # Если новая точка слишком близка к минимуму, сдвигаем её
    if abs(new_x - x_min) <= 0.01:
        new_x += 0.1

    # Возвращаем координаты новой точки
    return new_x, investigated_func(new_x)


def ask_user_interval(x_min, x_min_range):
    '''Функция для запроса у пользователя местоположения минимума.

    Открывает окно с вопросом, в каком интервале (левом или правом) 
    относительно средней точки выбранных значений находится минимум.
    В зависимости от ответа пользователя выполняется добавление или удаление точки.
    '''
    root = tk.Tk()
    root.title("Вопрос")

    # Текст вопроса
    label = tk.Label(
        root, text="Укажите, в каком интервале (левом или правом) находится минимум")
    label.pack(pady=10)

    def select_left():
        '''Проверка, находится ли минимум в левом интервале.

        Если минимум находится слева от средней точки, удаляется правая точка.
        Иначе выводится сообщение об ошибке, предлагая апроксимировать функцию ещё раз.
        '''
        global counter_iteration
        if x_min <= x_min_range[1]:
            messagebox.showinfo("Результат", "Верно")
            root.destroy()
            del_point(2)  # Удаляем правую точку

            # Если есть оставшиеся итерации, добавляем новую точку
            if counter_iteration:
                counter_iteration -= 1
                add_point(*search_new_point(x_min))
            else:
                reset_point()
        else:
            messagebox.showinfo(
                "Результат", "Неверно, апроксимируйте функцию ещё раз.")
            root.destroy()

    def select_right():
        '''Проверка, находится ли минимум в правом интервале.

        Если минимум находится справа от средней точки, удаляется левая точка.
        Иначе выводится сообщение об ошибке, предлагая апроксимировать функцию ещё раз.
        '''
        global counter_iteration
        if x_min >= x_min_range[1]:
            messagebox.showinfo("Результат", "Верно")
            root.destroy()
            del_point(0)  # Удаляем левую точку

            # Если есть оставшиеся итерации, добавляем новую точку
            if counter_iteration:
                counter_iteration -= 1
                add_point(*search_new_point(x_min))
            else:
                reset_point()
        else:
            messagebox.showinfo(
                "Результат", "Неверно, апроксимируйте функцию ещё раз.")
            root.destroy()

    def reset_point():
        '''Функция для сброса точек в начальные координаты.

        Устанавливает начальные точки в границах заданного диапазона.
        Обнуляет счётчик итераций и перерисовывает график.
        '''
        global counter_iteration
        messagebox.showinfo("Результат", "Надеюсь вы разобрались в методе.")
        counter_iteration = amount_iteration  # Сброс счётчика итераций

        # Удаляем все точки, кроме начальных
        for _ in range(2):
            del_point(0)

        # Добавляем три начальные точки: левая граница, середина и правая граница диапазона
        for x in [investigated_range[0], (investigated_range[0] + investigated_range[1]) / 2, investigated_range[1]]:
            add_point(x, investigated_func(x))

    # Создание кнопок "Левый" и "Правый" для выбора интервала
    button_left = tk.Button(root, text="Левый", command=select_left)
    button_left.pack(side="left", padx=10, pady=10)

    button_right = tk.Button(root, text="Правый", command=select_right)
    button_right.pack(side="right", padx=10, pady=10)

    root.mainloop()  # Запуск основного цикла окна


fig = figure()
ax = fig.add_subplot(111, xlim=(-20, 20), ylim=(-20, 20), autoscale_on=False)

scale = 1.1
zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale=scale)
figPan = zp.pan_factory(ax)

parabola_dragging = {'drag': False}

# Добавление начальных точек
for x in [investigated_range[0], (investigated_range[0] + investigated_range[1]) / 2, investigated_range[1]]:
    add_point(x, investigated_func(x))

# Создание параболы
x = np.linspace(-30, 30, 400)
a_initial = 1
x0_initial = 0
y0_initial = 0
y_parabola = a_initial * (x - x0_initial) ** 2 + y0_initial
parabola, = ax.plot(x, y_parabola, 'g-', label='Parabola: a(x - x0)^2 + y0')

# Добавление точки в вершину параболы
parabola_vertex, = ax.plot([x0_initial], [y0_initial], 'bo', markersize=8)

# Настройка текстовых полей для ввода параметров
axbox_a = fig.add_axes([0.15, 0.01, 0.2, 0.05])
axbox_x0 = fig.add_axes([0.4, 0.01, 0.2, 0.05])
axbox_y0 = fig.add_axes([0.65, 0.01, 0.2, 0.05])

textbox_a = TextBox(axbox_a, 'a', initial=str(a_initial))
textbox_x0 = TextBox(axbox_x0, 'x0', initial=str(x0_initial))
textbox_y0 = TextBox(axbox_y0, 'y0', initial=str(y0_initial))

textbox_a.on_submit(update_parabola)
textbox_x0.on_submit(update_parabola)
textbox_y0.on_submit(update_parabola)

# Создание кнопки для отображения информации в верхнем левом углу
ax_button_info = fig.add_axes([0.01, 0.95, 0.1, 0.05])
button_info = Button(ax_button_info, '?')
button_info.on_clicked(show_info)

# Создание кнопки для проверки нахождения минимума
ax_button_min = fig.add_axes([0.23, 0.95, 0.15, 0.05])
button_minimum = Button(ax_button_min, 'Проверка')
button_minimum.on_clicked(calculate_minimum_x)

# Добавление событий для перетаскивания параболы
fig.canvas.mpl_connect('motion_notify_event', on_drag)
fig.canvas.mpl_connect('button_press_event', on_click_parabola)
fig.canvas.mpl_connect('button_release_event', on_release)

# Глобальная переменная для отслеживания скорости изменения 'a'
a_current = a_initial
a_change_rate = 0

# Добавляем слайдер для изменения параметра a
ax_slider_a = fig.add_axes([0.17, 0.12, 0.7, 0.03],
                           facecolor='lightgoldenrodyellow')
slider_a = Slider(ax_slider_a, 'a', -1.0, 1.0, valinit=0, valstep=0.01)
slider_a.valtext.set_visible(False)

# Подключаем событияani
slider_a.on_changed(update_slider_a)
# Сброс слайдера при отпускании мыши
fig.canvas.mpl_connect('button_release_event', reset_slider)

# Анимация для постоянного изменения параметра 'a'
ani = FuncAnimation(fig, update_a_over_time, interval=50, save_count=200)

show()
