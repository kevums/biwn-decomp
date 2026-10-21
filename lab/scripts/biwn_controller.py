"""Controller IDs pinned to the bundled libretro.c standard-pad mapping.

Digits7–9 and Jaguar */# use its keyboard fallback. In that fallback,
RETROK_MINUS selects Jaguar * and RETROK_EQUALS selects Jaguar #.
"""
JOYPAD_BUTTONS={'U':4,'D':5,'L':6,'R':7,'A':8,'B':0,'C':1,
                'OPTION':3,'PAUSE':2,'0':9,'1':10,'2':11,'3':12,
                '4':13,'5':14,'6':15}
KEYBOARD_BUTTONS={'7':55,'8':56,'9':57,'*':45,'#':61}
BUTTONS=frozenset(JOYPAD_BUTTONS)|frozenset(KEYBOARD_BUTTONS)
