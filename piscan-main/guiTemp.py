from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.graphics import Color, Rectangle
import requests
from pathlib import Path
import random


class FirstScreen(Screen):
    def __init__(self, **kwargs):
        super(FirstScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=dp(20))
        layout.padding = [dp(20)]

        logo = Image(source='resources/Logo.png',
                     size_hint=(0.6, 0.6), pos_hint={'center_x': 0.5})
        layout.add_widget(logo)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(
            20), size_hint=(1, None), height=dp(120))

        button1 = Button(text='Select', background_color=(0.216, 0.349, 0.698, 1),
                         size_hint=(0.33, None), height=dp(40),
                         background_normal='', background_down='')
        button1.bind(on_release=self.select_file)
        buttons_layout.add_widget(button1)

        button2 = Button(text='Camera', background_color=(0.216, 0.349, 0.698, 1),
                         size_hint=(0.33, None), height=dp(40),
                         background_normal='', background_down='')

        button2.bind(on_release=self.capture_image)
        buttons_layout.add_widget(button2)

        button3 = Button(text='Exit', background_color=(0.216, 0.349, 0.698, 1),
                         size_hint=(0.33, None), height=dp(40),
                         background_normal='', background_down='')

        button3.bind(on_release=self.exit_app)
        buttons_layout.add_widget(button3)

        layout.add_widget(buttons_layout)

        tag_label = Label(text='by 0x1A1 Team', size_hint=(None, None), size=(dp(100), dp(20)),
                          pos_hint={'center_x': 0.5}, valign='bottom', color=(0.216, 0.349, 0.698, 1))
        layout.add_widget(tag_label)

        self.add_widget(layout)

    def select_file(self, instance):
        app = App.get_running_app()
        app.root.current = 'third_screen'

    def capture_image(self, instance):
        app = App.get_running_app()
        app.root.current = 'second_screen'

    def exit_app(self, instance):
        App.get_running_app().stop()


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        camera = Camera(play=True)
        layout.add_widget(camera)

        buttons_layout = BoxLayout(
            orientation='horizontal', spacing=dp(20), padding=dp(10))

        home_button = Button(text='Home', background_color=(0.216, 0.349, 0.698, 1),
                             size_hint=(0.5, None), height=dp(40),
                             background_normal='', background_down='')
        home_button.bind(on_release=self.goto_first_screen)
        buttons_layout.add_widget(home_button)

        capture_button = Button(text='Capture', background_color=(0.216, 0.349, 0.698, 1),
                                size_hint=(0.5, None), height=dp(40),
                                background_normal='', background_down='')
        capture_button.bind(on_release=self.capture_and_process_image)
        buttons_layout.add_widget(capture_button)

        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def capture_and_process_image(self, instance):
        app = App.get_running_app()
        camera = self.children[0].children[1]
        image_path = Path('images/document.png')
        if image_path.exists():
            image_path = 'images/document' + \
                str(random.randint(1, 1000)) + '.png'
        camera.export_to_png(image_path)

        # prepare the file to be sent to the backend in order to process it and extract text from if possible
        files = {'image': open(image_path, 'rb')}
        # establissing the connection with the database using a post method
        response = requests.post(
            'http://localhost:5000/process_image', files=files)

        if response.status_code == 200:
            data = response.json()
            extracted_text = data.get('text', '')
            app.root.current = 'fourth_screen'
            fourth_screen = app.root.get_screen('fourth_screen')
            fourth_screen.display_text(extracted_text)
        else:
            app.root.current = 'fourth_screen'
            fourth_screen = app.root.get_screen('fourth_screen')
            fourth_screen.display_text('Error processing the image')

    def goto_first_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'first_screen'


class ThirdScreen(Screen):
    def __init__(self, **kwargs):
        super(ThirdScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=dp(20))
        layout.padding = [dp(20)]  # Set padding for the layout

        file_chooser = FileChooserListView(path='.')
        layout.add_widget(file_chooser)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(20),
                                   size_hint=(1, None), height=dp(120))

        with layout.canvas.before:
            # Set the background color to dark blue
            Color(0.1, 0.1, 0.3, 1)
            self.rect = Rectangle(size=Window.size, pos=layout.pos)

        # Home Button
        home_button = Button(text='Home', background_color=(0.216, 0.349, 0.698, 1),
                             size_hint=(0.33, None), height=dp(40),
                             background_normal='', background_down='')
        # Bind the button release event, means if the button clicked go to the first screen, the home
        home_button.bind(on_release=self.goto_first_screen)
        buttons_layout.add_widget(home_button)

        # create the button to confirm the file selection and begain the process of communicating the database
        confirm_button = Button(text='Confirm', background_color=(0.216, 0.349, 0.698, 1),
                                size_hint=(0.33, None), height=dp(40),
                                background_normal='', background_down='')
        confirm_button.bind(on_release=lambda x: self.process_selected_file(
            file_chooser.path, file_chooser.selection))
        buttons_layout.add_widget(confirm_button)

        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def process_selected_file(self, path, filename):
        if filename:
            selected_file = filename[0]
            app = App.get_running_app()

            # preparing the selected image to be sent
            files = {'image': open(selected_file, 'rb')}
            response = requests.post(  # makeing the request to the database to process and get text
                'http://localhost:5000/process_image', files=files)

            # checking the status code of the reponse, if everything is good we get 200 code which means ok
            if response.status_code == 200:
                data = response.json()
                extracted_text = data.get('text', '')
                app.root.current = 'fourth_screen'
                fourth_screen = app.root.get_screen('fourth_screen')
                fourth_screen.display_text(extracted_text)
            else:   # if the communication with the backend was not successfull, we should display a message for the user to tell him that the image was not processed
                app.root.current = 'fourth_screen'
                fourth_screen = app.root.get_screen('fourth_screen')
                fourth_screen.display_text('Error processing the image')

    def goto_first_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'first_screen'


class FourthScreen(Screen):
    def __init__(self, **kwargs):
        super(FourthScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=dp(20))
        layout.padding = [dp(20)]

        with layout.canvas.before:
            Color(0.1, 0.1, 0.3, 1)
            self.rect = Rectangle(size=Window.size, pos=layout.pos)

        self.text_display = Label(text='Extracted Text', color=(1, 1, 1, 1))
        layout.add_widget(self.text_display)

        home_button = Button(text='Home', background_color=(0.216, 0.349, 0.698, 1),
                             size_hint=(1, None), height=dp(40),
                             background_normal='', background_down='')
        home_button.bind(on_release=self.goto_first_screen)
        layout.add_widget(home_button)

        self.add_widget(layout)

    def display_text(self, text):
        self.text_display.text = text

    def goto_first_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'first_screen'


class MyApp(App):
    def build(self):
        self.title = "Piscan"
        Window.size = (420, 600)
        Window.clearcolor = (1, 1, 1, 1)

        screen_manager = ScreenManager()

        first_screen = FirstScreen(name='first_screen')
        screen_manager.add_widget(first_screen)

        second_screen = SecondScreen(name='second_screen')
        screen_manager.add_widget(second_screen)

        third_screen = ThirdScreen(name='third_screen')
        third_screen.bind(on_enter=self.on_enter_third_screen)
        screen_manager.add_widget(third_screen)

        fourth_screen = FourthScreen(name='fourth_screen')
        screen_manager.add_widget(fourth_screen)

        return screen_manager

    def on_enter_third_screen(self, instance):
        pass


if __name__ == '__main__':
    MyApp().run()
