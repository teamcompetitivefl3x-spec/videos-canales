# Episodio infantil: "¡Aprendemos los colores con Tula y Pipo!" (largo, 2026-11-21)
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
TITLE = ("¡LOS", "COLORES!")
THUMB = {"lines": ("¡APRENDEMOS", "LOS COLORES!"), "objs": ["M_red", "M_yellow", "M_blue", "M_green"], "x": (790, 1345), "y": 640, "size": 230}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"

BLUE = (60, 120, 240); RED = (240, 70, 70); YEL = (255, 211, 51); GRN = (98, 196, 84); PUR = (160, 100, 230); PINK = (255, 130, 190)

# color: (clave, NOMBRE, "rojo", objetos [(sprite, color, NOMBRE, frase)], búsqueda en casa)
C = {
    "red": ("ROJO", "rojo", [("fresa", None, "FRESA", "La fresa es roja."),
                             ("manzanar", None, "MANZANA", "Esta manzana también es roja."),
                             ("corazon", None, "CORAZÓN", "¡Y un corazón rojo, lleno de amor!")],
            "Busca algo rojo en tu casa. ¿Lo encontraste? ¡Señálalo!"),
    "yellow": ("AMARILLO", "amarillo", [("sol", None, "SOL", "El sol es amarillo y brilla mucho."),
                                        ("banana", None, "PLÁTANO", "El plátano es amarillo."),
                                        ("pato", None, "PATITO", "¡Y el patito es amarillo! ¡Cuac, cuac!")],
               "¿Ves algo amarillo cerca de ti? ¡Tócalo con tu dedito!"),
    "blue": ("AZUL", "azul", [("pelota", None, "PELOTA", "La pelota es azul."),
                              ("gota", None, "GOTA", "Una gotita de agua azul. ¡Plic, plic!"),
                              ("pez", BLUE, "PEZ", "Y un pececito azul nadando en el mar.")],
             "Mira hacia arriba. ¿De qué color es el cielo? ¡Azul!"),
    "orange": ("NARANJA", "naranja", [("naranja", None, "NARANJA", "La naranja es… ¡naranja! Se llama igual que su color."),
                                      ("gato", None, "GATITO", "El gatito es naranja. ¡Miau!"),
                                      ("estrellamar", None, "ESTRELLA DE MAR", "Y la estrella de mar también es naranja.")],
               "Busca algo naranja a tu alrededor. ¿Lo encontraste?"),
    "green": ("VERDE", "verde", [("rana", None, "RANA", "La rana es verde. ¡Croac!"),
                                 ("arbol", None, "ÁRBOL", "Las hojas del árbol son verdes."),
                                 ("pera", None, "PERA", "Y la pera es verde y muy jugosa.")],
              "Busca algo verde. ¿Una planta? ¿Una hojita?"),
    "purple": ("MORADO", "morado", [("uvas", None, "UVAS", "Las uvas son moradas."),
                                    ("gorro", None, "GORRO", "Un gorro de fiesta morado."),
                                    ("estrella", None, "ESTRELLA", "¡Y una estrella morada que nos guiña el ojo!")],
               "¿Tienes algo morado en tu casa? ¡Búscalo!"),
    "pink": ("ROSADO", "rosado", [("cerdo", None, "CERDITO", "El cerdito es rosado. ¡Oinc!"),
                                  ("flor", None, "FLOR", "Esta flor es rosada y huele rico."),
                                  ("globoc", PINK, "GLOBO", "Y un globo rosado con forma de corazón.")],
             "¿Ves algo rosado? ¡Señálalo con tu dedito!"),
    "white": ("BLANCO", "blanco", [("nube", None, "NUBE", "La nube es blanca, como el algodón."),
                                   ("oveja", None, "OVEJA", "La oveja tiene lana blanca. ¡Bee!"),
                                   ("iglu", None, "IGLÚ", "Y el iglú es blanco, hecho de nieve.")],
              "Busca algo blanco. ¿Una hoja de papel? ¿Una media?"),
}
ASK1 = {"red": ("tula", "¡Mira, Pipo! ¡Cayó pintura! ¿Sabes cómo se llama este color?"),
        "yellow": ("pipo", "¡Otra mancha! Esta es muy brillante. ¿Qué color es?"),
        "blue": ("pipo", "¡Splash! Este color es igual que mis plumas. ¿Cuál es?"),
        "orange": ("pipo", "¡Volvió a caer pintura! ¿Te acuerdas de este color?"),
        "green": ("tula", "¡Splash! Es el color de mi caparazón. ¿Cómo se llama?"),
        "purple": ("pipo", "¿Y este color? ¿Lo recuerdas?"),
        "pink": ("tula", "¡Una mancha nueva! Es un color muy suave. ¿Sabes cuál es?"),
        "white": ("pipo", "¡Y la última mancha! Es clarita, clarita. ¿Qué color es?")}

