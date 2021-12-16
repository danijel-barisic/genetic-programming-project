MINIMAL_ANGLE = 5
MAXIMAL_ANGLE = 60

class OutputDecoder:
    def __init__(self):
        pass

class DirectionDecoder(OutputDecoder):
    def __init__(self):
        pass
    def decode(self, output):
        if output < 0:
            return 0
        else:
            return output

class AngleDecoder(OutputDecoder):
    def __init__(self):
        pass
    def decode(self, output):
        if abs(output) < MINIMAL_ANGLE:
            return 0
        elif output > 0:
            return min(output, MAXIMAL_ANGLE)
        else:
            return max(output, -MINIMAL_ANGLE)