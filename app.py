import os
import sqlite3
import random
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

MATEMATICAS = [
    ("Números enteros", "Los enteros incluyen números positivos, negativos y cero.", "Ejemplo: -3, -2, -1, 0, 1, 2."),
    ("Operaciones básicas", "La suma, resta, multiplicación y división permiten resolver operaciones.", "8 + 5 = 13."),
    ("Fracciones", "Representan partes de un todo.", "3/4 representa tres de cuatro partes."),
    ("Decimales", "Representan cantidades con partes de una unidad.", "2.5 equivale a 2 unidades y 5 décimas."),
    ("Porcentajes", "Un porcentaje expresa una cantidad de cada cien.", "25% = 25/100."),
    ("Proporciones", "Compara dos razones equivalentes.", "2/4 = 1/2."),
    ("Potencias", "Expresan multiplicaciones repetidas.", "3² = 3 × 3 = 9."),
    ("Raíces", "Buscan el número que produce otro al multiplicarse por sí mismo.", "√25 = 5."),
    ("Expresiones algebraicas", "Las letras representan valores desconocidos o variables.", "3x + 2."),
    ("Ecuaciones", "Establecen igualdad entre dos expresiones.", "x + 5 = 12; x = 7."),
    ("Plano cartesiano", "Localiza puntos usando coordenadas.", "(3,2) representa x=3 y y=2."),
    ("Perímetros", "El perímetro es la suma de los lados de una figura.", "Cuadrado de lado 4: P=16."),
    ("Áreas", "El área mide la superficie de una figura.", "Rectángulo: base × altura."),
    ("Volumen", "Mide el espacio ocupado por un cuerpo.", "Cubo: lado × lado × lado."),
    ("Estadística", "Organiza, representa y analiza datos.", "Tablas, gráficas y medidas."),
    ("Media, mediana y moda", "Describen conjuntos de datos.", "Media de 2,4,6 = 4."),
    ("Probabilidad", "Mide la posibilidad de que ocurra un evento.", "Cara en una moneda: 1/2."),
    ("Geometría", "Estudia figuras, propiedades y relaciones.", "Triángulos, círculos y polígonos."),
    ("Ángulos", "Se miden en grados.", "Un ángulo recto mide 90°."),
    ("Triángulos", "Tienen tres lados y sus ángulos suman 180°.", "60° + 60° + 60° = 180°."),
    ("Sistemas de ecuaciones", "Encuentran valores que satisfacen varias ecuaciones.", "x+y=5; x-y=1."),
    ("Funciones", "Relacionan una entrada con un resultado.", "f(x)=2x."),
    ("Funciones lineales", "Su gráfica es una línea recta.", "y=2x+3."),
    ("Funciones cuadráticas", "Incluyen variables al cuadrado.", "y=x²+2x+1."),
    ("Factorización", "Expresa una operación como producto de factores.", "x²-9=(x-3)(x+3)."),
    ("Sucesiones", "Son secuencias que siguen una regla.", "2,4,6,8..."),
    ("Trigonometría", "Estudia relaciones entre lados y ángulos.", "Seno, coseno y tangente."),
    ("Teorema de Pitágoras", "En un triángulo rectángulo: a²+b²=c².", "3²+4²=5²."),
    ("Matemáticas financieras", "Aplica cálculos a costos, ahorro e intereses.", "Descuentos e intereses."),
    ("Repaso general", "Integra diferentes conocimientos matemáticos.", "Resuelve problemas combinando operaciones.")
]

