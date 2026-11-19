# Episodio infantil: "¡Los animales de la granja y sus sonidos con Tula y Pipo!" (largo, 2026-11-19)
# Cada evento: who (tula/pipo/None), text, pause (silencio después, en s), do (acciones visuales), chap (capítulo opcional)
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
TITLE = ("¡ANIMALES", "DE GRANJA!")
THUMB = {"lines": ("¡ANIMALES", "DE LA GRANJA!"), "objs": ["vaca", "cerdo", "gallina"], "x": (830, 1330), "y": 640, "size": 250}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"
def cap(s): return s[0].upper() + s[1:]

# animal: (sonido en pantalla, NOMBRE en pantalla, "la vaca", sonido hablado, dato, invitación a imitar)
A = {
    "vaca": ("¡MUU!", "¡LA VACA!", "la vaca", "¡Muu, muu!", "La vaca vive en la granja, come pasto y nos da leche.", "¡Haz como la vaca! ¡Muu, muu!"),
    "cerdo": ("¡OINC!", "¡EL CERDITO!", "el cerdito", "¡Oinc, oinc!", "Al cerdito le encanta jugar en el barro. ¡Splash, splash!", "¡Ahora tú! Arruga la nariz y di: ¡oinc, oinc!"),
    "gallina": ("¡CLOC!", "¡LA GALLINA!", "la gallina", "¡Cloc, cloc, cloc!", "La gallina pone huevos y cuida a sus pollitos.", "Mueve los brazos como alitas y di: ¡cloc, cloc!"),
    "perro": ("¡GUAU!", "¡EL PERRO!", "el perro", "¡Guau, guau!", "El perro cuida la granja y mueve la cola cuando está feliz.", "¡Ladra como el perrito! ¡Guau, guau!"),
    "oveja": ("¡BEE!", "¡LA OVEJA!", "la oveja", "¡Bee, bee!", "La oveja tiene lana blanca, suave y calentita, como una nube.", "¡Tu turno! ¡Bee, bee!"),
    "caballo": ("¡HIII!", "¡EL CABALLO!", "el caballo", "¡Hi, hi, hi!", "El caballo corre muy rápido. Sus patas hacen: ¡clop, clop, clop!", "¡Galopa en tu lugar! ¡Clop, clop, clop!"),
    "pato": ("¡CUAC!", "¡EL PATO!", "el pato", "¡Cuac, cuac!", "El pato nada en el estanque. ¡Sus patas son como remos!", "¡Camina como un patito y di: cuac, cuac!"),
    "gato": ("¡MIAU!", "¡EL GATO!", "el gato", "¡Miau, miau!", "Al gato le gusta tomar la siesta al sol y jugar con un ovillo.", "¡Estírate como un gatito! ¡Miau!"),
    "rana": ("¡CROAC!", "¡LA RANA!", "la rana", "¡Croac, croac!", "La rana vive junto al estanque y salta muy, muy alto.", "¡Salta como la rana! ¡Uno, dos, tres! ¡Croac!"),
}
ORDER1 = [("vaca", "tula"), ("cerdo", "pipo"), ("gallina", "tula"), ("perro", "pipo")]
ORDER2 = [("oveja", "tula"), ("caballo", "pipo"), ("pato", "tula"), ("gato", "pipo"), ("rana", "tula")]

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿adónde vamos hoy?"),
    E("tula", "¡Hoy vamos de paseo a la granja!", pause=0.6,
      do=[("scene", "card", "¡LA GRANJA!", "red", ["vaca", "granero", "cerdo"])]),
    E("pipo", "¡En la granja viven muchos animales! Y cada uno hace un sonido diferente."),
    E("tula", "Vamos a escuchar con atención. ¿Nos ayudas a adivinar quién es?", pause=0.6),
    E("pipo", "¡Abre bien los oídos! ¡Vamos!", pause=0.8),
]

