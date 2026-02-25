from enum import IntFlag

class HeroOptions:
    KERRIGAN = "Kerrigan"
    NOVA = "Nova"
    ARTANIS = "Artanis" # not yet implemented


class HeroFlag(IntFlag):
    # get send to the mission, must match the SC2Data implementation
    NONE = 0
    KERRIGAN = 1
    NOVA = 2
    ARTANIS = 4
