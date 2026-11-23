# Episodio infantil: "¡Contamos del 1 al 10 con Tula y Pipo!"
# Cada evento: who (tula/pipo/None), text, pause (silencio después, en s), do (acciones visuales al empezar)
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
FEM = {"un": "una"}

def E(who=None, text=None, pause=0.35, do=None):
    return dict(who=who, text=text, pause=pause, do=do or [])

def count_block(n, who="tula"):
    ev = []
    for i in range(1, n + 1):
        ev.append(E(who, WORDS[i].capitalize() + ".", pause=0.6, do=[("pop", i)]))
    return ev

def label(n):
    k, s, p, cs, cp = OBJS[n]
    if n == 1:
        art = "Una" if k in ("manzana", "estrella", "flor", "burbuja", "pelota", "nube") else "Un"
        return f"¡{art} {s} {cs}!"
    return f"¡{WORDS[n].capitalize()} {p} {cp}!"

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")]),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("tula", "Hoy vamos a contar del uno al diez."),
    E("pipo", "¿Nos ayudas? ¡Cuenta con nosotros en voz alta!"),
    E("tula", "¿Estás listo? ¡Vamos!", pause=0.8),
]

LINES = {
    1: ([("pipo", "¡Tula, mira arriba! ¿Qué es eso tan brillante?"), ("tula", "¡Es el sol! Contemos cuántos soles hay.")], [("pipo", "¡Uno! ¡Qué fácil!")]),
    2: ([("tula", "Ahora miremos el agua. ¿Quién está nadando?"), ("pipo", "¡Son peces! ¡Peces naranjas! Vamos a contarlos.")], [("pipo", "¡Glu, glu! ¡Dos pececitos!")]),
    3: ([("pipo", "¡Uy! ¡Algo está volando, igual que yo!"), ("tula", "Son globos rojos. ¿Me ayudas a contarlos?")], [("pipo", "¡Tres! ¡Pío, pío!")]),
    4: ([("tula", "Tengo hambre… ¡Mira, Pipo, manzanas verdes!"), ("pipo", "¡Qué ricas! Contemos las manzanas.")], [("pipo", "¡Ñam, ñam! ¡Cuatro!")]),
    5: ([("tula", "Mira el cielo de la noche. Hay estrellas moradas."), ("tula", "Ahora te toca a ti. ¿Cuántas estrellas hay?")], [("pipo", "¡Muy bien! ¡Eran cinco!")]),
    6: ([("pipo", "¡Qué lindo jardín! ¡Hay flores rosadas!"), ("tula", "Contemos las flores, despacito.")], [("pipo", "¡Huelen muy rico!")]),
    7: ([("tula", "¿Y esas cosas redondas que flotan?"), ("pipo", "¡Son burbujas celestes! ¡Contemos las burbujas!")], [("pipo", "¡Me encantan las burbujas!")]),
    8: ([("pipo", "¡Mira! ¡Pelotas azules para jugar!"), ("pipo", "¿Cuántas pelotas ves tú?")], [("tula", "¡Muy bien! ¡Ocho pelotas para jugar!")]),
    9: ([("tula", "Mira el cielo otra vez, Pipo. ¿Qué ves?"), ("pipo", "¡Nubes blancas! ¡Parecen algodón! Contemos las nubes.")], [("pipo", "¡Nueve nubes esponjosas!")]),
    10: ([("pipo", "¡Llegamos al último número!"), ("tula", "Para terminar, diez corazones de colores. ¡Cuenta con nosotros!")], [("tula", "¡Lo lograste! ¡Contaste hasta diez!")]),
}
ASK = {5: 3.0, 8: 3.0}   # números con pregunta para que el niño responda

def number_segment(n):
    ev = [E(None, None, pause=1.6, do=[("scene", "count", n)])]
    before, after = LINES[n]
    for who, txt in before:
        ev.append(E(who, txt))
    if n in ASK:
        ev[-1]["pause"] = ASK[n]; ev[-1]["do"].append(("qmark", 1))
        ev.append(E("tula", "¡Contemos juntos para ver si acertaste!", do=[("qmark", 0)]))
    ev += count_block(n, "tula" if n % 2 else "pipo")
    ev.append(E("tula", label(n), pause=0.5, do=[("numeral", n)]))
    for who, txt in after:
        ev.append(E(who, txt, pause=0.6))
    return ev

REVIEW = [
    E(None, None, pause=1.4, do=[("scene", "review")]),
    E("tula", "¡Ahora contemos todos juntos, del uno al diez!", pause=0.6),
] + [E("tula", "¡" + WORDS[i].capitalize() + "!", pause=0.35, do=[("rpop", i)]) for i in range(1, 11)] + [
    E("pipo", "¡Bravo! ¡Bravo!", pause=2.5, do=[("confetti", 1)]),
]

SUMAS = [E(None, None, pause=1.2, do=[("scene", "sum_intro")]),
         E("tula", "¡Ahora, una sorpresa! Vamos a sumar con manzanas."),
         E("pipo", "¿Sumar? ¡Eso es juntar cosas! ¡Qué divertido!", pause=0.8)]
