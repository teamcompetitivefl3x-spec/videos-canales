# SHORT: "¿Cuántos hay?" — juego de contar con Tula y Pipo (2026-11-10)
from script_contar_1a10 import OBJS, WORDS
TITLE = ("¿CUÁNTOS", "HAY?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

# (objeto, cantidad, pregunta, respuesta, quién pregunta)
ROUNDS = [
    ("globo", 3, "¿Cuántos globos hay?", "¡Tres! ¡Hay tres globos!", "pipo"),
    ("estrella", 4, "¿Y cuántas estrellas hay?", "¡Cuatro! ¡Cuatro estrellas!", "tula"),
    ("pez", 5, "Y ahora, ¿cuántos peces hay?", "¡Cinco! ¡Hay cinco peces!", "pipo"),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A CONTAR!", "cyan", ["globo", "estrella", "pez"])]),
          E("tula", "¡Hola! ¿Jugamos a contar?"),
          E("pipo", "¡Cuenta en voz alta con nosotros! ¡Pío!", pause=0.4)]
    for obj, n, q, a, who in ROUNDS:
        other = "tula" if who == "pipo" else "pipo"
        ev += [E(None, None, pause=0.5, do=[("scene", "quiz", n, obj)]),
               E(who, q, pause=2.4, do=[("qmark", 1), ("popall", 1)]),
               E(None, None, pause=0.3, do=[("qmark", 0), ("scene", "count", n, obj)]),
               E(other, "¡Contemos juntos!", pause=0.2)]
        for i in range(1, n + 1):
            ev.append(E(other, WORDS[i].capitalize() + ".", pause=0.25, do=[("pop", i)]))
        ev.append(E(who, a, pause=0.8, do=[("numeral", n)]))
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Contaste muy bien! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