def animal_segment(ak, who, chap=None):
    snd, name, la, said, fact, imit = A[ak]; o = other(who)
    first = said.strip("¡!").split(",")[0].lower()
    return [E(None, None, pause=0.6, do=[("scene", "animal", ak, snd, name)], chap=chap),
            E(who, f"Escucha… {said} ¿Quién hace {first}?", pause=3.0, do=[("qmark", 1)]),
            E(o, f"¡{cap(la)}! ¡{cap(la)} hace {said.strip('¡!').lower()}!", pause=0.8, do=[("qmark", 0), ("reveal", 1)]),
            E(who, fact, pause=0.6),
            E(o, imit, pause=2.4)] + ([E(who, f"¡Otra vez, más fuerte! {said}", pause=2.2)] if ak in LOUD else [])
LOUD = {"vaca", "gallina", "caballo", "rana"}

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

MID = [E("pipo", "¡Cuántos amigos en la granja! Pero todavía hay más.", pause=0.5),
       E("tula", "Antes, ¡movamos el cuerpo!", pause=0.4)]

# ¿Cuántos hay? (n, animal, plural, femenino)
QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "cyan")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡A jugar! Te muestro animales y tú me dices cuántos hay.", pause=0.5),
        E("pipo", "¡Cuenta con tu dedito, uno por uno!", pause=0.6)]
for n, ak, pl, fem, who in ((3, "vaca", "vacas", True, "pipo"), (5, "pato", "patos", False, "tula"), (2, "caballo", "caballos", False, "pipo"),
                            (4, "cerdo", "cerditos", False, "tula"), (6, "gallina", "gallinas", True, "pipo"), (3, "rana", "ranas", True, "tula")):
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "quiz", n, ak)]),
             E(who, f"¿{'Cuántas' if fem else 'Cuántos'} {pl} hay?", pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), f"¡{cap(WORDS[n])}! ¡Hay {WORDS[n]} {pl}!", pause=0.9, do=[("qmark", 0), ("numeral", n)])]
QUIZ.append(E("tula", "¡Muy bien! ¡Cuentas como un granjero!", pause=0.6))

# Mamá y bebé (grande y pequeño): (animal, lado grande, meta, etiqueta grande, etiqueta pequeña, pregunta, respuesta)
BABY = [E(None, None, pause=1.0, do=[("scene", "card", "MAMÁ Y BEBÉ", "pink")], chap="Juego: mamá y bebé"),
        E("pipo", "En la granja también hay bebés. ¡Son pequeñitos!"),
        E("tula", "La mamá es grande y el bebé es pequeño. ¡Vamos a encontrarlos!", pause=0.6)]
