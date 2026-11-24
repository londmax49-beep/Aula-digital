import os
import sqlite3
import random
import unicodedata
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("AULA_SECRET", "aula-digital-secret-2026")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aula_digital.db")

GRADOS = [
    "Secundaria 1", "Secundaria 2", "Secundaria 3",
    "Preparatoria 1", "Preparatoria 2", "Preparatoria 3",
    "Preparatoria 4", "Preparatoria 5", "Preparatoria 6"
]

MATERIAS = {
    "matematicas": "Matemáticas",
    "lengua": "Lengua y Comunicación"
}

# ==========================================================
# TEMAS: 15 NIVELES POR MATERIA
# ==========================================================

MATEMATICAS = [
    ("Números y operaciones", "Los números permiten representar cantidades. Las operaciones básicas son suma, resta, multiplicación y división.", "Ejemplo: 12 + 8 = 20; 20 - 5 = 15."),
    ("Fracciones y decimales", "Las fracciones representan partes de un todo y los decimales expresan cantidades con partes de una unidad.", "Ejemplo: 1/2 = 0.5."),
    ("Porcentajes y proporciones", "Los porcentajes expresan cantidades de cada cien. Las proporciones relacionan cantidades de forma equivalente.", "Ejemplo: 25% de 200 = 50."),
    ("Potencias y raíces", "Una potencia representa una multiplicación repetida. La raíz permite encontrar el número que produjo una potencia.", "Ejemplo: 4² = 16 y √16 = 4."),
    ("Álgebra y expresiones", "Las letras representan valores que pueden ser desconocidos o cambiar. Las expresiones combinan números, letras y operaciones.", "Ejemplo: 3x + 5."),
    ("Ecuaciones de primer grado", "Una ecuación establece una igualdad. Se realizan operaciones inversas para encontrar el valor de la incógnita.", "Ejemplo: x + 7 = 15; x = 8."),
    ("Plano cartesiano y coordenadas", "El plano cartesiano permite ubicar puntos mediante coordenadas (x,y).", "Ejemplo: (3,2) significa avanzar 3 en x y 2 en y."),
    ("Perímetros y áreas", "El perímetro es la suma de los lados. El área mide la superficie de una figura.", "Ejemplo: área de rectángulo = base × altura."),
    ("Volumen y geometría", "El volumen mide el espacio que ocupa un cuerpo. La geometría estudia las figuras y sus propiedades.", "Ejemplo: volumen de cubo = lado³."),
    ("Estadística", "La estadística organiza y analiza datos. La media, mediana y moda ayudan a describirlos.", "Ejemplo: media de 2, 4 y 6 = 4."),
    ("Probabilidad", "La probabilidad mide qué tan posible es que ocurra un evento.", "Ejemplo: al lanzar una moneda, la probabilidad de cara es 1/2."),
    ("Sistemas de ecuaciones", "Un sistema reúne dos o más ecuaciones y busca valores que satisfagan todas al mismo tiempo.", "Ejemplo: x + y = 7; x - y = 1."),
    ("Funciones lineales y cuadráticas", "Una función relaciona una entrada con una salida. Las lineales forman rectas y las cuadráticas incluyen términos al cuadrado.", "Ejemplo: f(x)=2x+3; y=x²."),
    ("Factorización y sucesiones", "Factorizar permite expresar una operación como producto. Una sucesión sigue una regla de formación.", "Ejemplo: x²-9=(x-3)(x+3); 2,4,6,8..."),
    ("Trigonometría y matemáticas financieras", "La trigonometría relaciona lados y ángulos. Las matemáticas financieras ayudan a calcular costos, descuentos e intereses.", "Ejemplo: en un triángulo rectángulo se usa a²+b²=c².")
]

