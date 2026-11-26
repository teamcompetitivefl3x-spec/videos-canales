# Pulso IA · Short: entrenaron una IA en el espacio + FCC aprueba 1 millón de satélites de SpaceX (25-26 nov. 2026). "at" = índice de frase.
CHAPTERS = ["SHORT"]

SCENES = [
 dict(at=0, type="headline", icon="robot", kicker="ESTA SEMANA", text="Entrenaron una *IA*… en el *espacio*", size=104),
 dict(at=1, type="headline", kicker="ADASPACE · CHINA", text="Satélite *Libra*", size=120, sub="entrenó el modelo Qwen3-32B de Alibaba"),
 dict(at=1.55, type="headline", icon="bolt", text="Mientras daba vueltas a la *Tierra*", size=100),
 dict(at=2, type="stats", title="EN UNA SOLA ÓRBITA", cards=[("45 min 33 s", "de entrenamiento seguido", "accent"), ("32.000 M", "parámetros del modelo", "teal")], stagger=1.6),
 dict(at=3, type="headline", icon="warning", kicker="SEGÚN LA EMPRESA", text="*«Récord mundial»*", size=120, sub="dice que lo verificó un instituto del gobierno chino"),
 dict(at=4, type="number", value=2800, kicker="EL PLAN", label="satélites dedicados a la *IA*"),
 dict(at=5, type="headline", kicker="25 DE NOVIEMBRE · EE. UU.", text="La *FCC* aprobó el plan de *SpaceX*", size=100, sub="aprobación condicional"),
 dict(at=5.5, type="headline", text="Hasta *1 millón* de satélites", size=120, sub="con centros de datos de IA en órbita"),
 dict(at=6, type="compare", title="Se opusieron", left=("competidor de Starlink", "Amazon", "red"), right=("por la basura espacial", "Astrónomos", "accent"), stagger=1.2),
 dict(at=7, type="stats", title="LO QUE FALTA", cards=[("7 años", "para lanzar el primer satélite", "blue"), ("¿Cómo enfriar?", "los chips en el espacio, sin resolver", "red")], stagger=2.4),
 dict(at=8, type="headline", text="La carrera de la IA ya no es solo en la *Tierra*", size=100),
 dict(at=9, type="headline", icon="chat", text="¿Pondrías un centro de datos en *órbita*?", size=96),
 dict(at=10, type="headline", text="Más en *Pulso IA*", size=100),
]

SHORTS = [
 dict(name="short_ia_espacio", title="La IA se va al espacio", sents=list(range(11)),
      end_text="Suscríbete a *Pulso IA*", end_button="SUSCRÍBETE"),
]
