from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QWidget


from cube.commons import *


class ScramblePreview(QWidget):
    HORIZONTAL_CELL_COUNT = 4 * 3
    VERTICAL_CELL_COUNT = 3 * 3

    HORIZONTAL_LINES = HORIZONTAL_CELL_COUNT + 1
    VERTICAL_LINES = VERTICAL_CELL_COUNT + 1

    def __init__(self, width,
                 up_color, down_color, front_color,
                 back_color, right_color, left_color,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cellsize = max(1, int((width - ScramblePreview.HORIZONTAL_LINES) /
                                   ScramblePreview.HORIZONTAL_CELL_COUNT))
        self.margin = width - ScramblePreview.HORIZONTAL_LINES - \
                      (self.cellsize * ScramblePreview.HORIZONTAL_CELL_COUNT)
        self.state = None

        self.up_brush = QBrush(QColor(up_color))
        self.down_brush = QBrush(QColor(down_color))
        self.front_brush = QBrush(QColor(front_color))
        self.back_brush = QBrush(QColor(back_color))
        self.right_brush = QBrush(QColor(right_color))
        self.left_brush = QBrush(QColor(left_color))

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(ScramblePreview.HORIZONTAL_CELL_COUNT * self.cellsize + ScramblePreview.HORIZONTAL_LINES + 4,
                          ScramblePreview.VERTICAL_CELL_COUNT * self.cellsize + ScramblePreview.VERTICAL_LINES + 4)
        self.show()

    def update_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, a0: QPaintEvent):
        if not self.state:
            return
        painter = QPainter()
        painter.begin(self)
        self.draw_scramble(painter)
        painter.end()

    def draw_scramble(self, painter):
        painter.setPen(Qt.black)

        def draw_cell(cell, hmargin, vmargin, h, v):
            if cell == FACE_UP:
                painter.setBrush(self.up_brush)
            if cell == FACE_DOWN:
                painter.setBrush(self.down_brush)
            if cell == FACE_FRONT:
                painter.setBrush(self.front_brush)
            if cell == FACE_BACK:
                painter.setBrush(self.back_brush)
            if cell == FACE_LEFT:
                painter.setBrush(self.left_brush)
            if cell == FACE_RIGHT:
                painter.setBrush(self.right_brush)

            painter.drawRect(hmargin + h * self.cellsize,
                             vmargin + v * self.cellsize,
                             self.cellsize,
                             self.cellsize)

        def draw_face(face, pieces, hmargin, vmargin):
            painter.setPen(Qt.black)
            draw_cell(pieces[UL], hmargin, vmargin, 0, 0)
            draw_cell(pieces[UC], hmargin, vmargin, 1, 0)
            draw_cell(pieces[UR], hmargin, vmargin, 2, 0)
            draw_cell(pieces[ML], hmargin, vmargin, 0, 1)
            draw_cell(face, hmargin, vmargin, 1, 1)
            draw_cell(pieces[MR], hmargin, vmargin, 2, 1)
            draw_cell(pieces[DL], hmargin, vmargin, 0, 2)
            draw_cell(pieces[DC], hmargin, vmargin, 1, 2)
            draw_cell(pieces[DR], hmargin, vmargin, 2, 2)

            # Border

            bold = QPen()
            bold.setWidth(2)
            painter.setPen(bold)
            painter.setBrush(Qt.transparent)
            painter.drawRect(hmargin, vmargin, 3 * self.cellsize, 3 * self.cellsize)

        up_margins = (self.margin + 3 * self.cellsize, self.margin)
        left_margins = (self.margin, self.margin + 3 * self.cellsize)
        front_margins = (self.margin + 3 * self.cellsize, self.margin + 3 * self.cellsize)
        right_margins = (self.margin + 6 * self.cellsize, self.margin + 3 * self.cellsize)
        back_margins = (self.margin + 9 * self.cellsize, self.margin + 3 * self.cellsize)
        down_margins = (self.margin + 3 * self.cellsize, self.margin + 6 * self.cellsize)

        draw_face(FACE_UP, self.state.up, *up_margins)
        draw_face(FACE_LEFT, self.state.left, *left_margins)
        draw_face(FACE_FRONT, self.state.front, *front_margins)
        draw_face(FACE_RIGHT, self.state.right, *right_margins)
        draw_face(FACE_BACK, self.state.back, *back_margins)
        draw_face(FACE_DOWN, self.state.down, *down_margins)
