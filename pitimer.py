import json
import random
import time

from enum import Enum
from threading import Thread, Event

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import *

RUBIK_FACES = ["R", "L", "U", "D", "F", "B"]


def current_millis():
    return int(round(time.time() * 1000))

# === TIMER ===


class RubikTimer:

    class State(Enum):
        NONE = "none"
        INSPECTING = "inspecting"
        PLUS_TWO = "plus_two"
        ALMOST_READY = "almost_ready"
        READY = "ready"
        TIMING = "timing"

    class Event(Enum):
        INSPECTING = "inspecting"
        PLUS_TWO = "plus_two"
        DNF = "DNF"
        ALMOST_READY = "almost_ready"
        READY = "ready"
        START = "start"
        STOP = "stop"

    def __init__(self,
                 event_callback,
                 time_callback,
                 inspecting_sec=15,
                 ready_press_time=500):
        self.state = RubikTimer.State.NONE
        self.event_callback = event_callback
        self.time_callback = time_callback
        self.inspecting_sec = inspecting_sec
        self.ready_press_time = ready_press_time
        self.timer = None
        self.inspecting_start = 0

    def press(self):
        print("\n<press>")
        if self.state == RubikTimer.State.NONE:
            self._start_inspecting()
        elif self.state == RubikTimer.State.INSPECTING:
            self._almost_ready()
        elif self.state == RubikTimer.State.ALMOST_READY:
            if current_millis() - self.ready_begin_time > self.ready_press_time:
                self._ready()
            else:
                print("-- ignoring --")
        elif self.state == RubikTimer.State.TIMING:
            self._stop_timer()

    def release(self):
        print("\n<release>")
        if self.state == RubikTimer.State.ALMOST_READY:
            self._continue_inspecting()
        if self.state == RubikTimer.State.READY:
            self._start_timer()

    def _start_inspecting(self):
        print("Start inspecting")
        self.state = RubikTimer.State.INSPECTING
        self.event_callback(RubikTimer.Event.INSPECTING, self)

        self._deinit_timer()

        def handle_backward_timer(ms):
            if not self.timer:
                return

            print("Tick: %f" % self.timer.ticks)
            print("Elapsed: %f" % self.timer.elapsed_time())
            print("Remaining: %f" % self.timer.remaining_time())

            if self.timer.ticks >= self.inspecting_sec:
                if self.state == RubikTimer.State.PLUS_TWO and \
                        self.timer.ticks >= self.inspecting_sec + 2:
                    self._dnf()
                elif self.state == RubikTimer.State.INSPECTING or \
                        self.state == RubikTimer.State.ALMOST_READY or \
                        self.state == RubikTimer.State.READY:
                    self._plus_two()
            else:
                self.time_callback(ms, self)

        self.timer = BackwardTimer(self.inspecting_sec * 1000,
                                   handle_backward_timer)
        self.timer.start()

    def _continue_inspecting(self):
        print("Continue inspecting")
        self.state = RubikTimer.State.INSPECTING
        self.event_callback(RubikTimer.Event.INSPECTING, self)

    def _almost_ready(self):
        print("Almost ready")
        self.state = RubikTimer.State.ALMOST_READY
        self.event_callback(RubikTimer.Event.ALMOST_READY)
        self.ready_begin_time = current_millis()

    def _ready(self):
        print("Ready")
        self.state = RubikTimer.State.READY
        self.event_callback(RubikTimer.Event.READY)

    def _dnf(self):
        print("DNF")
        self.state = RubikTimer.State.NONE
        self.event_callback(RubikTimer.Event.DNF)

    def _plus_two(self):
        print("+2")
        self.state = RubikTimer.State.PLUS_TWO
        self.event_callback(RubikTimer.Event.PLUS_TWO)

    def _start_timer(self):
        print("Start timer")
        self.state = RubikTimer.State.TIMING
        self.event_callback(RubikTimer.Event.START)

        self._deinit_timer()
        self.timer = ForwardTimer(lambda t: self.time_callback(t, self))
        self.timer.start()

    def _stop_timer(self):
        print("Stop timer")
        self.state = RubikTimer.State.NONE
        self.event_callback(RubikTimer.Event.STOP)
        self._deinit_timer()

    def _deinit_timer(self):
        if self.timer:
            self.timer.stop()
        self.timer = None


