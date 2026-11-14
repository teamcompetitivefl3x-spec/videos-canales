# SHORT: "¿Qué forma es?" — juego de formas con Tula y Pipo (2026-11-14)
from script_contar_1a10 import OBJS, WORDS
TITLE = ("¿QUÉ FORMA", "ES?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "purple", ["circulo", "triangulo", "estrellaf"])]),
          E("tula", "¡Hola! ¿Jugamos a adivinar formas?"),
          E("pipo", "¡Mira bien y dilo en voz alta! ¡Pío!", pause=0.4),
          # ronda 1: triángulo (se dibuja, se adivina y se cuentan sus lados)
          E(None, None, pause=0.4, do=[("scene", "shape", "triangulo")]),
          E("tula", "¡Mira! Vamos a dibujar una forma.", pause=1.6, do=[("trace",)]),
          E("pipo", "¿Qué forma es?", pause=2.4, do=[("qmark", 1)]),
          E(None, None, pause=0.15, do=[("qmark", 0), ("fill",)]),
          E("tula", "¡Un triángulo! Tiene tres lados.", pause=0.3, do=[("reveal",)]),
          E("pipo", "Uno.", pause=0.25, do=[("side", 1)]),
          E("pipo", "Dos.", pause=0.25, do=[("side", 2)]),
          E("pipo", "Tres.", pause=0.6, do=[("side", 3)]),
          # ronda 2: estrella
          E(None, None, pause=0.4, do=[("scene", "shape", "estrellaf")]),
          E("pipo", "¡Ahora dibujo yo!", pause=2.0, do=[("trace",)]),
          E("tula", "¿Y esta forma, cuál es?", pause=2.4, do=[("qmark", 1)]),
          E(None, None, pause=0.15, do=[("qmark", 0), ("fill",)]),
          E("pipo", "¡Una estrella! ¡Brilla, brilla!", pause=0.7, do=[("reveal",), ("confetti", 1)]),
          # ronda 3: ¿qué forma falta?
          E(None, None, pause=0.4, do=[("scene", "spattern", ["circulo", "triangulo", "circulo", "triangulo"], 3)]),
          E("tula", "Círculo, triángulo, círculo...", pause=0.3),
          E("pipo", "¿Qué forma falta?", pause=2.6),
          E("tula", "¡Triángulo! ¡Muy bien!", pause=0.8, do=[("fill",)]),
          E(None, None, pause=0.2, do=[("scene", "bye")]),
          E("pipo", "¡Sabes muchas formas! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
          E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
