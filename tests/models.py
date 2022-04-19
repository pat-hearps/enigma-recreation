from dataclasses import dataclass


@dataclass
class Window3:
    letter0: str
    letter1: str
    letter2: str

    def window(self):
        return f"{self.letter0}{self.letter1}{self.letter2}".upper()
