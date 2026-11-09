# Episodio infantil: "¡Aprendemos las frutas con Tula y Pipo!" (largo, 2026-11-09)
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
TITLE = ("¡A CONOCER", "LAS FRUTAS!")
THUMB = {"lines": ("¡LAS", "FRUTAS!"), "objs": ["manzanar", "banana", "uvas", "fresa"]}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, tengo mucha hambre. ¿Qué comemos hoy?"),
    E("tula", "¡Algo rico y sano! Hoy vamos a conocer las frutas.", do=[("scene", "card", "¡LAS FRUTAS!", "orange", ["manzanar", "banana", "uvas"])]),
    E("pipo", "¡Frutas! ¡Qué ricas! ¿Me ayudas a adivinar cuál es cada una?"),
    E("tula", "Mira bien, escucha las pistas y dilo en voz alta. ¿Listo? ¡Vamos!", pause=0.8),
]

# (sprite, artículo + nombre, NOMBRE en pantalla, color en pantalla, color, pistas[(quién, texto)], respuesta, color dicho, cuenta n, plural, frase final)
FRUITS = [
    ("manzanar", "la manzana", "¡MANZANA!", "red",
     [("pipo", "Primera pista: es redonda, es roja y hace ¡crunch! cuando la muerdes.")],
     "¡Es la manzana!", "La manzana es roja.", 3, "manzanas", "rojas", ("pipo", "¡Crunch, crunch! ¡Qué rica!")),
    ("banana", "el plátano", "¡PLÁTANO!", "yellow",
     [("tula", "Esta fruta es larga, es amarilla y tiene forma de sonrisa."), ("pipo", "¡Y a los monos les encanta!")],
     "¡Es el plátano! Algunos le dicen banana.", "El plátano es amarillo. Para comerlo, le quitamos la cáscara.", 2, "plátanos", "amarillos", ("tula", "¡Uno para ti y uno para mí!")),
    ("naranja", "la naranja", "¡NARANJA!", "orange",
     [("pipo", "Es redonda como una pelota."), ("pipo", "Y su color se llama igual que ella.")],
     "¡Es la naranja!", "¿Y de qué color es la naranja? ¡Naranja!", 4, "naranjas", None, ("pipo", "¡Con naranjas hacemos un jugo muy rico!")),
    ("uvas", "las uvas", "¡UVAS!", "purple",
     [("tula", "Son pequeñitas y redondas, y crecen todas juntitas en un racimo.")],
     "¡Son las uvas!", "Estas uvas son moradas. ¡Y también hay uvas verdes!", 0, None, None, ("pipo", "¡Me como una uva! ¡Ñam, ñam!")),
]
FRUITS2 = [
    ("fresa", "la fresa", "¡FRESA!", "red",
     [("pipo", "Es pequeña y roja, tiene una hojita verde arriba…"), ("pipo", "¡Y puntitos amarillos por fuera!")],
     "¡Es la fresa!", "La fresa es roja y muy dulce.", 5, "fresas", "rojas", ("pipo", "¡Muy bien contado! ¡Qué dulces!")),
    ("pera", "la pera", "¡PERA!", "green",
     [("tula", "Es verde y dulce. Es chiquita arriba y grande abajo, como una campanita.")],
     "¡Es la pera!", "La pera es verde.", 6, "peras", "verdes", ("tula", "¡Cuántas peras! ¡Para compartir con todos!")),
    ("sandia", "la sandía", "¡SANDÍA!", "red",
     [("pipo", "Última fruta. Es muy, muy grande."), ("tula", "Por fuera es verde, y por dentro es roja con semillitas negras.")],
     "¡Es la sandía!", "La sandía es verde por fuera y roja por dentro.", 0, None, None, ("pipo", "¡Es fresquita, perfecta para el verano!")),
]

def fruit_segment(f, idx):
    fk, art, NAME, cn, clues, ans, colorline, n, plural, cpl, after = f
    ev = [E(None, None, pause=1.0, do=[("scene", "fruit", fk, "guess", NAME, cn)], chap=f"Fruta {idx}: {art}")]
    for k, (who, txt) in enumerate(clues):
        ev.append(E(who, txt, pause=0.5))
    asker = clues[-1][0]; other = "tula" if asker == "pipo" else "pipo"
    ev.append(E(asker, "¿Qué fruta es?", pause=3.4, do=[("qmark", 1)]))
    ev.append(E(other, ans, pause=0.9, do=[("qmark", 0), ("reveal", 1)]))
    word = art.split(" ", 1)[1]
    ev.append(E(asker, f"Repite conmigo: ¡{word}!", pause=2.2))
    ev.append(E(other, colorline, pause=0.8))
    if n:
        counter = "tula" if idx % 2 else "pipo"
        ev.append(E(None, None, pause=0.8, do=[("scene", "count", n, fk)]))
        ev.append(E(counter, f"Ahora, contemos {plural}. ¡Cuenta conmigo!", pause=0.5))
        for i in range(1, n + 1):
            ev.append(E(counter, WORDS[i].capitalize() + ".", pause=0.6, do=[("pop", i)]))
        ev.append(E("tula", f"¡{WORDS[n].capitalize()} {plural}" + (f" {cpl}!" if cpl else "!"), pause=0.6, do=[("numeral", n)]))
    ev.append(E(after[0], after[1], pause=0.8))
    return ev

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

