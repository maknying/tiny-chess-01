
import json, os, sys, urllib.request, urllib.error, random, base64

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")

VAL = [0, 82, 337, 365, 477, 1025, 0]
MATE = 100000
INF = 1000000
BG = 60000
MD = 64
SF = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq"
HS = set()

P=[0, 0, 0, 0, 52, 80, 96, 80, -16, 23, 40, 48, -4, 12, 24, 13, -17, 11, -16, 12, -26, 32, 3, 1, -27, 21, -12, -19, 0, 0, 0, 0, -139, -48, -64, 8, -48, -16, 55, 33, 0, 56, 80, 76, 8, 16, 32, 48, -8, 16, 22, 3, -16, 1, 9, 16, -24, -32, 0, 1, -64, -16, -40, -24, -16, 8, -48, -32, -32, 16, 16, 8, -8, 40, 53, 40, 0, 12, 16, 48, 0, 16, 17, 32, 11, 25, 27, 0, 0, 30, 16, 11, -24, -24, -26, -13, 42, 32, 16, 56, 32, 36, 64, 70, 16, 41, 28, 22, -25, -16, 24, 24, -32, -8, -8, 7, -42, -27, -12, -8, -56, -8, 0, -8, -8, -24, -8, 13, 8, 24, 32, 32, 16, -8, 24, -8, 24, 13, 32, 16, -16, -17, 0, 8, -8, -16, -11, -5, 0, 8, 0, 1, -16, -8, 14, 0, -24, -24, -16, -4, -24, 16, -8, -32, 0, -16, -16, -8, -16, 24, 0, -16, -24, -16, -16, -32, -48, -16, -32, -40, -16, -16, -23, -47, 0, 8, -16, -56, 0, 16, -13, -8, -48, -16, 0, -16, 0, 16, 24, 16, 16, 32, 32, 18, 0, 24, 32, 24, -19, 0, 24, 8, -16, 7, 19, 28, -24, -12, 8, 20, -48, -33, -16, -16]
BASE=[0,32,64,96,128,160]

KN = (-33, -31, -18, -14, 14, 18, 31, 33)
KI = (-17, -16, -15, -1, 1, 15, 16, 17)
BI = (-17, -15, 15, 17)
RO = (-16, -1, 1, 16)

_rng = random.Random(0xC0FFEE)
ZB = [[_rng.getrandbits(64) for _ in range(128)] for _ in range(12)]
ZS = _rng.getrandbits(64)
ZC = [_rng.getrandbits(64) for _ in range(16)]
ZE = [_rng.getrandbits(64) for _ in range(8)]

B = [0] * 128
SI = 1
RI = 0
EP = -1
KY = 0
PA = []
TT = {}
KL = [[0, 0] for _ in range(MD + 1)]
HI = [[0] * 128 * 128 for _ in range(2)]
NO = 0

class BO(Exception):
    pass

def zp(pc, sq):
    return ZB[(pc - 1 if pc > 0 else -pc - 1 + 6)][sq]

def fen(fen):
    global SI, RI, EP, KY
    for i in range(128):
        B[i] = 0
    parts = fen.split()
    rows = parts[0].split("/")
    for r, row in enumerate(rows):
        f = 0
        for c in row:
            if c.isdigit():
                f += int(c)
            else:
                sq = (7 - r) * 16 + f
                B[sq] = "PNBRQK".index(c.upper()) + 1
                if c.islower():
                    B[sq] = -B[sq]
                f += 1
    SI = 1 if parts[1] == "w" else -1
    RI = 0
    if len(parts) > 2:
        for c in parts[2]:
            if c == "K":
                RI |= 1
            elif c == "Q":
                RI |= 2
            elif c == "k":
                RI |= 4
            elif c == "q":
                RI |= 8
    EP = -1
    if len(parts) > 3 and parts[3] != "-":
        EP = (int(parts[3][1]) - 1) * 16 + (ord(parts[3][0]) - 97)
    KY = 0
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if p:
            KY ^= zp(p, sq)
    if SI < 0:
        KY ^= ZS
    KY ^= ZC[RI]
    if EP >= 0:
        KY ^= ZE[EP & 7]

def kg(side):
    k = 6 if side > 0 else -6
    for sq in range(128):
        if not (sq & 0x88) and B[sq] == k:
            return sq
    return -1

