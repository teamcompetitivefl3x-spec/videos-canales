# SHORT: "¿Qué número falta?" — juego de secuencias con Tula y Pipo (2026-11-22)
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
TITLE = ("¿QUÉ NÚMERO", "FALTA?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

# (secuencia, índice que falta, quién pregunta, pregunta, respuesta)
ROUNDS = [
    ([1, 2, 3, 4], 2, "pipo", "Uno, dos… ¿qué número falta?", "¡El tres! Uno, dos, tres, cuatro."),
    ([5, 6, 7, 8], 3, "tula", "Cinco, seis, siete… ¿y después?", "¡El ocho! Cinco, seis, siete, ocho."),
    ([2, 3, 4, 5], 0, "pipo", "¡Uy! Falta el primero. ¿Cuál es?", "¡El dos! Dos, tres, cuatro, cinco."),
    ([7, 8, 9, 10], 2, "tula", "El último. Siete, ocho… ¿qué falta?", "¡El nueve! Siete, ocho, nueve, diez."),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "purple", ["estrella", "globo", "pelota"])]),
          E("tula", "¡Hola! ¿Jugamos con los números?"),
          E("pipo", "¡Encuentra el número que falta! ¡Pío!", pause=0.4)]
    for seq, miss, who, q, a in ROUNDS:
        other = "pipo" if who == "tula" else "tula"
        ev += [E(None, None, pause=1.1, do=[("scene", "missing", seq, miss)]),
               E(who, q, pause=2.4, do=[("qmark", 1)]),
               E(other, a, pause=0.7, do=[("qmark", 0), ("fill", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Los encontraste todos! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
