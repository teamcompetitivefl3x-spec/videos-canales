# SHORT: "¿Cuál es diferente?" — juego de observación con Tula y Pipo (2026-11-20)
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
TITLE = ("¿CUÁL ES", "DIFERENTE?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

YEL = (255, 211, 51); BLU = (60, 120, 240)
# (objetos, índice distinto, texto en pantalla, color, quién pregunta, pregunta, respuesta)
ROUNDS = [
    ([("manzanar", None, 1), ("manzanar", None, 1), ("banana", None, 1), ("manzanar", None, 1)], 2, "¡EL PLÁTANO!", "yellow",
     "tula", "Mira bien las frutas. ¿Cuál es diferente?", "¡El plátano! Las otras son manzanas."),
    ([("estrella", YEL, 1), ("estrella", BLU, 1), ("estrella", YEL, 1), ("estrella", YEL, 1)], 1, "¡LA AZUL!", "blue",
     "pipo", "Ahora, estrellas. ¿Cuál es diferente?", "¡La estrella azul! Las otras son amarillas."),
    ([("globo", None, 1), ("globo", None, 1), ("globo", None, 1), ("globo", None, 0.5)], 3, "¡EL PEQUEÑO!", "red",
     "tula", "Globos rojos. ¿Cuál es diferente?", "¡El globo pequeño! Los otros son grandes."),
    ([("circulo", None, 1), ("corazon", None, 1), ("corazon", None, 1), ("corazon", None, 1)], 0, "¡EL CÍRCULO!", "red",
     "pipo", "¿Y aquí? ¿Cuál es diferente?", "¡El círculo! Los otros son corazones."),
    ([("perro", None, 1), ("perro", None, 1), ("gato", None, 1), ("perro", None, 1)], 2, "¡EL GATO!", "orange",
     "tula", "El último. ¿Cuál es diferente?", "¡El gato! ¡Miau! Los otros son perritos."),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "pink", ["manzanar", "banana", "estrella", "gato"])]),
          E("pipo", "¡Hola! ¡Juguemos a encontrar el diferente!"),
          E("tula", "Mira bien y señálalo con tu dedito.", pause=0.4)]
    for objs, oi, lab, cn, who, q, a in ROUNDS:
        other = "pipo" if who == "tula" else "tula"
        ev += [E(None, None, pause=0.3, do=[("scene", "odd", objs, oi, lab, cn)]),
               E(who, q, pause=2.3, do=[("qmark", 1)]),
               E(other, a, pause=0.7, do=[("qmark", 0), ("reveal", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Encontraste todos! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