def atk(sq, by):

    if by > 0:
        for d in (-15, -17):
            t = sq + d
            if not (t & 0x88) and B[t] == 1:
                return True
        for d in KN:
            t = sq + d
            if not (t & 0x88) and B[t] == 2:
                return True
    else:
        for d in (15, 17):
            t = sq + d
            if not (t & 0x88) and B[t] == -1:
                return True
        for d in KN:
            t = sq + d
            if not (t & 0x88) and B[t] == -2:
                return True
    for d in KI:
        t = sq + d
        if not (t & 0x88) and B[t] == 6 * by:
            return True
    for d in BI:
        t = sq + d
        while not (t & 0x88):
            p = B[t]
            if p:
                if p == 3 * by or p == 5 * by:
                    return True
                break
            t += d
    for d in RO:
        t = sq + d
        while not (t & 0x88):
            p = B[t]
            if p:
                if p == 4 * by or p == 5 * by:
                    return True
                break
            t += d
    return False

def gen(caps_only=False):
    global B
    mv = []
    side = SI
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if p == 0 or (p > 0) != (side > 0):
            continue
        t = abs(p)
        if t == 1:
            d = 16 if side > 0 else -16
            one = sq + d
            if not (one & 0x88) and B[one] == 0:
                if (one >> 4) in (0, 7):
                    if not caps_only:
                        for pr in (5, 4, 3, 2):
                            mv.append(sq | (one << 7) | (pr << 14))
                else:
                    if not caps_only:
                        mv.append(sq | (one << 7))
                    two = sq + 2 * d
                    if ((sq >> 4) == 1 and side > 0 or (sq >> 4) == 6 and side < 0)\
                            and B[two] == 0:
                        mv.append(sq | (two << 7))
            for dd in (d - 1, d + 1):
                to = sq + dd
                if to & 0x88:
                    continue
                q = B[to]
                if q and (q > 0) != (side > 0):
                    if (to >> 4) in (0, 7):
                        for pr in (5, 4, 3, 2):
                            mv.append(sq | (to << 7) | (pr << 14))
                    else:
                        mv.append(sq | (to << 7))
                elif to == EP:
                    mv.append(sq | (to << 7))
        elif t == 2 or t == 6:
            for d in (KN if t == 2 else KI):
                to = sq + d
                if to & 0x88:
                    continue
                q = B[to]
                if q == 0:
                    if not caps_only:
                        mv.append(sq | (to << 7))
                elif (q > 0) != (side > 0):
                    mv.append(sq | (to << 7))
        else:
            for d in (BI if t == 3 else RO if t == 4 else
                      BI + RO):
                to = sq + d
                while not (to & 0x88):
                    q = B[to]
                    if q == 0:
                        if not caps_only:
                            mv.append(sq | (to << 7))
                    else:
                        if (q > 0) != (side > 0):
                            mv.append(sq | (to << 7))
                        break
                    to += d

    if not caps_only:
        if side > 0:
            if RI & 1 and B[5] == 0 and B[6] == 0 and B[4] == 6\
                    and not atk(4, -1) and not atk(5, -1)\
                    and not atk(6, -1):
                mv.append(4 | (6 << 7))
            if RI & 2 and B[3] == 0 and B[2] == 0 and B[1] == 0 and B[4] == 6\
                    and not atk(4, -1) and not atk(3, -1)\
                    and not atk(2, -1):
                mv.append(4 | (2 << 7))
        else:
            if RI & 4 and B[117] == 0 and B[118] == 0 and B[116] == -6\
                    and not atk(116, 1) and not atk(117, 1)\
                    and not atk(118, 1):
                mv.append(116 | (118 << 7))
            if RI & 8 and B[115] == 0 and B[114] == 0 and B[113] == 0\
                    and B[116] == -6\
                    and not atk(116, 1) and not atk(115, 1)\
                    and not atk(114, 1):
                mv.append(116 | (114 << 7))
    return mv

