# Episodio infantil: "¡Contamos de 2 en 2 con Tula y Pipo!" (largo, 2026-11-25)
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
WORDS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
         "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte"]
TITLE = ("¡CONTAMOS", "DE 2 EN 2!")
THUMB = {"lines": ("¡DE 2", "EN 2!"), "objs": ["calcetin", "N_2", "N_4", "guante"], "x": (800, 1380), "y": 640, "size": 215}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"
def cap(s): return s[0].upper() + s[1:]

# objeto: (singular, plural)
NOUN = {"calcetin": ("calcetín", "calcetines"), "guante": ("guante", "guantes"), "zapato": ("zapato", "zapatos"),
        "cereza": ("cereza", "cerezas"), "pato": ("patito", "patitos")}
FEM = {"cereza"}

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿tú sabes contar muy, muy rápido?"),
    E("tula", "¡Sí! Hoy vamos a contar de dos en dos.", pause=0.6, do=[("scene", "card", "¡DE 2 EN 2!", "yellow", ["N_2", "N_4", "N_6"])]),
    E("pipo", "¿De dos en dos? ¡Qué divertido! ¿Nos ayudas, amiguito?", pause=0.8),
]

PAR = [
    E(None, None, pause=0.6, do=[("scene", "pairs", 1, "calcetin", False)], chap="¿Qué es un par?"),
    E("tula", "Mira, Pipo. ¡Dos calcetines rojos, iguales!", pause=0.5, do=[("pop", 1)]),
    E("pipo", "Cuando dos cosas iguales van juntas, se llaman un par."),
    E("tula", "¡Muy bien! Un par de calcetines. ¡Son dos!", pause=0.6, do=[("numeral", 2)]),
    E("pipo", "¡Y aquí hay un par de guantes para el frío!", pause=0.5, do=[("scene", "card", "¡UN PAR!", "cyan", ["guante", "guante"])]),
    E("tula", "Y un par de zapatos para caminar. ¡Uno y dos!", pause=0.5, do=[("scene", "card", "¡UN PAR!", "green", ["zapato", "zapato"])]),
    E("pipo", "¡Yo también tengo un par de alas! ¡Mira cómo vuelo!", pause=0.5),
    E("tula", "Y tú tienes un par de manos. ¿Puedes aplaudir dos veces? ¡Plas, plas!", pause=2.2),
    E("pipo", "¡Y un par de ojos para mirar! ¡Parpadea dos veces!", pause=2.2),
]

HOP = [
    E(None, None, pause=0.6, do=[("scene", "hop", 10)], chap="La rana salta de 2 en 2"),
    E("pipo", "¡Mira! Llegó nuestra amiga, la rana. ¡Quiere cruzar el río!"),
    E("tula", "Primero salta despacito, de uno en uno. ¡Cuenta con ella!", pause=0.5),
]
for i in range(1, 11):
    HOP.append(E("tula" if i % 2 else "pipo", cap(WORDS[i]) + ".", pause=0.3, do=[("rpop", i)]))
HOP += [
    E("pipo", "¡Diez! ¡Uf, cuántos saltos!", pause=0.6),
    E(None, None, pause=0.5, do=[("scene", "hop", 10)]),
    E("tula", "Ahora la rana da saltos más grandes. ¡Salta de dos en dos!"),
    E("pipo", "Se salta un número. Uno… ¡dos! Tres… ¡cuatro!", pause=0.5),
    E("tula", "¡A saltar! ¡Cuenta fuerte con nosotros!", pause=0.5),
]
for v in (2, 4, 6, 8, 10):
    HOP.append(E("pipo" if v % 4 else "tula", "¡" + cap(WORDS[v]) + "!", pause=0.55, do=[("rpop", v)]))
HOP += [
    E("tula", "¡Llegó con solo cinco saltos! ¡Qué rápido!", pause=0.6, do=[("confetti", 1)]),
    E("pipo", "Repite conmigo: ¡dos, cuatro, seis, ocho, diez!", pause=3.5),
]

def count_seg(npr, ok, multi, who, lines, ask=None, after=None, chap=None):
    s, pl = NOUN[ok]; o = other(who); n = 2 * npr
    ev = [E(None, None, pause=0.8, do=[("scene", "pairs", npr, ok, multi)], chap=chap)]
    for w, txt in lines:
        ev.append(E(w, txt))
    if ask:
        ev[-1]["pause"] = 4.0; ev[-1]["do"].append(("qmark", 1))
        ev.append(E(o, "¡Contemos juntos para ver si acertaste!", pause=0.4, do=[("qmark", 0)]))
    for k in range(1, npr + 1):
        ev.append(E(who if k % 2 else o, "¡" + cap(WORDS[2 * k]) + "!", pause=0.6, do=[("pop", k)]))
    par = "un par" if npr == 1 else f"{WORDS[npr]} pares"
    ev.append(E(who, f"¡{cap(WORDS[n])} {pl}! Son {par}.", pause=0.7, do=[("numeral", n)]))
    if after:
        ev.append(E(o, after, pause=0.7))
    return ev

