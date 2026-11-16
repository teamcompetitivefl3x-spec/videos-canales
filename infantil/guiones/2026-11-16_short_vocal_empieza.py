# SHORT: "¿Con qué vocal empieza?" — juego de vocales con Tula y Pipo (2026-11-16)
OBJS = {
    1: ("sol", "sol", "soles", "amarillo", "amarillos"),
    2: ("pez", "pez", "peces", "naranja", "naranjas"),
    3: ("globo", "globo", "globos", "rojo", "rojos"),
    4: ("manzana", "manzana", "manzanas", "verde", "verdes"),
    5: ("estrella", "estrella", "estrellas", "morada", "moradas"),
    6: ("flor", "flor", "flores", "rosada", "rosadas"),
    7: ("burbuja", "burbuja", "burbujas", "celeste", "celestes"),
    8: ("pelota", "pelota", "pelotas", "azul", "azules"),
    9: ("nube", "nube", "nubes", "blanca", "blancas"),
    10: ("corazon", "corazón", "corazones", "de colores", "de colores"),
}
WORDS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]
TITLE = ("¿CON QUÉ", "VOCAL EMPIEZA?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "orange", ["L_A", "L_E", "L_I", "L_O", "L_U"])]),
          E("tula", "¡Hola! ¿Jugamos con las vocales?"),
          E("pipo", "¡Mira el dibujo y dilo en voz alta! ¡Pío!", pause=0.4),
          # ronda 1: elefante -> E
          E(None, None, pause=0.3, do=[("scene", "vstart", "elefante", "ELEFANTE", "E")]),
          E("tula", "¡Mira! Es un elefante.", pause=0.2),
          E("pipo", "¿Con qué vocal empieza?", pause=2.4, do=[("qmark", 1)]),
          E("tula", "¡Con la E! E, elefante.", pause=0.7, do=[("qmark", 0), ("reveal",)]),
          # ronda 2: oso -> O
          E(None, None, pause=0.3, do=[("scene", "vstart", "oso", "OSO", "O")]),
          E("pipo", "¡Y este es un oso! ¡Grrr!", pause=0.2),
          E("tula", "¿Con qué vocal empieza oso?", pause=2.4, do=[("qmark", 1)]),
          E("pipo", "¡Con la O! O, oso.", pause=0.7, do=[("qmark", 0), ("reveal",)]),
          # ronda 3: iglú -> I
          E(None, None, pause=0.3, do=[("scene", "vstart", "iglu", "IGLÚ", "I")]),
          E("tula", "Esta es una casita de hielo: un iglú.", pause=0.2),
          E("pipo", "¿Con qué vocal empieza?", pause=2.4, do=[("qmark", 1)]),
          E("tula", "¡Con la I! I, iglú. ¡Muy bien!", pause=0.7, do=[("qmark", 0), ("reveal",)]),
          # ronda 4: ¿qué vocal falta?
          E(None, None, pause=0.4, do=[("scene", "lpattern", ["A", "E", "I", "O", "U"], 4)]),
          E("pipo", "A, E, I, O...", pause=0.3),
          E("tula", "¿Qué vocal falta?", pause=2.4),
          E("pipo", "¡La U! ¡A, E, I, O, U!", pause=0.8, do=[("fill",)]),
          E(None, None, pause=0.2, do=[("scene", "bye")]),
          E("tula", "¡Sabes las vocales! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
          E("pipo", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
