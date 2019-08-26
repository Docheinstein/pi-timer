import random

from cube.commons import *


def rotated_list(l, x):
    return l[-x:] + l[:-x]


class CubeState:
    MOVES = [
        'u', 'ui', 'u2',
        'd', 'di', 'd2',
        'f', 'fi', 'f2',
        'b', 'bi', 'b2',
        'r', 'ri', 'r2',
        'l', 'li', 'l2'
    ]

    def __init__(self):
        self.up = [FACE_UP] * 8
        self.down = [FACE_DOWN] * 8
        self.front = [FACE_FRONT] * 8
        self.back = [FACE_BACK] * 8
        self.right = [FACE_RIGHT] * 8
        self.left = [FACE_LEFT] * 8

    def u(self):
        t1, t2, t3 = self.left[UL], self.left[UC], self.left[UR]
        self.left[UL], self.left[UC], self.left[UR] = self.front[UL], self.front[UC], self.front[UR]
        self.front[UL], self.front[UC], self.front[UR] = self.right[UL], self.right[UC], self.right[UR]
        self.right[UL], self.right[UC], self.right[UR] = self.back[UL], self.back[UC], self.back[UR]
        self.back[UL], self.back[UC], self.back[UR] = t1, t2, t3
        self.up = rotated_list(self.up, 2)

    def ux(self, times=1):
        for i in range(times):
            self.u()

    def u2(self):
        self.ux(2)

    def ui(self):
        self.ux(3)

    def d(self):
        t1, t2, t3 = self.back[DL], self.back[DC], self.back[DR]
        self.back[DL], self.back[DC], self.back[DR] = self.right[DL], self.right[DC], self.right[DR]
        self.right[DL], self.right[DC], self.right[DR] = self.front[DL], self.front[DC], self.front[DR]
        self.front[DL], self.front[DC], self.front[DR] = self.left[DL], self.left[DC], self.left[DR]
        self.left[DL], self.left[DC], self.left[DR] = t1, t2, t3
        self.down = rotated_list(self.down, 2)

    def dx(self, times=1):
        for i in range(times):
            self.d()

    def d2(self):
        self.dx(2)

    def di(self):
        self.dx(3)

    def f(self):
        t1, t2, t3 = self.up[DL], self.up[DC], self.up[DR]
        self.up[DL], self.up[DC], self.up[DR] = self.left[DR], self.left[MR], self.left[UR]
        self.left[DR], self.left[MR], self.left[UR] = self.down[UR], self.down[UC], self.down[UL]
        self.down[UR], self.down[UC], self.down[UL] = self.right[UL], self.right[ML], self.right[DL]
        self.right[UL], self.right[ML], self.right[DL] = t1, t2, t3
        self.front = rotated_list(self.front, 2)

    def fx(self, times=1):
        for i in range(times):
            self.f()

    def f2(self):
        self.fx(2)

    def fi(self):
        self.fx(3)

    def b(self):
        t1, t2, t3 = self.up[UR], self.up[UC], self.up[UL]
        self.up[UR], self.up[UC], self.up[UL] = self.right[DR], self.right[MR], self.right[UR]
        self.right[DR], self.right[MR], self.right[UR] = self.down[DL], self.down[DC], self.down[DR]
        self.down[DL], self.down[DC], self.down[DR] = self.left[UL], self.left[ML], self.left[DL]
        self.left[UL], self.left[ML], self.left[DL] = t1, t2, t3
        self.back = rotated_list(self.back, 2)

    def bx(self, times=1):
        for i in range(times):
            self.b()

    def b2(self):
        self.bx(2)

    def bi(self):
        self.bx(3)

    def r(self):
        t1, t2, t3 = self.up[UR], self.up[MR], self.up[DR]
        self.up[UR], self.up[MR], self.up[DR] = self.front[UR], self.front[MR], self.front[DR]
        self.front[UR], self.front[MR], self.front[DR] = self.down[UR], self.down[MR], self.down[DR]
        self.down[UR], self.down[MR], self.down[DR] = self.back[DL], self.back[ML], self.back[UL]
        self.back[DL], self.back[ML], self.back[UL] = t1, t2, t3
        self.right = rotated_list(self.right, 2)

    def rx(self, times=1):
        for i in range(times):
            self.r()

    def r2(self):
        self.rx(2)

    def ri(self):
        self.rx(3)

    def l(self):
        t1, t2, t3 = self.back[UR], self.back[MR], self.back[DR]
        self.back[UR], self.back[MR], self.back[DR] = self.down[DL], self.down[ML], self.down[UL]
        self.down[DL], self.down[ML], self.down[UL] = self.front[DL], self.front[ML], self.front[UL]
        self.front[DL], self.front[ML], self.front[UL] = self.up[DL], self.up[ML], self.up[UL]
        self.up[DL], self.up[ML], self.up[UL] = t1, t2, t3
        self.left = rotated_list(self.left, 2)

    def lx(self, times=1):
        for i in range(times):
            self.l()

    def l2(self):
        self.lx(2)

    def li(self):
        self.lx(3)

    def alg(self, alg):
        for m in alg.moves:
            getattr(self, m[0].lower() + "x")(m[1])

    def moves(self, *moves):
        for m in moves:
            getattr(self, m)()

    def rand(self, apply=True):
        m = random.choice(CubeState.MOVES)
        if apply:
            getattr(self, m)()
        return m

    def __str__(self):
        return " " * 7 + self.up[UL] + " " + self.up[UC] + " " + self.up[UR] + "\n" + \
               " " * 7 + self.up[ML] + " " + FACE_UP + " " + self.up[MR] + " " + "\n" + \
               " " * 7 + self.up[DL] + " " + self.up[DC] + " " + self.up[DR] + " " + "\n\n" + \
               self.left[UL] + " " + self.left[UC] + " " + self.left[UR] + "  " + \
               self.front[UL] + " " + self.front[UC] + " " + self.front[UR] + "  " + \
               self.right[UL] + " " + self.right[UC] + " " + self.right[UR] + "  " + \
               self.back[UL] + " " + self.back[UC] + " " + self.back[UR] + "\n" + \
               self.left[ML] + " " + FACE_LEFT + " " + self.left[MR] + "  " + \
               self.front[ML] + " " + FACE_FRONT + " " + self.front[MR] + "  " + \
               self.right[ML] + " " + FACE_RIGHT + " " + self.right[MR] + "  " + \
               self.back[ML] + " " + FACE_BACK + " " + self.back[MR] + "\n" + \
               self.left[DL] + " " + self.left[DC] + " " + self.left[DR] + "  " + \
               self.front[DL] + " " + self.front[DC] + " " + self.front[DR] + "  " + \
               self.right[DL] + " " + self.right[DC] + " " + self.right[DR] + "  " + \
               self.back[DL] + " " + self.back[DC] + " " + self.back[DR] + "  " + "\n\n" + \
               " " * 7 + self.down[UL] + " " + self.down[UC] + " " + self.down[UR] + "\n" + \
               " " * 7 + self.down[ML] + " " + FACE_DOWN + " " + self.down[MR] + "\n" + \
               " " * 7 + self.down[DL] + " " + self.down[DC] + " " + self.down[DR] + "\n"
