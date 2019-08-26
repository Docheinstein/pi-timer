from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class ScrambleLabel(QLabel):
    def __init__(self, color, fontsize, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet("QLabel { color: %s; font-size: %dpx; }" %
                               (color, fontsize))
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMargin(20)
        self.show()

    def update_scramble(self, scramble):
        self.setText(str(scramble))
