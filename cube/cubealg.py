class CubeAlg:

    def __init__(self):
        self.moves = []

    def add_move(self, face, turns=1):
        self.moves.append((face, turns % 4))

    def __str__(self):
        if not len(self.moves):
            return ""
        s = ""
        for m in self.moves:
            if m[1] <= 0:
                continue
            s += m[0]
            if m[1] == 2:
                s += "2"
            if m[1] == 3:
                s += "'"
            s += " "
        return s[:len(s) - 1]
