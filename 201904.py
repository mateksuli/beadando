import subprocess

FNÉV = "201904.tex"

import random

def kalap_sorsoló(kalap=None):
    """Kisorsol egy elemet a kalapból.
    
    Ha a kalap tuple, akkor visszatevéses, ha pedig list akkor
    visszatevés nélküli húzást végez. Az utolsó elemet viszont
    mindig visszateszi.
    """
    if kalap is None:
        return None
    try:
        random.shuffle(kalap)
    except TypeError:
        return random.choice(kalap)
    else:
        if len(kalap) == 1:
            return kalap[0]
        else:
            return kalap.pop()

def randZ(számjegy_kalap=None):
    """Véletlenszerűen készít egy egész számot.

    Ha megadunk egész számokat a számjegy_kalap-ba, akkor
    abból húz, és a húzott szám dönti el, hány számjegyű lesz
    a véletlen számunk.

    A kalap egész számokat tartalmazzon. Ha a kalapból negatív
    előjelű számot húz a program, akkor az eredmény is negatív
    előjelű lesz.
    
    A kalap működéséről lásd a kalap_sorsoló doksiszövegét.
    Kalap hiányában hiányában egyjegyű egész számot ad
    eredményül.
    """
    számjegy_kalap = ((1, -1) if számjegy_kalap is None else számjegy_kalap)
    számjegy = kalap_sorsoló(számjegy_kalap)
    előjel = (-1 if számjegy < 0 else 1)
    x = 0
    számjegy = abs(számjegy)
    for i in range(számjegy):
        m = 10**i
        alsó = (1 if (1 < számjegy and i == számjegy - 1) else 0)
        y = m * random.randint(alsó, 9)
        x += y
    x *= előjel
    return x


with open(FNÉV) as f:
    tex = f.read()

for változat in range(1,10):

    sorok = []
    F = 10
    számjegy_kalap = (4,5,5,6)
    for f in range(F):
        a = randZ(számjegy_kalap)
        b = randZ(számjegy_kalap)
        sorok.append(f'\placeformula\startformula {a}+{b}= \stopformula % ={a+b}')
    F = 10
    számjegy_kalap = (4,5,5,6)
    for f in range(F):
        a = randZ(számjegy_kalap)
        b = randZ(számjegy_kalap)
        if a < b:
            a, b = b, a
        sorok.append(f'\placeformula\startformula {a}-{b}= \stopformula % ={a-b}')
    feladatok1 = "\n".join(sorok)

    tex = tex.replace("{{feladatok1}}", feladatok1)

    fnév = f'{FNÉV.split(".")[0]}_{változat:0>2}.tex'
    with open(fnév, "w") as f:
        f.write(tex)

    subprocess.check_call(['context', fnév])
