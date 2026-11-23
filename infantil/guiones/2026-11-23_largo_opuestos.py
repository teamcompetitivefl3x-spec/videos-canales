# Episodio infantil: "¡Aprendemos los opuestos con Tula y Pipo!" (largo, 2026-11-23)
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
TITLE = ("¡LOS", "OPUESTOS!")
THUMB = {"lines": ("¡APRENDEMOS", "LOS OPUESTOS!"), "objs": ["sol", "luna", "helado", "taza"], "x": (850, 1440), "y": 610, "size": 262}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"

# opuesto: clave -> (A, B, color A, color B, [(quién, texto A), (quién, pregunta), (quién, respuesta B), (quién, "¡son opuestos!"), (quién, juego con el cuerpo, pausa)])
OPP = {
    "tam": ("GRANDE", "PEQUEÑO", "orange", "cyan", [
        ("tula", "Mira esta pelota. ¡Es muy, muy grande!"),
        ("pipo", "Y lo contrario de grande… ¿qué es?"),
        ("tula", "¡Pequeño! Esta pelota es pequeña."),
        ("pipo", "Grande… y pequeño. ¡Son opuestos!"),
        ("tula", "Abre los brazos y hazte grande, grande… ¡Y ahora hazte pequeñito!", 2.8)]),
    "pos": ("ARRIBA", "ABAJO", "yellow", "green", [
        ("pipo", "¡Mira! La pelota saltó muy alto. Está arriba."),
        ("tula", "¿Y cuando cae al pasto? ¿Dónde está la pelota?"),
        ("pipo", "¡Abajo! La pelota está abajo."),
        ("tula", "Arriba… y abajo. ¡Son opuestos!"),
        ("pipo", "Señala arriba, al cielo… ¡Y ahora señala abajo, al piso!", 2.8)]),
    "dia": ("DÍA", "NOCHE", "yellow", "purple", [
        ("tula", "Salió el sol. ¡Es de día! De día jugamos en el parque."),
        ("pipo", "Y cuando el sol se va y sale la luna… ¿qué es?"),
        ("tula", "¡Es de noche! De noche vemos la luna y las estrellas."),
        ("pipo", "Día… y noche. ¡Son opuestos!"),
        ("tula", "De noche dormimos. Cierra los ojitos, como si durmieras…", 2.6)]),
    "vaso": ("LLENO", "VACÍO", "blue", "orange", [
        ("pipo", "¡Qué sed tengo! Este vaso tiene mucha agua. Está lleno."),
        ("tula", "Pipo se tomó toda el agua. ¿Cómo quedó el vaso?"),
        ("pipo", "¡Vacío! Ya no tiene nada de agua."),
        ("tula", "Lleno… y vacío. ¡Son opuestos!"),
        ("pipo", "Infla los cachetes, llenos de aire, como un globo… ¡Y suelta el aire!", 2.6)]),
    "puerta": ("ABIERTA", "CERRADA", "green", "red", [
        ("tula", "¡Toc, toc! Esta puerta está abierta. ¡Pasa, pasa!"),
        ("pipo", "Y si la empujamos así… ¿cómo queda la puerta?"),
        ("tula", "¡Cerrada! Ahora la puerta está cerrada."),
        ("pipo", "Abierta… y cerrada. ¡Son opuestos!"),
        ("tula", "Abre tus manos… ¡Y ciérralas! Abre… ¡Y cierra!", 2.8)]),
    "temp": ("CALIENTE", "FRÍO", "red", "cyan", [
        ("pipo", "Mira esta taza de chocolate. Sale humito. ¡Está caliente!"),
        ("tula", "¿Y el helado? ¿Cómo es el helado?"),
        ("pipo", "¡Frío! ¡El helado está muy frío!"),
        ("tula", "Caliente… y frío. ¡Son opuestos!"),
        ("pipo", "Cuando algo está caliente, soplamos así. ¡Sopla conmigo!", 2.6)]),
    "vel": ("RÁPIDO", "LENTO", "red", "purple", [
        ("tula", "¡Mira ese auto! Va muy, muy rápido. ¡Brum, brum!"),
        ("pipo", "Y el caracol camina despacito… ¿Cómo va el caracol?"),
        ("tula", "¡Lento! El caracol va lento, lento… igual que yo."),
        ("pipo", "Rápido… y lento. ¡Son opuestos!"),
        ("tula", "Aplaude rápido, rápido… ¡Y ahora lento, muy lento!", 3.0)]),
    "cara": ("FELIZ", "TRISTE", "yellow", "blue", [
        ("pipo", "Esta carita sonríe. ¡Está feliz!"),
        ("tula", "Y esta carita está llorando. ¿Cómo se siente?"),
        ("pipo", "¡Triste! Está triste."),
        ("tula", "Feliz… y triste. ¡Son opuestos! Cuando un amigo está triste, le damos un abrazo."),
        ("pipo", "Pon una cara feliz… ¡Ahora una cara triste! ¡Y otra vez feliz!", 2.8)]),
}

