#form_script.py

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import Application, Form, Button, Label, DialogResult, FormStartPosition, TextBox, Panel
from System.Drawing import Point, Size, Color

from pyrevit import forms

# Import script utilities
import annotation_utils
import family_annotation_utils
from family_annotation_utils import ask_for_font, test_selected_family

def hex_to_system_color(hex_value):
    hex_value = hex_value.lstrip('#')
    a = int(hex_value[0:2], 16)
    r = int(hex_value[2:4], 16)
    g = int(hex_value[4:6], 16)
    b = int(hex_value[6:8], 16)
    return Color.FromArgb(r, g, b)  # Exclude the alpha value for the swatch


class CustomForm(Form):
    def __init__(self):
        self.Text = 'Modify properties:'
        self.Width = 500
        self.Height = 300
        self.StartPosition = FormStartPosition.CenterScreen

        button_width = 200
        button_height = 40

        self.btn1 = Button()
        self.btn1.Text = "Choose Font..."
        self.btn1.Size = Size(button_width, button_height)
        self.btn1.Location = Point((self.Width - button_width * 2 - 20) // 2, 40)  # Centered
        self.btn1.Click += self.run_function_1
        self.Controls.Add(self.btn1)

        # Display chosen font name
        self.font_display = TextBox()
        self.font_display.ReadOnly = True
        self.font_display.Location = Point(self.btn1.Location.X, self.btn1.Bottom + 10)
        self.font_display.Width = button_width
        self.Controls.Add(self.font_display)

        self.btn2 = Button()
        self.btn2.Text = "Choose Color..."
        self.btn2.Size = Size(button_width, button_height)
        self.btn2.Location = Point(self.btn1.Right + 20, 40)
        self.btn2.Click += self.run_function_2
        self.Controls.Add(self.btn2)

        # Color swatch
        self.color_swatch = Panel()
        self.color_swatch.Size = Size(60, 60)
        self.color_swatch.Location = Point(self.btn2.Location.X + (button_width - 60) // 2, self.btn2.Bottom + 10)
        self.color_swatch.BackColor = Color.White  # Default color
        self.Controls.Add(self.color_swatch)

        # Bottom aligned OK and Cancel buttons
        self.ok_button = Button()
        self.ok_button.Text = "OK"
        self.ok_button.Size = Size(button_width, button_height)
        self.ok_button.Location = Point((self.Width - button_width * 2 - 20) // 2, self.Height - button_height - 80)
        self.ok_button.Click += self.ok_clicked
        self.Controls.Add(self.ok_button)

        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Size = Size(button_width, button_height)
        self.cancel_button.Location = Point(self.ok_button.Right + 20, self.ok_button.Location.Y)
        self.cancel_button.Click += self.cancel_clicked
        self.Controls.Add(self.cancel_button)

    def run_function_1(self, sender, event):
        user_font = annotation_utils.ask_for_font()  # Call from annotation_utils
        self.font_display.Text = user_font  # Use the variable you just assigned


    def run_function_2(self, sender, event):
        chosen_color = function_2()
        self.color_swatch.BackColor = chosen_color  # Use the variable you just assigned

    def ok_clicked(self, sender, event):
        self.DialogResult = DialogResult.OK
        self.Close()

    def cancel_clicked(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()

def function_1():
    user_font = family_annotation_utils.ask_for_font()  # Call from annotation_utils
    return user_font  # The selected font name


def function_2():
    hex_color = forms.ask_for_color()
    system_color = hex_to_system_color(hex_color)
    return system_color

form = CustomForm()
result = form.ShowDialog()

if result == DialogResult.OK:
    user_font = form.font_display.Text
    user_color = form.color_swatch.BackColor.ToArgb()
    # run_object_styles(user_font, user_color)
    test_selected_family(user_font, user_color)
    # Run the main function (can be executed directly or via a UI button)
    chosen_font = ask_for_font()
    chosen_color = forms.ask_for_color()  # Ask for color through a UI form
    # run_object_styles(chosen_font, chosen_color)
elif result == DialogResult.Cancel:
    # Exit or cleanup, whatever you want to happen when the user clicks Cancel
    pass