LENGUA = [
    ("Comunicación y sus elementos", "La comunicación transmite información. Sus elementos incluyen emisor, receptor, mensaje, canal y contexto.", "Ejemplo: una persona envía un mensaje a otra por teléfono."),
    ("Sustantivos y adjetivos", "Los sustantivos nombran seres, objetos, lugares e ideas. Los adjetivos describen sus características.", "Ejemplo: el sustantivo casa y el adjetivo grande."),
    ("Verbos y adverbios", "Los verbos expresan acciones, estados o procesos. Los adverbios modifican verbos, adjetivos u otros adverbios.", "Ejemplo: Ella camina lentamente."),
    ("Pronombres y oraciones", "Los pronombres sustituyen nombres. Las oraciones organizan palabras para expresar ideas completas.", "Ejemplo: Juan estudia. Él estudia."),
    ("Sujeto y predicado", "El sujeto indica de quién se habla y el predicado expresa lo que se dice del sujeto.", "Ejemplo: María (sujeto) estudia matemáticas (predicado)."),
    ("Ortografía y acentuación", "La ortografía establece reglas para escribir. La acentuación indica dónde se coloca la tilde según las reglas.", "Ejemplo: canción, árbol, rápido."),
    ("Puntuación y conectores", "Los signos de puntuación organizan el texto. Los conectores relacionan ideas.", "Ejemplo: Estudié; por lo tanto, aprobé."),
    ("Sinónimos y antónimos", "Los sinónimos tienen significados similares y los antónimos expresan significados opuestos.", "Ejemplo: alegre y contento; alto y bajo."),
    ("Comprensión lectora y resumen", "Comprender implica interpretar un texto. Un resumen presenta las ideas esenciales con palabras propias.", "Ejemplo: identificar el tema y explicar sus ideas principales."),
    ("Narración y descripción", "La narración cuenta hechos. La descripción explica características de personas, objetos, lugares o situaciones.", "Ejemplo: narrar un viaje y describir el paisaje."),
    ("Textos informativos y argumentativos", "Los textos informativos presentan datos. Los argumentativos defienden una postura mediante razones.", "Ejemplo: una noticia informa y un ensayo de opinión argumenta."),
    ("Figuras literarias y poesía", "Las figuras literarias enriquecen el lenguaje. La poesía puede utilizar versos, ritmo, imágenes y emociones.", "Ejemplo: metáfora, comparación y personificación."),
    ("Investigación y fuentes", "Investigar requiere buscar, evaluar y comparar información de fuentes confiables.", "Ejemplo: contrastar un libro y un artículo especializado."),
    ("Citas, referencias y ensayo", "Las citas reconocen ideas ajenas. Las referencias indican las fuentes. Un ensayo desarrolla una reflexión.", "Ejemplo: presentar una tesis y justificarla con argumentos."),
    ("Reseña, debate y argumentación", "Una reseña evalúa una obra. El debate intercambia posturas y argumentos de manera respetuosa.", "Ejemplo: defender una opinión utilizando evidencias.")
]


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def inicializar_db():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            escolaridad TEXT NOT NULL,
            fecha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS progreso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            materia TEXT NOT NULL,
            nivel INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            UNIQUE(usuario_id, materia, nivel)
        );

        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            calificacion INTEGER NOT NULL,
            aprobado INTEGER NOT NULL,
            fecha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS juegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            juego TEXT NOT NULL,
            puntos INTEGER NOT NULL,
            fecha TEXT NOT NULL
        );
        """)


def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper
@app.after_request
def evitar_cache_paginas_protegidas(response):
    if "usuario_id" in session and response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


def grado_actual():
    return session.get("escolaridad", GRADOS[0])


def obtener_temas(materia):
    if materia == "matematicas":
        return MATEMATICAS
    if materia == "lengua":
        return LENGUA
    return None


def crear_pregunta(pregunta, correcta, distractores):
    opciones = list(dict.fromkeys(
        [str(correcta)] + [str(x) for x in distractores]
    ))

    while len(opciones) < 4:
        opciones.append("Ninguna de las anteriores")

    opciones = opciones[:4]
    random.shuffle(opciones)

    return {
        "pregunta": pregunta,
        "opciones": opciones,
        "correcta": str(correcta)
    }


# ==========================================================
# BANCO DE MATEMÁTICAS ADAPTADO POR ESCOLARIDAD
# ==========================================================

def banco_matematicas(grado=None):
    grado = grado or grado_actual()
    g = GRADOS.index(grado) + 1 if grado in GRADOS else 1
    banco = []

    if g <= 3:
        for i in range(1, 51):
            a = g * 10 + i
            b = i + 2

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} + {b}?", a + b,
                [a + b + 2, a + b - 2, a * b]
            ))

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} - {b}?", a - b,
                [a - b + 3, a + b, a - b - 2]
            ))

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} × {b}?", a * b,
                [a + b, a * b + 5, a * b - 3]
            ))

            if b != 0:
                banco.append(crear_pregunta(
                    f"¿Cuánto es {a*b} ÷ {b}?", a,
                    [a + 2, a - 1, b]
                ))

    elif g <= 6:
        for i in range(1, 51):
            a = i + g
            b = (i % 9) + 2

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} × {b}?", a * b,
                [a + b, a * b + 4, a * b - 5]
            ))

            banco.append(crear_pregunta(
                f"¿Cuánto es {a}²?", a * a,
                [a * 2, a * a + 3, a * a - 4]
            ))

            porcentaje = (i % 5 + 1) * 10
            cantidad = (i + 5) * 10
            resultado = cantidad * porcentaje // 100

            banco.append(crear_pregunta(
                f"¿Cuánto es el {porcentaje}% de {cantidad}?",
                resultado,
                [resultado + 2, resultado + 5, resultado - 1]
            ))

    else:
        for i in range(1, 51):
            x = i + g
            a = (g + i % 5) + 1
            resultado = a * x

            banco.append(crear_pregunta(
                f"Resuelve {a}x = {resultado}. ¿Cuánto vale x?",
                x, [x + 1, x - 2, resultado]
            ))

            n = i + g

            banco.append(crear_pregunta(
                f"¿Cuánto es {n}²?", n * n,
                [n * 2, n * n + 3, n * n - 4]
            ))

            banco.append(crear_pregunta(
                f"Si f(x)=2x+{g}, ¿cuánto vale f({i})?",
                2 * i + g,
                [i + g, 2 * i, 2 * i + g + 2]
            ))

            banco.append(crear_pregunta(
                f"¿Cuál es la raíz cuadrada de {n*n}?",
                n, [n + 2, n - 1, n * n]
            ))

    return banco


# ==========================================================
# BANCO DE LENGUA
# ==========================================================

def banco_lengua(grado=None):
    grado = grado or grado_actual()
    g = GRADOS.index(grado) + 1 if grado in GRADOS else 1

    secundaria = [
        ("¿Cuál palabra es un sustantivo?", "escuela", ["correr", "rápidamente", "azul"]),
        ("¿Cuál palabra es un verbo?", "escribir", ["libro", "bonito", "mesa"]),
        ("¿Cuál es un sinónimo de alegre?", "contento", ["triste", "enojado", "preocupado"]),
        ("¿Cuál es el antónimo de alto?", "bajo", ["grande", "largo", "ancho"]),
        ("¿Qué signo indica una pregunta?", "¿ ?", ["¡ !", ".", ";"]),
        ("¿Cuál palabra es un adjetivo?", "hermoso", ["correr", "casa", "ayer"]),
        ("¿Qué es el sujeto?", "Quien realiza o protagoniza la acción", ["Un signo", "El final", "Una palabra de enlace"]),
        ("¿Para qué sirve un resumen?", "Presentar las ideas principales", ["Copiar todo", "Cambiar el tema", "Inventar datos"]),
        ("¿Cuál es un conector de consecuencia?", "por lo tanto", ["aunque", "mientras", "sin"]),
        ("¿Qué es una narración?", "Un relato de acontecimientos", ["Una lista", "Una operación", "Una señal"]),
        ("¿Cuál palabra lleva tilde?", "canción", ["mesa", "casa", "papel"]),
        ("¿Qué signo termina una oración?", "Punto", ["Coma", "Guion", "Paréntesis"]),
        ("¿Qué es un antónimo?", "Una palabra de significado opuesto", ["Un nombre", "Un verbo", "Una sílaba"]),
        ("¿Qué es una idea principal?", "La información más importante del texto", ["Un detalle", "El autor", "Una palabra"]),
        ("¿Cuál es una fuente de información?", "Un libro", ["Un rumor", "Una suposición", "Un comentario sin datos"]),
        ("¿Qué es un adverbio?", "Una palabra que modifica a otras palabras", ["Un nombre propio", "Un signo", "Una consonante"]),
        ("¿Qué es una descripción?", "Explicar características de algo o alguien", ["Una operación", "Un debate", "Una suma"]),
        ("¿Para qué sirve la coma?", "Separar elementos y organizar ideas", ["Cerrar todo texto", "Indicar pregunta", "Sustituir letras"]),
        ("¿Qué es un texto informativo?", "Un texto que presenta información sobre un tema", ["Una canción solamente", "Una operación", "Una lista de nombres"]),
        ("¿Qué es un personaje?", "Quien participa en una historia", ["El signo", "El título", "El párrafo"])
    ]

    preparatoria = [
        ("¿Qué caracteriza a un texto argumentativo?", "Defiende una postura mediante razones", ["Enumera objetos", "Solo presenta diálogos", "No tiene propósito"]),
        ("¿Qué es la tesis?", "La postura principal que se defiende", ["Una cita", "Un personaje", "Una descripción"]),
        ("¿Qué es una paráfrasis?", "Explicar una idea con palabras propias", ["Copiar", "Inventar", "Eliminar la idea"]),
        ("¿Qué es una falacia?", "Un razonamiento engañoso o incorrecto", ["Una fuente científica", "Una conclusión correcta", "Una descripción"]),
        ("¿Cuál es una fuente confiable?", "Una fuente verificable y con autoría identificable", ["Una publicación anónima", "Un rumor", "Una cadena sin referencias"]),
        ("¿Qué función tiene la conclusión?", "Cerrar y sintetizar las ideas principales", ["Introducir personajes", "Cambiar el tema", "Repetir el título"]),
        ("¿Qué es una metáfora?", "Una relación figurada entre elementos", ["Una instrucción", "Una pregunta", "Una enumeración"]),
        ("¿Qué es una reseña crítica?", "Una descripción y valoración fundamentada de una obra", ["Una copia", "Una lista sin opinión", "Una noticia sin fuentes"]),
        ("¿Para qué se utiliza un ensayo?", "Para desarrollar una reflexión y postura", ["Registrar fechas", "Escribir diálogos", "Hacer operaciones"]),
        ("¿Qué ayuda a detectar noticias falsas?", "Verificar autor, fecha y fuentes", ["Compartir", "Leer solo el título", "Ignorar evidencias"]),
        ("¿Qué es un argumento?", "Una razón que respalda una postura", ["Una palabra", "Un título", "Una ilustración"]),
        ("¿Qué es una cita?", "La reproducción o referencia de palabras de una fuente", ["Un dato inventado", "Un resumen sin fuente", "Una opinión"]),
        ("¿Cuál es el propósito de un debate?", "Intercambiar y evaluar argumentos", ["Imponer sin escuchar", "Evitar información", "Repetir"]),
        ("¿Qué es la coherencia?", "La conexión lógica entre ideas", ["El tamaño de letra", "Una falta", "El número de páginas"]),
        ("¿Qué es un texto expositivo?", "Un texto que explica o informa sobre un tema", ["Un texto sin ideas", "Una lista de personajes", "Un diálogo teatral"]),
        ("¿Qué es la objetividad?", "Presentar información basada en hechos", ["Inventar datos", "Ocultar fuentes", "Cambiar resultados"]),
        ("¿Qué es una bibliografía?", "Una lista de fuentes consultadas", ["Un personaje", "Una opinión", "Un resumen"]),
        ("¿Qué es la denotación?", "El significado literal de una palabra", ["Una metáfora", "Una rima", "Una exageración"]),
        ("¿Qué es la connotación?", "El significado asociado o figurado", ["Una suma", "Una regla ortográfica", "Una fecha"]),
        ("¿Qué es una hipótesis?", "Una explicación provisional que puede comprobarse", ["Un dato final", "Una cita", "Una conclusión obligatoria"])
    ]

    lista = secundaria if g <= 3 else preparatoria
    rotacion = (g * 3) % len(lista)
    lista = lista[rotacion:] + lista[:rotacion]

    return [
        crear_pregunta(p, c, d)
        for p, c, d in lista
    ]


def obtener_banco_completo(grado=None):
    grado = grado or grado_actual()
    return banco_matematicas(grado), banco_lengua(grado)


def generar_examen_completo():
    matematicas, lengua = obtener_banco_completo()

    examen = []

    for p in random.sample(matematicas, 10):
        examen.append({
            "materia": "Matemáticas",
            "pregunta": p["pregunta"],
            "opciones": p["opciones"],
            "correcta": p["correcta"]
        })

    for p in random.sample(lengua, 10):
        examen.append({
            "materia": "Lengua y Comunicación",
            "pregunta": p["pregunta"],
            "opciones": p["opciones"],
            "correcta": p["correcta"]
        })

    return random.sample(examen, len(examen))


# ==========================================================
# EJERCICIO FINAL DE CADA NIVEL
# ==========================================================

def generar_ejercicio_final(materia, nivel, grado):
    g = GRADOS.index(grado) + 1 if grado in GRADOS else 1

    if materia == "matematicas":
        if g <= 3:
            a = nivel + g + 5
            b = nivel + 2

            if nivel <= 5:
                correcta = a + b
                pregunta = f"Ejercicio: calcula {a} + {b}."
            elif nivel <= 10:
                correcta = a * b
                pregunta = f"Ejercicio: calcula {a} × {b}."
            else:
                correcta = a * b - b
                pregunta = f"Ejercicio: calcula ({a} × {b}) - {b}."

        elif g <= 6:
            a = nivel + g + 3
            b = nivel + 2

            if nivel <= 5:
                correcta = a * b
                pregunta = f"Resuelve el siguiente problema: {a} × {b}."
            elif nivel <= 10:
                correcta = a * a - b
                pregunta = f"Calcula {a}² - {b}."
            else:
                correcta = a * 3 + b
                pregunta = f"Calcula 3({a}) + {b}."

        else:
            a = nivel + g
            b = nivel + 2

            if nivel <= 5:
                correcta = a + b * 2
                pregunta = f"Resuelve: {a} + 2({b})."
            elif nivel <= 10:
                correcta = a * a - b * b
                pregunta = f"Calcula {a}² - {b}²."
            else:
                correcta = a * 2 + b
                pregunta = f"Si x = {a}, calcula 2x + {b}."

        return {
            "pregunta": pregunta,
            "correcta": str(correcta),
            "tipo": "numero"
        }

    ejercicios = [
        {"pregunta": "Escribe un sinónimo de la palabra alegre.", "correcta": "contento"},
        {"pregunta": "Escribe el antónimo de la palabra grande.", "correcta": "pequeño"},
        {"pregunta": "¿Cuál es el verbo en la oración: María estudia diariamente?", "correcta": "estudia"},
        {"pregunta": "Escribe el sustantivo de la oración: El perro corre.", "correcta": "perro"},
        {"pregunta": "¿Qué signo se utiliza para cerrar una oración?", "correcta": "."},
        {"pregunta": "Escribe un conector de consecuencia.", "correcta": "por lo tanto"},
        {"pregunta": "¿Cómo se llama el mensaje principal de un texto?", "correcta": "idea principal"},
        {"pregunta": "¿Qué tipo de texto defiende una opinión con argumentos?", "correcta": "argumentativo"},
        {"pregunta": "¿Cómo se llama explicar una idea con tus propias palabras?", "correcta": "parafrasis"},
        {"pregunta": "¿Qué apartado de un trabajo presenta el cierre de las ideas?", "correcta": "conclusion"},
        {"pregunta": "¿Cómo se llama la lista de fuentes consultadas?", "correcta": "bibliografia"},
        {"pregunta": "¿Qué recurso permite respaldar una opinión con razones?", "correcta": "argumento"},
        {"pregunta": "¿Cómo se llama revisar la veracidad de una información?", "correcta": "verificacion"},
        {"pregunta": "¿Qué tipo de significado es el literal de una palabra?", "correcta": "denotacion"},
        {"pregunta": "¿Cómo se llama la postura principal que se defiende en un ensayo?", "correcta": "tesis"}
    ]

    ejercicio = ejercicios[nivel - 1].copy()
    ejercicio["tipo"] = "texto"
    return ejercicio


# ==========================================================
# INICIO, REGISTRO Y LOGIN
# ==========================================================

@app.route("/")
def inicio():
    if "usuario_id" in session:
        return redirect(url_for("panel"))
    return render_template("inicio.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        escolaridad = request.form.get("escolaridad", "")

        if not nombre or not correo or not password:
            flash("Completa todos los campos.", "error")
            return render_template("registro.html", grados=GRADOS)

        if escolaridad not in GRADOS:
            flash("Selecciona tu grado escolar.", "error")
            return render_template("registro.html", grados=GRADOS)

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return render_template("registro.html", grados=GRADOS)

        try:
            with conectar() as con:
                con.execute("""
                    INSERT INTO usuarios(nombre, correo, password, escolaridad, fecha)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nombre, correo,
                    generate_password_hash(password),
                    escolaridad,
                    datetime.now().isoformat()
                ))

            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Este correo ya está registrado.", "error")

    return render_template("registro.html", grados=GRADOS)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")

        with conectar() as con:
            usuario = con.execute(
                "SELECT * FROM usuarios WHERE correo = ?",
                (correo,)
            ).fetchone()

        if usuario and check_password_hash(usuario["password"], password):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            session["escolaridad"] = usuario["escolaridad"]
            return redirect(url_for("panel"))

        flash("Correo o contraseña incorrectos.", "error")

    return render_template("login.html")