def color_segment(cn, who, chap=None, intro=None):
    NAME, nm, items, hunt = C[cn]; o = other(who); q_who, q = ASK1[cn]
    ev = [E(None, None, pause=1.2, do=[("scene", "paint", "M_" + cn, NAME, cn)], chap=chap)]
    if intro: ev.append(E(q_who, intro, pause=0.3))
    ev += [E(q_who, q, pause=2.8, do=[("qmark", 1)]),
           E(other(q_who), f"¡{nm.capitalize()}! ¡Es el color {nm}!", pause=0.7, do=[("qmark", 0), ("reveal", 1)]),
           E(q_who, f"Dilo conmigo: ¡{nm}!", pause=1.8),
           E(None, None, pause=0.7, do=[("scene", "colorw", NAME, cn, [(a, b, c) for a, b, c, _ in items])]),
           E(who, f"Vamos a buscar cosas de color {nm}.", pause=0.4)]
    for i, (a, b, c, f) in enumerate(items, 1):
        ev.append(E(who if i % 2 else o, f, pause=0.7, do=[("pop", i)]))
    ev.append(E(o, hunt, pause=3.0))
    return ev

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿qué vamos a aprender hoy?"),
    E("tula", "¡Hoy vamos a aprender los colores!", pause=0.6,
      do=[("scene", "card", "¡LOS COLORES!", "red", ["M_red", "M_yellow", "M_blue"])]),
    E("pipo", "¡El mundo está lleno de colores! Rojo, amarillo, azul… ¡y muchos más!"),
    E("tula", "Mira con atención y dime los colores en voz alta. ¿Nos ayudas?", pause=0.6),
    E("pipo", "¡Abre bien los ojos! ¡Vamos!", pause=0.8),
]

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

# Magia: mezclar colores
MIX = [E(None, None, pause=1.0, do=[("scene", "card", "¡MAGIA DE COLORES!", "purple", ["M_red", "M_yellow", "M_blue"])], chap="Magia: mezclamos colores"),
       E("tula", "¿Sabías que si juntamos dos colores sale un color nuevo?"),
       E("pipo", "¿De verdad? ¡Es como magia! ¡Probemos!", pause=0.6)]
for ca, cb, cr, lab, na, nb, nr, who in (("red", "yellow", "orange", "NARANJA", "rojo", "amarillo", "naranja", "tula"),
                                         ("blue", "yellow", "green", "VERDE", "azul", "amarillo", "verde", "pipo"),
                                         ("red", "blue", "purple", "MORADO", "rojo", "azul", "morado", "tula")):
    MIX += [E(None, None, pause=0.5, do=[("scene", "mix", ca, cb, cr, lab)]),
            E(who, f"Ponemos un poquito de {na}…", pause=0.4, do=[("sa", 1)]),
            E(other(who), f"…y un poquito de {nb}.", pause=0.4, do=[("sb", 1)]),
            E(who, "Mezclamos, mezclamos… ¿Qué color saldrá?", pause=3.0, do=[("qmark", 1)]),
            E(other(who), f"¡{nr.capitalize()}! ¡{na.capitalize()} y {nb} hacen {nr}!", pause=1.2, do=[("qmark", 0), ("reveal", 1)])]
MIX.append(E("pipo", "¡Qué magia! Ahora conozcamos esos colores nuevos.", pause=0.6))

# Juego: ¿de qué color es? (sin color -> se pinta)
GUESS = [E(None, None, pause=1.0, do=[("scene", "card", "¿DE QUÉ COLOR ES?", "cyan")], chap="Juego: ¿de qué color es?"),
         E("tula", "¡Oh, no! Estas cosas perdieron su color.", pause=0.4),
         E("pipo", "¡Ayúdanos a pintarlas! Dime de qué color son.", pause=0.6)]
for ok, lab, cn, q, a, who in (("globo", "¡ROJO!", "red", "¿De qué color es el globo?", "¡Rojo! ¡Un globo rojo!", "pipo"),
                               ("manzana", "¡VERDE!", "green", "¿Y esta manzana? ¿De qué color es?", "¡Verde! ¡Una manzana verde!", "tula"),
                               ("estrellaf", "¡AMARILLO!", "yellow", "¿De qué color es la estrella?", "¡Amarilla! ¡Una estrella amarilla!", "pipo"),
                               ("cuadrado", "¡AZUL!", "blue", "¿De qué color es el cuadrado?", "¡Azul! ¡Un cuadrado azul!", "tula"),
                               ("uvas", "¡MORADO!", "purple", "Y la última: ¿de qué color son las uvas?", "¡Moradas! ¡Las uvas son moradas!", "pipo")):
    GUESS += [E(None, None, pause=0.6, do=[("scene", "fruit", ok, "color", lab, cn)]),
              E(who, q, pause=3.2, do=[("qmark", 1)]),
              E(other(who), a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿cuántos hay?
QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "orange")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡Ahora contemos colores! Cuenta con tu dedito.", pause=0.5)]
for n, ok, q, a, who in ((3, "globo", "¿Cuántos globos rojos hay?", "¡Tres! ¡Hay tres globos rojos!", "pipo"),
                         (4, "pelota", "¿Cuántas pelotas azules hay?", "¡Cuatro! ¡Cuatro pelotas azules!", "tula"),
                         (5, "estrella", "¿Cuántas estrellas moradas ves?", "¡Cinco! ¡Cinco estrellas moradas!", "pipo")):
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "quiz", n, ok)]),
             E(who, q, pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), a, pause=0.9, do=[("qmark", 0), ("numeral", n)])]

