from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_string(
    """
<AddPersonPopup>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'Введите имя человека:'
        TextInput:
            id: name_input
            multiline: False
        BoxLayout:
            spacing: 5
            Button:
                text: 'Добавить'
                on_press: root.add_person()
            Button:
                text: 'Отмена'
                on_press: root.dismiss()

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Добавить человека'
            size_hint_y: 0.1
            on_press: root.show_add_person_popup()
        ScrollView:
            GridLayout:
                id: persons_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height

<PersonScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: root.person_name
            size_hint_y: 0.1
        Button:
            text: 'Добавить упражнение'
            size_hint_y: 0.1
            on_press: root.manager.current = 'add_exercise'
        ScrollView:
            GridLayout:
                id: exercises_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Назад'
            size_hint_y: 0.1
            on_press: root.manager.current = 'main'
        

<AddExerciseScreen>:
    BoxLayout:
        orientation: 'vertical'
        TextInput:
            id: exercise_input
            hint_text: 'Название упражнения'
            size_hint_y: 0.1
        Button:
            text: 'Добавить значения'
            size_hint_y: 0.1
            on_press: root.create_exercise()
        Button:
            text: 'Назад'
            size_hint_y: 0.1
            on_press: root.manager.current = 'person'

<AddValuesScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            GridLayout:
                id: input_grid
                cols: 3
                size_hint_y: None
                height: self.minimum_height
                row_default_height: '40dp'
        BoxLayout:
            size_hint_y: 0.15
            spacing: 5
            Button:
                text: 'Добавить строку'
                on_press: root.add_row()
            Button:
                text: 'Сохранить'
                on_press: root.save_data()
            Button:
                text: 'Назад'
                on_press: root.manager.current = 'exercise_detail'

<ExerciseDetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            GridLayout:
                id: data_table
                cols: 4
                size_hint_y: None
                height: self.minimum_height
                row_default_height: '40dp'
                spacing: 5
        BoxLayout:
            size_hint_y: 0.15
            Button:
                text: 'Добавить запись'
                on_press: root.add_record()
            Button:
                text: 'Назад'
                on_press: root.manager.current = 'person'
"""
)


class AddPersonPopup(Popup):   # 
    def add_person(self):
        name = self.ids.name_input.text.strip()
        if name:
            app = App.get_running_app()
            if name not in app.data:
                app.data[name] = {}
                app.save_data()
                main_screen = app.root.get_screen("main")
                main_screen.update_persons_list()
            self.dismiss()


class MainScreen(Screen):
    def show_add_person_popup(self):
        AddPersonPopup().open()

    def on_pre_enter(self):
        self.update_persons_list()

    def update_persons_list(self):
        grid = self.ids.persons_list
        grid.clear_widgets()
        app = App.get_running_app()
        for person in app.data:
            btn = Button(text=person, size_hint_y=None, height=40)
            btn.bind(on_press=lambda x, p=person: self.show_person(p))
            grid.add_widget(btn)

    def show_person(self, name):
        app = App.get_running_app()
        app.current_person = name
        person_screen = app.root.get_screen("person")
        person_screen.person_name = name
        app.root.current = "person"


class PersonScreen(Screen):
    person_name = StringProperty("")

    def on_pre_enter(self):
        self.update_exercises_list()

    def update_exercises_list(self):
        app = App.get_running_app()
        grid = self.ids.exercises_list
        grid.clear_widgets()
        if self.person_name in app.data:
            for exercise in app.data[self.person_name]:
                btn = Button(text=exercise, size_hint_y=None, height=40)
                btn.bind(on_press=lambda x, e=exercise: self.show_exercise(e))
                grid.add_widget(btn)

    def show_exercise(self, exercise):
        app = App.get_running_app()
        app.current_exercise = exercise
        detail_screen = app.root.get_screen("exercise_detail")
        detail_screen.update_table()
        app.root.current = "exercise_detail"


class AddExerciseScreen(Screen):
    def create_exercise(self):
        app = App.get_running_app()
        exercise_name = self.ids.exercise_input.text
        if exercise_name and app.current_person:
            app.current_exercise = exercise_name
            if app.current_person not in app.data:
                app.data[app.current_person] = {}
            app.data[app.current_person][exercise_name] = []
            app.save_data()
            app.root.current = "add_values"


class AddValuesScreen(Screen):
    def on_pre_enter(self):
        self.add_row()

    def add_row(self):
        grid = self.ids.input_grid
        grid.add_widget(TextInput(hint_text="дд.мм.гггг"))
        grid.add_widget(TextInput(hint_text="кг"))
        grid.add_widget(TextInput(hint_text="кол-во"))

    def save_data(self):
        app = App.get_running_app()
        grid = self.ids.input_grid
        inputs = [child for child in grid.children if isinstance(child, TextInput)]
        inputs.reverse()

        entries = []
        for i in range(0, len(inputs), 3):
            if i + 2 >= len(inputs):
                break
            date = inputs[i].text.strip()
            weight = inputs[i + 1].text.strip()
            reps = inputs[i + 2].text.strip()
            if date and weight and reps:
                entries.append(f"{date},{weight},{reps}")

        if app.current_person and app.current_exercise and entries:
            with open("data.txt", "a") as f:
                for entry in entries:
                    f.write(f"{app.current_person},{app.current_exercise},{entry}\n")

            app.load_data()
            grid.clear_widgets()
            app.root.current = "exercise_detail"


class ExerciseDetailScreen(Screen):
    def update_table(self):
        app = App.get_running_app()
        grid = self.ids.data_table
        grid.clear_widgets()

        grid.add_widget(Label(text="Дата", bold=True))
        grid.add_widget(Label(text="Вес", bold=True))
        grid.add_widget(Label(text="Повторения", bold=True))
        grid.add_widget(Label(text=""))

        if app.current_person in app.data:
            if app.current_exercise in app.data[app.current_person]:
                for entry in app.data[app.current_person][app.current_exercise]:
                    grid.add_widget(Label(text=entry["дата"]))
                    grid.add_widget(Label(text=entry["вес"]))
                    grid.add_widget(Label(text=entry["повторения"]))
                    grid.add_widget(Label(text=""))

    def add_record(self):
        App.get_running_app().root.current = "add_values"


class MyApp(App):
    data = {}
    current_person = StringProperty("")
    current_exercise = StringProperty("")

    def build(self):
        self.load_data()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(PersonScreen(name="person"))
        sm.add_widget(AddExerciseScreen(name="add_exercise"))
        sm.add_widget(AddValuesScreen(name="add_values"))
        sm.add_widget(ExerciseDetailScreen(name="exercise_detail"))
        return sm

    def load_data(self):
        self.data = {}
        try:
            with open("data.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 5:
                        person, exercise, date, weight, reps = parts
                        if person not in self.data:
                            self.data[person] = {}
                        if exercise not in self.data[person]:
                            self.data[person][exercise] = []
                        self.data[person][exercise].append(
                            {"дата": date, "вес": weight, "повторения": reps}
                        )
        except FileNotFoundError:
            pass

    def save_data(self):
        with open("data.txt", "w") as f:
            for person in self.data:
                for exercise in self.data[person]:
                    for entry in self.data[person][exercise]:
                        line = f"{person},{exercise},{entry['дата']},{entry['вес']},{entry['повторения']}\n"
                        f.write(line)


if __name__ == "__main__":
    MyApp().run()
