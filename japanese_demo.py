import pyxel

def draw_text_with_border(x, y, s, col, bcol, font):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx != 0 or dy != 0:
                pyxel.text(
                    x + dx,
                    y + dy,
                    s,
                    bcol,
                    font,
                )
    pyxel.text(x, y, s, col, font)

pyxel.init(128, 128, title="Japanese Text Demo")

# Load font
k8x12 = pyxel.Font("assets/k8x12.bdf")

pyxel.cls(1)
s = "▲Pyxel▲"
w = k8x12.text_width(s)
pyxel.rect(21, 18, w, 1, 15)
pyxel.text(21, 8, s, 8, k8x12)

# Draw Japanese text using the font
draw_text_with_border(4, 98, "こんにちは", 7, 5, k8x12)
draw_text_with_border(4, 113, "Pyxel!", 7, 5, k8x12)

pyxel.show()
