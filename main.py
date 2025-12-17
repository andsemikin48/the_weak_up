import pyglet
from datetime import datetime, timedelta
from pyglet import shapes
import os
from pathlib import Path


class Button:
    """Класс кнопки"""
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
    def __init__(self, alarm_app, width, height, title):
        super().__init__(width=width, height=height, caption=title)
        self.app = alarm_app
        self.buttons = []
        self.size_button = 260  # Стандартная ширина кнопки

    def create_button(self, x, y, color, text, width=None, height=50, **kwargs):
        """Создание кнопки с сохранением ссылки"""
        if width is None:
            width = self.size_button
        button = Button(x, y, width, height, color, text, **kwargs)
        self.buttons.append(button)
        return button

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_close(self):
        self.close()
        return True

    def on_draw(self):
        """Базовая отрисовка окна"""
        self.clear()


class MainWindow(BaseWindow):
    """Главное окно приложения"""
    def __init__(self, alarm_app):
        super().__init__(alarm_app, width=800, height=600, title="Будильник")
        self.background_image = None
        self.child_windows = []
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
            if not alarm['enabled']:
                continue

            if alarm['type'] == 'date':
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

            elif alarm['type'] == 'weekly':
                # Создаем время будильника
                alarm_time = datetime.strptime(alarm['time'], "%H:%M").time()
                current_weekday = now.weekday()

                # Ищем ближайший выбранный день недели
                min_days_diff = float('inf')

                for weekday in alarm['weekdays']:
                    days_ahead = (weekday - current_weekday) % 7
                    if days_ahead == 0:  # Сегодня
                        # Проверяем, не прошло ли уже время сегодня
                        alarm_datetime_today = datetime.combine(now.date(), alarm_time)
                        if alarm_datetime_today >= now:
                            days_ahead = 0
                        else:
                            days_ahead = 7

                    if days_ahead < min_days_diff:
                        min_days_diff = days_ahead

                # Вычисляем дату ближайшего срабатывания
                next_date = now.date() + timedelta(days=min_days_diff)
                alarm_datetime = datetime.combine(next_date, alarm_time)
                diff = alarm_datetime - now

                if diff.total_seconds() > 0:  # Только будущие будильники
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

    def draw_alarms_list(self):
        """Список будильников"""
        if not self.app.alarms:
            return

        start_x = 20
        start_y = 30

        for i, alarm in enumerate(self.app.alarms[:5]):
            y_pos = start_y + i * 34

            if alarm['type'] == 'date':
                day_month = f"{alarm['date'][8:10]}.{alarm['date'][5:7]}"
                alarm_info = f"{day_month} {alarm['time']}"
            else:
                weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                if alarm['weekdays']:
                    selected_days = [weekdays_ru[day] for day in alarm['weekdays']]
                    alarm_info = f"{','.join(selected_days)} {alarm['time']}"
                else:
                    alarm_info = f"- {alarm['time']}"

            status = "Вкл" if alarm['enabled'] else "Выкл"

            pyglet.text.Label(
                f"{alarm_info} {status}",
                font_name="Arial", font_size=24,
                x=start_x, y=y_pos,
                anchor_x="left", anchor_y="center",
                color=(200, 200, 255, 255)
            ).draw()

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
        self.draw_alarms_list()

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
            pyglet.clock.schedule_once(lambda dt: self.open_alarm_window(), 0.1)

        elif button == self.btn_settings:
            pyglet.clock.schedule_once(lambda dt: self.open_settings_window(), 0.1)

        elif button == self.btn_stop:
            self.app.stop_alarm()

        elif button == self.btn_list:
            pyglet.clock.schedule_once(lambda dt: self.open_list_window(), 0.1)

    def open_alarm_window(self):
        """Открыть окно будильника"""
        main_x, main_y = self.get_location()

        def create_window():
            alarm_window = AlarmWindow(self)
            alarm_window.set_location(main_x + 50, main_y + 50)

        pyglet.clock.schedule_once(lambda dt: create_window(), 0.05)

    def open_settings_window(self):
        """Открыть окно настроек"""
        main_x, main_y = self.get_location()

        def create_window():
            settings_window = SettingsWindow(self.app)
            settings_window.set_location(main_x + 100, main_y + 100)

        pyglet.clock.schedule_once(lambda dt: create_window(), 0.05)

    def open_list_window(self):
        """Открыть окно списка"""
        main_x, main_y = self.get_location()

        def create_window():
            list_window = AlarmListWindow(self.app)
            list_window.set_location(main_x + 150, main_y + 150)

        pyglet.clock.schedule_once(lambda dt: create_window(), 0.05)