@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("inicio"))


# ==========================================================
# PANEL
# ==========================================================

@app.route("/panel")
@login_requerido
def panel():
    usuario_id = session["usuario_id"]

    with conectar() as con:
        progreso = con.execute("""
            SELECT materia, COUNT(*) AS total
            FROM progreso
            WHERE usuario_id=?
            AND nivel BETWEEN 1 AND 15
            GROUP BY materia
        """, (usuario_id,)).fetchall()

        examen = con.execute("""
            SELECT * FROM examenes
            WHERE usuario_id=?
            ORDER BY id DESC LIMIT 1
        """, (usuario_id,)).fetchone()

    avances = {"matematicas": 0, "lengua": 0}

    for p in progreso:
        if p["materia"] in avances:
            avances[p["materia"]] = p["total"]

    return render_template("panel.html", avances=avances, examen=examen)


# ==========================================================
# MATERIAS Y NIVELES
# ==========================================================

@app.route("/materia/<materia>")
@login_requerido
def materia(materia):
    temas = obtener_temas(materia)

    if temas is None:
        return redirect(url_for("panel"))

    with conectar() as con:
        completados = con.execute("""
            SELECT nivel FROM progreso
            WHERE usuario_id=? AND materia=?
            AND nivel BETWEEN 1 AND 15
        """, (session["usuario_id"], materia)).fetchall()

    niveles_completados = [r["nivel"] for r in completados]

    return render_template(
        "materia.html",
        materia=materia,
        nombre_materia=MATERIAS[materia],
        temas=temas,
        completados=niveles_completados
    )