PL = {"banana": "plátanos", "fresa": "fresas", "pera": "peras", "naranja": "naranjas", "manzanar": "manzanas"}
MASC = {"banana"}
QUIZ = [E(None, None, pause=1.2, do=[("scene", "quiz_intro")], chap="Juego: ¿cuántas hay?"),
        E("tula", "¡Juguemos! Yo te muestro frutas y tú me dices cuántas hay.", pause=0.8)]
for n, fk, who in ((3, "banana", "pipo"), (5, "fresa", "tula"), (2, "pera", "pipo"), (7, "manzanar", "tula")):
    pl = PL[fk]; other = "tula" if who == "pipo" else "pipo"
    QUIZ += [E(None, None, pause=0.8, do=[("scene", "quiz", n, fk)]),
             E(who, f"¿Cuántos {pl} hay?" if fk in MASC else f"¿Cuántas {pl} hay?", pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other, f"¡{WORDS[n].capitalize()}! ¡Hay {WORDS[n]} {pl}!", pause=0.9, do=[("qmark", 0), ("numeral", n)])]

COLORS = [E(None, None, pause=1.0, do=[("scene", "card", "¿DE QUÉ COLOR ES?", "purple")], chap="Juego: ¿de qué color es?"),
          E("pipo", "¡Oh, no! ¡Las frutas perdieron su color!"),
          E("tula", "Ayúdanos a recordar. ¿De qué color es cada una?", pause=0.6)]
