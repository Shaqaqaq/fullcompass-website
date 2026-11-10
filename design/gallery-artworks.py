"""Draws the six gallery artworks in VectorCraft (control channel on 7979): one 600 x 800 document each."""
import sys, os, time, math
sys.path.insert(0, os.path.dirname(__file__))
from craftctl import Craft
A = os.path.dirname(os.path.abspath(__file__))
NAVY, INK, CREAM, GOLD, CORAL, SLATE, MIST, PAPER, MID = "#1f3a5f", "#16263d", "#f7f4ec", "#e2b866", "#e0645a", "#5b7fa6", "#dfe6ee", "#efe9dc", "#2f4d78"
c = Craft(7979)
def fill(col): c.ex("paint.setFill", {"color": col}); c.ex("paint.setStroke", {"none": True})
def stroke(col, w, cap="butt"): c.ex("paint.setFill", {"none": True}); c.ex("paint.setStroke", {"color": col}); c.ex("stroke.set", {"weight": w, "cap": cap, "join": "round"})
def rect(x, y, w, h, col, r=0): c.ex("shape.rectangle", {"x": x, "y": y, "width": w, "height": h, **({"radius": r} if r else {})}); fill(col)
def circ(cx, cy, r, col): c.ex("shape.ellipse", {"x": cx-r, "y": cy-r, "width": 2*r, "height": 2*r}); fill(col)
def ring(cx, cy, r, col, w): c.ex("shape.ellipse", {"x": cx-r, "y": cy-r, "width": 2*r, "height": 2*r}); stroke(col, w)
def ell(cx, cy, rx, ry, col, sc=None, sw=0):
    c.ex("shape.ellipse", {"x": cx-rx, "y": cy-ry, "width": 2*rx, "height": 2*ry}); fill(col)
    if sc: c.ex("paint.setStroke", {"color": sc}); c.ex("stroke.set", {"weight": sw})
def poly(pts, col): c.ex("path.create", {"anchors": [{"x": x, "y": y} for x, y in pts], "closed": True}); fill(col)
def path(d, col, w, cap="round"): c.ex("path.create", {"d": d}); stroke(col, w, cap)
def shape(d, col): c.ex("path.create", {"d": d}); fill(col)

def suite():
    rect(0, 0, 600, 800, NAVY)
    for a in (45, 135, 225, 315):
        x, y = 300 + 262*math.cos(math.radians(a)), 370 + 262*math.sin(math.radians(a))
        path(f"M300 370 L{x:.1f} {y:.1f}", MID, 2)
    ring(300, 370, 262, MID, 2)
    circ(300, 370, 214, CREAM)
    ring(300, 370, 178, NAVY, 7)
    for x, y, w, h in ((292, 176, 16, 50), (292, 514, 16, 50), (106, 362, 50, 16), (444, 362, 50, 16)): rect(x, y, w, h, NAVY)
    poly([(300, 236), (336, 370), (264, 370)], CORAL)
    poly([(264, 370), (336, 370), (300, 504)], NAVY)
    circ(300, 370, 13, CREAM)
    rect(60, 700, 480, 3, GOLD); rect(60, 716, 150, 3, MID)
    circ(516, 92, 12, GOLD)

def accounts():
    rect(0, 0, 600, 800, CREAM)
    circ(112, 122, 30, CORAL)
    rect(60, 206, 480, 8, NAVY); rect(296, 206, 8, 420, NAVY)
    for i, (w, col) in enumerate(((190, NAVY), (150, NAVY), (110, NAVY))): rect(80, 256 + i*64, w, 34, col)
    for i, (w, col) in enumerate(((170, SLATE), (120, SLATE), (160, GOLD))): rect(326, 256 + i*64, w, 34, col)
    for x in (80, 326):
        rect(x, 560, 190, 5, NAVY); rect(x, 574, 190, 5, NAVY)
    rect(60, 700, 480, 3, NAVY); rect(390, 716, 150, 3, GOLD)

def books():
    rect(0, 0, 600, 800, GOLD)
    poly([(84, 262), (300, 306), (300, 622), (84, 578)], CREAM)
    poly([(300, 306), (516, 262), (516, 578), (300, 622)], "#ffffff")
    for i in range(5):
        y = 330 + i*48
        path(f"M116 {y} L268 {y+31}", NAVY, 7)
    for i, h in enumerate((70, 120, 96, 170)):
        x = 334 + i*42; base = 560 - (i+0.5)*42*0.204
        poly([(x, base), (x+26, base-5.3), (x+26, base-5.3-h), (x, base-h)], NAVY if i != 3 else CORAL)
    path("M300 306 L300 622", NAVY, 6, "butt")
    poly([(440, 277.5), (474, 270.5), (474, 372), (457, 356), (440, 379)], CORAL)
    rect(60, 700, 480, 3, NAVY); rect(60, 716, 150, 3, CREAM)

def businesstax():
    rect(0, 0, 600, 800, MID)
    circ(476, 136, 36, CORAL)
    poly([(104, 304), (300, 184), (496, 304)], GOLD)
    rect(104, 316, 392, 30, CREAM)
    for i in range(4): rect(128 + i*98.7, 366, 48, 216, CREAM)
    rect(92, 600, 416, 28, CREAM); rect(68, 640, 464, 24, CREAM)
    rect(60, 716, 480, 3, GOLD); rect(390, 732, 150, 3, CREAM)

def personaltax():
    rect(0, 0, 600, 800, PAPER)
    ring(300, 286, 150, GOLD, 5)
    circ(300, 286, 84, NAVY)
    shape("M124 640 C124 500 204 424 300 424 C396 424 476 500 476 640 Z", NAVY)
    path("M418 150 L446 180 L500 112", CORAL, 14)
    rect(60, 676, 480, 6, NAVY)
    rect(60, 704, 300, 3, NAVY); rect(60, 720, 210, 3, GOLD)

def pay():
    rect(0, 0, 600, 800, INK)
    for r in range(3):
        for k in range(4):
            col = GOLD if (r, k) == (2, 3) else (CREAM if (r, k) in ((0, 1), (1, 2)) else MID)
            rect(110 + k*100, 132 + r*100, 80, 80, col, 12)
    for i in range(4):
        ell(300, 640 - i*30, 128, 38, GOLD, INK, 6)
    rect(60, 716, 480, 3, GOLD); rect(60, 732, 150, 3, CORAL)

pieces = {"suite": suite, "accounts": accounts, "books": books, "business-tax": businesstax, "personal-tax": personaltax, "pay": pay}
only = sys.argv[1:]
for name, fn in pieces.items():
    if only and name not in only: continue
    c.ex("file.new", {"name": f"Gallery {name}", "width": 600, "height": 800, "units": "Pixels", "colorMode": "rgb"})
    fn()
    c.ex("select.none", {}, check=False)
    c.call("app.save", {"path": f"{A}/gallery-{name}.vectorcraft"})
    c.call("app.export", {"path": f"{A}/{name}.svg"})
    c.call("ui.render", {"path": f"{A}/{name}.png", "scale": 0.5})
    print("drew", name)
time.sleep(3)