@app.route("/nivel/<materia>/<int:nivel>", methods=["GET", "POST"])
@login_requerido
def nivel(materia, nivel):
    temas = obtener_temas(materia)

    if temas is None or not 1 <= nivel <= 15:
        return redirect(url_for("panel"))

    usuario_id = session["usuario_id"]

    with conectar() as con:
        if nivel > 1:
            previo = con.execute("""
                SELECT 1 FROM progreso
                WHERE usuario_id=? AND materia=? AND nivel=?
            """, (usuario_id, materia, nivel-1)).fetchone()

            if not previo:
                flash("Primero debes completar el nivel anterior.", "warning")
                return redirect(url_for("materia", materia=materia))

        completado = con.execute("""
            SELECT 1 FROM progreso
            WHERE usuario_id=? AND materia=? AND nivel=?
        """, (usuario_id, materia, nivel)).fetchone()

    if completado:
        flash("Ya completaste este nivel.", "success")
        return redirect(url_for("materia", materia=materia))

    titulo, explicacion, ejemplo = temas[nivel - 1]
    llave = f"actividad_{materia}_{nivel}"

    if request.method == "GET" or llave not in session:
        banco = banco_matematicas() if materia == "matematicas" else banco_lengua()
        preguntas = random.sample(banco, min(4, len(banco)))
        ejercicio = generar_ejercicio_final(materia, nivel, grado_actual())

        session[llave] = {
            "preguntas": preguntas,
            "ejercicio": ejercicio,
            "preguntas_completadas": False
        }

    actividad = session.get(llave)

    if not actividad:
        return redirect(url_for("nivel", materia=materia, nivel=nivel))

    mensaje = None

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "preguntas":
            respuestas_correctas = 0

            for i, pregunta in enumerate(actividad["preguntas"]):
                respuesta = request.form.get(f"q{i}", "")
                if respuesta == pregunta["correcta"]:
                    respuestas_correctas += 1

            if respuestas_correctas == 4:
                actividad["preguntas_completadas"] = True
                mensaje = "¡Excelente! Respondiste correctamente las 4 preguntas. Ahora resuelve el ejercicio final."
            else:
                mensaje = f"Obtuviste {respuestas_correctas} de 4 respuestas correctas. Revisa el tema e inténtalo nuevamente."

            session[llave] = actividad

        elif accion == "ejercicio":
            if not actividad.get("preguntas_completadas"):
                mensaje = "Primero debes contestar correctamente las 4 preguntas."
            else:
                respuesta = request.form.get("ejercicio_respuesta", "").strip().lower()
                correcta = str(actividad["ejercicio"]["correcta"]).strip().lower()

                respuesta = "".join(
                    c for c in unicodedata.normalize("NFD", respuesta)
                    if unicodedata.category(c) != "Mn"
                )
                correcta = "".join(
                    c for c in unicodedata.normalize("NFD", correcta)
                    if unicodedata.category(c) != "Mn"
                )

                if respuesta == correcta:
                    with conectar() as con:
                        con.execute("""
                            INSERT OR IGNORE INTO progreso
                            (usuario_id, materia, nivel, fecha)
                            VALUES (?, ?, ?, ?)
                        """, (
                            usuario_id, materia, nivel,
                            datetime.now().isoformat()
                        ))

                    session.pop(llave, None)
                    flash("¡Felicidades! Completaste las 4 preguntas y el ejercicio.", "success")

                    if nivel < 15:
                        return redirect(url_for("nivel", materia=materia, nivel=nivel+1))

                    return redirect(url_for("materia", materia=materia))

                mensaje = "Respuesta incorrecta. Revisa el tema e inténtalo nuevamente."

    return render_template(
        "nivel.html",
        materia=materia,
        nivel=nivel,
        titulo=titulo,
        explicacion=explicacion,
        ejemplo=ejemplo,
        preguntas=actividad["preguntas"],
        ejercicio=actividad["ejercicio"],
        preguntas_completadas=actividad.get("preguntas_completadas", False),
        nombre_materia=MATERIAS[materia],
        mensaje=mensaje
    )