def _m(n): return "manzana" if n == 1 else "manzanas"
for a, b in ((1, 1), (2, 1), (2, 2), (3, 2)):
    c = a + b
    SUMAS += [E(None, None, pause=0.6, do=[("scene", "sum", a, b)]),
              E("pipo", f"Yo tengo {'una' if a == 1 else WORDS[a]} {_m(a)}.", do=[("sa", 1)]),
              E("tula", f"Y yo te doy {'una' if b == 1 else WORDS[b]} {_m(b)} más.", do=[("sb", 1)]),
              E("pipo", "¿Cuántas manzanas hay ahora?", pause=3.0, do=[("qmark", 1)]),
              E("tula", f"¡{WORDS[c].capitalize()}! {WORDS[a].capitalize()} más {WORDS[b]} son {WORDS[c]}.", pause=1.0, do=[("qmark", 0), ("sc", 1)])]

FALTA = [E(None, None, pause=1.0, do=[("scene", "missing_intro")]),
         E("tula", "¡Otro juego! Te muestro unos números y tú me dices cuál falta."),
         E("pipo", "¡Mira bien! ¡Pío!", pause=0.6)]
for seq, miss in (([1, 2, 3, 4], 2), ([5, 6, 7, 8], 1), ([7, 8, 9, 10], 3), ([2, 3, 4, 5], 2)):
    shown = [WORDS[x] for x in seq]; shown[miss] = "…"
    FALTA += [E(None, None, pause=0.5, do=[("scene", "missing", seq, miss)]),
              E("pipo", ", ".join(w for w in shown if w != "…").capitalize() + ". ¿Qué número falta?", pause=3.2, do=[("qmark", 1)]),
              E("tula", f"¡El {WORDS[seq[miss]]}! " + ", ".join(WORDS[x] for x in seq).capitalize() + ".", pause=0.9, do=[("qmark", 0), ("fill", 1)])]

def dance(intro_who, intro):
    return [E(None, None, pause=0.6, do=[("scene", "dance")]), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

COUNTDOWN = [
    E(None, None, pause=1.2, do=[("scene", "rocket")]),
    E("pipo", "¿Y si contamos al revés? ¡Como un cohete!"),
    E("tula", "¡Sí! Del diez al cero. ¿Listos?", pause=0.6),
] + [E("pipo" if i % 2 else "tula", WORDS[i].capitalize() + ".", pause=0.4, do=[("cd", i)]) for i in range(10, 0, -1)] + [
    E("tula", "¡Cero! ¡Despegue!", pause=3.0, do=[("cd", 0), ("launch", 1)]),
]

QUIZ = [E(None, None, pause=1.2, do=[("scene", "quiz_intro")]),
        E("tula", "¡Juguemos un juego! Yo te muestro cosas y tú me dices cuántas hay.", pause=0.8)]
PL = {"manzana": "manzanas", "estrella": "estrellas", "pez": "peces", "globo": "globos", "flor": "flores", "nube": "nubes"}
MASC = {"pez", "globo"}
for n, obj in ((3, "manzana"), (7, "estrella"), (5, "pez"), (2, "globo"), (6, "flor"), (9, "nube")):
    from_name = PL[obj]
    QUIZ += [E(None, None, pause=0.8, do=[("scene", "quiz", n, obj)]),
             E("pipo", f"¿Cuántos {from_name} hay?" if obj in MASC else f"¿Cuántas {from_name} hay?", pause=3.5, do=[("qmark", 1), ("popall", 1)]),
             E("tula", f"¡{WORDS[n].capitalize()}! ¡Hay {WORDS[n]} {from_name}!", pause=0.9, do=[("qmark", 0), ("numeral", n)])]

COLORS = [E(None, None, pause=1.0, do=[("scene", "colors", 1)]),
          E("pipo", "¿Y te acuerdas de los colores? ¿De qué color era el sol?", pause=3.0, do=[("qmark", 1)]),
          E("tula", "¡Amarillo! ¡El sol era amarillo!", pause=0.8, do=[("qmark", 0), ("reveal", 1)]),
          E(None, None, pause=0.6, do=[("scene", "colors", 4)]),
          E("pipo", "¿Y de qué color eran las manzanas?", pause=3.0, do=[("qmark", 1)]),
          E("tula", "¡Verdes! ¡Manzanas verdes!", pause=0.8, do=[("qmark", 0), ("reveal", 1)]),
          E(None, None, pause=0.6, do=[("scene", "colors", 7)]),
          E("pipo", "¿Y las burbujas? ¿De qué color eran?", pause=3.0, do=[("qmark", 1)]),
          E("tula", "¡Celestes! ¡Burbujas celestes!", pause=0.8, do=[("qmark", 0), ("reveal", 1)]),
          E(None, None, pause=0.6, do=[("scene", "colors", 8)]),
          E("pipo", "¿Y las pelotas?", pause=3.0, do=[("qmark", 1)]),
          E("tula", "¡Azules! ¡Eran azules!", pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")]),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "¡Ya sabes contar hasta diez! ¡Y al revés también!"),
    E("tula", "Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    for n in range(1, 11):
        ev += number_segment(n)
        if n == 5:
            ev += dance("pipo", "¡Ya contamos hasta cinco! ¡Hagamos una pausa para bailar!")
    ev += REVIEW + dance("tula", "¡Muy bien! ¡A bailar otra vez!") + QUIZ + SUMAS + FALTA + COUNTDOWN + COLORS + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