LENGUA = [
    ("Comunicación", "La comunicación transmite información entre personas.", "Hablar, escribir o gesticular."),
    ("Elementos de comunicación", "Emisor, receptor, mensaje, canal y contexto.", "Una persona escribe a otra."),
    ("Sustantivos", "Nombran personas, animales, cosas, lugares o ideas.", "Escuela, perro, alegría."),
    ("Adjetivos", "Describen características de los sustantivos.", "Libro interesante."),
    ("Verbos", "Expresan acciones, procesos o estados.", "Correr, pensar, estar."),
    ("Adverbios", "Modifican verbos, adjetivos u otros adverbios.", "Corre rápidamente."),
    ("Pronombres", "Sustituyen o señalan nombres.", "Ella, nosotros, aquello."),
    ("Oraciones", "Expresan ideas con palabras organizadas.", "María estudia por la tarde."),
    ("Sujeto y predicado", "El sujeto es de quien se habla; el predicado expresa algo sobre él.", "Pedro juega."),
    ("Ortografía", "Reglas para escribir correctamente.", "Uso correcto de b, v, c, s y z."),
    ("Acentuación", "Reglas para colocar tildes.", "Canción, árbol, rápido."),
    ("Puntuación", "Los signos organizan y aclaran el texto.", "Punto, coma, interrogación."),
    ("Sinónimos", "Palabras con significados iguales o similares.", "Alegre y contento."),
    ("Antónimos", "Palabras con significados opuestos.", "Alto y bajo."),
    ("Comprensión lectora", "Interpreta y entiende la información de un texto.", "Identifica la idea principal."),
    ("Resumen", "Presenta brevemente las ideas esenciales.", "Explica un texto en pocas palabras."),
    ("Narración", "Relata hechos reales o imaginarios.", "Cuentos y novelas."),
    ("Descripción", "Explica características de personas, objetos o lugares.", "Describe un paisaje."),
    ("Texto informativo", "Expone información clara y verificable.", "Noticias y artículos."),
    ("Texto argumentativo", "Defiende una opinión mediante argumentos.", "Ensayo de opinión."),
    ("Conectores", "Relacionan ideas dentro de un texto.", "Además, por lo tanto, sin embargo."),
    ("Figuras literarias", "Recursos que enriquecen el lenguaje.", "Metáfora y personificación."),
    ("Poesía", "Expresa ideas y emociones con lenguaje artístico.", "Versos, estrofas y ritmo."),
    ("Investigación", "Busca y analiza información para responder preguntas.", "Consultar fuentes confiables."),
    ("Fuentes de información", "Respaldan los datos que se utilizan.", "Libros y artículos."),
    ("Citas y referencias", "Reconocen las fuentes de información.", "Autor y documento consultado."),
    ("Ensayo", "Desarrolla una reflexión o postura.", "Introducción, desarrollo y conclusión."),
    ("Reseña", "Describe y evalúa una obra.", "Reseña de un libro."),
    ("Debate", "Intercambia argumentos sobre un tema.", "Defender una postura con respeto."),
    ("Repaso general", "Integra lectura, escritura y comunicación.", "Interpretar, argumentar y redactar.")
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
# BANCO DE MATEMÁTICAS ADAPTADO POR GRADO
# ==========================================================

def banco_matematicas(grado=None):
    grado = grado or grado_actual()
    g = GRADOS.index(grado) + 1 if grado in GRADOS else 1
    banco = []

    if g <= 3:
        for i in range(1, 31):
            a = g * 10 + i
            b = i + 2

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} + {b}?", a+b,
                [a+b+2, a+b-2, a*b]
            ))

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} - {b}?", a-b,
                [a-b+3, a+b, a-b-2]
            ))

            banco.append(crear_pregunta(
                f"¿Cuánto es {a} × {b}?", a*b,
                [a+b, a*b+5, a*b-3]
            ))

        for i in range(1, 31):
            cantidad = 20 + i * 5
            porcentaje = 10 + (i % 9) * 10
            resultado = cantidad * porcentaje // 100

            banco.append(crear_pregunta(
                f"¿Cuánto es el {porcentaje}% de {cantidad}?",
                resultado,
                [resultado+2, resultado+5, resultado-1]
            ))

    else:
        for i in range(1, 41):
            x = i + g
            a = g + (i % 5) + 1
            resultado = a * x

            banco.append(crear_pregunta(
                f"Resuelve {a}x = {resultado}. ¿Cuánto vale x?",
                x,
                [x+1, x-2, resultado]
            ))

            n = i + g
            banco.append(crear_pregunta(
                f"¿Cuánto es {n}²?",
                n*n,
                [n*2, n*n+3, n*n-4]
            ))

            banco.append(crear_pregunta(
                f"Si f(x)=2x+{g}, ¿cuánto vale f({i})?",
                2*i+g,
                [i+g, 2*i, 2*i+g+2]
            ))

            banco.append(crear_pregunta(
                f"¿Cuál es la raíz cuadrada de {n*n}?",
                n,
                [n+2, n-1, n*n]
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
            GROUP BY materia
        """, (usuario_id,)).fetchall()

        examen = con.execute("""
            SELECT * FROM examenes
            WHERE usuario_id=?
            ORDER BY id DESC LIMIT 1
        """, (usuario_id,)).fetchone()

    avances = {"matematicas": 0, "lengua": 0}

    for p in progreso:
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

    if temas is None or not 1 <= nivel <= 30:
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

    titulo, explicacion, ejemplo = temas[nivel - 1]

    # La pregunta se guarda en sesión para que no cambie al responder.
    llave = f"pregunta_{materia}_{nivel}"

    if request.method == "GET" or llave not in session:
        banco = banco_matematicas() if materia == "matematicas" else banco_lengua()
        session[llave] = random.choice(banco)

    pregunta = session[llave]

    if request.method == "POST":
        respuesta = request.form.get("respuesta", "")

        if respuesta == pregunta["correcta"]:
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
            flash("¡Correcto! Nivel completado.", "success")

            if nivel < 30:
                return redirect(url_for("nivel", materia=materia, nivel=nivel+1))

            return redirect(url_for("materia", materia=materia))

        flash("Respuesta incorrecta. Intenta nuevamente.", "error")

    return render_template(
        "nivel.html",
        materia=materia,
        nivel=nivel,
        titulo=titulo,
        explicacion=explicacion,
        ejemplo=ejemplo,
        pregunta=pregunta,
        nombre_materia=MATERIAS[materia]
    )


# ==========================================================
# ZONA GAMER
# ==========================================================

@app.route("/juegos")
@login_requerido
def juegos():
    return render_template("juegos.html")


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
        total = con.execute("""
            SELECT COUNT(*) FROM progreso
            WHERE usuario_id=?
        """, (usuario_id,)).fetchone()[0]

    if total < 60:
        flash("Debes completar los 60 niveles antes de presentar el examen.", "warning")
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
        total = con.execute("""
            SELECT COUNT(*) FROM progreso WHERE usuario_id=?
        """, (usuario_id,)).fetchone()[0]

        examen = con.execute("""
            SELECT * FROM examenes
            WHERE usuario_id=? AND aprobado=1
            ORDER BY id DESC LIMIT 1
        """, (usuario_id,)).fetchone()

    if total < 60 or not examen:
        flash("Completa los niveles y aprueba el examen para obtener tu diploma.", "warning")
        return redirect(url_for("panel"))

    return render_template(
        "diploma.html",
        nombre=session["nombre"],
        fecha=datetime.now().strftime("%d/%m/%Y"),
        calificacion=examen["calificacion"]
    )


# ==========================================================
# PROFE ALEX - SOLO APOYO EDUCATIVO
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

    if "fracci" in pregunta:
        respuesta = (
            "Una fracción representa partes de un todo. "
            "El numerador indica las partes que tomamos y el denominador "
            "en cuántas partes se divide la unidad."
        )
    elif "porcentaje" in pregunta or "%" in pregunta:
        respuesta = (
            "Para calcular un porcentaje, multiplica la cantidad por el porcentaje "
            "y divide entre 100. Ejemplo: 20% de 150 = 150 × 20 ÷ 100 = 30."
        )
    elif "ecuacion" in pregunta:
        respuesta = (
            "Para resolver una ecuación, realiza operaciones inversas en ambos lados "
            "hasta dejar la variable sola. Comprueba sustituyendo el resultado."
        )
    elif "sujeto" in pregunta:
        respuesta = (
            "El sujeto es de quien se habla en una oración. "
            "El predicado expresa lo que se dice del sujeto."
        )
    elif "verbo" in pregunta:
        respuesta = (
            "Los verbos expresan acciones, estados o procesos. "
            "Ejemplos: estudiar, correr, pensar y ser."
        )
    elif "resumen" in pregunta:
        respuesta = (
            "Para hacer un resumen, identifica las ideas principales, "
            "elimina detalles secundarios y redacta con tus propias palabras."
        )
    elif "sinonimo" in pregunta:
        respuesta = "Los sinónimos son palabras con significado igual o parecido. Ejemplo: alegre y contento."
    elif "antonimo" in pregunta:
        respuesta = "Los antónimos son palabras con significado opuesto. Ejemplo: alto y bajo."
    elif "matemat" in pregunta:
        respuesta = (
            f"Vamos a resolverlo de acuerdo con tu nivel {grado}. "
            "Identifica los datos, determina la operación y resuelve paso a paso. "
            "Después comprueba tu resultado."
        )
    elif "lengua" in pregunta or "comunicacion" in pregunta:
        respuesta = (
            f"Para estudiar Lengua y Comunicación en {grado}, "
            "identifica el tema, las ideas principales y el contexto. "
            "Explica lo que comprendiste con tus propias palabras."
        )
    else:
        respuesta = (
            f"Vamos a estudiarlo según tu nivel {grado}. "
            "Primero identifica el tema, revisa su definición y observa un ejemplo. "
            "Después intenta resolver una actividad por tu cuenta."
        )

    return jsonify({"respuesta": respuesta})


# ==========================================================
# INICIALIZAR Y EJECUTAR
# ==========================================================

inicializar_db()

if __name__ == "__main__":
    app.run(debug=True)