# ==========================================================
# ZONA GAMER
# ==========================================================

@app.route("/juegos")
@login_requerido
def juegos():
    return render_template("juegos.html")

@app.route("/juegos_lengua")
@login_requerido
def juegos_lengua():
    return render_template("juegos_lengua.html")    


@app.route("/api/banco_juegos")
@login_requerido
def api_banco_juegos():
    matematicas, lengua = obtener_banco_completo()

    return jsonify({
        "matematicas": matematicas,
        "lengua": lengua,
        "grado": grado_actual()
    })


@app.route("/api/guardar_juego", methods=["POST"])
@login_requerido
def guardar_juego():
    data = request.get_json(silent=True) or {}

    juegos_validos = {
        "batalla", "tiempo", "racha",
        "verdadero", "palabras", "memoria"
    }

    juego = str(data.get("juego", ""))
    puntos = data.get("puntos", 0)

    if juego not in juegos_validos:
        return jsonify({"ok": False}), 400

    try:
        puntos = max(0, min(int(puntos), 100000))
    except (ValueError, TypeError):
        puntos = 0

    with conectar() as con:
        con.execute("""
            INSERT INTO juegos(usuario_id, juego, puntos, fecha)
            VALUES (?, ?, ?, ?)
        """, (
            session["usuario_id"],
            juego,
            puntos,
            datetime.now().isoformat()
        ))

    return jsonify({"ok": True})


