from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget


class KeyDetectWindow(QWidget):

    def __init__(self,
                 key_press, key_release, mouse_press, mouse_release,
                 title=None,
                 background=None,
                 icon=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_press_callback = key_press
        self.key_release_callback = key_release
        self.mouse_press_callback = mouse_press
        self.mouse_release_callback = mouse_release

        self.setContentsMargins(20, 8, 20, 8)

        if title:
            self.setWindowTitle(title)

        if background:
            self.setAutoFillBackground(True)
            self.setStyleSheet("background-color: %s" % background)

        if icon:
            self.setWindowIcon(QIcon(icon))

    def keyPressEvent(self, event):
        self.key_press_callback(event)

    def keyReleaseEvent(self, event):
        self.key_release_callback(event)

    def mousePressEvent(self, event):
        self.mouse_press_callback(event)

    def mouseReleaseEvent(self, event):
        self.mouse_release_callback(event)