def opp_segment(key, chap=None, intro=None):
    A, B, ca, cb, ls = OPP[key]
    (wa, ta), (wq, tq), (wr, tr), (wx, tx), (wd, td, pd) = ls
    ev = [E(None, None, pause=0.9, do=[("scene", "opp", key, A, B, ca, cb)], chap=chap)]
    if intro: ev.append(E(intro[0], intro[1], pause=0.3))
    ev += [E(wa, ta, pause=0.6, do=[("sa", 1)]),
           E(wq, tq, pause=3.0, do=[("qmark", 1)]),
           E(wr, tr, pause=0.8, do=[("qmark", 0), ("sb", 1)]),
           E(wx, tx, pause=0.5),
           E(other(wx), f"Dilo conmigo: ¡{A.lower()}… {B.lower()}!", pause=2.0),
           E(wd, td, pause=pd)]
    return ev

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿qué vamos a aprender hoy?"),
    E("tula", "¡Hoy vamos a aprender los opuestos!", pause=0.6,
      do=[("scene", "card", "¡LOS OPUESTOS!", "orange", ["sol", "luna"])]),
    E("pipo", "¿Opuestos? ¿Qué es eso?"),
    E("tula", "Los opuestos son cosas muy, muy distintas. ¡Como el día y la noche!"),
    E("pipo", "¡Ah, ya sé! ¡Como yo, que soy rápido, y tú, que eres lenta!"),
    E("tula", "¡Exacto! Mira bien y responde en voz alta. ¿Nos ayudas?", pause=0.6),
    E("pipo", "¡Vamos!", pause=0.8),
]

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

# Juego: ¿cuál es? (un solo cuadro)
ONE = [E(None, None, pause=1.0, do=[("scene", "card", "¡A JUGAR!", "cyan", ["vaso_vacio", "carafeliz", "auto"])], chap="Juego: ¿cómo está?"),
       E("tula", "¡Juguemos! Yo te muestro un dibujo y tú me dices cómo está.", pause=0.4),
       E("pipo", "¡Responde fuerte, fuerte! ¡Pío!", pause=0.5)]