def make(m):
    global SI, RI, EP, KY
    f = m & 127
    t = (m >> 7) & 127
    pr = (m >> 14) & 7
    pc = B[f]
    cap = 0
    cap_sq = t
    if B[t]:
        cap = B[t]
    elif abs(pc) == 1 and t == EP:
        cap_sq = t - 16 if pc > 0 else t + 16
        cap = B[cap_sq]
    undo = (cap, cap_sq, RI, EP, KY, pc)
    KY ^= zp(pc, f)
    if cap:
        KY ^= zp(cap, cap_sq)
        B[cap_sq] = 0

    if abs(pc) == 6 and abs(t - f) == 2:
        if t > f:
            rs, re = f + 3, f + 1
        else:
            rs, re = f - 4, f - 1
        rook = B[rs]
        KY ^= zp(rook, rs) ^ zp(rook, re)
        B[re] = rook
        B[rs] = 0
    new_piece = (pr if pr else abs(pc)) * (1 if pc > 0 else -1)
    KY ^= zp(new_piece, t)
    B[t] = new_piece
    B[f] = 0

    old_rights = RI
    if f == 4 or t == 4:
        RI &= ~3
    if f == 116 or t == 116:
        RI &= ~12
    if f == 7 or t == 7:
        RI &= ~1
    if f == 0 or t == 0:
        RI &= ~2
    if f == 119 or t == 119:
        RI &= ~4
    if f == 112 or t == 112:
        RI &= ~8
    KY ^= ZC[old_rights] ^ ZC[RI]
    if EP >= 0:
        KY ^= ZE[EP & 7]
    EP = -1
    if abs(pc) == 1 and abs(t - f) == 32:
        EP = (f + t) // 2
        KY ^= ZE[EP & 7]
    SI = -SI
    KY ^= ZS
    return undo

def unmake(m, undo):
    global SI, RI, EP, KY
    f = m & 127
    t = (m >> 7) & 127
    pr = (m >> 14) & 7
    cap, cap_sq, RI, EP, KY, pc = undo
    SI = -SI
    B[f] = pc
    B[t] = 0
    if cap:
        B[cap_sq] = cap
    if abs(pc) == 6 and abs(t - f) == 2:
        if t > f:
            rs, re = f + 3, f + 1
        else:
            rs, re = f - 4, f - 1
        B[rs] = B[re]
        B[re] = 0

def ev():
    sc = 0
    nb = 0
    wb = 0
    bb = 0
    wk = 0
    bk = 0
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if not p:
            continue
        t = abs(p)
        if t != 1 and t != 6:
            nb += VAL[t]
        if t == 3:
            if p > 0:
                wb += 1
            else:
                bb += 1
        if t == 6:
            if p > 0:
                wk = sq
            else:
                bk = sq
        r = sq >> 4
        f = sq & 7
        c = f if f < 4 else 7 - f
        if p > 0:
            sc += VAL[t] + P[BASE[t - 1] + (7 - r) * 4 + c]
        else:
            sc -= VAL[t] + P[BASE[t - 1] + r * 4 + c]
    if wb >= 2:
        sc += 30
    if bb >= 2:
        sc -= 30
    if nb < 1400:
        r = wk >> 4
        f = wk & 7
        c = f if f < 4 else 7 - f
        sc += P[192 + (7 - r) * 4 + c] - P[160 + (7 - r) * 4 + c]
        r = bk >> 4
        f = bk & 7
        c = f if f < 4 else 7 - f
        sc -= P[192 + r * 4 + c] - P[160 + r * 4 + c]
    return sc if SI > 0 else -sc

def odr(mv, tm, y):
    def key_of(m):
        t = (m >> 7) & 127
        cap = B[t]
        f = m & 127
        s = 1000000 if m == tm else 0
        if cap:
            s += 10 * VAL[abs(cap)] - VAL[abs(B[f])] // 10
        elif abs(B[f]) == 1 and t == EP:
            s += 10 * VAL[1]
        if m == KL[y][0]:
            s += 9000
        elif m == KL[y][1]:
            s += 8000
        else:
            s += HI[0 if SI > 0 else 1][m & 16383]
        return -s
    mv.sort(key=key_of)
    return mv

def qs(a, b, y):
    global NO
    NO += 1
    if NO >= BG:
        raise BO()
    if KY in PA[:-1]:
        return 0
    ck = atk(kg(SI), -SI)
    if not ck:
        stand = ev()
        if stand >= b:
            return b
        if stand > a:
            a = stand
    mv = gen(caps_only=not ck)
    odr(mv, 0, y)
    lg = 0
    for m in mv:
        undo = make(m)
        if atk(kg(-SI), SI):
            unmake(m, undo)
            continue
        lg += 1
        PA.append(KY)
        v = -qs(-b, -a, y + 1)
        PA.pop()
        unmake(m, undo)
        if v >= b:
            return b
        if v > a:
            a = v
    if ck and lg == 0:
        return -MATE + y
    return a

