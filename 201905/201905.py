NÉV = "201905"
VÁLTOZATOK = 10
PRÍMEK_FELSŐ_KORLÁTJA = 200

import collections
from fractions import Fraction
import math
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


def mathsor(oszlopok_száma, math_szövegek, sor_vége='\\NR \n'):
    s = " "
    for n, s_m in enumerate(math_szövegek, 1):
        m = n % oszlopok_száma
        s += f' \\NC {s_m}'
        if m == 0:
            s += sor_vége
    else:
        if m != 0:
            s += sor_vége
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

        feladat = "feladatok_egyszerusites"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 12
        for f in range(F):
            n = kalap_sorsoló((1,2,3,4,5,6,7,8,9))
            d = kalap_sorsoló((1,2,3,4,5,6,7,8,9))
            div_, mod_ = divmod(n,d)
            if not mod_:
                n = n//div_
            m = 0
            while not m:
                m = randZ((1,1,2,3))
            sorok.append(f'{{\\fraction{{{n*m}}}{{{d*m}}}}}')
            eredmények.append(f'{{\\fraction{{{n*m}}}{{{d*m}}}}}={{\\fraction{{{n}}}{{{d}}}}}')


        változat_adat[feladat]["fcontext"] = mathsor(4, sorok, sor_vége='\\NR \\TB[line]\n')
        változat_adat[feladat]["mcontext"] = mathsor(2, eredmények, sor_vége='\\NR \\TB[line]\n')

        feladat = "feladatok_bovites"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 9
        for f in range(F):
            n = randZ((1,1,2,2,3))
            d = 0
            while not d:
                d = randZ((1,2))
            sorok.append(f'{{\\fraction{{{n}}}{{{d}}}}}')
            eredmények.append(f'{{\\fraction{{{n}}}{{{d}}}}}')

        változat_adat[feladat]["fcontext"] = mathsor(3, sorok, sor_vége='\\NR \\TB[line]\n')
        változat_adat[feladat]["mcontext"] = mathsor(3, eredmények, sor_vége='\\NR \\TB[line]\n')

        feladat = "feladatok_tortmuv1"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 12
        for f in range(F):
            n1 = randZ((1,1,2,2,3))
            n2 = randZ((1,1,2,2,3))
            muv = kalap_sorsoló(("+", "-"))
            if muv == "-" and n1 < n2:
                n1, n2 = n2, n1
            d = 0
            while not d:
                d = randZ((1,2))
            sorok.append(f'{{\\fraction{{{n1}}}{{{d}}}}}{muv}{{\\fraction{{{n2}}}{{{d}}}}}')
            if muv == "+":
                n = n1+n2
            else:
                n = n1-n2
            eredmények.append(f'{{\\fraction{{{n1}}}{{{d}}}}}{muv}{{\\fraction{{{n2}}}{{{d}}}}}={{\\fraction{{{n}}}{{{d}}}}}')

        változat_adat[feladat]["fcontext"] = mathsor(3, sorok, sor_vége='\\NR \\TB[line]\n')
        változat_adat[feladat]["mcontext"] = mathsor(2, eredmények, sor_vége='\\NR \\TB[line]\n')

        feladat = "feladatok_tortmuv2"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 12
        for f in range(F):
            n1 = randZ((1,1,2,2,3))
            n2 = randZ((1,1,2,2,3))
            d1,d2 = 0,0
            while not d1:
                d1 = randZ((1,1,2,2,3))
            while not d2:
                d2 = randZ((1,1,2,2,3))
            muv = kalap_sorsoló(("+", "-"))
            if muv == "-" and n1/d1 < n2/d2:
                n1, n2, d1, d2 = n2, n1, d2, d1
            sorok.append(f'{{\\fraction{{{n1}}}{{{d1}}}}}{muv}{{\\fraction{{{n2}}}{{{d2}}}}}')
            F1 = Fraction(n1,d1)
            F2 = Fraction(n2,d2)
            if muv == "+":
                f = F1+F2
            else:
                f = F1-F2
            eredmények.append(f'{{\\fraction{{{n1}}}{{{d1}}}}}{muv}{{\\fraction{{{n2}}}{{{d2}}}}}={{\\fraction{{{f.numerator}}}{{{f.denominator}}}}}')

        változat_adat[feladat]["fcontext"] = mathsor(3, sorok, sor_vége='\\NR \\TB[line]\n')
        változat_adat[feladat]["mcontext"] = mathsor(2, eredmények, sor_vége='\\NR \\TB[line]\n')

        feladat = "feladatok_alapegyseg"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 18
        kalap = ["m", "kg", "s", "m\\high{2}", "m\\high{3}", "min", "h", "d", "t", "ha", "l", "km", "dm", "cm", "mm", "g", "dkg", "mg"]
        for f in range(F):
            me = kalap_sorsoló(kalap)
            n = randZ((1,1,2,2,3,4))
            if me == "min":
                n = random.randint(1,120)
            elif me == "h":
                n = random.randint(1,24)
            elif me == "d":
                n = random.randint(1,2)
            elif me == "l":
                n = 1000 * n
            elif me == "dm":
                n = 10 * n
            elif me == "cm":
                n = 100 * n
            elif me == "mm":
                n = 1000 * n
            elif me == "g":
                n = 1000 * n
            elif me == "g":
                n = 100 * n
            elif me == "mg":
                n = 1000000 * n
            sorok.append(f'{n}\,{me}')
            eredmények.append(f'{n}\,{me}')

        változat_adat[feladat]["fcontext"] = mathsor(3, sorok)
        változat_adat[feladat]["mcontext"] = mathsor(3, eredmények)


        feladat = "feladatok_megadottegyseg"
        sorok, eredmények = [], []
        változat_adat[feladat] = {"sorok": sorok, "eredmények": eredmények}

        F = 20
        mertek_kalap0 = {
            "hosszúság": ("mm", "cm", "dm", "m", "km",),
            "tömeg": ("mg", "g", "dkg", "kg", "t", "t"),
            "idő": ("s", "min", "h", "d"),
            "terület": ("mm\\high{2}", "cm\\high{2}", "dm\\high{2}", "m\\high{2}", "ha", "ha", "km\\high{2}"),
            "térfogat": ("mm\\high{3}", "cm\\high{3}", "ml", "cl", "dl", "dm\\high{3}", "l", "l", "hl", "m\\high{3}", "km\\high{3}"),
        }
        mertek_kalap1 = {k: list(e) for k, e in mertek_kalap0.items()}
        for f in range(F):
            k = random.choice(list(mertek_kalap1.keys()))
            kalap = mertek_kalap1[k]
            alap_kalap = mertek_kalap0[k]
            me1 = kalap_sorsoló(kalap)
            me2 = kalap_sorsoló(kalap)
            if len(kalap) < 2:
                mertek_kalap1[k] = list(mertek_kalap0[k])
            if alap_kalap.index(me2) < alap_kalap.index(me1):
                me1, me2 = me2, me1
            n = 0
            while not n:
                n = randZ((1,2,2,3,3,4))
            sorok.append(f'\\text{{{n}\,{me1}}} = \\text{{\\dots\,{me2}}}')
            eredmények.append(f'\\text{{{n}\,{me1}}} = \\text{{\\dots\,{me2}}}')

        változat_adat[feladat]["fcontext"] = mathsor(2, sorok)
        változat_adat[feladat]["mcontext"] = mathsor(2, eredmények)


        with jfájl.open("w") as f:
            json.dump(változat_adat, f, indent="\t", ensure_ascii=False)


    for kulcs, érték in változat_adat.items():
        változat_ftex = változat_ftex.replace(f'{{{{{kulcs}}}}}', (érték.get("fcontext") or érték.get("context") or ""))
        változat_mtex = változat_mtex.replace(f'{{{{{kulcs}}}}}', (érték.get("mcontext") or érték.get("context") or ""))

    változat_adatok.append(változat_adat)

    with ffájl.open("w") as f:
        f.write(változat_ftex)

    subprocess.check_call(['context', str(ffájl)])

    with mfájl.open("w") as f:
        f.write(változat_mtex)

    subprocess.check_call(['context', str(mfájl)])