for key, side, lab, cn, hdr, q, a, who in (
        ("vaso", "B", "¡VACÍO!", "orange", "¿LLENO O VACÍO?", "¿Este vaso está lleno o vacío?", "¡Vacío! No tiene agua.", "pipo"),
        ("pos", "A", "¡ARRIBA!", "yellow", "¿ARRIBA O ABAJO?", "¿La pelota está arriba o abajo?", "¡Arriba! ¡Muy alto!", "tula"),
        ("dia", "B", "¡NOCHE!", "purple", "¿DÍA O NOCHE?", "¿Es de día o es de noche?", "¡Es de noche! Mira la luna.", "pipo"),
        ("cara", "A", "¡FELIZ!", "yellow", "¿FELIZ O TRISTE?", "¿Esta carita está feliz o triste?", "¡Feliz! ¡Qué linda sonrisa!", "tula"),
        ("temp", "A", "¡CALIENTE!", "red", "¿CALIENTE O FRÍO?", "¿El chocolate está caliente o frío?", "¡Caliente! Hay que soplar.", "pipo"),
        ("puerta", "B", "¡CERRADA!", "red", "¿ABIERTA O CERRADA?", "¿La puerta está abierta o cerrada?", "¡Cerrada! ¡Muy bien!", "tula")):
    ONE += [E(None, None, pause=0.6, do=[("scene", "opp1", key, side, lab, cn, hdr)]),
            E(who, q, pause=3.2, do=[("qmark", 1)]),
            E(other(who), a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

# Juego con el cuerpo
CMDS = [("¡ARRIBA!", "yellow", "up", "pipo", "¡Manos arriba! ¡Bien alto!", 1.8),
        ("¡ABAJO!", "green", "down", "tula", "¡Manos abajo! Toca el piso.", 1.8),
        ("¡GRANDE!", "orange", None, "pipo", "¡Hazte grande, grande, como un gigante!", 2.0),
        ("¡PEQUEÑO!", "cyan", None, "tula", "¡Ahora pequeñito, como una bolita!", 2.0),
        ("¡RÁPIDO!", "red", None, "pipo", "¡Corre en tu lugar! ¡Rápido, rápido!", 2.6),
        ("¡LENTO!", "purple", None, "tula", "¡Ahora camina lento… muy lento!", 2.6),
        ("¡ABRE!", "green", None, "pipo", "¡Abre bien la boca, grande!", 1.8),
        ("¡CIERRA!", "pink", None, "tula", "¡Y ciérrala! ¡Boca cerrada!", 1.8)]
BODY = [E(None, None, pause=0.6, do=[("scene", "cmd", [(a, b, c) for a, b, c, *_ in CMDS])], chap="Juego: ¡muévete con nosotros!"),
        E("tula", "¡Ahora, a moverse! Haz lo que te decimos. ¿Listo?", pause=0.8)]
for i, (_, _, _, who, txt, p) in enumerate(CMDS, 1):
    BODY.append(E(who, txt, pause=p, do=[("rpop", i)]))
BODY.append(E("pipo", "¡Muy bien! ¡Qué bien te mueves!", pause=1.5, do=[("confetti", 1)]))

# Juego: ¿cuál es diferente? (grande / pequeño / triste)
ODD = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁL ES DIFERENTE?", "pink")], chap="Juego: ¿cuál es diferente?"),
       E("pipo", "¡Uno de estos es diferente! ¿Lo encuentras?", pause=0.5)]
for items, oi, lab, cn, q, a, who in (
        ([("pelota", None, 0.62), ("pelota", None, 0.62), ("pelota", None, 0.62), ("pelota", None, 1.2)], 3, "¡LA GRANDE!", "orange",
         "Pelotas pequeñas… y una diferente. ¿Cuál es la grande?", "¡Esta! La pelota grande.", "tula"),
        ([("globo", None, 1.0), ("globo", None, 0.5), ("globo", None, 1.0), ("globo", None, 1.0)], 1, "¡EL PEQUEÑO!", "cyan",
         "Ahora, ¿cuál globo es pequeño?", "¡Este! El globo pequeño.", "pipo"),
        ([("carafeliz", None, 1.0), ("carafeliz", None, 1.0), ("caratriste", None, 1.0), ("carafeliz", None, 1.0)], 2, "¡LA TRISTE!", "blue",
         "¿Qué carita está triste?", "¡Esta! Vamos a darle un abrazo para que esté feliz.", "tula")):
    ODD += [E(None, None, pause=0.6, do=[("scene", "odd", items, oi, lab, cn)]),
            E(who, q, pause=3.4, do=[("qmark", 1)]),
            E(other(who), a, pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

# Juego: ¿cuántos hay?
QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "orange")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡Ahora a contar! Cuenta con tu dedito.", pause=0.5)]
for n, ok, q, a, who in ((3, "auto", "¿Cuántos autos rápidos hay?", "¡Tres! ¡Hay tres autos rápidos!", "pipo"),
                         (5, "caracol", "¿Cuántos caracoles lentos ves?", "¡Cinco! ¡Cinco caracoles lentos!", "tula"),
                         (4, "helado", "¿Cuántos helados fríos hay?", "¡Cuatro! ¡Cuatro helados!", "pipo")):
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "quiz", n, ok)]),
             E(who, q, pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), a, pause=0.9, do=[("qmark", 0), ("numeral", n)])]