# ==========================================================
# EXAMEN FINAL
# ==========================================================

@app.route("/examen", methods=["GET", "POST"])
@login_requerido
def examen():
    usuario_id = session["usuario_id"]

    with conectar() as con:
        matematicas_completadas = con.execute("""
            SELECT COUNT(*) FROM progreso
            WHERE usuario_id=?
            AND materia='matematicas'
            AND nivel BETWEEN 1 AND 15
        """, (usuario_id,)).fetchone()[0]

        lengua_completados = con.execute("""
            SELECT COUNT(*) FROM progreso
            WHERE usuario_id=?
            AND materia='lengua'
            AND nivel BETWEEN 1 AND 15
        """, (usuario_id,)).fetchone()[0]

    if matematicas_completadas < 15 or lengua_completados < 15:
        flash(
            "Debes completar los 15 niveles de Matemáticas y los 15 de Lengua y Comunicación antes de presentar el examen.",
            "warning"
        )
        return redirect(url_for("panel"))

    if request.method == "GET":
        session["examen_actual"] = generar_examen_completo()

    preguntas = session.get("examen_actual")

    if not preguntas:
        flash("No se pudo generar el examen.", "error")
        return redirect(url_for("panel"))

    if request.method == "POST":
        aciertos = sum(
            1 for i, p in enumerate(preguntas)
            if request.form.get(f"q{i}") == p["correcta"]
        )

        calificacion = aciertos * 5
        aprobado = calificacion >= 70

        with conectar() as con:
            con.execute("""
                INSERT INTO examenes(usuario_id, calificacion, aprobado, fecha)
                VALUES (?, ?, ?, ?)
            """, (
                usuario_id, calificacion, int(aprobado),
                datetime.now().isoformat()
            ))

        session.pop("examen_actual", None)

        return render_template(
            "resultado_examen.html",
            calificacion=calificacion,
            aprobado=aprobado
        )

    return render_template("examen.html", preguntas=preguntas)