class BackwardTimer(Thread):

    PRECISION = 1

    def __init__(self, fulltime, callback, precision=PRECISION, **kwargs):
        Thread.__init__(self, **kwargs)
        self.running = True
        self.full_time = fulltime
        self.start_time = 0
        self.precision = precision
        self.callback = callback
        self.ticks = 0

    def run(self):
        self.start_time = current_millis()
        e = Event()

        self.callback(self.remaining_time())

        while self.running:
            e.wait(timeout=self.precision)
            self.ticks += 1
            if self.callback:
                self.callback(self.remaining_time())

    def stop(self):
        self.callback = None
        self.running = False

    def remaining_time(self):
        return self.full_time - (current_millis() - self.start_time)

    def elapsed_time(self):
        return current_millis() - self.start_time


class ForwardTimer(Thread):

    PRECISION = 0.01

    def __init__(self, callback, precision=PRECISION, **kwargs):
        Thread.__init__(self, **kwargs)
        self.running = True
        self.start_time = 0
        self.precision = precision
        self.callback = callback
        self.ticks = 0

    def run(self):
        self.start_time = current_millis()
        e = Event()

        self.callback(self.elapsed_time())

        while self.running:
            e.wait(timeout=self.precision)
            self.ticks += 1
            if self.callback:
                self.callback(self.elapsed_time())

    def stop(self):
        self.callback = None
        self.running = False

    def elapsed_time(self):
        return current_millis() - self.start_time


# === GUI ===


class KeyDetectWindow(QWidget):

    def __init__(self, key_press, key_release, mouse_press, mouse_release,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_press_callback = key_press
        self.key_release_callback = key_release
        self.mouse_press_callback = mouse_press
        self.mouse_release_callback = mouse_release
        self.grabGesture(Qt.TapAndHoldGesture)

    def keyPressEvent(self, event):
        self.key_press_callback(event)

    def keyReleaseEvent(self, event):
        self.key_release_callback(event)

    def mousePressEvent(self, event):
        self.mouse_press_callback(event)

    def mouseReleaseEvent(self, event):
        self.mouse_release_callback(event)

    # def event(self, event):
    #     print("event_type: %s", event.type())
    #
    #     # if event.type() == QGestureEvent.MouseButtonPress:
    #         # event.accept()
    #     if event.type == QGestureEvent.Gesture:
    #         self.mouse_press_callback(event)
    #
    #     return QEvent(event)


def main():
    # CONFIG (from json)

    try:
        with open("config.json", "r") as config_file:
            config = json.loads(config_file.read())
            print("Loaded config: %s" % config)
    except:
        print("Cannot find config.json")
        exit(-1)

    app = QApplication([])

    # MAIN WINDOW

    def on_key_pressed(event):
        if event.key() in config["timer_buttons"]:
            timer.press()

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

    container.setAutoFillBackground(True)
    container.setStyleSheet("background-color: %s" % config["background_color"])

    # SCRAMBLE LABEL

    scramble = QLabel()
    scramble.setStyleSheet("QLabel { color: %s; font-size %dpx;}" %
                           (config["scramble_color"], config["scramble_fontsize"]))
    scramble.setAlignment(Qt.AlignHCenter)
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

    def handle_time_callback(ms, instance=None):
        fmt = "%.2f" if instance is None or instance.state == RubikTimer.State.TIMING else "%.0f"
        sec = ms / 1000
        display.setText(fmt % sec)

    def handle_event_callback(rubik_event, instance=None):
        print(">> Current state: %s" % rubik_event.value)
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

        if rubik_event == RubikTimer.Event.STOP or \
                rubik_event == RubikTimer.Event.DNF:
            update_scramble()

        display.setStyleSheet(display_style(c, config["display_fontsize"]))
        if t:
            display.setText(t)

    timer = RubikTimer(event_callback=handle_event_callback,
                       time_callback=handle_time_callback,)

    handle_time_callback(0)

    # SETUP

    layout = QVBoxLayout()
    layout.addWidget(scramble, stretch=0)
    layout.addWidget(display, stretch=1)

    container.setLayout(layout)

    container.resize(config["width"], config["height"])
    container.show()

    app.exec_()


if __name__ == "__main__":
    main()