# Juego: ¿de qué color es?
COLOR = [E(None, None, pause=1.0, do=[("scene", "card", "¿DE QUÉ COLOR ES?", "yellow")], chap="Juego: ¿de qué color es?"),
         E("pipo", "¡Estos dibujos perdieron su color! ¿Nos ayudas a pintarlos?", pause=0.5)]
for ok, lab, cn, q, a, who in (("sol", "¡AMARILLO!", "yellow", "¿De qué color es el sol?", "¡Amarillo! ¡El sol es amarillo!", "tula"),
                               ("auto", "¡ROJO!", "red", "¿De qué color es el auto rápido?", "¡Rojo! ¡Un auto rojo!", "pipo"),
                               ("caracol", "¡MORADO!", "purple", "¿Y la casita del caracol? ¿De qué color es?", "¡Morada! ¡Qué linda casita!", "tula")):
    COLOR += [E(None, None, pause=0.6, do=[("scene", "fruit", ok, "color", lab, cn)]),
              E(who, q, pause=3.2, do=[("qmark", 1)]),
              E(other(who), a, pause=0.9, do=[("qmark", 0), ("reveal", 1)])]

# Repaso
ORDER = ["tam", "pos", "dia", "vaso", "puerta", "temp", "vel", "cara"]
REVIEW = [E(None, None, pause=1.0, do=[("scene", "oreview", [(k, OPP[k][0], OPP[k][1]) for k in ORDER])], chap="Repaso: ¡todos los opuestos!"),
          E("tula", "¡Repasemos todos los opuestos! Yo digo uno y Pipo dice el contrario.", pause=0.4),
          E("pipo", "¡Y tú lo dices con nosotros!", pause=0.8)]
for i, k in enumerate(ORDER, 1):
    A, B = OPP[k][0], OPP[k][1]
    REVIEW += [E("tula", f"¡{A.capitalize()}!", pause=0.9, do=[("rpop", i)]),
               E("pipo", f"¡{B.capitalize()}!", pause=1.1, do=[("pop", i)])]
REVIEW += [E("tula", "¡Bravo! ¡Ya conoces un montón de opuestos!", pause=2.5, do=[("confetti", 1)])]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "Una última pregunta: yo soy pequeño… ¿y Tula es…?", pause=2.6),
    E("tula", "¡Grande! Y Pipo vuela arriba, en el cielo… y yo camino abajo, en el pasto."),
    E("pipo", "Hoy, en tu casa, busca opuestos con tu familia: algo grande y algo pequeño, algo lleno y algo vacío.", pause=1.2),
    E("tula", "Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    ev += opp_segment("tam", "Grande y pequeño")
    ev += opp_segment("pos", "Arriba y abajo")
    ev += opp_segment("dia", "Día y noche")
    ev += dance("pipo", "¡Ya aprendimos tres opuestos! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    ev += opp_segment("vaso", "Lleno y vacío")
    ev += opp_segment("puerta", "Abierta y cerrada")
    ev += opp_segment("temp", "Caliente y frío")
    ev += opp_segment("vel", "Rápido y lento")
    ev += opp_segment("cara", "Feliz y triste")
    ev += ONE + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + BODY + ODD + QUIZ + COLOR + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