class AlarmWindow(pyglet.window.Window):
    """Окно установки будильника"""
    def __init__(self, main_window):
        super().__init__(width=600, height=550, caption="Установка будильника")
        self.main_window = main_window

        # Тип будильника: 'date' (по дате) или 'weekly' (по дням недели)
        self.alarm_type = 'date'  # По умолчанию

        # Устанавливаем ТЕКУЩЕЕ время
        now = datetime.now()
        time_str = now.strftime("%H%M")  # "1430"
        self.time_digits = [int(digit) for digit in time_str]

        # Устанавливаем ТЕКУЩУЮ дату
        date_str = now.strftime("%d%m%Y")  # "01012025"
        self.date_digits = [int(digit) for digit in date_str]

        # Дни недели (0-понедельник, 6-воскресенье)
        self.selected_weekdays = [now.weekday()]  # Выбранные дни недели

        # Повтор через 5 минут
        self.repeat_5min = False

        # Загрузка спрайтов
        self.time_sprites = self.load_digit_sprites()
        self.date_sprites = self.load_digit_sprites()
        self.weekday_sprites = self.load_weekday_sprites()

        # Спрайты для переключателей
        self.type_sprites = {
            'date': None,
            'weekly': None
        }
        self.repeat_sprite = None
        self.load_type_sprites()

        # Области кликов
        self.time_areas = []
        self.date_areas = []
        self.type_areas = []
        self.weekday_areas = []
        self.repeat_area = None

        self.setup_ui()
        self.setup_click_areas()

    def load_digit_sprites(self):
        """Загрузка цифр"""
        digit_sprites = []
        for i in range(10):
            try:
                path = Path(f"res/{i}.png")
                if path.exists():
                    images = pyglet.image.load(str(path))
                    sprite = pyglet.sprite.Sprite(images, x=0, y=0)
                    sprite.scale = 0.7
                    digit_sprites.append(sprite)
                else:
                    digit_sprites.append(None)
            except:
                digit_sprites.append(None)
        return digit_sprites

    def load_weekday_sprites(self):
        """Загрузка спрайтов дней недели"""
        weekday_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        sprites = []
        for name in weekday_names:
            try:
                path = Path(f"res/{name}.png")
                if path.exists():
                    img = pyglet.image.load(str(path))
                    sprite = pyglet.sprite.Sprite(img, x=0, y=0)
                    sprite.scale = 0.7
                    sprites.append(sprite)
                else:
                    sprites.append(None)
            except:
                sprites.append(None)
        return sprites

    def load_type_sprites(self):
        """Загрузка спрайтов переключателей"""
        try:
            # Загружаем спрайт для типа "по дате"
            path = Path("res/type_date.png")
            if path.exists():
                img = pyglet.image.load(str(path))
                self.type_sprites['date'] = pyglet.sprite.Sprite(img, x=0, y=0)
            else:
                # Если файла нет, создаем текстовую метку как запасной вариант
                self.type_sprites['date'] = None
        except Exception as e:
            print(f"Ошибка загрузки type_date.png: {e}")
            self.type_sprites['date'] = None

        try:
            # Загружаем спрайт для типа "по дням недели"
            path = Path("res/type_weekly.png")
            if path.exists():
                img = pyglet.image.load(str(path))
                self.type_sprites['weekly'] = pyglet.sprite.Sprite(img, x=0, y=0)
            else:
                self.type_sprites['weekly'] = None
        except Exception as e:
            print(f"Ошибка загрузки type_weekly.png: {e}")
            self.type_sprites['weekly'] = None

        try:
            # Загружаем спрайт для чекбокса повтора (выключенное состояние)
            path = Path("res/check_off.png")
            if path.exists():
                img = pyglet.image.load(str(path))
                self.repeat_sprite = pyglet.sprite.Sprite(img, x=0, y=0)
            else:
                self.repeat_sprite = None
        except Exception as e:
            print(f"Ошибка загрузки check_off.png: {e}")
            self.repeat_sprite = None

    def setup_ui(self):
        """Настройка интерфейса"""
        # Кнопка добавления
        self.btn_add = Button(
            x=300,
            y=30,
            width=260,
            height=50,
            color=(50, 180, 50),
            text="Добавить будильник",
            font_size=18
        )

    def setup_click_areas(self):
        """Настройка областей кликов"""
        # Области для переключения типа будильника
        self.type_areas = [
            (250, self.height - 100, 120*0.8, 35, 'date'),     # По дате
            (350, self.height - 100, 120*0.8, 35, 'weekly')   # По дням недели
        ]

        # Время: ЧЧ:ММ
        time_x = 150
        time_y = self.height - 170
        for i in range(4):
            x_pos = time_x + i * 60
            if i == 2:
                x_pos += 30
            elif i > 2:
                x_pos += 20
            self.time_areas.append((x_pos, time_y - 25, 40, 50, i))

        # Дата: ДД.ММ.ГГГГ (только для типа 'date')
        date_x = 150
        offset_click = 0
        date_y = self.height - 250
        for i in range(8):
            x_pos = date_x + i * 40 + offset_click
            if i == 2 or i == 4:
                offset_click += 30
                x_pos += 30
            if not (i == 4 or i == 5):
                self.date_areas.append((x_pos, date_y - 20, 25, 40, i))

        # Дни недели (только для типа 'weekly')
        weekday_start_x = 100
        weekday_y = self.height - 250
        for i in range(7):
            x_pos = weekday_start_x + i * 70
            self.weekday_areas.append((x_pos, weekday_y - 25, 60, 50, i))

        # Повтор через 5 минут
        self.repeat_area = (300, self.height - 350, 150, 40)

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

        # Тип будильника
        type_label = pyglet.text.Label(
            "Тип будильника:", font_name="Arial", font_size=18,
            x=50, y=self.height - 80,
            anchor_x="left", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        type_label.draw()

        # Отрисовка переключателей типа
        if self.type_sprites['date']:
            sprite = self.type_sprites['date']
            sprite.x = 250
            sprite.y = self.height - 100
            sprite.scale = 0.8
            if self.alarm_type == 'date':
                sprite.color = (255, 255, 255)
            else:
                sprite.color = (150, 150, 150)
            sprite.draw()

        if self.type_sprites['weekly']:
            sprite = self.type_sprites['weekly']
            sprite.x = 350
            sprite.y = self.height - 100
            sprite.scale = 0.8
            if self.alarm_type == 'weekly':
                sprite.color = (255, 255, 255)
            else:
                sprite.color = (150, 150, 150)
            sprite.draw()

        # Подписи
        time_label = pyglet.text.Label(
            "Время:", font_name="Arial", font_size=20,
            x=50, y=self.height - 170,
            anchor_x="left", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        time_label.draw()

        # Двоеточие
        time_y = self.height - 170
        colon_x = 150 + 2 * 50 + 5
        try:
            colon = pyglet.sprite.Sprite(pyglet.image.load("res/dthc.png"),
                                         x=colon_x, y=time_y-25)
            colon.scale = 0.7
            colon.draw()
        except:
            pass

        # Отрисовка времени
        for i in range(4):
            x_pos = 150 + i * 60
            if i == 2:
                x_pos += 30
            elif i > 2:
                x_pos += 20

            digit = self.time_digits[i]
            sprite = self.time_sprites[digit]
            if sprite is not None:
                sprite_copy = pyglet.sprite.Sprite(sprite.image, x=x_pos, y=time_y -25)
                sprite_copy.scale = 0.7
                sprite_copy.draw()
            else:
                label = pyglet.text.Label(
                    str(digit), font_name="Arial", font_size=36,
                    x=x_pos + 20, y=time_y,
                    anchor_x="center", anchor_y="center",
                    color=(255, 255, 255, 255)
                )
                label.draw()

        if self.alarm_type == 'date':
            # Отрисовка даты
            date_label = pyglet.text.Label(
                "Дата:", font_name="Arial", font_size=20,
                x=50, y=self.height - 250,
                anchor_x="left", anchor_y="center",
                color=(255, 255, 255, 255)
            )
            date_label.draw()

            # Точки в дате
            date_y = self.height - 250
            offset = 0
            for pos in [2, 5]:
                dot_x = 150 + pos * 30 + 30
                try:
                    dot = pyglet.sprite.Sprite(pyglet.image.load("res/thc.png"))
                    dot.x = dot_x
                    dot.y = date_y - 20
                    dot.scale = 0.7
                    dot.draw()
                except:
                    pass

            # Отрисовка даты
            offset = 0
            for i in range(8):
                x_pos = 150 + i * 40 + offset
                if i == 2 or i == 4:
                    x_pos += 30
                    offset += 30

                digit = self.date_digits[i]
                sprite = self.date_sprites[digit]
                if sprite is not None:
                    sprite_copy = pyglet.sprite.Sprite(sprite.image, x=x_pos, y=date_y - 20)
                    sprite_copy.scale = 0.7
                    sprite_copy.draw()
                else:
                    label = pyglet.text.Label(
                        str(digit), font_name="Arial", font_size=28,
                        x=x_pos + 12, y=date_y,
                        anchor_x="center", anchor_y="center",
                        color=(255, 255, 255, 255)
                    )
                    label.draw()
        else:
            # Отрисовка дней недели
            weekday_label = pyglet.text.Label(
                "Выбрать дени недели:", font_name="Arial", font_size=20,
                x=50, y=self.height - 220,
                anchor_x="left", anchor_y="center",
                color=(255, 255, 255, 255)
            )
            weekday_label.draw()

            # Отрисовка спрайтов дней недели
            date_y = self.height - 250
            for i in range(7):
                x_pos = 100 + i * 70
                sprite = self.weekday_sprites[i]
                if sprite is not None:
                    sprite_copy = pyglet.sprite.Sprite(sprite.image, x=x_pos, y=date_y - 25)
                    sprite_copy.scale = 0.7
                    if i in self.selected_weekdays:
                        sprite_copy.color = (255, 255, 255)
                    else:
                        sprite_copy.color = (100, 100, 100)
                    sprite_copy.draw()

        # Отрисовка переключателя повтора
        repeat_label = pyglet.text.Label(
            "Повтор через 5 минут:", font_name="Arial", font_size=18,
            x=50, y=self.height - 330,
            anchor_x="left", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        repeat_label.draw()

        if self.repeat_sprite:
            self.repeat_sprite.x = 320
            self.repeat_sprite.y = self.height - 360
            self.repeat_sprite.scale = 0.7

            # Загружаем нужный спрайт в зависимости от состояния
            try:
                if self.repeat_5min:
                    path = Path("res/check_on.png")
                    if path.exists():
                        img = pyglet.image.load(str(path))
                        self.repeat_sprite.image = img
                    else:
                        # Если файла нет, используем запасной вариант
                        self.repeat_sprite.color = (100, 255, 100)
                else:
                    path = Path("res/check_off.png")
                    if path.exists():
                        img = pyglet.image.load(str(path))
                        self.repeat_sprite.image = img
                    else:
                        self.repeat_sprite.color = (150, 150, 150)
            except Exception as e:
                print(f"Ошибка загрузки спрайта чекбокса: {e}")

            self.repeat_sprite.draw()

        # Кнопка
        self.btn_add.draw()

        # Подсказка
        help_label = pyglet.text.Label(
            "Кликните на цифру/элемент чтобы изменить",
            font_name="Arial", font_size=12,
            x=self.width//2, y=15,
            anchor_x="center", anchor_y="center",
            color=(200, 200, 200, 255)
        )
        help_label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""

        # Кнопка добавления
        if self.btn_add.is_clicked(x, y):
            self.add_alarm()
            return

        # Клики по переключателям типа
        for area_x, area_y, width, height, alarm_type in self.type_areas:
            if area_x <= x <= area_x + width and area_y <= y <= area_y + height:
                self.alarm_type = alarm_type
                return

        # Клики по цифрам времени
        for area_x, area_y, width, height, idx in self.time_areas:
            if (area_x <= x <= area_x + width and
                    area_y <= y <= area_y + height):
                self.change_time_digit(idx)
                return

        # Клики по цифрам даты (только если тип 'date')
        if self.alarm_type == 'date':
            for area_x, area_y, width, height, idx in self.date_areas:
                if area_x <= x <= area_x + width and area_y <= y <= area_y + height:
                    self.change_date_digit(idx)
                    return

        # Клики по дням недели (только если тип 'weekly')
        if self.alarm_type == 'weekly':
            for area_x, area_y, width, height, idx in self.weekday_areas:
                if area_x <= x <= area_x + width and area_y <= y <= area_y + height:
                    if idx in self.selected_weekdays:
                        self.selected_weekdays.remove(idx)
                    else:
                        self.selected_weekdays.append(idx)
                    return

        # Клик по переключателю повтора
        if self.repeat_area:
            area_x, area_y, width, height = self.repeat_area
            if area_x <= x <= area_x + width and area_y <= y <= area_y + height:
                self.repeat_5min = not self.repeat_5min
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
        if len(self.main_window.app.alarms) >= 5:
            print("Максимум 5 будильников!")
            return

        # Формируем время
        hours = self.time_digits[0] * 10 + self.time_digits[1]
        minutes = self.time_digits[2] * 10 + self.time_digits[3]

        # Проверяем время
        if hours > 23 or minutes > 59:
            print("Некорректное время!")
            return

        time_str = f"{hours:02d}:{minutes:02d}"

        if self.alarm_type == 'date':
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
                'type': 'date',
                'date': f"{year:04d}-{month:02d}-{day:02d}",
                'time': time_str,
                'repeat_5min': self.repeat_5min,
                'enabled': True,
                'last_triggered': None,
                'repeat_scheduled': None
            }

            self.main_window.app.alarms.append(new_alarm)
            print(f"Будильник добавлен (по дате): {new_alarm['date']} {new_alarm['time']}")

        else:  # подразумеваем что weekly
            # Проверяем, что выбран хотя бы один день
            if not self.selected_weekdays:
                print("Выберите хотя бы один день недели!")
                return

            # Добавляем будильник
            new_alarm = {
                'type': 'weekly',
                'weekdays': self.selected_weekdays.copy(),
                'time': time_str,
                'repeat_5min': self.repeat_5min,
                'enabled': True,
                'last_triggered': None,
                'repeat_scheduled': None
            }

            weekdays_ru = ["Понедельник", "Вторник", "Среда", "Четверг",
                           "Пятница", "Суббота", "Воскресенье"]
            selected_days = ",".join([weekdays_ru[day] for day in self.selected_weekdays])
            self.main_window.app.alarms.append(new_alarm)
            print(f"Будильник добавлен (еженедельный): {selected_days} {new_alarm['time']}")

        pyglet.clock.schedule_once(lambda dt: self.close(), 0.01)


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
                         color=(0, 0, 0)).draw()

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
            # Открываем окно выбора мелодии
            def open_sound_window():
                sound_window = SoundSelectWindow(self.app)
                # Позиционируем окно рядом с текущим
                main_x, main_y = self.get_location()
                sound_window.set_location(main_x + 50, main_y + 50)

            pyglet.clock.schedule_once(lambda dt: open_sound_window(), 0.1)

        elif button == self.btn_reset:
            pyglet.clock.schedule_once(lambda dt: self.app.alarms.clear(), 0.1)
            print("Все будильники сброшены")


class AlarmListWindow(BaseWindow):
    """Окно списка будильников"""
    def __init__(self, app):
        super().__init__(app, width=500, height=400, title="Список будильников")
        self.delete_buttons = []  # Кнопки удаления для каждого будильника
        self.toggle_buttons = []  # Кнопки включения/выключения

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
            "Тип       Дата/День    Время      Статус",
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
            # Очищаем старые кнопки
            self.delete_buttons.clear()
            self.toggle_buttons.clear()

            for i, alarm in enumerate(self.app.alarms):
                y_pos = self.height - 120 - i * 30

                # Тип будильника
                if alarm['type'] == 'date':
                    type_text = "Дата"
                    # Форматирование даты из YYYY-MM-DD в DD.MM.YYYY
                    date_parts = alarm['date'].split('-')
                    date_text = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0][2:]}"
                else:
                    type_text = "Неделя"
                    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                    weekday_idx = alarm['weekdays'][0] if alarm['weekdays'] else 0
                    date_text = weekdays_ru[weekday_idx]

                # Статус
                status_color = (100, 255, 100) if alarm['enabled'] else (255, 100, 100)
                status_text = "ВКЛ" if alarm['enabled'] else "ВЫКЛ"

                # Повтор через 5 мин
                repeat_text = "Повт" if alarm.get('repeat_5min', False) else ""

                # Тип
                type_label = pyglet.text.Label(
                    type_text, font_name="Arial", font_size=14,
                    x=50, y=y_pos,
                    anchor_x="left", anchor_y="center",
                    color=(200, 200, 255, 255)
                )
                type_label.draw()

                # Дата/День
                date_label = pyglet.text.Label(
                    date_text, font_name="Arial", font_size=14,
                    x=120, y=y_pos,
                    anchor_x="left", anchor_y="center",
                    color=(200, 200, 255, 255)
                )
                date_label.draw()

                # Время
                time_label = pyglet.text.Label(
                    alarm['time'], font_name="Arial", font_size=14,
                    x=220, y=y_pos,
                    anchor_x="left", anchor_y="center",
                    color=(200, 200, 255, 255)
                )
                time_label.draw()

                # Статус
                status_label = pyglet.text.Label(
                    status_text, font_name="Arial", font_size=14,
                    x=290, y=y_pos,
                    anchor_x="center", anchor_y="center",
                    color=status_color + (255,)
                )
                status_label.draw()

                # Повтор
                repeat_label = pyglet.text.Label(
                    repeat_text, font_name="Arial", font_size=12,
                    x=330, y=y_pos,
                    anchor_x="center", anchor_y="center",
                    color=(255, 255, 100, 255)
                )
                repeat_label.draw()

                # Кнопка включения/выключения
                toggle_color = (100, 200, 100) if alarm['enabled'] else (200, 100, 100)
                toggle_text = "Выкл" if alarm['enabled'] else "Вкл"
                toggle_button = Button(
                    x=370,
                    y=y_pos - 10,
                    width=50,
                    height=25,
                    color=toggle_color,
                    text=toggle_text,
                    font_size=10
                )
                toggle_button.draw()
                self.toggle_buttons.append((toggle_button, i))

                # Кнопка удаления
                delete_button = Button(
                    x=430,
                    y=y_pos - 10,
                    width=60,
                    height=25,
                    color=(200, 80, 80),
                    text="Удалить",
                    font_size=10
                )
                delete_button.draw()
                self.delete_buttons.append((delete_button, i))

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        # Проверка кликов по кнопкам включения/выключения
        for toggle_button, index in self.toggle_buttons:
            if toggle_button.is_clicked(x, y):
                if index < len(self.app.alarms):
                    # Переключаем статус
                    self.app.alarms[index]['enabled'] = not self.app.alarms[index]['enabled']
                    print(f"Будильник {index+1} переключен: {'ВКЛ' if self.app.alarms[index]['enabled'] else 'ВЫКЛ'}")
                    return

        # Проверка кликов по кнопкам удаления
        for delete_button, index in self.delete_buttons:
            if delete_button.is_clicked(x, y):
                if index < len(self.app.alarms):
                    # Удаляем будильник
                    def delete_alarm(dt):
                        if index < len(self.app.alarms):
                            del self.app.alarms[index]
                            print(f"Будильник {index+1} удален")

                    pyglet.clock.schedule_once(delete_alarm, 0.01)
                    return