def sr(dp, a, b, y):
    global NO, KY, EP, SI
    NO += 1
    if NO >= BG:
        raise BO()
    if KY in PA[:-1] or KY in HS:
        return 0
    if dp <= 0:
        return qs(a, b, y)
    oa = a
    tm = 0
    ent = TT.get(KY)
    if ent:
        _, flag, val, mv = ent
        tm = mv
        if ent[0] >= dp:
            if flag == 0:
                return val
            if flag == 1 and val > a:
                a = val
            elif flag == 2 and val < b:
                b = val
            if a >= b:
                return val
    ck = atk(kg(SI), -SI)
    if dp >= 3 and not ck and b < MATE - 1000:
        ok = KY
        oe = EP
        if EP >= 0:
            KY ^= ZE[EP & 7]
        EP = -1
        SI = -SI
        KY ^= ZS
        PA.append(KY)
        v = -sr(dp - 3, -b, -b + 1, y + 1)
        PA.pop()
        SI = -SI
        KY = ok
        EP = oe
        if v >= b:
            return b
    mv = gen()
    odr(mv, tm, y)
    best = -INF
    bm = 0
    lg = 0
    for m in mv:
        undo = make(m)
        if atk(kg(-SI), SI):
            unmake(m, undo)
            continue
        lg += 1
        PA.append(KY)
        v = -sr(dp - 1, -b, -a, y + 1)
        PA.pop()
        unmake(m, undo)
        if v > best:
            best = v
            bm = m
        if v > a:
            a = v
            if a >= b:
                if not B[(m >> 7) & 127]:
                    if KL[y][0] != m:
                        KL[y][1] = KL[y][0]
                        KL[y][0] = m
                    HI[0 if SI > 0 else 1][m & 16383] += dp * dp
                break
    if lg == 0:
        return -MATE + y if ck else 0
    if abs(best) < MATE - 1000:
        if best <= oa:
            flag = 2
        elif best >= b:
            flag = 1
        else:
            flag = 0
        TT[KY] = (dp, flag, best, bm)
    return best

def enc(u):
    f = (ord(u[0]) - 97) + (int(u[1]) - 1) * 16
    t = (ord(u[2]) - 97) + (int(u[3]) - 1) * 16
    pr = 0
    if len(u) == 5:
        pr = "nbrq".index(u[4]) + 2
    return f | (t << 7) | (pr << 14)

def dec(m):
    f = m & 127
    t = (m >> 7) & 127
    pr = (m >> 14) & 7
    s = chr(97 + (f & 7)) + str((f >> 4) + 1) + chr(97 + (t & 7)) + str((t >> 4) + 1)
    if pr:
        s += "nbrq"[pr - 2]
    return s

def best(fs, lg, mv):
    global NO, PA, HS
    fen(SF)
    HS = set()
    for u in mv:
        HS.add(KY)
        make(enc(u))
    fen(fs)
    if len(lg) == 1:
        return lg[0]
    root = [enc(u) for u in lg]

    root.sort(key=lambda m: -(10 * VAL[abs(B[(m >> 7) & 127])] if B[(m >> 7) & 127] else 0))
    NO = 0
    PA = [KY]
    bm = root[0]
    dp = 1
    while dp <= MD:
        try:
            cb = None
            cs = -INF
            a = -INF
            for m in root:
                undo = make(m)
                PA.append(KY)
                v = -sr(dp - 1, -INF, -a, 1)
                PA.pop()
                unmake(m, undo)
                if v > cs:
                    cs = v
                    cb = m
                if v > a:
                    a = v
            bm = cb

            root.remove(bm)
            root.insert(0, bm)
            dp += 1
        except BO:
            break
    return dec(bm)

def post(path, body):
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")

def main():
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            g = post("/move", {"game": g["game"],
                               "move": best(g["fen"], g["legal_moves"], g["moves"])})

if __name__ == "__main__":
    main()
