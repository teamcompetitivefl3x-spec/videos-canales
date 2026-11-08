# SHORT: "¿Quién hace muu?" — adivina el animal por su sonido, con Tula y Pipo
from script_contar_1a10 import OBJS, WORDS
TITLE = ("¿QUIÉN", "HACE MUU?")

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

# (animal, sonido en pantalla, nombre en pantalla, pregunta, respuesta, quién pregunta)
ROUNDS = [
    ("vaca", "¡MUU!", "¡LA VACA!", "Escucha: ¡Muu, muu! ¿Quién hace muu?", "¡La vaca! ¡La vaca hace muu!", "tula"),
    ("perro", "¡GUAU!", "¡EL PERRO!", "¡Guau, guau! ¿Quién hace guau?", "¡El perro! ¡Guau, guau!", "pipo"),
    ("gato", "¡MIAU!", "¡EL GATO!", "Ahora: ¡Miau, miau! ¿Quién será?", "¡El gato! ¡El gatito hace miau!", "tula"),
    ("pato", "¡CUAC!", "¡EL PATO!", "¡Cuac, cuac! ¿Quién hace cuac?", "¡El pato! ¡Cuac, cuac!", "pipo"),
    ("oveja", "¡BEE!", "¡LA OVEJA!", "Y el último: ¡Bee, bee! ¿Quién hace bee?", "¡La oveja! ¡Bee, bee!", "tula"),
]

def build():
    ev = [E(None, None, pause=0.3, do=[("scene", "card", "¡A ADIVINAR!", "yellow", ["vaca", "perro", "gato", "pato", "oveja"])]),
          E("tula", "¡Hola! ¡Adivina qué animal hace cada sonido!"),
          E("pipo", "¡Escucha bien y dilo en voz alta! ¡Pío!", pause=0.4)]
    for ak, snd, name, q, a, who in ROUNDS:
        other = "pipo" if who == "tula" else "tula"
        ev += [E(None, None, pause=0.5, do=[("scene", "animal", ak, snd, name)]),
               E(who, q, pause=2.4, do=[("qmark", 1)]),
               E(other, a, pause=0.8, do=[("qmark", 0), ("reveal", 1)])]
    ev += [E(None, None, pause=0.2, do=[("scene", "bye")]),
           E("pipo", "¡Adivinaste todos! ¡Bravo!", pause=0.3, do=[("confetti", 1)]),
           E("tula", "¡Hasta la próxima, amiguito! ¡Adiós!", pause=1.4)]
    return ev

if __name__ == "__main__":
    ev = build(); print(len(ev), "eventos")