COUNT10 = (
    count_seg(5, "calcetin", True, "tula",
              [("pipo", "¡Es día de lavar la ropa! ¡Hay muchos calcetines de colores!"),
               ("tula", "Vamos a contarlos de dos en dos. ¡Cuenta conmigo!")],
              after="¡Qué limpios y qué lindos!", chap="Contamos pares hasta el 10")
    + count_seg(4, "cereza", False, "pipo",
                [("tula", "¡Mmm, cerezas! Las cerezas crecen de a dos, colgaditas juntas."),
                 ("pipo", "¿Contamos las cerezas de dos en dos?")],
                after="¡Ñam, ñam! ¡Qué ricas!")
    + count_seg(3, "zapato", True, "tula",
                [("pipo", "¡Uy, cuántos zapatos de colores!"),
                 ("tula", "Contemos los zapatos. Cada par tiene dos.")],
                after="¡Seis zapatos para salir a pasear!")
    + count_seg(5, "guante", True, "pipo",
                [("tula", "Hace frío… ¡Mira todos estos guantes!"),
                 ("pipo", "Ahora te toca a ti. ¿Cuántos guantes hay? ¡Cuenta de dos en dos!")],
                ask=True, after="¡Muy bien! ¡Diez guantes calentitos!")
)

EYES = [E(None, None, pause=0.8, do=[("scene", "card", "¿CUÁNTOS OJITOS?", "green", ["vaca", "perro", "gato"])], chap="¿Cuántos ojitos?"),
        E("pipo", "¡Llegaron los animales de la granja a saludar!"),
        E("tula", "Cada animal tiene un par de ojitos. ¡Dos ojitos!", pause=0.5),
        E(None, None, pause=0.6, do=[("scene", "pairs", 3, ["vaca", "perro", "gato"], False)]),
        E("pipo", "La vaca, el perro y el gato. ¿Cuántos ojitos hay? ¡Contemos de dos en dos!", pause=0.5)]
for k in range(1, 4):
    EYES.append(E("tula" if k % 2 else "pipo", "¡" + cap(WORDS[2 * k]) + "!", pause=0.6, do=[("pop", k)]))
EYES += [E("tula", "¡Seis ojitos que nos miran!", pause=0.7, do=[("numeral", 6)]),
         E(None, None, pause=0.6, do=[("scene", "pairs", 4, ["oveja", "cerdo", "gallina", "caballo"], False)]),
         E("tula", "Ahora la oveja, el cerdito, la gallina y el caballo. ¿Cuántos ojitos tienen?", pause=4.0, do=[("qmark", 1)]),
         E("pipo", "¡Contemos juntos!", pause=0.4, do=[("qmark", 0)])]
for k in range(1, 5):
    EYES.append(E("pipo" if k % 2 else "tula", "¡" + cap(WORDS[2 * k]) + "!", pause=0.6, do=[("pop", k)]))
EYES += [E("pipo", "¡Ocho ojitos! ¡Muy bien!", pause=0.7, do=[("numeral", 8)])]

SONG = [E(None, None, pause=0.6, do=[("scene", "dance")], chap="Canción de los pares"),
        E("tula", "¡Ahora cantemos la canción de los pares! ¡Canta con nosotros!", pause=0.6, do=[("dancing", 1)]),
        E("pipo", "¡Dos, cuatro, seis, ocho, diez!", pause=0.5),
        E("tula", "¡Contamos de dos en dos otra vez!", pause=0.6),
        E("pipo", "¡Dos, cuatro, seis, ocho, diez!", pause=0.5),
        E("tula", "¡Aplaude, salta y cuenta otra vez!", pause=2.5),
        E("pipo", "¡Dos, cuatro, seis, ocho, diez!", pause=0.5),
        E("tula", "¡Ya sabemos contar de dos en dos!", pause=1.5)]

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

TO20 = [
    E(None, None, pause=0.8, do=[("scene", "card", "¡HASTA EL 20!", "orange", ["N_12", "N_16", "N_20"])], chap="De 2 en 2 hasta el 20"),
    E("pipo", "Tula, ¿podemos contar de dos en dos hasta veinte?"),
    E("tula", "¡Claro que sí! Mira, llegan los patitos. Caminan de dos en dos.", pause=0.5),
    E(None, None, pause=0.6, do=[("scene", "pairs", 10, "pato", False)]),
]
for k in range(1, 11):
    TO20.append(E("tula" if k % 2 else "pipo", "¡" + cap(WORDS[2 * k]) + "!", pause=0.55, do=[("pop", k)]))
    if k == 5:
        TO20.append(E("pipo", "¡Llegamos al diez! ¡Y seguimos!", pause=0.5))
TO20 += [E("tula", "¡Veinte patitos! ¡Son diez pares!", pause=0.7, do=[("numeral", 20)]),
         E("pipo", "¡Cua, cua! ¡Contamos hasta veinte!", pause=0.7)]

QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "cyan")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡A jugar! Mira bien y dime cuántos hay."),
        E("pipo", "¡Un truco: cuenta de dos en dos, es más rápido!", pause=0.7)]