# ==========================================================
# DIPLOMA
# ==========================================================

@app.route("/diploma")
@login_requerido
def diploma():
    usuario_id = session["usuario_id"]

    with conectar() as con:
        matematicas_completadas = con.execute("""
            SELECT COUNT(*) FROM progreso
            WHERE usuario_id=?
            AND materia='matematicas'
            AND nivel BETWEEN 1 AND 15
        """, (usuario_id,)).fetchone()[0]

        lengua_completados = con.execute("""
            SELECT COUNT(*) FROM progreso
            WHERE usuario_id=?
            AND materia='lengua'
            AND nivel BETWEEN 1 AND 15
        """, (usuario_id,)).fetchone()[0]

        examen = con.execute("""
            SELECT * FROM examenes
            WHERE usuario_id=? AND aprobado=1
            ORDER BY id DESC LIMIT 1
        """, (usuario_id,)).fetchone()

    if matematicas_completadas < 15 or lengua_completados < 15 or not examen:
        flash(
            "Completa los 15 niveles de cada materia y aprueba el examen para obtener tu diploma.",
            "warning"
        )
        return redirect(url_for("panel"))

    return render_template(
        "diploma.html",
        nombre=session["nombre"],
        fecha=datetime.now().strftime("%d/%m/%Y"),
        calificacion=examen["calificacion"]
    )


