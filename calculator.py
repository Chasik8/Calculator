import sympy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
import re


class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        self.operators = ["+", "-", "*", "/", "(", ")"]
        self.home_buttons = [
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            ",", "0", ".", "/"
        ]
        self.trig_buttons = ["sin", "cos", "tan", "asin", "acos", "atan"]
        self.nav_buttons = ["←", "→", "(", ")","x", "⌫", "C", "="]
        self.modul_buttons = ["Trig", "d/dx"]
        self.const = ["pi", "e"]
        self.last_was_operator = False
        self.last_button = None
        self.cursor_position = 0
        self.is_trig_mode = False

        self.main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.panel_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 0.8))
        self.input_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(0.8, 1))
        self.result_layout = BoxLayout(orientation="vertical", spacing=10, size_hint=(1, 0.2))

        self.result_input = TextInput(
            focus=True, multiline=False, readonly=True, halign="right", font_size=32, size_hint=(1, 0.2)
        )

        self.num_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.8))
        self.trig_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.8))
        self.navigation_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.2))
        self.modul_layout = GridLayout(cols=1, spacing=10, size_hint=(0.2, 1))

        self.add_number_buttons()
        self.add_trig_buttons()
        self.nav()
        self.modul()


        self.result_layout.add_widget(self.result_input)
        self.main_layout.add_widget(self.result_layout)

        self.panel_layout.add_widget(self.modul_layout)
        self.input_layout.add_widget(self.navigation_layout)
        self.input_layout.add_widget(self.num_layout)

        self.panel_layout.add_widget(self.input_layout)
        self.main_layout.add_widget(self.panel_layout)

        return self.main_layout

    def modul(self):
        for nav in self.modul_buttons:
            self.modul_layout.add_widget(Button(
                text=nav, on_press=self.switch_to_trig, font_size=24
            ))
    def nav(self):
        for nav in self.nav_buttons:
            if nav == "Trig":
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.switch_to_trig, font_size=24
                ))
            elif nav == "⌫":  # Backspace
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.backspace, font_size=24
                ))
            elif nav == "C":  # Clear
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.clear, font_size=24
                ))
            elif nav == "=":  # Equals
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.calculate, font_size=24
                ))
            elif nav =="←" or nav=="→":
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.move_cursor, font_size=24
                ))
            else:
                self.navigation_layout.add_widget(Button(
                    text=nav, on_press=self.add_to_expression, font_size=24
                ))

    def add_number_buttons(self):

        for button in self.home_buttons:
            self.num_layout.add_widget(Button(
                text=button, on_press=self.add_to_expression, font_size=24
            ))

    def add_trig_buttons(self):
        for button in self.trig_buttons:
            self.trig_layout.add_widget(Button(
                text=button, on_press=self.add_to_expression_trig, font_size=24
            ))

    def add_to_expression_trig(self, instance):
        current_text = self.result_input.text
        button_text = instance.text
        if button_text in self.trig_buttons:
            button_text += "()"
        self.result_input.text = (
                current_text[:self.cursor_position] + button_text + current_text[self.cursor_position:]
        )
        self.cursor_position += len(button_text)-1
        self.result_input.cursor = (self.cursor_position, 0)
    def add_to_expression(self, instance):
        current_text = self.result_input.text
        button_text = instance.text

        if button_text in self.operators:
            if current_text == "" or self.last_was_operator:
                return

            self.last_was_operator = True
        else:
            self.last_was_operator = False

        if button_text == "π":  # Pi constant
            button_text = str(sympy.pi)
        self.result_input.text = (
                current_text[:self.cursor_position] + button_text + current_text[self.cursor_position:]
        )
        self.cursor_position += len(button_text)
        self.result_input.cursor = (self.cursor_position, 0)


    def backspace(self, instance):
        if self.cursor_position > 0:
            current_text = self.result_input.text
            self.result_input.text = (
                    current_text[:self.cursor_position - 1] + current_text[self.cursor_position:]
            )
            self.cursor_position -= 1
            self.result_input.cursor = (self.cursor_position, 0)

    def clear(self, instance):
        self.result_input.text = ""
        self.cursor_position = 0

    def calculate(self, instance):
        try:
            ss = self.add_parentheses_to_numbers(self.result_input.text)
            self.result_input.text = str(sympy.simplify(ss))
            self.cursor_position = len(self.result_input.text)
            self.result_input.cursor = (self.cursor_position, 0)
        except Exception as e:
            self.result_input.text = "Error"
            self.cursor_position = 0
            print(e)

    def move_cursor(self, instance):
        direction = instance.text
        if direction == "←" and self.cursor_position > 0:
            self.cursor_position -= 1
        elif direction == "→" and self.cursor_position < len(self.result_input.text):
            self.cursor_position += 1
        self.result_input.cursor = (self.cursor_position, 0)

    def switch_to_trig(self, instance):
        if not self.is_trig_mode:
            self.input_layout.remove_widget(self.num_layout)
            self.input_layout.add_widget(self.trig_layout, index=0)
        else:
            self.input_layout.remove_widget(self.trig_layout)
            self.input_layout.add_widget(self.num_layout, index=0)
        self.is_trig_mode = not self.is_trig_mode

    def add_parentheses_to_numbers(self, input_string):
        # Регулярное выражение для поиска целых и вещественных чисел
        return re.sub(r'(\d+(?:\.\d+)?)', r'S(\1)', input_string)


if __name__ == "__main__":
    CalculatorApp().run()