class SoundSelectWindow(BaseWindow):
    """Окно выбора мелодии будильника"""
    def __init__(self, app):
        super().__init__(app, width=500, height=500, title="Выбор мелодии")
        self.sound_files = []
        self.selected_index = -1
        self.scroll_offset = 0
        self.max_visible_items = 10
        self.scroll_up_button = None
        self.scroll_down_button = None
        self.select_button = None
        self._sound_files_lock = False  # Флаг блокировки изменений

        self.load_sound_files()
        self.setup_ui()

    def load_sound_files(self):
        """Загрузка списка звуковых файлов из папки res"""
        # Создаем новый список вместо изменения существующего
        new_sound_files = []
        res_path = Path("res")

        if res_path.exists():
            # Ищем файлы .wav и .mp3
            for ext in ["*.wav", "*.mp3"]:
                for file_path in res_path.glob(ext):
                    new_sound_files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'is_current': str(file_path) == self.app.current_sound_path
                    })

        # Сортируем по имени
        new_sound_files.sort(key=lambda x: x['name'].lower())

        # Заменяем весь список целиком, а не изменяем его по частям
        self.sound_files = new_sound_files

    def setup_ui(self):
        """Настройка интерфейса окна выбора мелодии"""
        # Кнопка выбора
        self.select_button = self.create_button(
            x=self.width // 2 - 200,
            y=10,
            width=200,
            height=40,
            color=(50, 180, 50),
            text="Выбрать",
            font_size=18
        )

        # Кнопка закрыть
        self.cancel_button = self.create_button(
            x=self.width // 2 + 20,
            y=10,
            width=200,
            height=40,
            color=(200, 80, 80),
            text="Закрыть",
            font_size=18
        )

        # Кнопки прокрутки
        scroll_button_width = 40
        self.scroll_up_button = self.create_button(
            x=self.width - scroll_button_width - 20,
            y=self.height - 150,
            width=scroll_button_width,
            height=30,
            color=(100, 100, 150),
            text="↑",
            font_size=10
        )

        self.scroll_down_button = self.create_button(
            x=self.width - scroll_button_width - 20,
            y=70,
            width=scroll_button_width,
            height=30,
            color=(100, 100, 150),
            text="↓",
            font_size=10
        )

    def on_draw(self):
        """Отрисовка окна выбора мелодии"""
        super().on_draw()

        # Фон
        shapes.Rectangle(0, 0, self.width, self.height,
                         color=(0, 0, 0)).draw()

        # Заголовок
        title = pyglet.text.Label(
            "Выберите мелодию будильника",
            font_name="Arial", font_size=20,
            x=self.width // 2, y=self.height - 40,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )
        title.draw()

        # Информация о текущей мелодии
        current_info = pyglet.text.Label(
            f"Текущая: {Path(self.app.current_sound_path).name}",
            font_name="Arial", font_size=14,
            x=20, y=self.height - 70,
            anchor_x="left", anchor_y="center",
            color=(200, 200, 100, 255)
        )
        current_info.draw()

        # Список файлов
        if not self.sound_files:
            no_files_label = pyglet.text.Label(
                "В папке 'res' нет файлов .wav или .mp3",
                font_name="Arial", font_size=16,
                x=self.width // 2, y=self.height // 2,
                anchor_x="center", anchor_y="center",
                color=(200, 100, 100, 255)
            )
            no_files_label.draw()
            return

        # Область списка
        list_start_y = self.height - 100
        list_height = 350
        item_height = 30

        # Фон списка
        shapes.Rectangle(20, list_start_y - list_height + 20,
                         self.width - 80, list_height - 40,
                         color=(50, 60, 80)).draw()

        # Создаем копию данных для безопасной итерации
        visible_files = []
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_items, len(self.sound_files))

        # Копируем только видимые элементы
        for i in range(start_idx, end_idx):
            if i < len(self.sound_files):
                # Создаем копию каждого элемента
                sound_file = dict(self.sound_files[i])
                sound_file['original_index'] = i  # Сохраняем оригинальный индекс
                visible_files.append(sound_file)

        # Отрисовка видимых элементов
        for i, sound_file in enumerate(visible_files):
            y_pos = list_start_y - (i + 1) * item_height
            original_idx = sound_file['original_index']

            # Цвет фона в зависимости от выбора
            if original_idx == self.selected_index:
                color = (80, 100, 150)  # Выбранный элемент
            elif sound_file['is_current']:
                color = (70, 120, 70)   # Текущая мелодия
            else:
                color = (60, 70, 90)    # Обычный элемент

            # Фон элемента
            shapes.Rectangle(25, y_pos - 25, self.width - 90, item_height,
                             color=color).draw()

            # Имя файла
            text_color = (255, 255, 255) if original_idx == self.selected_index or sound_file['is_current'] else (200, 200, 200)

            file_label = pyglet.text.Label(
                sound_file['name'],
                font_name="Arial", font_size=14,
                x=30, y=y_pos - 10,
                anchor_x="left", anchor_y="center",
                color=text_color + (255,)
            )
            file_label.draw()

            # Индикатор текущей мелодии
            if sound_file['is_current']:
                current_mark = pyglet.text.Label(
                    "*",
                    font_name="Arial", font_size=12,
                    x=self.width - 100, y=y_pos - 10,
                    anchor_x="right", anchor_y="center",
                    color=(100, 255, 100, 255)
                )
                current_mark.draw()

        # Индикатор прокрутки
        if len(self.sound_files) > self.max_visible_items:
            scroll_info = pyglet.text.Label(
                f"{start_idx+1}-{end_idx} из {len(self.sound_files)}",
                font_name="Arial", font_size=12,
                x=self.width - 40, y=list_start_y - list_height - 20,
                anchor_x="center", anchor_y="center",
                color=(150, 150, 150, 255)
            )
            scroll_info.draw()

        # Кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов"""
        # Кнопка выбора
        if self.select_button and self.select_button.is_clicked(x, y):
            if 0 <= self.selected_index < len(self.sound_files):
                # Берем данные напрямую без промежуточных переменных
                self.app.current_sound_path = self.sound_files[self.selected_index]['path']
                print(f"Выбрана мелодия: {self.sound_files[self.selected_index]['name']}")
            return

        # Кнопка закрыть
        if self.cancel_button and self.cancel_button.is_clicked(x, y):
            # Просто закрываем окно
            self.close()
            return

        # Кнопки прокрутки
        if self.scroll_up_button and self.scroll_up_button.is_clicked(x, y):
            if self.scroll_offset > 0:
                self.scroll_offset -= 1
            return

        if self.scroll_down_button and self.scroll_down_button.is_clicked(x, y):
            if self.scroll_offset < len(self.sound_files) - self.max_visible_items:
                self.scroll_offset += 1
            return

        # Клик по элементам списка
        list_start_y = self.height - 100
        list_height = 350
        item_height = 40

        if 20 <= x <= self.width - 60:
            list_y_start = list_start_y - list_height
            list_y_end = list_start_y

            if list_y_start <= y <= list_y_end:
                # Определяем, по какому элементу кликнули
                click_idx = self.scroll_offset + int((list_y_end - y) // item_height)

                if 0 <= click_idx < len(self.sound_files):
                    # Просто меняем индекс, не трогая сам список
                    self.selected_index = click_idx

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Обработка прокрутки колесиком мыши"""
        if scroll_y > 0 and self.scroll_offset > 0:  # Прокрутка вверх
            self.scroll_offset -= 1
        elif scroll_y < 0 and self.scroll_offset < len(self.sound_files) - self.max_visible_items:  # Прокрутка вниз
            self.scroll_offset += 1

class MessageWindow(BaseWindow):
    """Окно с сообщением"""
    def __init__(self, app, message):
        super().__init__(app, width=400, height=250, title="Сообщение")  # Увеличил размеры
        self.message = message
        self.setup_ui()

    def setup_ui(self):
        center_x = self.width // 2

        # Текст сообщения (динамический)
        self.message_label = pyglet.text.Label(
            self.message,
            font_name="Arial", font_size=18,
            x=center_x, y=self.height * 0.6,
            anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255)
        )

        # Кнопка закрытия
        self.btn_close = self.create_button(
            x=center_x - 100,
            y=50,
            width=200,
            height=40,
            color=(200, 80, 80),
            text="Я понял",
            font_size=18
        )

    def on_draw(self):
        """Отрисовка окна с сообщением"""
        self.clear()

        # Фон
        shapes.Rectangle(0, 0, self.width, self.height,
                         color=(0, 0, 0)).draw()

        # Заголовок и текст

        self.message_label.draw()

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
        if button == self.btn_close:
            self.close()

class AlarmApp:
    """Основной класс приложения"""
    def __init__(self):
        self.alarms = []  # Список будильников
        self.current_sound_path = "res/alarm.wav"
        self.alarm_player = None
        self.alarm_start_time = None  # Время срабатывания будильника
        self.current_alarm_index = None  # Индекс текущего будильника
        self.is_repeat_alarm = False  # Проверка повтор ли это
        self.waiting_for_repeat = False  # Ждём ли повтор после остановки основного
        self.alarm_waiting_for_repeat = None  # Индекс будильника, для которого ждём повтор

        # Создание главного окна
        self.main_window = MainWindow(self)

        # Запуск таймера обновления
        pyglet.clock.schedule_interval(self.update, 1.0)

    def update(self, dt):
        """Обновление состояния приложения"""
        self.main_window.update_time()
        self.check_alarms()

    def trigger_alarm(self, alarm_index, is_repeat=False):
        """Срабатывание будильника"""
        # Проверяем, что индекс в пределах диапазона
        if alarm_index < 0 or alarm_index >= len(self.alarms):
            print(f"Ошибка: неверный индекс будильника {alarm_index}")
            return

        # Выводим сообщение
        message_window = MessageWindow(self, message =(f"Будильник {alarm_index+1} сработал!"))
        try:
            main_x, main_y = self.main_window.get_location()
            message_window.set_location(main_x+200, main_y+200)
        except:
            message_window.set_location(300,300)
        print(f"БУДИЛЬНИК {alarm_index+1} СРАБОТАЛ! {'(ПОВТОР)' if is_repeat else ''}")

        self.current_alarm_index = alarm_index
        self.is_repeat_alarm = is_repeat
        self.alarm_start_time = datetime.now()
        self.waiting_for_repeat = False  # Сбрасываем флаг ожидания

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

            # Проверяем, что current_alarm_index в пределах диапазона
            if (self.current_alarm_index is not None and
                    self.current_alarm_index < len(self.alarms)):

                # Логика для основного будильника
                if not self.is_repeat_alarm:
                    alarm = self.alarms[self.current_alarm_index]

                    if alarm.get('repeat_5min'):
                        # Если включен повтор и нажали стоп - ждём повтора
                        self.waiting_for_repeat = True
                        self.alarm_waiting_for_repeat = self.current_alarm_index
                        alarm['repeat_scheduled'] = datetime.now() + timedelta(minutes=5)
                        print("Будильник остановлен, ждём повтор через 5 минут")
                    else:
                        # Если повтор не включен - просто останавливаем
                        print("Будильник остановлен")
                        self.waiting_for_repeat = False
                        self.alarm_waiting_for_repeat = None

                # Логика для повторного будильника
                elif self.is_repeat_alarm:
                    alarm = self.alarms[self.current_alarm_index]

                    if alarm['type'] == 'date':
                        # Для будильника по дате - отключаем полностью
                        alarm['enabled'] = False
                        print(f"Будильник {self.current_alarm_index+1} (по дате) отключен после повтора")
                    else:
                        # Для еженедельного - оставляем активным
                        print(f"Будильник {self.current_alarm_index+1} (еженедельный) остановлен, остаётся активным")

                    self.waiting_for_repeat = False
                    self.alarm_waiting_for_repeat = None

            self.current_alarm_index = None
            self.alarm_start_time = None
            self.is_repeat_alarm = False

    def check_alarms(self):
        """Проверка срабатывания будильников"""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday()

        # Автостоп основного будильника через 1 минуту
        if (self.alarm_player and
                self.alarm_start_time and
                not self.is_repeat_alarm and
                now - self.alarm_start_time >= timedelta(minutes=1)):

            print("Основной будильник остановлен (автостоп через 1 минуту)")

            # Проверяем, нужно ли ждать повтора
            if (self.current_alarm_index is not None and
                    self.current_alarm_index < len(self.alarms) and
                    self.alarms[self.current_alarm_index].get('repeat_5min')):

                self.waiting_for_repeat = True
                self.alarm_waiting_for_repeat = self.current_alarm_index
                self.alarms[self.current_alarm_index]['repeat_scheduled'] = now + timedelta(minutes=5)
                print("Ждём повтор через 5 минут")

            # Останавливаем звук
            if self.alarm_player:
                self.alarm_player.pause()
                self.alarm_player = None

            self.current_alarm_index = None
            self.alarm_start_time = None
            self.is_repeat_alarm = False
            return

        # Используем копию списка для итерации, чтобы избежать изменения во время итерации
        alarms_to_check = list(enumerate(self.alarms))

        for i, alarm in alarms_to_check:
            if not alarm['enabled']:
                continue

            # Проверка основного срабатывания (только если не ждём повтор для этого будильника)
            should_check_main = True
            if (self.waiting_for_repeat and
                    self.alarm_waiting_for_repeat is not None and
                    i == self.alarm_waiting_for_repeat):
                should_check_main = False

            if should_check_main:
                if alarm['type'] == 'date':
                    if alarm['date'] == current_date and alarm['time'] == current_time:
                        # Проверяем, не срабатывал ли уже сегодня
                        last_triggered = alarm.get('last_triggered')
                        if last_triggered and last_triggered.date() == now.date():
                            continue

                        self.trigger_alarm(i, is_repeat=False)
                        alarm['last_triggered'] = now
                        return

                elif alarm['type'] == 'weekly':
                    if current_weekday in alarm['weekdays'] and alarm['time'] == current_time:
                        last_triggered = alarm.get('last_triggered')
                        if last_triggered and last_triggered.date() == now.date():
                            continue

                        self.trigger_alarm(i, is_repeat=False)
                        alarm['last_triggered'] = now
                        return

            # Проверка повтора через 5 минут
            if (alarm.get('repeat_5min') and
                    alarm.get('repeat_scheduled') and
                    now >= alarm['repeat_scheduled']):

                self.trigger_alarm(i, is_repeat=True)
                # Сбрасываем расписание повтора
                alarm['repeat_scheduled'] = None
                self.waiting_for_repeat = False
                self.alarm_waiting_for_repeat = None
                return

    def run(self):
        """Запуск приложения"""
        pyglet.app.run()


if __name__ == "__main__":
    # Создание папки ресурсов если её нет
    Path("res").mkdir(exist_ok=True)

    # Запуск приложения
    app = AlarmApp()
    app.run()