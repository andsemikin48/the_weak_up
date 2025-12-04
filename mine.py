"""Это приложение будильник.
Функционал:
    основное окно содержит:
        текущее время
        текущие дата
        время до срабатывания ближайшего будильника
        кнопки установить будильник, выключить будильник, настройки.
     Вспомогательные окна:
        окно установки будильника
            окно текущих будильников(до 5)
                кнопки: удалить, изменить
            кнопки: установить время, закрыть
        окно настроек:
            установить фон.
            установить музыку.
            сбросить все будильники.
            закрыть
    используемые библиотеки: pyglet, time, io
"""


import pyglet
import time
from datetime import datetime, timedelta
from pyglet import shapes
from pyglet.window import key
import os

class AlarmApp:
    def __init__(self, width=800, height=600, name="Будильник"):
        self.width = width
        self.height = height
        self.alarms = []  # Список будильников: каждый будильник - словарь с временем и статусом
        self.background_image = pyglet.image.load('res/bg.jpg')
        self.alarm_sound = None
        self.alarm_player = None
        self.time_digits = [0, 0, 0, 0]
        self.digit_sprites = []
        for i in range(10):
            try:
                # Пробуем загрузить спрайт
                img = pyglet.image.load(f'res/{i}.png')
                self.digit_sprites.append(img)
            except:
                # Если нет файла, создаем текстовую метку
                label = pyglet.text.Label(
                    str(i), font_name="Times New Roman", font_size=36,
                    x=0, y=0, anchor_x="center", anchor_y="center"
                )
                self.digit_sprites.append(label)

        # Создание главного окна
        self.window = pyglet.window.Window(width, height, name)
        self.window.push_handlers(self)

        # Создание текстовых меток
        self.time_label = pyglet.text.Label(
            "", font_name="Times New Roman", font_size=48,
            x=width//2, y=height*0.7,
            anchor_x="center", anchor_y="center"
        )

        self.date_label = pyglet.text.Label(
            "", font_name="Times New Roman", font_size=24,
            x=width//2, y=height*0.6,
            anchor_x="center", anchor_y="center"
        )

        self.next_alarm_label = pyglet.text.Label(
            "Нет активных будильников", font_name="Times New Roman", font_size=20,
            x=width//2, y=height*0.5,
            anchor_x="center", anchor_y="center",
            color=(255, 50, 50, 255)
        )

        # Кнопки (прямоугольники с текстом)
        button_height = 40
        button_width = 220
        button_y = height*0.3

        self.set_alarm_button = shapes.Rectangle(
            width//2 - button_width - 10, button_y, button_width, button_height,
            color=(50, 150, 50)
        )
        self.set_alarm_text = pyglet.text.Label(
            "Установить будильник", font_name="Times New Roman", font_size=16,
            x=width//2 - button_width - 10 + button_width//2, y=button_y + button_height//2,
            anchor_x="center", anchor_y="center"
        )

        self.settings_button = shapes.Rectangle(
            width//2 + 10, button_y, button_width, button_height,
            color=(50, 100, 200)
        )
        self.settings_text = pyglet.text.Label(
            "Настройки", font_name="Times New Roman", font_size=16,
            x=width//2 + 10 + button_width//2, y=button_y + button_height//2,
            anchor_x="center", anchor_y="center"
        )
        self.stop_button = shapes.Rectangle(
            width//2 -120, button_y-50, button_width, button_height,
            color=(50, 100, 200)
        )
        self.stop_text = pyglet.text.Label(
            "Остановить", font_name="Times New Roman", font_size=16,
            x=width//2 - 120 + button_width//2, y=button_y + button_height//2-50,
            anchor_x="center", anchor_y="center"
        )
        self.bg_button = shapes.Rectangle(
            width//2 -120, button_y+150, button_width, button_height,
            color=(50, 100, 200)
        )
        self.bg_text = pyglet.text.Label(
            "Сменить фон", font_name="Times New Roman", font_size=16,
            x=width//2 - 120 + button_width//2, y=button_y+150 + button_height//2,
            anchor_x="center", anchor_y="center"
        )

        # Флаги для вспомогательных окон
        self.show_alarm_window = False
        self.show_settings_window = False

        # Обновление времени каждую секунду
        pyglet.clock.schedule_interval(self.update_time, 1.0)

        # Загрузка звука по умолчанию
        self.load_default_sound()

        #Файловый менеджер
        self.show_file_manager = False
        self.current_directory = os.getcwd()
        self.file_list = []
        self.selected_file = None
        self.scroll_offset = 0

        self.update_file_list()

    def update_file_list(self):
        self.file_list = []
        try:
            if self.current_directory != os.path.dirname(self.current_directory):
                self.file_list.append(("..","directory"))
            for item in os.listdir(self.current_directory):
                item_path = os.path.join(self.current_directory, item)
                if os.path.isdir(item_path):
                    self.file_list.append((item, "directory"))
                elif item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.file_list.append((item, "image"))
                else:
                    self.file_list.append((item, "file"))

        except Exception as err:
            print(f"Ошибка {err}")

    def draw_file_manager(self):
        """Отрисовка файлового менеджера"""
        # Полупрозрачный фон
        overlay = shapes.Rectangle(0, 0, self.width, self.height, color=(0, 0, 0, 200))
        overlay.draw()

        # Окно файлового менеджера
        window_width = 600
        window_height = 500
        window_x = (self.width - window_width) // 2
        window_y = (self.height - window_height) // 2

        # Фон окна
        window_bg = shapes.Rectangle(
            window_x, window_y, window_width, window_height,
            color=(240, 240, 240)
        )
        window_bg.draw()

        # Рамка окна
        window_frame = shapes.Rectangle(
            window_x-2, window_y-2, window_width+4, window_height+4,
            color=(100, 100, 100)
        )
        window_frame.draw()

        # Заголовок окна
        title_bg = shapes.Rectangle(
            window_x, window_y + window_height - 50, window_width, 50,
            color=(200, 200, 200)
        )
        title_bg.draw()

        title = pyglet.text.Label(
            f"Выбор фона: {self.current_directory}",
            font_name="Times New Roman", font_size=18,
            x=self.width//2, y=window_y + window_height - 25,
            anchor_x="center", anchor_y="center"
        )
        title.draw()

        # Кнопка закрытия
        close_button = shapes.Rectangle(
            window_x + window_width - 40, window_y + window_height - 40, 30, 30,
            color=(255, 100, 100)
        )
        close_button.draw()

        close_text = pyglet.text.Label(
            "X", font_name="Times New Roman", font_size=16,
            x=window_x + window_width - 25, y=window_y + window_height - 25,
            anchor_x="center", anchor_y="center"
        )
        close_text.draw()

        # Область списка файлов
        list_x = window_x + 20
        list_y = window_y + window_height - 90
        list_width = window_width - 40
        list_height = window_height - 150

        # Фон списка
        list_bg = shapes.Rectangle(
            list_x, list_y - list_height, list_width, list_height,
            color=(255, 255, 255)
        )
        list_bg.draw()

        # Рамка списка
        list_frame = shapes.Rectangle(
            list_x-1, list_y - list_height - 1, list_width+2, list_height+2,
            color=(150, 150, 150)
        )
        list_frame.draw()

        # Отображение файлов
        item_height = 30
        max_items = list_height // item_height
        start_index = max(0, self.scroll_offset)
        end_index = min(len(self.file_list), start_index + max_items)

        for i, (file_name, file_type) in enumerate(self.file_list[start_index:end_index]):
            item_y = list_y - (i * item_height) - 20

            # Выделение выбранного файла
            if file_name == self.selected_file:
                selection_bg = shapes.Rectangle(
                    list_x, item_y - item_height, list_width, item_height,
                    color=(200, 220, 255)
                )
                selection_bg.draw()

            # Иконка в зависимости от типа
            if file_type == "directory":
                icon = "📁 "
                color = (0, 0, 200, 255)
            elif file_type == "image":
                icon = "🖼️ "
                color = (0, 150, 0, 255)
            else:
                icon = "📄 "
                color = (100, 100, 100, 255)

            # Имя файла
            file_label = pyglet.text.Label(
                f"{icon}{file_name}",
                font_name="Times New Roman", font_size=14,
                x=list_x + 10, y=item_y - item_height//2,
                anchor_x="left", anchor_y="center",
                color=color
            )
            file_label.draw()

        # Кнопки управления
        button_y = window_y + 40
        button_width = 120
        button_height = 40

        # Кнопка "Выбрать"
        select_button = shapes.Rectangle(
            window_x + 50, button_y, button_width, button_height,
            color=(50, 150, 50) if self.selected_file else (150, 150, 150)
        )
        select_button.draw()

        select_text = pyglet.text.Label(
            "Выбрать", font_name="Times New Roman", font_size=14,
            x=window_x + 50 + button_width//2, y=button_y + button_height//2,
            anchor_x="center", anchor_y="center"
        )
        select_text.draw()

        # Кнопка "Отмена"
        cancel_button = shapes.Rectangle(
            window_x + window_width - 50 - button_width, button_y, button_width, button_height,
            color=(150, 150, 150)
        )
        cancel_button.draw()

        cancel_text = pyglet.text.Label(
            "Отмена", font_name="Times New Roman", font_size=14,
            x=window_x + window_width - 50 - button_width//2, y=button_y + button_height//2,
            anchor_x="center", anchor_y="center"
        )
        cancel_text.draw()

        # Подсказка
        hint = pyglet.text.Label(
            "Поддерживаемые форматы: PNG, JPG, JPEG, BMP",
            font_name="Times New Roman", font_size=12,
            x=self.width//2, y=window_y + 20,
            anchor_x="center", anchor_y="center",
            color=(100, 100, 100, 255)
        )
        hint.draw()


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Прокрутка списка файлов"""
        if self.show_file_manager:
            self.scroll_offset = max(0, self.scroll_offset - int(scroll_y))




    def load_default_sound(self):
        # Создаем простой звук (в реальном приложении загрузите файл)
        try:
            # Пытаемся загрузить звуковой файл
            if os.path.exists("res/alarm.wav"):
                self.alarm_sound = pyglet.media.load("res/alarm.wav")
        except:
            # Если файла нет, создаем пустой плеер
            self.alarm_sound = None

    def update_time(self, dt):
        """Обновление времени и проверка будильников"""
        now = datetime.now()

        # Обновление времени
        self.time_label.text = now.strftime("%H:%M:%S")
        self.date_label.text = now.strftime("%d.%m.%Y")

        # Проверка будильников
        self.check_alarms(now)

        # Обновление информации о ближайшем будильнике
        self.update_next_alarm_info()

    def check_alarms(self, now):
        """Проверка срабатывания будильников"""
        current_time = now.strftime("%H:%M")
        for alarm in self.alarms:
            if alarm['time'] == current_time and not alarm['triggered']:
                alarm['triggered'] = True
                self.trigger_alarm()

    def trigger_alarm(self):
        """Срабатывание будильника"""

        print("Будильник сработал!")
        if self.alarm_sound:
            self.alarm_player = pyglet.media.Player()
            self.alarm_player.queue(self.alarm_sound)
            self.alarm_player.play()

    def stop_alarm(self):
        if hasattr(self, 'alarm_player') and self.alarm_player:
            self.alarm_player.pause()

    def update_next_alarm_info(self):
        """Обновление информации о ближайшем будильнике"""
        if not self.alarms:
            self.next_alarm_label.text = "Нет активных будильников"
            return

        now = datetime.now()
        next_alarm = None
        min_diff = timedelta(days=1)

        for alarm in self.alarms:
            if not alarm['triggered']:
                alarm_time = datetime.strptime(alarm['time'], "%H:%M")
                alarm_datetime = now.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0)

                if alarm_datetime < now:
                    alarm_datetime += timedelta(days=1)

                diff = alarm_datetime - now
                if diff < min_diff:
                    min_diff = diff
                    next_alarm = alarm

        if next_alarm:
            hours = min_diff.seconds // 3600
            minutes = (min_diff.seconds % 3600) // 60
            self.next_alarm_label.text = f"Следующий будильник через: {hours:02d}:{minutes:02d}"
        else:
            self.next_alarm_label.text = "Нет активных будильников"

    def on_draw(self):
        """Отрисовка окна"""
        self.window.clear()

        # Рисуем фон
        if self.background_image:
            self.background_image.blit(0, 0)

        # Рисуем метки
        self.time_label.draw()
        self.date_label.draw()
        self.next_alarm_label.draw()

        # Рисуем кнопки
        self.set_alarm_button.draw()
        self.set_alarm_text.draw()
        self.settings_button.draw()
        self.settings_text.draw()
        self.stop_button.draw()
        self.stop_text.draw()

        # Отрисовка вспомогательных окон
        if self.show_alarm_window:
            self.draw_alarm_window()
        elif self.show_settings_window:
            self.draw_settings_window()
            self.bg_button.draw()
            self.bg_text.draw()

        #Рисуем файл менеджер
        if self.show_file_manager:
            self.draw_file_manager()
    def draw_alarm_window(self):
        """Отрисовка окна установки будильника"""
        # Полупрозрачный фон
        overlay = shapes.Rectangle(0, 0, self.width, self.height, color=(0, 0, 0, 150))
        overlay.draw()

        # Окно
        window_width = 500
        window_height = 400
        window_x = (self.width - window_width) // 2
        window_y = (self.height - window_height) // 2

        # Фон окна
        window_bg = shapes.Rectangle(window_x-5, window_y-5, window_width+10, window_height+10, color=(255, 255, 100))
        window_frame = shapes.Rectangle(window_x, window_y, window_width, window_height,color=(40, 40, 40))
        window_bg.draw()
        window_frame.draw()

        # Заголовок
        title = pyglet.text.Label(
            "Установка будильника", font_name="Times New Roman", font_size=24,
            x=self.width//2, y=window_y + window_height - 40,
            anchor_x="center", anchor_y="center"
        )
        title.draw()

        # Блок для установки времени
        time_block_y = window_y + window_height - 120

        # Текст "Время:"
        time_label = pyglet.text.Label(
            "Время:", font_name="Times New Roman", font_size=20,
            x=window_x + 50, y=time_block_y,
            anchor_x="left", anchor_y="center"
        )
        time_label.draw()

        # 4 кнопки с цифрами (ЧЧ:ММ)
        digit_width = 50//2
        digit_height = 70//2
        start_x = window_x+170

        # Позиции для 4 цифр
        positions = [
            (start_x, time_block_y - 10),                    # Ч1
            (start_x + digit_width + 5, time_block_y - 10),  # Ч2
            (start_x + 2*digit_width + 20, time_block_y - 10),  # М1 (после двоеточия)
            (start_x + 3*digit_width + 25, time_block_y - 10),  # М2
        ]

        # Рисуем 4 кнопки с цифрами
        for i in range(4):
            x, y = positions[i]

            # Фон кнопки
            btn_bg = shapes.Rectangle(
                x, y - digit_height//2, digit_width, digit_height,
                color=(200, 200, 200)
            )
            btn_bg.draw()

            # Рамка кнопки
            btn_frame = shapes.Rectangle(
                x-1, y - digit_height//2 - 1, digit_width+2, digit_height+2,
                color=(100, 100, 100)
            )
            btn_frame.draw()

            # Цифра (используем спрайты из digit_sprites)
            if hasattr(self, 'time_digits') and i < len(self.time_digits):
                digit = self.time_digits[i]

                # Проверяем, есть ли спрайты
                if hasattr(self, 'digit_sprites') and len(self.digit_sprites) > digit:
                    # Берем спрайт для текущей цифры
                    sprite = self.digit_sprites[digit]

                    # Рисуем спрайт по центру кнопки
                    sprite_x = x
                    sprite_y = y-17
                    if isinstance(sprite, pyglet.sprite.Sprite):
                        # Если это уже готовый спрайт
                        sprite.x = sprite_x
                        sprite.y = sprite_y
                        sprite.draw()
                    elif isinstance(sprite, pyglet.image.AbstractImage):
                        # Если это изображение, создаем спрайт
                        spr = pyglet.sprite.Sprite(sprite, x=sprite_x, y=sprite_y)
                        spr.scale = 0.5  # Настрой масштаб под свои спрайты
                        spr.draw()
                    else:
                        # Если это текстовая метка
                        sprite.x = sprite_x
                        sprite.y = sprite_y
                        sprite.text = str(digit)
                        sprite.draw()
                else:
                    # Запасной вариант - просто текст
                    digit_text = pyglet.text.Label(
                        str(digit), font_name="Times New Roman", font_size=36,
                        x=x + digit_width//2, y=y,
                        anchor_x="center", anchor_y="center"
                    )
                    digit_text.draw()

        # Двоеточие между часами и минутами
        colon_x = start_x + 2*digit_width + 10
        colon = pyglet.text.Label(
            ":", font_name="Times New Roman", font_size=36,
            x=colon_x, y=time_block_y - 10,
            anchor_x="center", anchor_y="center"
        )
        colon.draw()

        # Кнопка "Добавить"
        add_button = shapes.Rectangle(
            window_x + 200, window_y + 50, 200, 40,
            color=(50, 150, 50)
        )
        add_button.draw()

        add_text = pyglet.text.Label(
            "Добавить будильник", font_name="Times New Roman", font_size=16,
            x=window_x + 250, y=window_y + 70,
            anchor_x="center", anchor_y="center"
        )
        add_text.draw()

        # Список установленных будильников
        alarms_label = pyglet.text.Label(
            "Установленные будильники:", font_name="Times New Roman", font_size=18,
            x=window_x + 20, y=time_block_y - 100,
            anchor_x="left", anchor_y="center"
        )
        alarms_label.draw()

        if self.alarms:
            for i, alarm in enumerate(self.alarms):
                alarm_text = pyglet.text.Label(
                    f"{i+1}. {alarm['time']} {'(активен)' if not alarm['triggered'] else '(сработал)'}",
                    font_name="Times New Roman", font_size=16,
                    x=window_x + 40, y=time_block_y - 140 - i*30,
                    anchor_x="left", anchor_y="center"
                )
                alarm_text.draw()



    def draw_settings_window(self):
        """Отрисовка окна настроек"""
        # Полупрозрачный фон
        overlay = shapes.Rectangle(0, 0, self.width, self.height, color=(0, 0, 100, 150))
        overlay.draw()

        # Окно
        window_width = 400
        window_height = 300
        window_x = (self.width - window_width) // 2
        window_y = (self.height - window_height) // 2

        window_bg = shapes.Rectangle(window_x-5, window_y-5, window_width+10, window_height+10,color=( 255, 255, 100))
        window_frame = shapes.Rectangle(window_x, window_y, window_width, window_height,color=(40, 40, 40))
        window_bg.draw()
        window_frame.draw()

        # Заголовок
        title = pyglet.text.Label(
            "Настройки", font_name="Times New Roman", font_size=24,
            x=self.width//2, y=window_y + window_height - 40,
            anchor_x="center", anchor_y="center"
        )
        title.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов в файловом менеджере"""
        if self.show_file_manager:
            window_width = 600
            window_height = 500
            window_x = (self.width - window_width) // 2
            window_y = (self.height - window_height) // 2

            # Кнопка закрытия
            if (window_x + window_width - 40 <= x <= window_x + window_width - 10 and
                    window_y + window_height - 40 <= y <= window_y + window_height - 10):
                self.show_file_manager = False
                self.selected_file = None
                return

            # Кнопка "Выбрать"
            button_y = window_y + 40
            button_width = 120
            button_height = 40

            if (window_x + 50 <= x <= window_x + 50 + button_width and
                    button_y <= y <= button_y + button_height and
                    self.selected_file):


                # Формируем полный путь
                file_path = os.path.join(self.current_directory, self.selected_file)

                # Проверяем, что это изображение
                if self.selected_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    try:
                        self.background_image = pyglet.image.load(file_path)
                        print(f"Фон установлен: {self.selected_file}")
                        self.show_file_manager = False
                        self.selected_file = None
                    except Exception as e:
                        print(f"Ошибка загрузки изображения: {e}")
                else:
                    print("Выберите файл изображения!")

            # Кнопка "Отмена"
            if (window_x + window_width - 50 - button_width <= x <= window_x + window_width - 50 and
                    button_y <= y <= button_y + button_height):
                self.show_file_manager = False
                self.selected_file = None

            # Клик по списку файлов
            list_x = window_x + 20
            list_y = window_y + window_height - 90
            list_width = window_width - 40
            list_height = window_height - 150

            if (list_x <= x <= list_x + list_width and
                    list_y - list_height <= y <= list_y):

                # Определяем, по какому файлу кликнули
                item_height = 30
                max_items = list_height // item_height
                start_index = max(0, self.scroll_offset)

                click_index = start_index + int((list_y - y -20) // item_height)

                if 0 <= click_index < len(self.file_list):
                    file_name, file_type = self.file_list[click_index]

                    if file_type == "directory":
                        # Переход в директорию или на уровень выше
                        if file_name == "..":
                            self.current_directory = os.path.dirname(self.current_directory)
                        else:
                            self.current_directory = os.path.join(self.current_directory, file_name)

                        self.update_file_list()
                        self.selected_file = None
                        self.scroll_offset = 0
                    else:
                        # Выбор файла
                        self.selected_file = file_name

        # Проверка клика по кнопке "Установить будильник"
        if (self.set_alarm_button.x <= x <= self.set_alarm_button.x + self.set_alarm_button.width and
                self.set_alarm_button.y <= y <= self.set_alarm_button.y + self.set_alarm_button.height):
            self.show_alarm_window = True
            self.show_settings_window = False

            # В реальном приложении здесь будет добавление нового будильника
            """# Для демонстрации добавим тестовый будильник
            if len(self.alarms) < 5:
                new_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
                self.alarms.append({'time': new_time, 'triggered': False})"""
            # Открываем окно установки времени
            # Проверка клика в окне установки будильника
        if self.show_alarm_window:
            window_width = 500
            window_height = 400
            window_x = (self.width - window_width) // 2
            window_y = (self.height - window_height) // 2

            # Координаты 4-х кнопок с цифрами
            digit_width = 50
            digit_height = 70
            start_x = window_x + 170
            time_block_y = window_y + window_height - 120

            positions = [
                (start_x, time_block_y - 10),                    # Ч1
                (start_x + digit_width + 5, time_block_y - 10),  # Ч2
                (start_x + 2*digit_width + 20, time_block_y - 10),  # М1
                (start_x + 3*digit_width + 25, time_block_y - 10),  # М2
            ]

            # Проверяем клик по каждой кнопке-цифре
            for i, (btn_x, btn_y) in enumerate(positions):
                # Центр кнопки в btn_y, нужно пересчитать границы
                btn_top = btn_y - digit_height//2
                btn_bottom = btn_y + digit_height//2

                if (btn_x <= x <= btn_x + digit_width and
                        btn_top <= y <= btn_bottom):

                    # Меняем цифру по кругу: 0→1→2...→9→0
                    self.time_digits[i] = (self.time_digits[i] + 1) % 10
                    return

            # Кнопка "Добавить будильник"
            if (window_x + 150 <= x <= window_x + 350 and
                    window_y + 50 <= y <= window_y + 90):

                # Формируем время из цифр
                hours = self.time_digits[0] * 10 + self.time_digits[1]
                minutes = self.time_digits[2] * 10 + self.time_digits[3]

                # Проверяем корректность
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    if len(self.alarms) < 5:  # Не больше 5 будильников
                        time_str = f"{hours:02d}:{minutes:02d}"
                        self.alarms.append({
                            'time': time_str,
                            'triggered': False
                        })
                        print(f"Будильник добавлен на {time_str}")

                        # Сбрасываем цифры
                        self.time_digits = [0, 0, 0, 0]
                    else:
                        print("Максимум 5 будильников!")
                else:
                    print("Некорректное время!")
                return
            # Закрытие при клике вне окна
            if not (window_x <= x <= window_x + window_width and
                    window_y <= y <= window_y + window_height):
                self.show_alarm_window = False
                self.time_digits = [0, 0, 0, 0]
                return


        # Проверка клика по кнопке "Настройки"
        elif (self.settings_button.x <= x <= self.settings_button.x + self.settings_button.width and
              self.settings_button.y <= y <= self.settings_button.y + self.settings_button.height):
            self.show_settings_window = True
            self.show_alarm_window = False

        # Проверяем клик по кнопке "Остановить"
        elif (self.stop_button.x <= x <= self.stop_button.x + self.stop_button.width and
              self.stop_button.y <= y <= self.stop_button.y + self.stop_button.height):
            self.stop_alarm()


        # Проверка клика по кнопке "Сменить фон"
        elif self.bg_button.x <= x <= self.bg_button.x + self.bg_button.width and self.bg_button.y <= y <= self.bg_button.y + self.bg_button.height:
            # Открываем файловый менеджер
            self.show_file_manager = True
            self.show_settings_window = False

        # Закрытие вспомогательных окон при клике вне их
        elif self.show_alarm_window or self.show_settings_window:
            # Проверяем, был ли клик вне окна
            window_width = 400
            window_height = 300
            window_x = (self.width - window_width) // 2
            window_y = (self.height - window_height) // 2

            if not (window_x <= x <= window_x + window_width and
                    window_y <= y <= window_y + window_height):
                self.show_alarm_window = False
                self.show_settings_window = False



    def run(self):
        """Запуск приложения"""
        pyglet.app.run()

# Создание и запуск приложения
if __name__ == "__main__":
    app = AlarmApp()
    app.run()