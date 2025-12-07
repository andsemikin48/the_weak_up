"""Приложение будильник с отдельными окнами для каждой функции"""

import pyglet
from datetime import datetime, timedelta
from pyglet import shapes
import os
from pathlib import Path
import calendar


class Button:
    """Универсальный класс кнопки"""
    def __init__(self, x, y, width, height, color, text,
                 font_name="Arial", font_size=16, text_color=(255, 255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color

        # Создаем прямоугольник
        self.rectangle = shapes.Rectangle(x, y, width, height, color=color)

        # Создаем текст
        self.label = pyglet.text.Label(
            text, font_name=font_name, font_size=font_size,
            x=x + width//2, y=y + height//2,
            anchor_x="center", anchor_y="center",
            color=text_color
        )

    def draw(self):
        """Отрисовка кнопки"""
        self.rectangle.draw()
        self.label.draw()

    def is_clicked(self, x, y):
        """Проверка, был ли клик по кнопке"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


class BaseWindow(pyglet.window.Window):
    """Базовый класс для всех окон"""
    def __init__(self, app, width, height, title):
        super().__init__(width=width, height=height, caption=title)
        self.app = app
        self.buttons = []
        self.size_button = 260  # Стандартная ширина кнопки

    def create_button(self, x, y, color, text, width=None, height=50, **kwargs):
        """Создание кнопки с сохранением ссылки"""
        if width is None:
            width = self.size_button
        button = Button(x, y, width, height, color, text, **kwargs)
        self.buttons.append(button)
        return button

    def on_draw(self):
        """Базовая отрисовка окна"""
        self.clear()


class MainWindow(BaseWindow):
    """Главное окно приложения"""
    def __init__(self, app):
        super().__init__(app, width=800, height=600, title="Будильник")
        self.background_image = None
        self.load_background()
        self.setup_ui()

    def load_background(self):
        """Загрузка фона"""
        try:
            bg_path = Path("res/bg.jpg")
            if bg_path.exists():
                self.background_image = pyglet.image.load(str(bg_path))
        except:
            self.background_image = None

    def setup_ui(self):
        """Настройка интерфейса главного окна"""
        # Центр для кнопок
        center_x = 500
        start_y = self.height * 0.35

        # Кнопка установки будильника
        self.btn_set_alarm = self.create_button(
            x=center_x,
            y=start_y + 20,
            color=(50, 180, 50),
            text="Установить будильник",
            font_size=18
        )

        # Кнопка настроек
        self.btn_settings = self.create_button(
            x=center_x,
            y=start_y - 40,
            color=(50, 100, 200),
            text="Настройки",
            font_size=18
        )

        # Кнопка остановки будильника
        self.btn_stop = self.create_button(
            x=center_x,
            y=start_y - 100,
            color=(200, 50, 50),
            text="Остановить",
            font_size=18
        )

        # Кнопка списка будильников
        self.btn_list = self.create_button(
            x=center_x,
            y=start_y - 160,
            color=(180, 100, 50),
            text="Список будильников",
            font_size=18
        )

        # Текстовые метки
        self.time_label = pyglet.text.Label(
            "", font_name="Arial", font_size=48,
            x=self.width//2, y=self.height*0.7,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )

        self.date_label = pyglet.text.Label(
            "", font_name="Arial", font_size=24,
            x=self.width//2, y=self.height*0.63,
            anchor_x="center", anchor_y="center",
            color=(220, 220, 220, 255)
        )

        self.next_alarm_label = pyglet.text.Label(
            "Нет активных будильников",
            font_name="Arial", font_size=20,
            x=self.width//2, y=self.height*0.55,
            anchor_x="center", anchor_y="center",
            color=(255, 100, 100, 255)
        )

        self.title_label = pyglet.text.Label(
            "БУДИЛЬНИК", font_name="Arial", font_size=36,
            x=self.width//2, y=self.height*0.85,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )

    def update_time(self):
        """Обновление времени"""
        now = datetime.now()
        self.time_label.text = now.strftime("%H:%M:%S")
        self.date_label.text = now.strftime("%d.%m.%Y")
        self.update_next_alarm_info()

    def update_next_alarm_info(self):
        """Обновление информации о ближайшем будильнике"""
        if not self.app.alarms:
            self.next_alarm_label.text = "Нет активных будильников"
            return

        now = datetime.now()
        next_alarm = None
        min_diff = None

        for alarm in self.app.alarms:
            if alarm['triggered']:
                continue

            alarm_datetime = datetime.strptime(
                f"{alarm['date']} {alarm['time']}",
                "%Y-%m-%d %H:%M"
            )

            if alarm_datetime < now:
                continue

            diff = alarm_datetime - now
            if min_diff is None or diff < min_diff:
                min_diff = diff
                next_alarm = alarm

        if next_alarm and min_diff:
            days = min_diff.days
            hours = min_diff.seconds // 3600
            minutes = (min_diff.seconds % 3600) // 60

            if days > 0:
                self.next_alarm_label.text = f"Следующий через: {days}д {hours:02d}:{minutes:02d}"
            else:
                self.next_alarm_label.text = f"Следующий через: {hours:02d}:{minutes:02d}"
        else:
            self.next_alarm_label.text = "Нет активных будильников"

    def on_draw(self):
        """Отрисовка главного окна"""
        super().on_draw()

        # Фон
        if self.background_image:
            self.background_image.blit(0, 0)
        else:
            shapes.Rectangle(0, 0, self.width, self.height,
                             color=(40, 60, 100)).draw()

        # Заголовок и текст
        self.title_label.draw()
        self.time_label.draw()
        self.date_label.draw()
        self.next_alarm_label.draw()

        # Кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        for btn in self.buttons:
            if btn.is_clicked(x, y):
                self.handle_button_click(btn)
                return

    def handle_button_click(self, button):
        """Обработка кликов по кнопкам главного окна"""
        if button == self.btn_set_alarm:
            # Получаем позицию главного окна
            main_x, main_y = self.get_location()
            alarm_window = AlarmWindow(self.app)
            alarm_window.set_location(main_x + 50, main_y + 50)

        elif button == self.btn_settings:
            main_x, main_y = self.get_location()
            settings_window = SettingsWindow(self.app)
            settings_window.set_location(main_x + 100, main_y + 100)

        elif button == self.btn_stop:
            self.app.stop_alarm()

        elif button == self.btn_list:
            main_x, main_y = self.get_location()
            list_window = AlarmListWindow(self.app)
            list_window.set_location(main_x + 150, main_y + 150)


class AlarmWindow(pyglet.window.Window):
    """Окно установки будильника"""
    def __init__(self, main_window):
        super().__init__(width=600, height=500, caption="Установка будильника")
        self.main_window = main_window

        # Устанавливаем ТЕКУЩЕЕ время
        now = datetime.now()
        time_str = now.strftime("%H%M")  # "1430"
        self.time_digits = [int(digit) for digit in time_str]

        # Устанавливаем ТЕКУЩУЮ дату
        date_str = now.strftime("%d%m%Y")  # "01012025"
        self.date_digits = [int(digit) for digit in date_str]

        # Загрузка спрайтов
        self.digit_sprites = self.load_digit_sprites()

        # Области кликов
        self.time_areas = []
        self.date_areas = []

        self.setup_ui()
        self.setup_click_areas()

    def load_digit_sprites(self):
        """Загрузка цифр"""
        digit_sprites = []
        for i in range(10):
            try:
                path = Path(f"res/{i}.png")
                if path.exists():
                    images = pyglet.image.load_animation(str(path))
                    sprite = pyglet.sprite.Sprite(images, x=0, y=0)
                    sprite.scale= 0.7
                    digit_sprites.append(pyglet.sprite.Sprite(images))
                else:
                    digit_sprites.append(None)
            except:
                digit_sprites.append(None)
        return digit_sprites

    def setup_ui(self):
        """Настройка интерфейса"""
        # Кнопка добавления
        self.btn_add = Button(
            x=300,
            y=60,
            width=260,
            height=50,
            color=(50, 180, 50),
            text="Добавить будильник",
            font_size=18
        )

    def setup_click_areas(self):
        """Настройка областей кликов"""
        # Время: ЧЧ:ММ
        time_x = 150
        time_y = self.height - 100
        for i in range(4):
            x_pos = time_x + i * 60
            if i == 1:
                x_pos += 20
            elif i > 2:
                x_pos += 20
            self.time_areas.append((x_pos, time_y - 25, 40, 50, i))

        # Дата: ДД.ММ.ГГГГ
        date_x = 150
        offset_click = 0
        date_y = self.height - 180
        for i in range(8):
            x_pos = date_x + i * 40 + offset_click
            if i == 2 or i ==4:
                offset_click += 20
            if not (i == 4 or i == 5):
                self.date_areas.append((x_pos, date_y - 20, 25, 40, i))

    def on_draw(self):
        """Отрисовка"""
        self.clear()

        # Фон
        shapes.Rectangle(0, 0, self.width, self.height,
                         color=(0, 0, 0)).draw()

        # Заголовок
        title = pyglet.text.Label(
            "Установка будильника", font_name="Arial", font_size=24,
            x=self.width//2, y=self.height - 40,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        title.draw()

        # Подписи
        time_label = pyglet.text.Label(
            "Время:", font_name="Arial", font_size=20,
            x=50, y=self.height - 100,
            anchor_x="left", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        time_label.draw()

        date_label = pyglet.text.Label(
            "Дата:", font_name="Arial", font_size=20,
            x=50, y=self.height - 180,
            anchor_x="left", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        date_label.draw()

        # Отрисовка времени
        time_y = self.height - 100
        for i in range(4):
            x_pos = 150 + i * 60
            if i == 2:
                x_pos += 20
            elif i > 2:
                x_pos += 20

            digit = self.time_digits[i]
            sprite = self.digit_sprites[digit]
            if sprite is not None:
                sprite.x = x_pos
                sprite.y = time_y - 25
                sprite.draw()
            else:
                label = pyglet.text.Label(
                    str(digit), font_name="Arial", font_size=36,
                    x=x_pos + 20, y=time_y,
                    anchor_x="center", anchor_y="center",
                    color=(255, 255, 255, 255)
                )
                label.draw()

        # Двоеточие
        colon_x = 150 + 2 * 50 + 5
        colon = (pyglet.sprite.Sprite(pyglet.image.load("res/dthc.png"), x=colon_x, y=time_y-25))
        colon.scale = 0.75
        colon.draw()

        # Отрисовка даты
        date_y = self.height - 180
        offset = 0
        for i in range(8):
            x_pos = 150 + i * 40 + offset
            if i == 2 or i == 4:
                x_pos += 20
                offset += 20

            digit = self.date_digits[i]
            sprite = self.digit_sprites[digit]
            if sprite is not None:
                sprite.x = x_pos

                sprite.y = date_y - 20
                sprite.draw()
            else:
                label = pyglet.text.Label(
                    str(digit), font_name="Arial", font_size=28,
                    x=x_pos + 12, y=date_y,
                    anchor_x="center", anchor_y="center",
                    color=(255, 255, 255, 255)
                )
                label.draw()

        # Точки в дате
        for pos in [2, 5]:
            dot_x = 150 + pos * 30 + 20
            dot = pyglet.sprite.Sprite(pyglet.image.load("res/thc.png"))
            dot.x = dot_x
            dot.y = date_y - 20
            dot.scale = 0.5
            dot.draw()

        # Кнопка
        self.btn_add.draw()

        # Подсказка
        hint = pyglet.text.Label(
            "Кликните на цифру чтобы изменить",
            font_name="Arial", font_size=12,
            x=self.width//2, y=30,
            anchor_x="center", anchor_y="center",
            color=(200, 200, 200, 255)
        )
        hint.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        # Кнопка добавления
        if self.btn_add.is_clicked(x, y):
            self.add_alarm()
            return

        # Клики по цифрам времени
        for area_x, area_y, width, height, idx in self.time_areas:
            if (area_x <= x <= area_x + width and
                    area_y <= y <= area_y + height):
                self.change_time_digit(idx)
                return

        # Клики по цифрам даты
        for area_x, area_y, width, height, idx in self.date_areas:
            if (area_x <= x <= area_x + width and
                    area_y <= y <= area_y + height):
                self.change_date_digit(idx)
                return

    def change_time_digit(self, idx):
        """Изменить цифру времени"""
        if idx == 0:  # Первая цифра часов
            self.time_digits[idx] = (self.time_digits[idx] + 1) % 3
        elif idx == 1:  # Вторая цифра часов
            if self.time_digits[0] == 2:
                self.time_digits[idx] = (self.time_digits[idx] + 1) % 4
            else:
                self.time_digits[idx] = (self.time_digits[idx] + 1) % 10
        elif idx == 2:  # Первая цифра минут
            self.time_digits[idx] = (self.time_digits[idx] + 1) % 6
        else:  # Вторая цифра минут
            self.time_digits[idx] = (self.time_digits[idx] + 1) % 10

    def change_date_digit(self, idx):
        """Изменить цифру даты"""
        if idx == 0:  # Первая цифра дня
            self.date_digits[idx] = (self.date_digits[idx] + 1) % 4
        elif idx == 1:  # Вторая цифра дня
            if self.date_digits[0] == 3:
                self.date_digits[idx] = (self.date_digits[idx] + 1) % 2
            else:
                self.date_digits[idx] = (self.date_digits[idx] + 1) % 10
        elif idx == 2:  # Первая цифра месяца
            self.date_digits[idx] = (self.date_digits[idx] + 1) % 2
        elif idx == 3:  # Вторая цифра месяца
            if self.date_digits[2] == 1:
                self.date_digits[idx] = (self.date_digits[idx] + 1) % 3
            else:
                self.date_digits[idx] = (self.date_digits[idx] + 1) % 10
        else:  # Цифры года
            self.date_digits[idx] = (self.date_digits[idx] + 1) % 10

    def add_alarm(self):
        """Добавить будильник"""
        # Проверяем количество
        if len(self.main_window.alarms) >= 5:
            print("Максимум 5 будильников!")
            return

        # Формируем время
        hours = self.time_digits[0] * 10 + self.time_digits[1]
        minutes = self.time_digits[2] * 10 + self.time_digits[3]

        # Проверяем время
        if hours > 23 or minutes > 59:
            print("Некорректное время!")
            return

        # Формируем дату
        day = self.date_digits[0] * 10 + self.date_digits[1]
        month = self.date_digits[2] * 10 + self.date_digits[3]
        year = (self.date_digits[4] * 1000 + self.date_digits[5] * 100 +
                self.date_digits[6] * 10 + self.date_digits[7])

        # Проверяем дату
        try:
            alarm_date = datetime(year, month, day, hours, minutes)
            if alarm_date < datetime.now():
                print("Нельзя установить на прошедшее время!")
                return
        except:
            print("Некорректная дата!")
            return

        # Добавляем будильник
        new_alarm = {
            'date': f"{year:04d}-{month:02d}-{day:02d}",
            'time': f"{hours:02d}:{minutes:02d}",
            'triggered': False
        }

        self.main_window.alarms.append(new_alarm)
        print(f"Будильник добавлен: {new_alarm['date']} {new_alarm['time']}")

        # Закрываем окно
        self.close()


class SettingsWindow(BaseWindow):
    """Окно настроек"""
    def __init__(self, app):
        super().__init__(app, width=400, height=350, title="Настройки")
        self.size_button = 300  # Шире чем стандартная
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса окна настроек"""
        center_x = self.width // 2
        start_y = self.height - 120

        # Кнопка смены фона
        self.btn_bg = self.create_button(
            x=center_x - self.size_button//2,
            y=start_y,
            color=(70, 100, 150),
            text="Сменить фон",
            font_size=18,
            width=self.size_button
        )

        # Кнопка смены мелодии
        self.btn_sound = self.create_button(
            x=center_x - self.size_button//2,
            y=start_y - 70,
            color=(70, 100, 150),
            text="Сменить мелодию",
            font_size=18,
            width=self.size_button
        )

        # Кнопка сброса будильников
        self.btn_reset = self.create_button(
            x=center_x - self.size_button//2,
            y=start_y - 140,
            color=(200, 80, 80),
            text="Сбросить все будильников",
            font_size=18,
            width=self.size_button
        )

    def on_draw(self):
        """Отрисовка окна"""
        super().on_draw()

        # Темный фон
        shapes.Rectangle(0, 0, self.width, self.height,
                         color=(40, 50, 70)).draw()

        # Заголовок
        title = pyglet.text.Label(
            "Настройки", font_name="Arial", font_size=24,
            x=self.width//2, y=self.height - 40,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        title.draw()

        # Кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        for btn in self.buttons:
            if btn.is_clicked(x, y):
                self.handle_button_click(btn)
                return

    def handle_button_click(self, button):
        """Обработка кликов по кнопкам"""
        if button == self.btn_bg:
            print("Смена фона (тут пока ищу решение)")

        elif button == self.btn_sound:
            print("Смена мелодии (тут пока ищу решение)")

        elif button == self.btn_reset:
            self.app.alarms.clear()
            print("Все будильники сброшены")


class AlarmListWindow(BaseWindow):
    """Окно списка будильников"""
    def __init__(self, app):
        super().__init__(app, width=500, height=400, title="Список будильников")
        self.delete_buttons = []  # Кнопки удаления для каждого будильника

    def on_draw(self):
        """Отрисовка окна"""
        super().on_draw()

        # Темный фон
        shapes.Rectangle(0, 0, self.width, self.height,
                         color=(0, 0, 0)).draw()

        # Заголовок
        title = pyglet.text.Label(
            "Список будильников", font_name="Arial", font_size=24,
            x=self.width//2, y=self.height - 40,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        title.draw()

        # Заголовок таблицы
        header = pyglet.text.Label(
            "Дата          Время      Статус",
            font_name="Arial", font_size=16,
            x=50, y=self.height - 90,
            anchor_x="left", anchor_y="center",
            color=(200, 200, 100, 255)
        )
        header.draw()

        # Список будильников
        if not self.app.alarms:
            no_alarms = pyglet.text.Label(
                "Нет установленных будильников",
                font_name="Arial", font_size=18,
                x=self.width//2, y=self.height//2,
                anchor_x="center", anchor_y="center",
                color=(150, 150, 150, 255)
            )
            no_alarms.draw()
        else:
            # Очищаем старые кнопки удаления
            self.delete_buttons.clear()

            for i, alarm in enumerate(self.app.alarms):
                y_pos = self.height - 120 - i * 30

                # Форматирование даты из YYYY-MM-DD в DD.MM.YYYY
                date_parts = alarm['date'].split('-')
                formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"

                # Статус
                status = "✓" if alarm['triggered'] else "○"
                status_color = (100, 255, 100) if alarm['triggered'] else (255, 255, 100)

                # Дата
                date_label = pyglet.text.Label(
                    formatted_date, font_name="Arial", font_size=14,
                    x=50, y=y_pos,
                    anchor_x="left", anchor_y="center",
                    color=(200, 200, 255, 255)
                )
                date_label.draw()

                # Время
                time_label = pyglet.text.Label(
                    alarm['time'], font_name="Arial", font_size=14,
                    x=180, y=y_pos,
                    anchor_x="left", anchor_y="center",
                    color=(200, 200, 255, 255)
                )
                time_label.draw()

                # Статус
                status_label = pyglet.text.Label(
                    status, font_name="Arial", font_size=16,
                    x=280, y=y_pos,
                    anchor_x="center", anchor_y="center",
                    color=status_color + (255,)
                )
                status_label.draw()

                # Создаем кнопку удаления
                delete_button = Button(
                    x=350,
                    y=y_pos - 10,
                    width=80,
                    height=25,
                    color=(200, 80, 80),
                    text="Удалить",
                    font_size=12
                )
                delete_button.draw()
                self.delete_buttons.append((delete_button, i))

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        # Проверка кликов по кнопкам удаления
        for delete_button, index in self.delete_buttons:
            if delete_button.is_clicked(x, y):
                if index < len(self.app.alarms):
                    # Удаляем будильник
                    del self.app.alarms[index]
                    print(f"Будильник {index+1} удален")
                    # Обновляем отображение
                    return


class AlarmApp:
    """Основной класс приложения"""
    def __init__(self):
        self.alarms = []  # Список будильников
        self.current_sound_path = "res/alarm.wav"
        self.alarm_player = None

        # Создание главного окна
        self.main_window = MainWindow(self)

        # Запуск таймера обновления
        pyglet.clock.schedule_interval(self.update, 1.0)

    def update(self, dt):
        """Обновление состояния приложения"""
        # Обновление времени в главном окне
        self.main_window.update_time()

        # Проверка срабатывания будильников
        self.check_alarms()

    def check_alarms(self):
        """Проверка срабатывания будильников"""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        for alarm in self.alarms:
            if (alarm['date'] == current_date and
                    alarm['time'] == current_time and
                    not alarm['triggered']):
                alarm['triggered'] = True
                self.trigger_alarm()

    def trigger_alarm(self):
        """Срабатывание будильника"""
        print("БУДИЛЬНИК СРАБОТАЛ!")
        try:
            if os.path.exists(self.current_sound_path):
                self.alarm_player = pyglet.media.Player()
                sound = pyglet.media.load(self.current_sound_path)
                self.alarm_player.queue(sound)
                self.alarm_player.play()
                self.alarm_player.loop = True
            else:
                print(f"Звуковой файл не найден: {self.current_sound_path}")
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

    def stop_alarm(self):
        """Остановка будильника"""
        if self.alarm_player:
            self.alarm_player.pause()
            self.alarm_player = None
            print("Будильник остановлен")

    def run(self):
        """Запуск приложения"""
        pyglet.app.run()


if __name__ == "__main__":
    # Создание папки ресурсов если её нет
    Path("res").mkdir(exist_ok=True)

    # Запуск приложения
    app = AlarmApp()
    app.run()