for ak, side, goal, lb, ls, q, a, who in (
        ("vaca", "L", "small", "MAMÁ", "TERNERO", "Aquí está la mamá vaca con su bebé. ¿Cuál es el bebé?", "¡El pequeño! El bebé de la vaca se llama ternero.", "tula"),
        ("gallina", "R", "small", "MAMÁ", "POLLITO", "Mira a la gallina y a su bebé. ¿Dónde está el bebé?", "¡Aquí! Es el pollito. Los pollitos dicen: ¡pío, pío, como yo!", "pipo"),
        ("oveja", "L", "big", "MAMÁ", "CORDERITO", "Ahora al revés. ¿Cuál es la mamá oveja?", "¡La grande! Y su bebé pequeñito es el corderito.", "tula"),
        ("perro", "R", "small", "MAMÁ", "CACHORRO", "¿Y cuál es el bebé del perro?", "¡El pequeño! El bebé del perro es el cachorro.", "pipo"),
        ("caballo", "L", "big", "MAMÁ", "POTRILLO", "¿Cuál es la mamá caballo? ¿La grande o la pequeña?", "¡La grande! Y el bebé del caballo es el potrillo.", "tula")):
    BABY += [E(None, None, pause=0.6, do=[("scene", "size", ak, side, goal, lb, ls)]),
             E(who, q, pause=3.2, do=[("qmark", 1)]),
             E(other(who), a, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]
BABY.append(E("pipo", "¡Qué lindos los bebés de la granja!", pause=0.6))

# ¿De qué color es?
COLOR = [E(None, None, pause=1.0, do=[("scene", "card", "¿DE QUÉ COLOR ES?", "purple")], chap="Juego: ¿de qué color es?"),
         E("tula", "¡Oh, no! Los animales perdieron su color.", pause=0.4),
         E("pipo", "¡Ayúdanos a pintarlos! Dime de qué color son.", pause=0.6)]
for ak, lab, cn, q, a, who in (("cerdo", "¡ROSADO!", "pink", "¿De qué color es el cerdito?", "¡Rosado! ¡El cerdito es rosado!", "pipo"),
                               ("rana", "¡VERDE!", "green", "¿De qué color es la rana?", "¡Verde! ¡La rana es verde!", "tula"),
                               ("pato", "¡AMARILLO!", "yellow", "¿Y el patito? ¿De qué color es?", "¡Amarillo! ¡Un patito amarillo!", "pipo"),
                               ("gato", "¡NARANJA!", "orange", "¿De qué color es el gato?", "¡Naranja! ¡El gatito es naranja!", "tula"),
                               ("caballo", "¡MARRÓN!", "brown", "Y el último: ¿de qué color es el caballo?", "¡Marrón! ¡El caballo es marrón!", "pipo")):
    COLOR += [E(None, None, pause=0.6, do=[("scene", "fruit", ak, "color", lab, cn)]),
              E(who, q, pause=3.2, do=[("qmark", 1)]),
              E(other(who), a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

# ¿Quién falta? (patrones)
PAT = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUIÉN FALTA?", "orange")], chap="Juego: ¿quién falta?"),
       E("pipo", "¡Último juego! Los animales hicieron una fila. ¡Pero uno se escondió!", pause=0.6)]
for seq, miss, q, a, who in ((["vaca", "pato", "vaca", "pato", "vaca", "pato"], 5, "Vaca, pato, vaca, pato, vaca… ¿Quién sigue?", "¡El pato! Vaca, pato, vaca, pato, vaca, pato.", "tula"),
                             (["cerdo", "gallina", "cerdo", "gallina", "cerdo"], 3, "Cerdito, gallina, cerdito… ¿y quién falta aquí?", "¡La gallina! Cerdito, gallina, cerdito, gallina, cerdito.", "pipo"),
                             (["gato", "perro", "rana", "gato", "perro", "rana"], 4, "Gato, perro, rana, gato… ¿quién falta?", "¡El perro! Gato, perro, rana, gato, perro, rana.", "tula")):
    PAT += [E(None, None, pause=0.6, do=[("scene", "spattern", seq, miss, "¿QUIÉN FALTA?")]),
            E(who, q, pause=3.4, do=[("qmark", 1)]),
            E(other(who), a, pause=1.0, do=[("qmark", 0), ("fill", 1)])]

# Repaso: todos los animales con su sonido
RITEMS = [("vaca", "VACA"), ("cerdo", "CERDITO"), ("gallina", "GALLINA"), ("perro", "PERRO"), ("oveja", "OVEJA"),
          ("caballo", "CABALLO"), ("pato", "PATO"), ("gato", "GATO"), ("rana", "RANA")]
REVIEW = [E(None, None, pause=1.0, do=[("scene", "freview", RITEMS)], chap="Repaso: todos los sonidos"),
          E("tula", "¡Ahora el gran coro de la granja! Yo digo el animal y tú haces su sonido.", pause=0.8)]
for i, (ak, _) in enumerate(RITEMS, 1):
    snd, name, la, said, fact, imit = A[ak]; who = "tula" if i % 2 else "pipo"
    REVIEW += [E(who, f"¡{cap(la)}!", pause=1.6, do=[("rpop", i)]),
               E(other(who), said, pause=0.5)]
REVIEW += [E("pipo", "¡Qué concierto tan bonito!", pause=0.6, do=[("confetti", 1)]),
           E("tula", "¡Bravo! ¡Conoces a todos los animales de la granja!", pause=2.5)]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "¿Cuál es tu animal favorito? ¡El mío es el pollito, porque dice pío, pío!", pause=2.5),
    E("tula", "Hoy, juega a imitar animales con tu familia. Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    for i, (ak, who) in enumerate(ORDER1):
        ev += animal_segment(ak, who, "Vaca, cerdito, gallina y perro" if i == 0 else None)
    ev += MID + dance("pipo", "¡Bailemos como los animales de la granja!", "Pausa para bailar")
    for i, (ak, who) in enumerate(ORDER2):
        ev += animal_segment(ak, who, "Oveja, caballo, pato, gato y rana" if i == 0 else None)
    ev += QUIZ + BABY + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + COLOR + PAT + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
