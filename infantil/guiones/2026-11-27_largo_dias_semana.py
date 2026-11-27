# Episodio infantil: "¡Los días de la semana con Tula y Pipo!" (largo, 2026-11-27)
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
TITLE = ("¡LOS DÍAS DE", "LA SEMANA!")
THUMB = {"lines": ("¡LOS DÍAS DE", "LA SEMANA!"), "objs": ["cal_1", "tambor", "cal_7"], "x": (850, 1320), "y": 640, "size": 260}

DN = ["", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿qué vamos a aprender hoy?"),
    E("tula", "¡Hoy vamos a aprender los días de la semana!", pause=0.6,
      do=[("scene", "card", "¡LOS DÍAS DE LA SEMANA!", "orange", ["cal_1", "cal_4", "cal_7"])]),
    E("pipo", "¿Días de la semana? ¿Qué es una semana?"),
    E("tula", "Una semana es un grupito de días que se repite, una y otra vez, como una ronda."),
    E("pipo", "¿Y cuántos días tiene una semana?"),
    E("tula", "¡Vamos a contarlos! Cuenta con tu dedito.", pause=0.6),
]

COUNT = [E(None, None, pause=0.6, do=[("scene", "week", 7, None, None, "count")], chap="¿Cuántos días tiene la semana?")]
for i in range(1, 8):
    COUNT.append(E("tula" if i % 2 else "pipo", "¡" + WORDS[i].capitalize() + "!", pause=0.55, do=[("rpop", i)]))
COUNT += [
    E("pipo", "¡Siete! ¡La semana tiene siete días!", pause=0.6, do=[("confetti", 1)]),
    E("tula", "Muy bien. Levanta siete deditos: cinco en una mano… y dos en la otra.", pause=2.6),
    E("pipo", "¡Siete días! ¡Ahora vamos a conocerlos uno por uno!", pause=0.6),
]

def song(chap, intro_who, intro, fast=False):
    ev = [E(None, None, pause=0.5, do=[("scene", "week", 7, None, None, "names")], chap=chap),
          E(intro_who, intro, pause=0.7)]
    for i in range(1, 8):
        ev.append(E("tula" if i % 2 else "pipo", "¡" + DN[i].capitalize() + "!", pause=0.35 if fast else 0.6, do=[("rpop", i)]))
    return ev

