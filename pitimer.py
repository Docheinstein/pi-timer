import json
import random


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from timer import RubikTimer

RUBIK_FACES = ["R", "L", "U", "D", "F", "B"]


# === GUI ===


class KeyDetectWindow(QWidget):

    def __init__(self, key_press, key_release, mouse_press, mouse_release,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_press_callback = key_press
        self.key_release_callback = key_release
        self.mouse_press_callback = mouse_press
        self.mouse_release_callback = mouse_release

    def keyPressEvent(self, event):
        self.key_press_callback(event)

    def keyReleaseEvent(self, event):
        self.key_release_callback(event)

    def mousePressEvent(self, event):
        self.mouse_press_callback(event)

    def mouseReleaseEvent(self, event):
        self.mouse_release_callback(event)


def main():
    # CONFIG (from json)

    try:
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
            print("Loaded config: %s" % config)
    except Exception as e:
        print("Cannot find/parse config.json\n", e)
        exit(-1)

    app = QApplication([])

    # MAIN WINDOW

    def on_key_pressed(event):
        if event.key() in config["timer_buttons"]:
            timer.press()
        elif event.key() in config["cancel_buttons"]:
            timer.reset()

    def on_key_released(event):
        if not event.isAutoRepeat() and event.key() in config["timer_buttons"]:
            timer.release()

    def on_mouse_pressed(event):
        print("<mouse_press>")
        timer.press()

    def on_mouse_released(event):
        timer.release()

    container = KeyDetectWindow(
        key_press=on_key_pressed,
        key_release=on_key_released,
        mouse_press=on_mouse_pressed,
        mouse_release=on_mouse_released)

    container.setContentsMargins(20, 8, 20, 8)
    container.setAutoFillBackground(True)
    container.setStyleSheet("background-color: %s" % config["background_color"])

    # SCRAMBLE LABEL

    scramble = QLabel()
    scramble.setStyleSheet("QLabel { color: %s; font-size: %dpx; }" %
                           (config["scramble_color"], config["scramble_fontsize"]))
    scramble.setAlignment(Qt.AlignCenter)
    scramble.setWordWrap(True)
    scramble.setMargin(20)
    scramble.show()

    def generate_scramble():
        scramble_parts = []

        last_face = None

        for i in range(config["scramble_length"]):
            face = None

            while not face or face == last_face:
                face = random.choice(RUBIK_FACES)

            turns = random.randint(1, 3)

            scramble_part = face
            if turns == 2:
                scramble_part += "2"
            if turns == 3:
                scramble_part += "'"

            scramble_parts.append(scramble_part)

            last_face = face

        return " ".join(scramble_parts)

    def update_scramble():
        scramble.setText(generate_scramble())

    update_scramble()

    # DISPLAY LABEL

    def display_style(color, font_size):
        return "QLabel { color: %s; font-size: %dpx }" % (color, font_size)

    display = QLabel()
    display.setStyleSheet(display_style(config["display_color"], config["display_fontsize"]))
    display.setAlignment(Qt.AlignCenter)
    display.show()

    # TIMER INIT

    def generate_time_string(ms, decimals=2):
        fmt = "%." + str(decimals) + "f"
        sec = ms / 1000
        return fmt % sec

    def handle_time_callback(ms, instance=None):
        display.setText(
            generate_time_string(ms, decimals=0 if instance and instance.state == RubikTimer.State.INSPECTING else 2))

    def handle_event_callback(rubik_event, instance=None):
        print(">> Current state: %s" % rubik_event)
        c = config["display_color"]
        t = None

        if rubik_event == RubikTimer.Event.READY:
            c = config["ready_color"]
        elif rubik_event == RubikTimer.Event.PLUS_TWO:
            c = config["plus_two_color"]
            t = "+2"
        elif rubik_event == RubikTimer.Event.DNF:
            c = config["dnf_color"]
            t = "DNF"
        elif rubik_event == RubikTimer.Event.RESET:
            t = generate_time_string(0)
        elif rubik_event == RubikTimer.Event.STOP:
            if instance.has_plus_two():
                t = display.text() + "+"

        if rubik_event == RubikTimer.Event.STOP or \
                rubik_event == RubikTimer.Event.DNF or \
                rubik_event == RubikTimer.Event.RESET:
            update_scramble()

        display.setStyleSheet(display_style(c, config["display_fontsize"]))
        if t:
            # print("Text => ", t)
            display.setText(t)

    timer = RubikTimer(event_callback=handle_event_callback,
                       time_callback=handle_time_callback,
                       inspecting_sec=config["inspection_seconds"])

    handle_time_callback(0)

    # SPLITTER
    divider = QFrame()
    divider.setFixedHeight(2)
    divider.setFrameShape(QFrame.HLine)
    divider.setFrameShadow(QFrame.Sunken)
    # divider.setStyleSheet("QFrame { background-color: #494d4a; } ")

    # SETUP
    layout = QVBoxLayout()
    layout.addWidget(scramble, stretch=0)
    layout.addWidget(divider)
    layout.addWidget(display, stretch=1)

    container.setLayout(layout)

    container.resize(config["width"], config["height"])
    container.show()

    app.exec_()


if __name__ == "__main__":
    main()