# ==========================================================
# PROFE ALEX - APOYO EDUCATIVO
# NO DISPONIBLE DURANTE EXAMEN
# ==========================================================

@app.route("/preguntar_alex", methods=["POST"])
@login_requerido
def preguntar_alex():
    if "examen_actual" in session:
        return jsonify({
            "respuesta": "Profe Alex no está disponible durante el examen. Al finalizar podrás consultarme."
        }), 403

    data = request.get_json(silent=True) or {}
    pregunta = str(data.get("pregunta", "")).strip().lower()

    if not pregunta:
        return jsonify({"respuesta": "Escribe una pregunta."})

    grado = grado_actual()

    def normalizar(texto):
        texto = unicodedata.normalize("NFD", str(texto).lower())
        texto = "".join(
            letra for letra in texto
            if unicodedata.category(letra) != "Mn"
        )
        return "".join(
            letra if letra.isalnum() else " "
            for letra in texto
        )

    palabras_vacias = {
        "que", "como", "cual", "cuales", "cuando", "donde",
        "porque", "para", "por", "con", "sin", "una", "uno",
        "unos", "unas", "los", "las", "del", "de", "la",
        "el", "y", "o", "es", "son", "se", "me", "puedes",
        "explica", "explicame", "dime", "quiero", "saber",
        "ayuda", "hacer", "hago", "hace", "sobre"
    }

    palabras = {
        palabra.rstrip("s")
        for palabra in normalizar(pregunta).split()
        if len(palabra) >= 3 and palabra not in palabras_vacias
    }

    materias = [
        ("Matemáticas", MATEMATICAS),
        ("Lengua y Comunicación", LENGUA)
    ]

    mejor_resultado = None
    mejor_puntuacion = 0

    palabras_pregunta = set(normalizar(pregunta).split()) - palabras_vacias

    for nombre_materia, temas in materias:
        for tema in temas:
            titulo, explicacion, ejemplo = tema

            titulo_normalizado = normalizar(titulo)
            explicacion_normalizada = normalizar(explicacion)
            ejemplo_normalizado = normalizar(ejemplo)

            palabras_titulo = set(titulo_normalizado.split())
            palabras_explicacion = set(explicacion_normalizada.split())
            palabras_ejemplo = set(ejemplo_normalizado.split())

            puntuacion = (
                len(palabras_pregunta & palabras_titulo) * 4
                + len(palabras_pregunta & palabras_explicacion) * 2
                + len(palabras_pregunta & palabras_ejemplo)
            )

            if titulo_normalizado in normalizar(pregunta):
                puntuacion += 10

            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_resultado = (
                    nombre_materia,
                    titulo,
                    explicacion,
                    ejemplo
                )

 
    if mejor_resultado is None or mejor_puntuacion == 0:
        respuesta = (
            "Ese tema no está disponible en los contenidos de Aula Digital. "
            "Puedo ayudarte con los temas incluidos en Matemáticas "
            "y Lengua y Comunicación."
        )
    else:
        materia, titulo, explicacion, ejemplo = mejor_resultado

        respuesta = (
            f"¡Claro! Vamos a estudiar este tema según tu nivel {grado}.\n\n"
            f"Materia: {materia}\n"
            f"Tema: {titulo}\n\n"
            f"Explicación:\n{explicacion}\n\n"
            f"Ejemplo:\n{ejemplo}"
        )

    return jsonify({"respuesta": respuesta})


# ==========================================================
# INICIALIZAR Y EJECUTAR
# ==========================================================

inicializar_db()

if __name__ == "__main__":
    app.run(debug=False,use_reloader=False)