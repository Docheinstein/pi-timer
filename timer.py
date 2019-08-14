import random
import time
from threading import Thread, Event

# === TIMER ===


def current_millis():
    return int(round(time.time() * 1000))


class RubikTimer:

    class State:
        IDLE = "idle"
        INSPECTING = "inspecting"
        TIMING = "timing"

    class StateFlags:
        ALMOST_READY = 0x01
        READY = 0x02
        PLUS_TWO = 0x04
        DNF = 0x08

    class Event:
        INSPECTING = "inspecting"
        PLUS_TWO = "plus_two"
        DNF = "DNF"
        ALMOST_READY = "almost_ready"
        READY = "ready"
        START = "start"
        STOP = "stop"
        RESET = "reset"

    def __init__(self,
                 event_callback,
                 time_callback,
                 inspecting_sec=15,
                 ready_press_time=500):
        self.event_callback = event_callback
        self.time_callback = time_callback
        self.inspecting_sec = inspecting_sec
        self.ready_press_time = ready_press_time
        self.state = RubikTimer.State.IDLE
        self.state_flags = 0
        self.timer = None
        self.pressing = False
        self.almost_ready_action_id = None
        self.malus = False

    def press(self):
        if self.pressing:
            return
        print("\n<press>")
        self.pressing = True
        if self.state == RubikTimer.State.IDLE:
            self._start_inspecting()
        elif self.state == RubikTimer.State.INSPECTING:
            if not self.has_dnf():
                self._almost_ready()
        elif self.state == RubikTimer.State.TIMING:
            self._stop_timer()

    def release(self):
        print("\n<release>")
        self.pressing = False
        self.almost_ready_action_id = None
        if self.state == RubikTimer.State.INSPECTING:
            if self.state_flags & RubikTimer.StateFlags.ALMOST_READY:
                self._continue_inspecting()
            elif self.state_flags & RubikTimer.StateFlags.READY:
                self._start_timer()

    def reset(self):
        print("\n<reset>")
        self._cleanup()
        self.event_callback(RubikTimer.Event.RESET, self)

    def has_plus_two(self):
        return self.state_flags & RubikTimer.StateFlags.PLUS_TWO

    def has_dnf(self):
        return self.state_flags & RubikTimer.StateFlags.DNF

    def _start_inspecting(self):
        print("Start inspecting")
        self._deinit_timer()

        self.state = RubikTimer.State.INSPECTING
        self.event_callback(RubikTimer.Event.INSPECTING, self)

        def handle_backward_timer(ms):
            if not self.timer:
                return

            if self.state == RubikTimer.State.INSPECTING and \
                    self.timer.ticks >= self.inspecting_sec:
                if self.state_flags & RubikTimer.StateFlags.PLUS_TWO and \
                        self.timer.ticks >= self.inspecting_sec + 2:
                    self._dnf()
                else:
                    self._plus_two()
            else:
                self.time_callback(ms, self)

        self.timer = BackwardTimer(self.inspecting_sec * 1000,
                                   handle_backward_timer)
        self.timer.start()

    def _continue_inspecting(self):
        print("Continue inspecting")
        self.state = RubikTimer.State.INSPECTING
        self.state_flags = self.state_flags & RubikTimer.StateFlags.PLUS_TWO
        self.event_callback(RubikTimer.Event.INSPECTING, self)

    def _almost_ready(self):
        action_id = int(random.random() * 2147483647)
        self.almost_ready_action_id = action_id
        print("Almost ready")
        self.state = RubikTimer.State.INSPECTING
        self.state_flags = self.state_flags & RubikTimer.StateFlags.PLUS_TWO
        self.state_flags = self.state_flags | RubikTimer.StateFlags.ALMOST_READY
        self.event_callback(RubikTimer.Event.ALMOST_READY, self)

        def almost_ready_waiter():
            time.sleep(self.ready_press_time / 1000)
            if self.almost_ready_action_id == action_id:
                self._ready()

        t = Thread(target=almost_ready_waiter)
        t.start()

    def _ready(self):
        print("Ready")
        self.state = RubikTimer.State.INSPECTING
        self.state_flags = self.state_flags & RubikTimer.StateFlags.PLUS_TWO
        self.state_flags = self.state_flags | RubikTimer.StateFlags.READY
        self.event_callback(RubikTimer.Event.READY, self)

    def _dnf(self):
        print("DNF")
        self._deinit_timer()
        self.state = RubikTimer.State.IDLE
        self.state_flags = RubikTimer.StateFlags.DNF
        self.event_callback(RubikTimer.Event.DNF, self)

    def _plus_two(self):
        print("+2")
        self.state = RubikTimer.State.INSPECTING
        self.state_flags = self.state_flags | RubikTimer.StateFlags.PLUS_TWO
        self.event_callback(RubikTimer.Event.PLUS_TWO, self)

    def _start_timer(self):
        print("Start timer")
        self._deinit_timer()
        self.timer = ForwardTimer(lambda t: self.time_callback(t, self))
        self.timer.start()

        self.state = RubikTimer.State.TIMING
        self.event_callback(RubikTimer.Event.START, self)

    def _stop_timer(self):
        print("Stop timer")
        t = self.timer.elapsed_time()
        print("Elapsed time", t)
        self._deinit_timer()
        self.state = RubikTimer.State.IDLE
        self.time_callback(t + (0 if not (self.has_plus_two()) else 2000), self)
        self.event_callback(RubikTimer.Event.STOP, self)
        self._cleanup()

    def _cleanup(self):
        self._deinit_timer()
        self.state = RubikTimer.State.IDLE
        self.state_flags = 0
        self.pressing = False
        self.almost_ready_action_id = None

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

