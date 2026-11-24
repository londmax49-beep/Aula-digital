document.addEventListener("DOMContentLoaded", () => {
    const juegosLengua = {
        ortografia: {
            preguntas: [
                { q: "¿Cuál palabra está escrita correctamente?", o: ["Haber", "Aver", "Haver"], r: "Haber" },
                { q: "¿Cuál palabra está escrita correctamente?", o: ["Escuela", "Ezcuela", "Ecuela"], r: "Escuela" },
                { q: "¿Cuál palabra está escrita correctamente?", o: ["Biblioteca", "Biblioteka", "Vivlioteca"], r: "Biblioteca" }
            ]
        },
        sinonimos: {
            preguntas: [
                { q: "¿Cuál es un sinónimo de FELIZ?", o: ["Alegre", "Enojado", "Triste"], r: "Alegre" },
                { q: "¿Cuál es un sinónimo de RÁPIDO?", o: ["Lento", "Veloz", "Débil"], r: "Veloz" },
                { q: "¿Cuál es un sinónimo de BONITO?", o: ["Hermoso", "Feo", "Oscuro"], r: "Hermoso" }
            ]
        },
        acentos: {
            preguntas: [
                { q: "¿Cuál palabra lleva tilde?", o: ["Arbol", "Mesa", "Casa"], r: "Árbol" },
                { q: "¿Cuál es la escritura correcta?", o: ["Cancion", "Canción", "Cancíon"], r: "Canción" },
                { q: "¿Cuál palabra está escrita correctamente?", o: ["Telefono", "Teléfono", "Telefonó"], r: "Teléfono" }
            ]
        },
        lectura: {
            preguntas: [
                {
                    texto: "María plantó un árbol en el jardín de su casa. Todos los días lo regaba y cuidaba. Después de varios meses, el árbol comenzó a dar frutos.",
                    q: "¿Qué plantó María?",
                    o: ["Una flor", "Un árbol", "Un arbusto"],
                    r: "Un árbol"
                },
                {
                    texto: "Luis fue a la biblioteca para investigar sobre los planetas. Consultó varios libros y escribió sus apuntes en un cuaderno.",
                    q: "¿A dónde fue Luis?",
                    o: ["Al parque", "A la biblioteca", "Al mercado"],
                    r: "A la biblioteca"
                },
                {
                    texto: "Sofía encontró un perro perdido. Le dio agua y buscó a su dueño. Finalmente, logró reunir al perro con su familia.",
                    q: "¿Qué hizo Sofía?",
                    o: ["Abandonó al perro", "Lo escondió", "Ayudó al perro a encontrar a su familia"],
                    r: "Ayudó al perro a encontrar a su familia"
                }
            ]
        },
        oraciones: {
            preguntas: [
                { q: "Ordena las palabras para formar una oración:", o: ["estudia", "Ana", "matemáticas"], r: "Ana estudia matemáticas" },
                { q: "Ordena las palabras para formar una oración:", o: ["libro", "El", "interesante", "es"], r: "El libro es interesante" },
                { q: "Ordena las palabras para formar una oración:", o: ["juegan", "niños", "Los"], r: "Los niños juegan" }
            ]
        },
        puntuacion: {
            preguntas: [
                { q: "¿Qué signo completa esta pregunta? ¿Cómo estás __", o: ["?", ".", ","], r: "?" },
                { q: "¿Qué signo se usa para terminar una oración? Me gusta leer __", o: [",", ".", ":"], r: "." },
                { q: "¿Qué signo se usa para enumerar elementos? Compré pan __ leche y fruta.", o: [".", ",", "?"], r: "," }
            ]
        }
    };

    const estado = {};

    Object.keys(juegosLengua).forEach(nombre => {
        estado[nombre] = { indice: 0, puntos: 0, respondida: false };
        mostrarPregunta(nombre);
    });

    function mostrarPregunta(nombre) {
        const zona = document.getElementById(nombre);
        const juego = juegosLengua[nombre];
        const datos = estado[nombre];

        if (datos.indice >= juego.preguntas.length) {
            zona.innerHTML = `
                <h3>¡Juego terminado!</h3>
                <p>Tu puntuación: ${datos.puntos} de ${juego.preguntas.length}</p>
                <button class="reiniciar">Volver a jugar</button>
            `;
            zona.querySelector(".reiniciar").addEventListener("click", () => {
                estado[nombre] = { indice: 0, puntos: 0, respondida: false };
                mostrarPregunta(nombre);
            });
            return;
        }

        const pregunta = juego.preguntas[datos.indice];
        datos.respondida = false;

        let html = `<p><strong>Pregunta ${datos.indice + 1} de ${juego.preguntas.length}</strong></p>`;

        if (pregunta.texto) {
            html += `<div class="texto-lectura">${pregunta.texto}</div>`;
        }

        html += `<p class="pregunta-lengua">${pregunta.q}</p>`;

        if (nombre === "oraciones") {
            const palabras = [...pregunta.o];
            html += `<p id="${nombre}-seleccion">Tu oración: </p>`;
            html += `<div class="opciones-lengua">`;
            palabras.sort(() => Math.random() - 0.5);
            palabras.forEach(palabra => {
                html += `<button type="button" data-palabra="${palabra}">${palabra}</button>`;
            });
            html += `</div>`;
            html += `<button type="button" class="comprobar">Comprobar oración</button>`;
        } else {
            html += `<div class="opciones-lengua">`;
            pregunta.o.forEach(opcion => {
                html += `<button type="button" data-respuesta="${opcion}">${opcion}</button>`;
            });
            html += `</div>`;
        }

        html += `<p class="resultado-lengua" aria-live="polite"></p>`;
        html += `<button type="button" class="siguiente" hidden>Siguiente pregunta</button>`;

        zona.innerHTML = html;

        if (nombre === "oraciones") {
            const seleccion = [];
            const textoSeleccion = zona.querySelector(`#${nombre}-seleccion`);

            zona.querySelectorAll("[data-palabra]").forEach(boton => {
                boton.addEventListener("click", () => {
                    if (datos.respondida) return;
                    seleccion.push(boton.dataset.palabra);
                    boton.disabled = true;
                    textoSeleccion.textContent = "Tu oración: " + seleccion.join(" ");
                });
            });

            zona.querySelector(".comprobar").addEventListener("click", () => {
                comprobar(nombre, seleccion.join(" "));
            });
        } else {
            zona.querySelectorAll("[data-respuesta]").forEach(boton => {
                boton.addEventListener("click", () => {
                    comprobar(nombre, boton.dataset.respuesta);
                });
            });
        }

        zona.querySelector(".siguiente").addEventListener("click", () => {
            datos.indice++;
            mostrarPregunta(nombre);
        });
    }

    function comprobar(nombre, respuesta) {
        const zona = document.getElementById(nombre);
        const datos = estado[nombre];

        if (datos.respondida) return;
        datos.respondida = true;

        const correcta = juegosLengua[nombre].preguntas[datos.indice].r;
        const resultado = zona.querySelector(".resultado-lengua");

        if (respuesta.trim().toLowerCase() === correcta.toLowerCase()) {
            datos.puntos++;
            resultado.textContent = "✅ ¡Correcto!";
            resultado.style.color = "green";
        } else {
            resultado.textContent = "❌ Respuesta correcta: " + correcta;
            resultado.style.color = "crimson";
        }

        zona.querySelectorAll(".opciones-lengua button").forEach(boton => {
            boton.disabled = true;
        });

        const comprobarBtn = zona.querySelector(".comprobar");
        if (comprobarBtn) comprobarBtn.disabled = true;

        zona.querySelector(".siguiente").hidden = false;
    }
});