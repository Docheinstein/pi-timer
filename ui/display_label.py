
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class DisplayLabel(QLabel):

    def __init__(self, fontsize, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fontsize = fontsize
        self.setAlignment(Qt.AlignCenter)
        self.show()

    def update_color(self, color):
        self.setStyleSheet("QLabel { color: %s; font-size: %dpx }" %
                           (color, self.fontsize))

    def update_display(self, text):
        self.setText(text)