for npr, ok, multi, who in ((3, "calcetin", True, "pipo"), (2, "cereza", False, "tula"), (4, "guante", True, "pipo"), (5, "zapato", True, "tula")):
    s, pl = NOUN[ok]; n = 2 * npr
    seq = ", ".join(WORDS[2 * k] for k in range(1, npr + 1))
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "pairs", npr, ok, multi)]),
             E(who, f"¿{'Cuántas' if ok in FEM else 'Cuántos'} {pl} hay?", pause=4.0, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), f"{cap(seq)}. ¡{cap(WORDS[n])} {pl}!", pause=0.9, do=[("qmark", 0), ("numeral", n)])]
QUIZ.append(E("tula", "¡Excelente! ¡Cuentas como un campeón!", pause=0.6))

MISS = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ NÚMERO FALTA?", "purple")], chap="Juego: ¿qué número falta?"),
        E("pipo", "¡Oh, no! ¡Un número se escondió!"),
        E("tula", "Contemos de dos en dos y descubramos cuál falta.", pause=0.6)]
for seq, miss, who in (([2, 4, 6, 8, 10], 2, "tula"), ([2, 4, 6, 8, 10], 3, "pipo"), ([10, 12, 14, 16, 18], 1, "tula"), ([12, 14, 16, 18, 20], 4, "pipo")):
    said = ", ".join(cap(WORDS[v]) if i == 0 else WORDS[v] for i, v in enumerate(seq[:miss]))
    rest = ", ".join(WORDS[v] for v in seq[miss + 1:])
    q = f"{said}… y luego {rest}. ¿Qué número falta?" if rest else f"{said}… y después, ¿qué viene?"
    MISS += [E(None, None, pause=0.6, do=[("scene", "missing", seq, miss)]),
             E(who, q, pause=3.8, do=[("qmark", 1)]),
             E(other(who), f"¡El {WORDS[seq[miss]]}! " + ", ".join(cap(WORDS[v]) if i == 0 else WORDS[v] for i, v in enumerate(seq)) + ".",
               pause=1.0, do=[("qmark", 0), ("fill", 1)])]

MATCH = [E(None, None, pause=1.0, do=[("scene", "card", "¡BUSCA EL PAR!", "pink", ["calcetin", "calcetin"])], chap="Juego: ¿cuál es su pareja?"),
         E("tula", "¡Ay, ay, ay! Algunas cosas perdieron a su pareja."),
         E("pipo", "¡Ayúdanos a encontrar el par! Tiene que ser del mismo color.", pause=0.6)]
CN = {"red": ("rojo", "roja"), "green": ("verde", "verde"), "blue": ("azul", "azul"), "purple": ("morado", "morada"),
      "yellow": ("amarillo", "amarilla"), "orange": ("naranja", "naranja"), "pink": ("rosado", "rosada")}
for ok, tc, opts, ci, who in (("calcetin", "red", ["blue", "red", "yellow"], 1, "tula"),
                              ("guante", "green", ["green", "pink", "orange"], 0, "pipo"),
                              ("zapato", "blue", ["yellow", "red", "blue"], 2, "tula"),
                              ("calcetin", "purple", ["orange", "purple", "green"], 1, "pipo")):
    s, pl = NOUN[ok]; c = CN[tc][0]
    MATCH += [E(None, None, pause=0.6, do=[("scene", "match", ok, tc, opts, ci, f"¡{c.upper()} CON {c.upper()}!")]),
              E(who, f"Este {s} {c} está solito. ¿Cuál es su pareja?", pause=3.8, do=[("qmark", 1)]),
              E(other(who), f"¡El {s} {c}! {cap(c)} con {c}. ¡Ahora son un par!", pause=1.0, do=[("qmark", 0), ("reveal", 1)])]
MATCH.append(E("tula", "¡Bravo! ¡Encontraste todos los pares!", pause=0.6))

REVIEW = [E(None, None, pause=0.8, do=[("scene", "hop", 20)], chap="Repaso: de 2 en 2 hasta el 20"),
          E("tula", "¡El gran final! La rana va a saltar hasta veinte. ¡Salta tú también en tu casa!", pause=0.6)]
for v in range(2, 21, 2):
    REVIEW.append(E("tula" if v % 4 else "pipo", "¡" + cap(WORDS[v]) + "!", pause=0.55, do=[("rpop", v)]))
REVIEW += [E("pipo", "¡Veinte! ¡Lo logramos!", pause=0.6, do=[("confetti", 1)]),
           E("tula", "¡Bravo! ¡Ya sabes contar de dos en dos!", pause=2.5)]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "Hoy busca pares en tu casa: calcetines, zapatos, guantes… ¡y cuéntalos de dos en dos!", pause=1.0),
    E("tula", "Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO) + PAR + HOP + COUNT10
    ev += dance("pipo", "¡Ya contamos hasta diez! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    ev += EYES + TO20 + QUIZ + MISS + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + MATCH + REVIEW + SONG + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
