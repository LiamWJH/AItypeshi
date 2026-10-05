import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from overlay import Overlay, TextHud

remaining = int(sys.argv[1])
x = int(sys.argv[2])
y = int(sys.argv[3])
overlay = Overlay(x=x, y=y)
# the part above this should be the same for all tools

clock = TextHud(overlay.body, bg=overlay.bg)

def tick():
  global remaining
  h, rem = divmod(remaining, 3600)
  m, s = divmod(rem, 60)
  clock.set(f"{h:02d}:{m:02d}:{s:02d}")
  if remaining <= 0:
    overlay.close()
    return
  remaining -= 1

overlay.every(1000, tick)
overlay.run()