# Juego: ¿cuál es diferente?
ODD = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁL ES DIFERENTE?", "pink")], chap="Juego: ¿cuál es diferente?"),
       E("pipo", "¡Uno de estos tiene otro color! ¿Lo encuentras?", pause=0.5)]
for items, oi, lab, cn, q, a, who in (
        ([("pelota", BLUE, 1.0), ("pelota", BLUE, 1.0), ("pelota", RED, 1.0), ("pelota", BLUE, 1.0)], 2, "¡LA ROJA!", "red",
         "Pelotas azules… y una diferente. ¿Cuál es?", "¡La roja! Las otras son azules.", "tula"),
        ([("globo", GRN, 1.0), ("globo", YEL, 1.0), ("globo", YEL, 1.0), ("globo", YEL, 1.0)], 0, "¡EL VERDE!", "green",
         "¿Qué globo tiene otro color?", "¡El verde! Los demás son amarillos.", "pipo"),
        ([("corazon", PINK, 1.0), ("corazon", PINK, 1.0), ("corazon", PINK, 1.0), ("corazon", PINK, 1.0), ("corazon", PUR, 1.0)], 4, "¡EL MORADO!", "purple",
         "Corazones rosados… ¿cuál es diferente?", "¡El morado! ¡Lo encontraste!", "tula")):
    ODD += [E(None, None, pause=0.6, do=[("scene", "odd", items, oi, lab, cn)]),
            E(who, q, pause=3.4, do=[("qmark", 1)]),
            E(other(who), a, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿qué color falta?
PAT = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ COLOR FALTA?", "yellow")], chap="Juego: ¿qué color falta?"),
       E("tula", "¡Las manchas de pintura hicieron una fila! Pero una se escondió.", pause=0.5)]
for seq, miss, q, a, who in ((["M_red", "M_blue", "M_red", "M_blue", "M_red", "M_blue"], 5, "Rojo, azul, rojo, azul, rojo… ¿Qué color sigue?", "¡Azul! Rojo, azul, rojo, azul, rojo, azul.", "pipo"),
                             (["M_yellow", "M_green", "M_yellow", "M_green", "M_yellow"], 3, "Amarillo, verde, amarillo… ¿y qué falta aquí?", "¡Verde! Amarillo, verde, amarillo, verde, amarillo.", "tula"),
                             (["M_red", "M_yellow", "M_blue", "M_red", "M_yellow", "M_blue"], 4, "Rojo, amarillo, azul, rojo… ¿qué color falta?", "¡Amarillo! Rojo, amarillo, azul, rojo, amarillo, azul.", "pipo")):
    PAT += [E(None, None, pause=0.6, do=[("scene", "spattern", seq, miss, "¿QUÉ COLOR FALTA?")]),
            E(who, q, pause=3.4, do=[("qmark", 1)]),
            E(other(who), a, pause=1.0, do=[("qmark", 0), ("fill", 1)])]

# Repaso: el arcoíris
RB = [("red", "ROJO"), ("orange", "NARANJA"), ("yellow", "AMARILLO"), ("green", "VERDE"), ("blue", "AZUL"), ("purple", "MORADO")]
REVIEW = [E(None, None, pause=1.0, do=[("scene", "rainbow", RB)], chap="Repaso: ¡el arcoíris!"),
          E("pipo", "¡Mira, Tula! ¡Salió el sol después de la lluvia!"),
          E("tula", "¡Vamos a pintar un arcoíris! Di cada color conmigo.", pause=0.8)]
for i, (cn, NM) in enumerate(RB, 1):
    REVIEW += [E("tula" if i % 2 else "pipo", f"¡{NM.capitalize()}!", pause=1.6, do=[("rpop", i)])]
REVIEW += [E("pipo", "¡Qué arcoíris tan bonito!", pause=0.6, do=[("confetti", 1)]),
           E("tula", "Rojo, naranja, amarillo, verde, azul y morado. ¡Bravo!", pause=2.5)]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito! Ya conoces muchos colores."),
    E("pipo", "Una pregunta más: ¿de qué color es Tula?", pause=2.6),
    E("tula", "¡Verde! ¿Y de qué color es Pipo?", pause=2.6),
    E("pipo", "¡Azul! ¡Muy bien!"),
    E("tula", "¿Cuál es tu color favorito? ¡Hoy busca cosas de ese color con tu familia!", pause=1.5),
    E("tula", "Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    ev += color_segment("red", "tula", "Rojo, amarillo y azul")
    ev += color_segment("yellow", "pipo")
    ev += color_segment("blue", "tula")
    ev += dance("pipo", "¡Ya conocemos tres colores! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    ev += MIX
    ev += color_segment("orange", "pipo", "Naranja, verde y morado")
    ev += color_segment("green", "tula")
    ev += color_segment("purple", "pipo")
    ev += color_segment("pink", "tula", "Rosado y blanco")
    ev += color_segment("white", "pipo")
    ev += GUESS + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + QUIZ + ODD + PAT + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