# Cada día: (sprites, [(quién, texto, pausa)...]) — color del día en DAYS de kids_render
DAY = {
    1: ([("paleta", None)], [
        ("tula", "El primer día de la semana es… ¡el lunes!", 0.5),
        ("pipo", "El lunes es rojo, como una frutilla. Dilo conmigo: ¡lunes!", 2.0),
        ("tula", "¿Y qué hacemos el lunes? ¡Pintamos un dibujo con muchos colores!", 0.6, "pop1"),
        ("pipo", "Mueve tu mano como un pincel: arriba… y abajo. Arriba… y abajo.", 3.0),
        ("tula", "¡Qué lindo dibujo! Después del lunes viene… ¿qué día viene?", 2.8, "q"),
    ]),
    2: ([("pelota", "orange")], [
        ("pipo", "¡El martes! El segundo día de la semana.", 0.5),
        ("tula", "El martes es naranja, como una naranja jugosa. Dilo conmigo: ¡martes!", 2.0),
        ("pipo", "¿Y qué hacemos el martes? ¡Jugamos a la pelota!", 0.6, "pop1"),
        ("tula", "¡Patea la pelota! ¡Uno, dos… y gol!", 3.0),
        ("pipo", "¡Goool! Después del martes viene… ¿qué día viene?", 2.8, "q"),
    ]),
    3: ([("regadera", "yellow"), ("flor", "pink")], [
        ("tula", "¡El miércoles! Mi… ér… co… les. ¡Es una palabra larga!", 0.5),
        ("pipo", "El miércoles es amarillo, como el sol. Dilo conmigo: ¡miércoles!", 2.0),
        ("tula", "¿Y qué hacemos el miércoles? ¡Regamos las flores del jardín!", 0.6, "pop1"),
        ("pipo", "¡Mira cómo crece la flor!", 0.6, "pop2"),
        ("tula", "Mueve tus deditos como gotitas de agua: plic, plic, plic.", 3.0),
        ("pipo", "Después del miércoles viene… ¿qué día viene?", 2.8, "q"),
    ]),
    4: ([("rana", None)], [
        ("pipo", "¡El jueves! Ya estamos en la mitad de la semana.", 0.5),
        ("tula", "El jueves es verde, como el pasto. Dilo conmigo: ¡jueves!", 2.0),
        ("pipo", "¿Y qué hacemos el jueves? ¡Vamos al estanque a ver a la rana!", 0.6, "pop1"),
        ("tula", "La rana dice: ¡croac, croac! Salta como una rana… ¡salta, salta, salta!", 3.2),
        ("pipo", "¡Qué bien saltas! Después del jueves viene… ¿qué día viene?", 2.8, "q"),
    ]),
    5: ([("tambor", "blue")], [
        ("tula", "¡El viernes! El quinto día de la semana.", 0.5),
        ("pipo", "El viernes es azul, como el mar. Dilo conmigo: ¡viernes!", 2.0),
        ("tula", "¿Y qué hacemos el viernes? ¡Hacemos música con el tambor!", 0.6, "pop1"),
        ("pipo", "Toca el tambor en tus piernas: ¡pum, pum, pum! ¡Pum, pum, pum!", 3.0),
        ("tula", "¡Muy bien! Después del viernes viene… ¿qué día viene?", 2.8, "q"),
    ]),
    6: ([("cometa", "purple")], [
        ("pipo", "¡El sábado! ¡Llegó el fin de semana!", 0.5),
        ("tula", "El sábado es morado, como las uvas. Dilo conmigo: ¡sábado!", 2.0),
        ("pipo", "¿Y qué hacemos el sábado? ¡Vamos al parque a volar la cometa!", 0.6, "pop1"),
        ("tula", "Sopla el viento… Mueve tus brazos como el viento: ¡fuuu, fuuu!", 3.0),
        ("pipo", "¡La cometa vuela alto! Después del sábado viene… ¿qué día viene?", 2.8, "q"),
    ]),
    7: ([("pastel", "pink"), ("corazon", "red")], [
        ("tula", "¡El domingo! El último día de la semana.", 0.5),
        ("pipo", "El domingo es rosado, como un chicle. Dilo conmigo: ¡domingo!", 2.0),
        ("tula", "¿Y qué hacemos el domingo? ¡Visitamos a los abuelos y comemos pastel!", 0.6, "pop1"),
        ("pipo", "¡Y les damos mucho amor!", 0.6, "pop2"),
        ("tula", "Dale un abrazo grande a alguien de tu familia. ¡Un abrazo de oso!", 3.0),
        ("pipo", "El sábado y el domingo son el fin de semana. ¡Días para descansar y jugar en familia!", 0.8),
    ]),
}
CHAPS = {1: "Lunes: ¡a pintar!", 2: "Martes: ¡a jugar a la pelota!", 3: "Miércoles: ¡a regar las flores!", 4: "Jueves: ¡a saltar como la rana!",
         5: "Viernes: ¡a tocar el tambor!", 6: "Sábado: ¡a volar la cometa!", 7: "Domingo: ¡con los abuelos!"}

def day_segment(i):
    objs, lines = DAY[i]
    ev = [E(None, None, pause=0.9, do=[("scene", "day", i, objs, False)], chap=CHAPS[i])]
    for ln in lines:
        who, txt, p = ln[:3]; tag = ln[3] if len(ln) > 3 else None
        do = []
        if tag == "pop1": do = [("pop", 1)]
        elif tag == "pop2": do = [("pop", 2)]
        elif tag == "q": do = [("qmark", 1)]
        ev.append(E(who, txt, pause=p, do=do))
    return ev

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

# Juego: ¿qué día sigue?
NEXT = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ DÍA SIGUE?", "cyan")], chap="Juego: ¿qué día sigue?"),
        E("tula", "¡A jugar! Te mostramos unos días… y tú nos dices cuál viene después.", pause=0.4),
        E("pipo", "¡Responde fuerte, fuerte! ¡Pío!", pause=0.5)]
