# SHORT: "¿Cuál es el grande?" — juego de grande y pequeño con Tula y Pipo
from script_contar_1a10 import OBJS, WORDS
TITLE = ("¡GRANDE Y", "PEQUEÑO!")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

# (objeto, lado grande, meta, etiqueta grande, etiqueta pequeña, pregunta, respuesta, quien pregunta)
ROUNDS = [
    ("manzana", "L", "big", "GRANDE", "PEQUEÑA", "Mira estas manzanas. ¿Cuál es la manzana grande?", "¡Esta! ¡La manzana grande!", "pipo"),
    ("pelota", "R", "small", "GRANDE", "PEQUEÑA", "Ahora, pelotas. ¿Cuál es la pelota pequeña?", "¡Muy bien! ¡La pelota pequeña!", "tula"),
    ("pez", "R", "big", "GRANDE", "PEQUEÑO", "¡Glu, glu! ¿Cuál es el pez grande?", "¡El pez grande! ¡Qué grandote!", "pipo"),
    ("estrella", "L", "small", "GRANDE", "PEQUEÑA", "Y la última. ¿Cuál es la estrella pequeña?", "¡La estrellita pequeña! ¡Bravo!", "tula"),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¿GRANDE O PEQUEÑO?", "yellow")]),
          E("tula", "¡Hola! ¡Juguemos a grande y pequeño!"),
          E("pipo", "¡Mira bien y señala con tu dedito! ¡Pío!", pause=0.5)]
    for obj, side, goal, lb, ls, q, a, who in ROUNDS:
        other = "tula" if who == "pipo" else "pipo"
        ev += [E(None, None, pause=0.7, do=[("scene", "size", obj, side, goal, lb, ls)]),
               E(who, q, pause=2.6, do=[("qmark", 1)]),
               E(other, a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Lo hiciste genial!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.5)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