for fk, q, word, ans, cn, who in (("banana", "¿De qué color es el plátano?", "¡AMARILLO!", "¡Amarillo! El plátano es amarillo.", "yellow", "pipo"),
                                  ("uvas", "¿De qué color son estas uvas?", "¡MORADAS!", "¡Moradas! Las uvas son moradas.", "purple", "tula"),
                                  ("pera", "¿De qué color es la pera?", "¡VERDE!", "¡Verde! La pera es verde.", "green", "pipo"),
                                  ("naranja", "¿Y de qué color es la naranja?", "¡NARANJA!", "¡Naranja! ¡La naranja es naranja!", "orange", "tula")):
    other = "tula" if who == "pipo" else "pipo"
    COLORS += [E(None, None, pause=0.6, do=[("scene", "fruit", fk, "color", word, cn)]),
               E(who, q, pause=3.4, do=[("qmark", 1)]),
               E(other, ans, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

SUMAS = [E(None, None, pause=1.0, do=[("scene", "sum_intro")], chap="Juego: sumamos manzanas"),
         E("pipo", "¡Mira, Tula! ¡También hay manzanas verdes!"),
         E("tula", "¡Sí! Vamos a juntar manzanas verdes. Eso se llama sumar.", pause=0.6)]
for a, b in ((1, 2), (2, 2)):
    c = a + b; ma = "manzana" if a == 1 else "manzanas"; mb = "manzana" if b == 1 else "manzanas"
    na = "una" if a == 1 else WORDS[a]; nb = "una" if b == 1 else WORDS[b]
    SUMAS += [E(None, None, pause=0.6, do=[("scene", "sum", a, b)]),
              E("pipo", f"Yo tengo {na} {ma}.", do=[("sa", 1)]),
              E("tula", f"Y yo te doy {nb} {mb} más.", do=[("sb", 1)]),
              E("pipo", "¿Cuántas manzanas hay ahora?", pause=3.2, do=[("qmark", 1)]),
              E("tula", f"¡{WORDS[c].capitalize()}! {WORDS[a].capitalize()} más {WORDS[b]} son {WORDS[c]}.", pause=1.0, do=[("qmark", 0), ("sc", 1)])]

SIZE = [E(None, None, pause=1.0, do=[("scene", "card", "¡GRANDE Y PEQUEÑO!", "pink", ["sandia", "fresa"])], chap="Juego: grande y pequeño"),
        E("tula", "Algunas frutas son grandes y otras son pequeñas."),
        E("pipo", "¡Encuentra la que te pido! Señálala con tu dedito.", pause=0.6)]
for fk, side, goal, lb, ls, q, ans, who in (
        ("sandia", "L", "big", "GRANDE", "PEQUEÑA", "¿Cuál sandía es la grande?", "¡Esta! ¡La sandía grande!", "pipo"),
        ("fresa", "R", "small", "GRANDE", "PEQUEÑA", "¿Cuál fresa es la pequeña?", "¡Esta! ¡La fresa pequeña!", "tula"),
        ("naranja", "L", "small", "GRANDE", "PEQUEÑA", "¿Y cuál naranja es la pequeña?", "¡Esta! ¡La naranja pequeñita!", "pipo")):
    other = "tula" if who == "pipo" else "pipo"
    SIZE += [E(None, None, pause=0.6, do=[("scene", "size", fk, side, goal, lb, ls)]),
             E(who, q, pause=3.2, do=[("qmark", 1)]),
             E(other, ans, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

FALTA = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ FRUTA FALTA?", "green")], chap="Juego: ¿qué fruta falta?"),
         E("tula", "¡Otro juego! Mira la fila de frutas. Una se escondió."),
         E("pipo", "¿Cuál falta? ¡Mira bien! ¡Pío!", pause=0.6)]
for seq, miss, who, ans in ((["manzanar", "banana", "manzanar", "banana"], 3, "pipo", "¡El plátano! Manzana, plátano, manzana, plátano."),
                            (["fresa", "pera", "fresa", "pera"], 2, "tula", "¡La fresa! Fresa, pera, fresa, pera."),
                            (["naranja", "uvas", "naranja", "uvas"], 1, "pipo", "¡Las uvas! Naranja, uvas, naranja, uvas.")):
    other = "tula" if who == "pipo" else "pipo"
    FALTA += [E(None, None, pause=0.6, do=[("scene", "spattern", seq, miss, "¿QUÉ FRUTA FALTA?")]),
              E(who, "¿Qué fruta falta?", pause=3.6, do=[("qmark", 1)]),
              E(other, ans, pause=1.0, do=[("qmark", 0), ("fill", 1)])]

BOWL_FR = ["manzanar", "banana", "naranja", "fresa", "uvas", "pera"]
BOWL = [E(None, None, pause=0.8, do=[("scene", "bowl", BOWL_FR)], chap="Ensalada de frutas"),
        E("pipo", "¡Tula, tengo una idea! ¡Hagamos una ensalada de frutas!"),
        E("tula", "¡Sí! Echamos todas las frutas en el tazón. ¿Nos ayudas?", pause=0.6)]
for i, (who, txt) in enumerate((("tula", "Una manzana."), ("pipo", "Un plátano."), ("tula", "Una naranja."),
                                ("pipo", "Una fresa."), ("tula", "Unas uvas."), ("pipo", "¡Y una pera!")), 1):
    BOWL.append(E(who, txt, pause=0.8, do=[("pop", i)]))
BOWL += [E("tula", "¡Ahora, a mezclar! Mueve las manos así: ¡da vueltas, da vueltas!", pause=1.5),
         E("pipo", "¡Mmm! ¡Una ensalada de frutas de todos los colores!", pause=0.5, do=[("confetti", 1)]),
         E("tula", "Las frutas nos dan energía para jugar y crecer fuertes.", pause=1.0)]

REVIEW_FR = [("manzanar", "MANZANA"), ("banana", "PLÁTANO"), ("naranja", "NARANJA"), ("uvas", "UVAS"),
             ("fresa", "FRESA"), ("pera", "PERA"), ("sandia", "SANDÍA")]
REVIEW = [E(None, None, pause=1.0, do=[("scene", "freview", REVIEW_FR)], chap="Repaso de las frutas"),
          E("tula", "¡Repasemos! Di el nombre de cada fruta conmigo.", pause=0.6)]
for i, (fk, nm) in enumerate(REVIEW_FR, 1):
    REVIEW.append(E("tula" if i % 2 else "pipo", "¡" + nm.capitalize() + "!", pause=0.9, do=[("rpop", i)]))
REVIEW.append(E("pipo", "¡Bravo! ¡Te sabes todas las frutas!", pause=2.5, do=[("confetti", 1)]))

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "¿Cuál es tu fruta favorita? ¡La mía es la fresa!", pause=2.5),
    E("tula", "Hoy, pídele a mamá o a papá una fruta rica. Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    for k, f in enumerate(FRUITS, 1):
        ev += fruit_segment(f, k)
    ev += dance("pipo", "¡Ya conocemos cuatro frutas! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    for k, f in enumerate(FRUITS2, 5):
        ev += fruit_segment(f, k)
    ev += QUIZ + SUMAS + COLORS + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + FALTA + SIZE + BOWL + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
