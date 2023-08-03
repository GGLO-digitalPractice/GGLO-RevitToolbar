import clr
clr.AddReference("IronPython.Wpf")

import wpf

from System.Windows import Window
from System.Windows.Controls import Button, PasswordBox, TextBox

class MyWindow(Window):
    def __init__(self):
        # Make sure x:Class directive in XAML matches this class
        wpf.LoadComponent(self, r'C:\_GGLO\RevitTools\GGLO-Toolbar.extension\gglo.tab\Areas.panel\Boundaries.pushbutton\MainWindow.xaml')
        
        # Add event handler for the Login button
        self.LoginButton.Click += self.handle_login

    def handle_login(self, sender, args):
        # Print 'Test' when the button is clicked
        print('Test')

# Run the Window
MyWindow().ShowDialog()
