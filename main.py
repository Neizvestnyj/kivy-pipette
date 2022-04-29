from kivymd.app import MDApp

from kivy.lang.builder import Builder
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from behaviour.touch_behaviour import TouchBehavior

import os
from PIL import Image as PILImage


class BorderImage(Image):
    pass


class TouchableScreen(Screen, TouchBehavior):
    pass


class PipetteMouse(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor = Image(source='transparent.png', size_hint=(None, None), size=[64, 64])
        self.scaled_area = BorderImage(source='transparent.png', size_hint=(None, None), size=[90, 90])

        self.add_widget(self.scaled_area)
        self.add_widget(self.cursor)

        self.auto_bring_to_front = True

    def update_bg_widget(self, source: str):
        self.scaled_area.source = source
        self.scaled_area.reload()

    def set_cursor_icon(self, source: str):
        self.cursor.source = source
        self.cursor.reload()


class PipetteApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = 'pipette.png'
        self.screen = Builder.load_file('main.kv')

        Window.bind(mouse_pos=self.mouse_pos)
        Window.bind(on_keyboard=self.keyboard_handler)

        self.screen.bind(on_long_touch=lambda inst, touch: self.get_pixel(*touch.pos))
        self.screen.bind(on_touch_up=lambda inst, touch: self.reset_cursor())
        self.screen.bind(on_touch_move=self.touch_move)

        self.mouse = PipetteMouse()
        self.screen.add_widget(self.mouse)

        self.transparent_bg = 'transparent.png'
        self.incr_area = 'increasing_area.jpg'
        self.scr_img = 'screen.png'

        self.on_move_counter = 0  # in order to reduce lags

    def build(self):
        return self.screen

    def on_stop(self):
        if os.path.exists(self.incr_area):
            os.remove(self.incr_area)

        if os.path.exists(self.scr_img):
            os.remove(self.scr_img)

    def show_cursor(self, show: bool):
        Window.show_cursor = show

    def reset_cursor(self):
        self.mouse.update_bg_widget(self.transparent_bg)

    def touch_move(self, inst, touch):
        if self.on_move_counter == 2:
            self.on_move_counter = 0

        if self.on_move_counter == 0:
            self.get_pixel(*touch.pos)

        self.on_move_counter += 1

    def mouse_pos(self, window: Window, pos: tuple):
        self.mouse.cursor.pos = pos[0] - self.mouse.cursor.width // 2, pos[1] - self.mouse.cursor.height // 2

        self.mouse.scaled_area.pos = pos[0] - self.mouse.scaled_area.width // 2, pos[
            1] - self.mouse.scaled_area.height // 2

    def increasing_the_area(self, img: Image, pos: tuple):
        box_size = 50

        left = pos[0] - box_size / 2
        upper = pos[1] - box_size / 2

        right = left + box_size
        lower = upper + box_size

        """
        left - upper##############
        ##########################
        ##########################
        ##########################
        ##########################
        ##########################
        ###############right-lower
        """

        img = img.crop((left, upper, right, lower))
        img = img.resize((box_size * 4, box_size * 4), PILImage.ANTIALIAS)
        img.save(self.incr_area)

        self.mouse.update_bg_widget(self.incr_area)

    def get_pixel(self, x: float, y: float):
        coords = int(x), 600 - int(y)  # change coordination start

        if self.screen.ids.scr_manager.current == '1':
            self.screen.ids.layout_1.export_to_png(self.scr_img)
        elif self.screen.ids.scr_manager.current == '2':
            self.screen.ids.layout_2.export_to_png(self.scr_img)
        else:
            return

        color = ()

        try:
            img = PILImage.open(self.scr_img).convert('RGB')
            color = img.getpixel(coords)

            self.increasing_the_area(img, coords)
            print('Area color:', color)
        except IndexError:
            pass

        return color

    def change_screen(self, name: str):
        if self.screen.ids.scr_manager.current != name:
            if name == 'home':
                self.screen.ids.scr_manager.transition.direction = 'right'
            else:
                self.screen.ids.scr_manager.transition.direction = 'left'

            self.screen.ids.scr_manager.current = name

    def keyboard_handler(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            self.change_screen('home')
            return True


PipetteApp().run()
