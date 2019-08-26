import random

from cube.commons import FACES
from cube.cubealg import CubeAlg


class CubeScramble(CubeAlg):

    def __init__(self, length=20):
        super().__init__()

        last_face = None

        for i in range(length):
            face = None

            while not face or face == last_face:
                face = random.choice(FACES)

            turns = random.randint(1, 3)

            self.add_move(face, turns)

            # scramble_part = face
            # if turns == 2:
            #     scramble_part += "2"
            # if turns == 3:
            #     scramble_part += "'"

            # scramble_parts.append(scramble_part)

            last_face = face


