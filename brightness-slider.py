#! /usr/bin/python3
"""
    Brightness Slider - Control the screen brightness
    This program is not related to Apache or the Apache Software Foundation in any way
    Copyright (C) 2019  Nicholas Shiell

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import subprocess
import signal

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


def get_brighness():
    cmd = subprocess.Popen(
        ['brightness'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, errors = cmd.communicate()
    cmd = cmd.wait()
    return int(output.decode('UTF-8').strip())


def set_brightness(new_value):
    current_value = get_brighness()

    if current_value == new_value:
        return current_value

    needsToDarken = current_value > new_value

    # bound the brightness change to 200 attempts - incase
    # something goes wrong
    for x in range(0, 200):
        print(str(current_value), file=sys.stderr)
        window.brightness = current_value
        window.set_title()
        
        if needsToDarken:
            if current_value > new_value:
                subprocess.Popen(['brightness', 'down'])
            else:
                return current_value
        else:
            if current_value < new_value:
                subprocess.Popen(['brightness', 'up'])
            else:
                return current_value
        current_value = get_brighness()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        # Get the current brightness before setting the title
        self.brightness = get_brighness()
        self.set_title()

        self.setFixedSize(300, 40)
        # todo find a nice png
        #self.setWindowIcon(QtGui.QIcon("icon.png"))
        hbox = QHBoxLayout()
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(self.brightness)

        hbox.addWidget(self.slider)
        button = QPushButton("set")
        button.clicked.connect(lambda: self.changedValue())
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(button)
        self.setLayout(hbox)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_Return:
            self.changedValue()

    def set_title(self):
        self.setWindowTitle(str(self.brightness) + '% - Brightness')

    def changedValue(self):
        value = self.slider.value()
        value_set = set_brightness(value)
        self.slider.setValue(value_set)
        self.brightness = value_set
        self.set_title()


if __name__ == '__main__':
    # Kill the app on ctrl-c
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())