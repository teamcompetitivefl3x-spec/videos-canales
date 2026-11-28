# SHORT: "¿Qué falta?" — juego de memoria con Tula y Pipo (2026-11-28)
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
TITLE = ("¿QUÉ", "FALTA?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

# (objetos, índice que desaparece, texto, color, quién pregunta, "mira bien", "¿qué falta?", respuesta)
ROUNDS = [
    ([("manzanar", None), ("banana", None), ("uvas", None)], 1, "¡PLÁTANO!", "yellow",
     "tula", "Mira bien: manzana, plátano y uvas.", "¡Ábrelos! ¿Qué falta?", "¡El plátano!"),
    ([("perro", None), ("gato", None), ("pato", None)], 1, "¡GATO!", "orange",
     "pipo", "Ahora, animalitos: perro, gato y pato.", "¡Ábrelos! ¿Quién falta?", "¡El gatito! ¡Miau!"),
    ([("sol", None), ("nube", None), ("estrella", None), ("luna", None)], 2, "¡ESTRELLA!", "purple",
     "tula", "¡El más difícil! Sol, nube, estrella y luna.", "¡Ábrelos! ¿Qué falta?", "¡La estrella!"),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "purple", ["manzanar", "gato", "estrella", "uvas"])]),
          E("pipo", "¡Hola! ¡Juguemos a qué falta!"),
          E("tula", "Mira bien y recuerda todo.", pause=0.3)]
    for objs, mi, lab, cn, who, look, q, a in ROUNDS:
        other = "pipo" if who == "tula" else "tula"
        ev += [E(None, None, pause=0.4, do=[("scene", "gone", objs, mi, lab, cn)]),
               E(who, look, pause=0.9),
               E(other, "¡Cierra los ojitos!", pause=1.1, do=[("sa", 1)]),
               E(who, q, pause=2.2, do=[("sb", 1), ("qmark", 1)]),
               E(other, a, pause=0.8, do=[("qmark", 0), ("reveal", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Qué buena memoria! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.3)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
