NÉV = "201904"
VÁLTOZATOK = 12
PRÍMEK_FELSŐ_KORLÁTJA = 200

import collections
from fractions import Fraction
import functools
import json
import pathlib
import operator
import random
import subprocess


# http://code.activestate.com/recipes/303060-group-a-list-into-sequential-n-tuples/
def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    return zip(*[lst[i::n] for i in range(n)]) 

# https://stackoverflow.com/a/48648756/2334951
def prod(iterable):
    return functools.reduce(operator.mul, iterable, 1)

class ErasztotenészSzitája:

    def __init__(self):
        self.n = 1
        self.köv_összetett = collections.defaultdict(list)

    def __iter__(self):
        return self
    
    def __next__(self):
        while True:
            self.n += 1
            n = self.n
            prímosztók = self.köv_összetett.get(n)
            if prímosztók is None:
                p = n  # csak jelzem, hogy n prím
                self.köv_összetett[n+p].append(p)
                return n
            else:
                for p in prímosztók:
                    self.köv_összetett[n+p].append(p)
                del self.köv_összetett[n]


szita = ErasztotenészSzitája()
prímek = []
for p in szita:
    if PRÍMEK_FELSŐ_KORLÁTJA <= p:
        break
    prímek.append(p)


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
    if számjegy == 0:
        return 0
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


def mathtab(oszlopok_száma, math_szövegek):
    s = "\\starttabulate["
    osztások_táblája = (
        ("1",), 
        ("0.5","0.5"), 
        ("0.33","0.34","0.33"), 
        ("0.25","0.25","0.25","0.25"),
        ("0.20","0.20","0.20","0.20","0.20"),
        ("0.166","0.167","0.167","0.167","0.167","0.166"), 
    )
    osztások = osztások_táblája[oszlopok_száma-1]
    for s_o in osztások:
        #s += f'|Mcw({s_o}\\textwidth)CC{{yellow}}'
        #s += f'|Mcw(\\dimexpr{s_o}\\textwidth-{float(s_o)*(oszlopok_száma-1)}em\\relax)CC{{yellow}}'
        s += f'|Mcw(\\dimexpr{s_o}\\textwidth-{float(s_o)*(oszlopok_száma-1)}em\\relax)'
    #s += "|][unit=0pt]\n"
    s += "|]\n"
    for n, s_m in enumerate(math_szövegek, 1):
        m = n % oszlopok_száma
        s += f' \\NC {s_m}'
        if m == 0:
            s += f'\\NR \n'
    else:
        if m != 0:
            s += f'\\NR \n'
    s += "\\stoptabulate\n"
    return s


with open(f'{NÉV}f.tex') as f:
    ftex = f.read()
with open(f'{NÉV}m.tex') as f:
    mtex = f.read()

prímek_súlyai = []
for i, p in enumerate(prímek):
    súly = int(1.5 ** (len(prímek) - i))
    prímek_súlyai.append((prímek_súlyai[-1] if prímek_súlyai else 0) + súly)

változat_adatok = []

for változat in range(1,VÁLTOZATOK+1):

    változat_ftex = ftex
    változat_mtex = mtex

    jfájl = pathlib.Path(f'{NÉV}j{változat:0>2}.json')
    ffájl = pathlib.Path(f'{NÉV}f{változat:0>2}.tex')
    mfájl = pathlib.Path(f'{NÉV}m{változat:0>2}.tex')

    if jfájl.is_file():
        with jfájl.open("r") as f:
            változat_adat = json.load(f)
    else:
        változat_adat = {}

        változat_adat["azonosító"] = {"context": f'{változat}/{VÁLTOZATOK}'}

        feladat = "feladatok11"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 10
        számjegy_kalap = (4,5,5,6)
        for f in range(F):
            a = randZ(számjegy_kalap)
            b = randZ(számjegy_kalap)
            sorok.append(f'{a}+{b}')
            eredmények.append(f'{a}+{b}={a+b}')

        F = 10
        számjegy_kalap = (4,5,5,6)
        for f in range(F):
            a = randZ(számjegy_kalap)
            b = randZ(számjegy_kalap)
            if a < b:
                a, b = b, a
            sorok.append(f'{a}-{b}')
            eredmények.append(f'{a}-{b}={a-b}')

        változat_adat[feladat]["fcontext"] = mathtab(2, sorok)
        változat_adat[feladat]["mcontext"] = mathtab(2, eredmények)



        feladat = "feladatok12"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 10
        számjegy_kalap = (-3,-2,-2,-1,1,2,2,3)
        operátor_kalap = ('-', '+')
        for f in range(F):
            abc = [randZ(számjegy_kalap) for _ in range(3)]
            op = [kalap_sorsoló(operátor_kalap) for _ in range(2)]
            s_abc = [(str(x) if 0 <=x else f'({x})') for x in abc]
            e = abc[0]
            s = s_abc[0]
            for i in range(2):
                e += (abc[1+i] if op[i] == '+' else -abc[1+i])
                s += op[i] + s_abc[1+i]
            sorok.append(s)
            eredmények.append(f'{s}={e}')

        változat_adat[feladat]["fcontext"] = mathtab(2, sorok)
        változat_adat[feladat]["mcontext"] = mathtab(2, eredmények)



        feladat = "feladatok20"
        változat_adat[feladat] = {}
        változat_adat[feladat]["mcontext"] = mathtab(6, prímek)



        feladat = "feladatok21"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 20
        tényezők_kalap = (3,4,4,5,5,5,6,6,7)
        számok = set()
        while len(számok) < F:
            t = kalap_sorsoló(tényezők_kalap)
            tényezők = []
            for _ in range(t):
                r = random.randint(0, prímek_súlyai[-1])
                for i, p in enumerate(prímek[:-1]):
                    if r < prímek_súlyai[i+1]:
                        break
                tényezők.append(p)
            tényezők.sort()
            a = prod(tényezők)
            if a in számok:
                continue
            számok.add(a)
            cnt = collections.Counter(tényezők)
            sorok.append(f'{a}')
            e = f'{a}='
            for i, (alap, kitevő) in enumerate(cnt.items()):
                if 1 < kitevő:
                    e += f'{alap}^{kitevő}'
                else:
                    e += f'{alap}'
                if i < len(cnt) - 1:
                    e += "\\cdot"
            eredmények.append(e)

        változat_adat[feladat]["fcontext"] = mathtab(4, sorok)
        változat_adat[feladat]["mcontext"] = mathtab(2, eredmények)

        with jfájl.open("w") as f:
            json.dump(változat_adat, f, indent="\t", ensure_ascii=False)


    for kulcs, érték in változat_adat.items():
        változat_ftex = változat_ftex.replace(f'{{{kulcs}}}', (érték.get("fcontext") or érték.get("context") or ""))
        változat_mtex = változat_mtex.replace(f'{{{kulcs}}}', (érték.get("mcontext") or érték.get("context") or ""))

    változat_adatok.append(változat_adat)

    with ffájl.open("w") as f:
        f.write(változat_ftex)

    subprocess.check_call(['context', str(ffájl)])

    with mfájl.open("w") as f:
        f.write(változat_mtex)

    subprocess.check_call(['context', str(mfájl)])