for upto, q, a, who in ((2, "Lunes… y después… ¿qué día sigue?", "¡Martes! Lunes, martes.", "pipo"),
                        (4, "Lunes, martes, miércoles… ¿y qué día sigue?", "¡Jueves! ¡Muy bien!", "tula"),
                        (7, "Jueves, viernes, sábado… ¿y qué día sigue?", "¡Domingo! El último día de la semana.", "pipo")):
    NEXT += [E(None, None, pause=0.8, do=[("scene", "week", upto, upto, "¿QUÉ DÍA SIGUE?")]),
             E(who, q, pause=3.4, do=[("qmark", 1)]),
             E(other(who), a, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿qué día falta?
MISS = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ DÍA FALTA?", "purple")], chap="Juego: ¿qué día falta?"),
        E("pipo", "¡Oh, no! ¡Se escondió un día de la semana! ¿Nos ayudas a encontrarlo?", pause=0.5)]
for m, q, a, who in ((5, "Lunes, martes, miércoles, jueves… ¿y qué día falta?", "¡Viernes! ¡Lo encontraste!", "tula"),
                     (2, "Lunes… ¿y qué día falta?… miércoles.", "¡Martes! ¡Lunes, martes, miércoles!", "pipo"),
                     (6, "Viernes… ¿qué día falta?… domingo.", "¡Sábado! ¡El día de la cometa!", "tula")):
    MISS += [E(None, None, pause=0.8, do=[("scene", "week", 7, m, "¿QUÉ DÍA FALTA?")]),
             E(who, q, pause=3.4, do=[("qmark", 1)]),
             E(other(who), a, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿qué día fue? (memoria)
MEM = [E(None, None, pause=1.0, do=[("scene", "card", "¿TE ACUERDAS?", "pink")], chap="Juego: ¿te acuerdas qué día fue?"),
       E("tula", "¡Un juego de memoria! ¿Te acuerdas qué hicimos cada día?", pause=0.5)]
for i, objs, q, a, who in ((5, [("tambor", "blue")], "¿Qué día tocamos el tambor? Pum, pum, pum…", "¡El viernes! ¡El viernes azul!", "pipo"),
                           (1, [("paleta", None)], "¿Qué día pintamos el dibujo?", "¡El lunes! ¡El lunes rojo!", "tula"),
                           (4, [("rana", None)], "¿Y qué día saltamos con la rana? Croac, croac…", "¡El jueves! ¡El jueves verde!", "pipo")):
    MEM += [E(None, None, pause=0.8, do=[("scene", "day", i, objs, True)]),
            E(who, q, pause=3.6, do=[("qmark", 1)]),
            E(other(who), a, pause=1.2, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿cuántos hay?
QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "orange")], chap="Juego: ¿cuántos hay?"),
        E("pipo", "¡Ahora a contar! Cuenta con tu dedito.", pause=0.5)]
for n, ok, q, a, who in ((3, "tambor", "¿Cuántos tambores hay?", "¡Tres! ¡Tres tambores! Pum, pum, pum.", "tula"),
                         (5, "cometa", "¿Cuántas cometas vuelan en el cielo?", "¡Cinco! ¡Cinco cometas!", "pipo"),
                         (4, "pastel", "¿Cuántos pasteles hay para los abuelos?", "¡Cuatro! ¡Cuatro pasteles! ¡Ñam, ñam!", "tula")):
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "quiz", n, ok)]),
             E(who, q, pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), a, pause=0.9, do=[("qmark", 0), ("numeral", n)])]

# Juego: ¿de qué color es?
COLOR = [E(None, None, pause=1.0, do=[("scene", "card", "¿DE QUÉ COLOR ES?", "yellow")], chap="Juego: ¿de qué color es?"),
         E("tula", "¡Estos dibujos perdieron su color! ¿Nos ayudas a pintarlos?", pause=0.5)]
for ok, lab, cn, q, a, who in (("tambor", "¡AZUL!", "blue", "¿De qué color es el tambor del viernes?", "¡Azul! ¡Como el viernes!", "pipo"),
                               ("regadera", "¡AMARILLO!", "yellow", "¿Y la regadera del miércoles? ¿De qué color es?", "¡Amarilla! ¡Como el sol!", "tula"),
                               ("cometa", "¡MORADO!", "purple", "¿De qué color es la cometa del sábado?", "¡Morada! ¡Qué linda cometa!", "pipo")):
    COLOR += [E(None, None, pause=0.6, do=[("scene", "fruit", ok, "color", lab, cn)]),
              E(who, q, pause=3.2, do=[("qmark", 1)]),
              E(other(who), a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

# Repaso
REVIEW = [E(None, None, pause=0.6, do=[("scene", "week", 7, None, None, "names")], chap="Repaso: ¡los siete días!"),
          E("tula", "¡Ahora repasemos todos los días, bien rápido! ¿Listo?", pause=0.6)]
for i in range(1, 8):
    REVIEW.append(E("pipo" if i % 2 else "tula", "¡" + DN[i].capitalize() + "!", pause=0.3, do=[("rpop", i)]))
REVIEW += [E("tula", "¡Bravo! ¡Ya sabes los siete días de la semana!", pause=2.5, do=[("confetti", 1)])]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("pipo", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("tula", "Una última pregunta: ¿qué día es hoy? Pregúntale a mamá o a papá.", pause=3.0),
    E("pipo", "Y cada mañana, cuando te despiertes, di el nombre del día. ¡Así nunca lo olvidas!", pause=0.8),
    E("tula", "Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO) + COUNT
    ev += song("La canción de los días", "pipo", "¡Ahora cantemos sus nombres! Repite con nosotros.")
    for i in (1, 2, 3, 4):
        ev += day_segment(i)
    ev += dance("pipo", "¡Ya llegamos a la mitad de la semana! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    for i in (5, 6, 7):
        ev += day_segment(i)
    ev += song("¡Cantamos otra vez!", "tula", "¡Cantemos otra vez la canción de los días, ahora más rápido!", fast=True)
    ev += NEXT + MISS + MEM + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + QUIZ + COLOR + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
