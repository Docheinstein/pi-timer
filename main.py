import json
import os

from PyQt5.QtWidgets import *

from cube.cubescramble import CubeScramble
from cube.cubestate import CubeState
from core.timer import RubikTimer
from ui.display_label import DisplayLabel
from ui.key_detect_window import KeyDetectWindow
from ui.scramble_label import ScrambleLabel
from ui.scramble_preview import ScramblePreview

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():
    # CONFIG (from json)

    try:
        with open(os.path.join(__location__, "config.json"), "r") as config_file:
            config = json.loads(config_file.read())
            print("Loaded config: %s" % config)
    except Exception as e:
        print("Cannot find/parse config.json\n", e)
        exit(-1)

    app = QApplication([])

    # MAIN WINDOW

    pressed_buttons = {}

    def on_key_pressed(event):
        if event.key() in config["timer_buttons"]:
            pressed_buttons[event.key()] = True
            valid_buttons_pressed_count = 0
            for b in config["timer_buttons"]:
                if pressed_buttons.get(b):
                    valid_buttons_pressed_count += 1
            count_threshold = 2 if config["stackmat_mode"] else 1
            if valid_buttons_pressed_count >= count_threshold:
                timer.press()

        elif event.key() in config["cancel_buttons"]:
            timer.reset()

    def on_key_released(event):
        pressed_buttons[event.key()] = False
        if not event.isAutoRepeat() and event.key() in config["timer_buttons"]:
            timer.release()

    def on_mouse_pressed(event):
        print("<mouse_press>")
        timer.press()

    def on_mouse_released(event):
        timer.release()

    window = KeyDetectWindow(
        key_press=on_key_pressed,
        key_release=on_key_released,
        mouse_press=on_mouse_pressed,
        mouse_release=on_mouse_released,
        title="Pi Timer",
        background=config["background_color"],
        icon="icon.png",
        size=(config["width"], config["height"])
    )

    # SCRAMBLE LABEL

    scramble_label = ScrambleLabel(config["scramble_color"],
                                   config["scramble_fontsize"])

    # SCRAMBLE PREVIEW

    scramble_preview = ScramblePreview(width=config["scramble_preview_size"],
                                       up_color=config["scramble_up_color"],
                                       down_color=config["scramble_down_color"],
                                       front_color=config["scramble_front_color"],
                                       back_color=config["scramble_back_color"],
                                       right_color=config["scramble_right_color"],
                                       left_color=config["scramble_left_color"])

    def update_scramble():
        scramble = CubeScramble(config["scramble_length"])
        scramble_label.update_scramble(scramble)
        print("Scramble: " + str(scramble))

        state = CubeState()
        state.alg(scramble)
        scramble_preview.update_state(state)

        print("Cube state after scramble :\n" + str(state))

    update_scramble()

    # DISPLAY LABEL

    display_label = DisplayLabel(fontsize=config["display_fontsize"])
    display_label.update_color(config["display_color"])

    # TIMER INIT

    def generate_time_string(ms, decimals=2):
        sec = ms / 1000

        fmt = "%." + str(decimals) + "f"
        text = fmt % (sec % 60)

        if sec >= 60:
            text = "%02d:" % int((sec % 3600) / 60) + text

            if sec >= 3600:
                text = str(int(sec / 3600)) + ":"

        return text

    def handle_time_callback(ms, instance=None):
        display_label.update_display(generate_time_string(
            ms, decimals=0 if instance and instance.state == RubikTimer.State.INSPECTING else 2))

    def handle_event_callback(rubik_event, instance=None):
        print(">> Current state: %s" % rubik_event)
        color = config["display_color"]
        text = None

        if rubik_event == RubikTimer.Event.READY:
            color = config["ready_color"]
        elif rubik_event == RubikTimer.Event.PLUS_TWO:
            color = config["plus_two_color"]
            text = "+2"
        elif rubik_event == RubikTimer.Event.DNF:
            color = config["dnf_color"]
            text = "DNF"
        elif rubik_event == RubikTimer.Event.RESET:
            text = generate_time_string(0)
        elif rubik_event == RubikTimer.Event.STOP:
            if instance.has_plus_two():
                text = display_label.text() + "+"

        if rubik_event == RubikTimer.Event.STOP or \
                rubik_event == RubikTimer.Event.DNF or \
                rubik_event == RubikTimer.Event.RESET:
            update_scramble()

        display_label.update_color(color)
        if text:
            # print("Text => ", t)
            display_label.update_display(text)

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

    scramble_layout = QHBoxLayout()
    scramble_layout.addWidget(scramble_label)
    scramble_layout.addWidget(scramble_preview)

    layout.addLayout(scramble_layout, stretch=0)

    layout.addWidget(divider)

    layout.addWidget(display_label, stretch=1)

    window.setLayout(layout)

    window.resize(config["width"], config["height"])
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
