# SHORT: "¿Qué sigue?" — juego de patrones con Tula y Pipo (2026-11-26)
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
TITLE = ("¿QUÉ", "SIGUE?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

R_, B_ = ("globo", "red"), ("globo", "blue")
ST, CO = ("estrella", "yellow"), ("corazon", "red")
MA, PL = ("manzanar", None), ("banana", None)
SO, NU, GO = ("sol", None), ("nube", None), ("gota", None)
# (objetos, índice que falta, texto en pantalla, color, quién pregunta, pregunta, respuesta)
ROUNDS = [
    ([R_, B_, R_, B_, R_, B_], 5, "¡AZUL!", "blue",
     "tula", "Rojo, azul, rojo, azul, rojo… ¿qué sigue?", "¡El globo azul!"),
    ([ST, CO, ST, CO, ST, CO], 5, "¡CORAZÓN!", "red",
     "pipo", "Estrella, corazón, estrella, corazón, estrella… ¿y ahora?", "¡Un corazón!"),
    ([MA, MA, PL, MA, MA, PL], 5, "¡PLÁTANO!", "yellow",
     "tula", "Manzana, manzana, plátano, manzana, manzana… ¿qué viene?", "¡El plátano!"),
    ([SO, NU, GO, SO, NU, GO], 5, "¡LLUVIA!", "blue",
     "pipo", "Sol, nube, lluvia, sol, nube… ¿y después?", "¡La lluvia! ¡Plic, plic!"),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A JUGAR!", "orange", ["globo", "estrella", "banana", "sol"])]),
          E("pipo", "¡Hola! ¡Juguemos a qué sigue!"),
          E("tula", "Mira cómo se repiten las cosas.", pause=0.3)]
    for objs, mi, lab, cn, who, q, a in ROUNDS:
        other = "pipo" if who == "tula" else "tula"
        ev += [E(None, None, pause=0.5, do=[("scene", "seq", objs, mi, lab, cn)]),
               E(who, q, pause=2.0, do=[("qmark", 1)]),
               E(other, a, pause=0.7, do=[("qmark", 0), ("reveal", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Muy bien! ¡Eres un genio!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.3)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
