(() => {
    "use strict";

    const juegos = {
        batalla: "card-batalla",
        tiempo: "card-tiempo",
        racha: "card-racha",
        verdadero: "card-verdadero",
        palabras: "card-palabras",
        memoria: "card-memoria"
    };

    let bancoPreguntas = [];
    let preguntasJuego = [];
    let modoActual = null;
    let preguntaActual = 0;
    let puntos = 0;
    let aciertos = 0;
    let errores = 0;
    let racha = 0;
    let tiempoRestante = 60;
    let temporizador = null;
    let bloqueado = false;
    let cartasVolteadas = [];
    let paresEncontrados = 0;

    function mezclar(lista) {
        return [...lista].sort(() => Math.random() - 0.5);
    }

    function tarjetaActual() {
        return modoActual
            ? document.getElementById(juegos[modoActual])
            : null;
    }

    function contenidoActual() {
        return tarjetaActual()?.querySelector(".game-content");
    }

    function elemento(clase) {
        return contenidoActual()?.querySelector("." + clase);
    }

    function detenerTemporizador() {
        if (temporizador) {
            clearInterval(temporizador);
            temporizador = null;
        }
    }

    function normalizar(texto) {
        return String(texto)
            .trim()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function respuestaCorrecta(p) {
        return String(
            p.correcta ??
            p.respuesta ??
            p.answer ??
            p.respuesta_correcta ??
            ""
        ).trim();
    }

    async function cargarPreguntas() {
        try {
            const respuesta = await fetch("/api/banco_juegos");

            if (!respuesta.ok) {
                throw new Error("Error al cargar preguntas");
            }

            const datos = await respuesta.json();

            bancoPreguntas = Array.isArray(datos)
                ? datos
                : Object.values(datos || {}).flat();

            bancoPreguntas = bancoPreguntas.filter(p =>
                p &&
                p.pregunta &&
                Array.isArray(p.opciones) &&
                p.opciones.length >= 2 &&
                respuestaCorrecta(p) !== ""
            );

            console.log("Preguntas cargadas:", bancoPreguntas.length);

            return bancoPreguntas.length > 0;

        } catch (error) {
            console.error(error);
            alert("No se pudieron cargar las preguntas.");
            return false;
        }
    }

    function restaurarTarjetas() {
        document.querySelectorAll(".game-content").forEach(contenido => {
            contenido.hidden = true;
        });

        Object.values(juegos).forEach(id => {
            const tarjeta = document.getElementById(id);
            const boton = tarjeta?.querySelector(":scope > .btn");

            if (boton) boton.hidden = false;
        });
    }

    async function iniciarModo(tipo) {
        if (!juegos[tipo]) return;

        if (bancoPreguntas.length === 0) {
            if (!(await cargarPreguntas())) return;
        }

        detenerTemporizador();
        restaurarTarjetas();

        modoActual = tipo;
        preguntaActual = 0;
        puntos = 0;
        aciertos = 0;
        errores = 0;
        racha = 0;
        tiempoRestante = 60;
        bloqueado = false;
        cartasVolteadas = [];
        paresEncontrados = 0;

        preguntasJuego = mezclar(bancoPreguntas).slice(
            0,
            tipo === "memoria" ? 6 : 10
        );

        if (tipo === "memoria" && preguntasJuego.length < 2) {
            alert("Se necesitan al menos dos preguntas para jugar.");
            return;
        }

        const tarjeta = tarjetaActual();
        const contenido = contenidoActual();

        if (!tarjeta || !contenido) {
            alert("No se encontró la tarjeta del juego.");
            return;
        }

        contenido.hidden = false;

        const botonJugar = tarjeta.querySelector(":scope > .btn");
        if (botonJugar) botonJugar.hidden = true;

        const opciones = elemento("game-options");
        const feedback = elemento("game-feedback");

        if (opciones) opciones.innerHTML = "";
        if (feedback) feedback.textContent = "";

        actualizarHUD();

        if (tipo === "memoria") {
            iniciarMemoria();
            return;
        }

        if (tipo === "tiempo") {
            iniciarTemporizador();
        }

        mostrarPregunta();
    }

    function iniciarTemporizador() {
        detenerTemporizador();

        temporizador = setInterval(() => {
            tiempoRestante--;

            const reloj = elemento("game-timer");
            if (reloj) reloj.textContent = tiempoRestante;

            if (tiempoRestante <= 0) {
                detenerTemporizador();
                terminarJuego();
            }
        }, 1000);
    }

    function mostrarPregunta() {
        if (preguntaActual >= preguntasJuego.length) {
            terminarJuego();
            return;
        }

        bloqueado = false;

        const pregunta = preguntasJuego[preguntaActual];
        const titulo = elemento("game-question");
        const opciones = elemento("game-options");
        const feedback = elemento("game-feedback");
        const siguiente = elemento("game-next");

        if (!titulo || !opciones) return;

        titulo.textContent = pregunta.pregunta;
        opciones.innerHTML = "";

        if (feedback) feedback.textContent = "";
        if (siguiente) siguiente.hidden = true;

        if (modoActual === "palabras") {
            mostrarPalabra(pregunta);
            return;
        }

        let respuestas = [...pregunta.opciones];

        if (modoActual === "verdadero") {
            respuestas = ["Verdadero", "Falso"];
        }

        mezclar(respuestas).forEach(respuesta => {
            const boton = document.createElement("button");

            boton.type = "button";
            boton.className = "game-option";
            boton.textContent = respuesta;

            boton.addEventListener("click", () => {
                comprobarRespuesta(respuesta);
            });

            opciones.appendChild(boton);
        });
    }

    function comprobarRespuesta(respuesta) {
        if (bloqueado) return;

        bloqueado = true;

        const pregunta = preguntasJuego[preguntaActual];
        const correcta = respuestaCorrecta(pregunta);

        const esCorrecta =
            normalizar(respuesta) === normalizar(correcta);

        const feedback = elemento("game-feedback");
        const opciones = elemento("game-options");
        const siguiente = elemento("game-next");

        if (esCorrecta) {
            puntos += 10;
            aciertos++;
            racha++;

            if (feedback) {
                feedback.textContent = "¡Correcto! +10 puntos ⭐";
                feedback.style.color = "#16a34a";
            }
        } else {
            errores++;
            racha = 0;

            if (feedback) {
                feedback.textContent =
                    "Incorrecto. La respuesta era: " + correcta;
                feedback.style.color = "#dc2626";
            }
        }

        if (opciones) {
            opciones.querySelectorAll("button").forEach(boton => {
                boton.disabled = true;
            });
        }

        actualizarHUD();

        if (modoActual === "tiempo") {
            setTimeout(() => {
                if (modoActual !== "tiempo" || tiempoRestante <= 0) return;

                preguntaActual++;
                mostrarPregunta();
            }, 800);
        } else if (siguiente) {
            siguiente.hidden = false;
        }
    }

    function mostrarPalabra(pregunta) {
        const opciones = elemento("game-options");
        if (!opciones) return;

        const correcta = respuestaCorrecta(pregunta);

        const letras = document.createElement("p");
        letras.textContent = mezclar(correcta.split("")).join(" ");
        letras.style.fontSize = "25px";

        const entrada = document.createElement("input");
        entrada.type = "text";
        entrada.placeholder = "Escribe la respuesta";
        entrada.className = "game-word-input";

        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "btn";
        boton.textContent = "Comprobar";

        const comprobar = () => {
            if (!entrada.value.trim()) {
                alert("Escribe una respuesta.");
                return;
            }

            comprobarRespuesta(entrada.value);
        };

        boton.addEventListener("click", comprobar);

        entrada.addEventListener("keydown", evento => {
            if (evento.key === "Enter") comprobar();
        });

        opciones.appendChild(letras);
        opciones.appendChild(entrada);
        opciones.appendChild(boton);

        entrada.focus();
    }

    function siguienteJuego() {
        if (!modoActual || !bloqueado) return;

        preguntaActual++;

        if (preguntaActual >= preguntasJuego.length) {
            terminarJuego();
        } else {
            mostrarPregunta();
        }
    }

    function iniciarMemoria() {
        const opciones = elemento("game-options");
        const pregunta = elemento("game-question");

        if (!opciones || !pregunta) return;

        pregunta.textContent =
            "Encuentra las parejas de preguntas y respuestas.";

        opciones.innerHTML = "";

        const cartas = [];

        preguntasJuego.forEach((p, indice) => {
            cartas.push({
                pareja: indice,
                texto: p.pregunta
            });

            cartas.push({
                pareja: indice,
                texto: respuestaCorrecta(p)
            });
        });

        mezclar(cartas).forEach(carta => {
            const boton = document.createElement("button");

            boton.type = "button";
            boton.className = "memory-card";
            boton.textContent = "❓";

            boton.dataset.pareja = carta.pareja;
            boton.dataset.texto = carta.texto;

            boton.addEventListener("click", () => {
                voltearCarta(boton);
            });

            opciones.appendChild(boton);
        });
    }

    function voltearCarta(boton) {
        if (
            boton.disabled ||
            cartasVolteadas.length >= 2 ||
            cartasVolteadas.includes(boton)
        ) return;

        boton.textContent = boton.dataset.texto;
        boton.disabled = true;

        cartasVolteadas.push(boton);

        if (cartasVolteadas.length !== 2) return;

        const [primera, segunda] = cartasVolteadas;

        if (primera.dataset.pareja === segunda.dataset.pareja) {
            primera.classList.add("matched");
            segunda.classList.add("matched");

            paresEncontrados++;
            puntos += 10;
            aciertos++;

            cartasVolteadas = [];
            actualizarHUD();

            if (paresEncontrados === preguntasJuego.length) {
                setTimeout(terminarJuego, 500);
            }
        } else {
            errores++;
            racha = 0;
            actualizarHUD();

            setTimeout(() => {
                primera.textContent = "❓";
                segunda.textContent = "❓";

                primera.disabled = false;
                segunda.disabled = false;

                cartasVolteadas = [];
            }, 1000);
        }
    }

    function actualizarHUD() {
        const marcador = elemento("game-score");
        const rachaElemento = elemento("game-streak");
        const reloj = elemento("game-timer");

        if (marcador) marcador.textContent = puntos;
        if (rachaElemento) rachaElemento.textContent = racha;

        if (reloj) {
            reloj.textContent =
                modoActual === "tiempo" ? tiempoRestante : "—";
        }
    }

    function terminarJuego() {
        if (!modoActual) return;

        detenerTemporizador();
        bloqueado = true;

        const pregunta = elemento("game-question");
        const opciones = elemento("game-options");
        const feedback = elemento("game-feedback");
        const siguiente = elemento("game-next");

        if (pregunta) pregunta.textContent = "¡Juego terminado! 🏆";

        if (opciones) opciones.innerHTML = "";

        if (siguiente) siguiente.hidden = true;

        if (feedback) {
            feedback.style.color = "";
            feedback.textContent =
                `Puntos: ${puntos} | Aciertos: ${aciertos} | Errores: ${errores}`;
        }

        const reiniciar = document.createElement("button");

        reiniciar.type = "button";
        reiniciar.className = "btn";
        reiniciar.textContent = "Volver a jugar";

        reiniciar.addEventListener("click", () => {
            iniciarModo(modoActual);
        });

        if (opciones) opciones.appendChild(reiniciar);

        guardarPuntaje();
        actualizarEstadisticas();
    }

    async function guardarPuntaje() {
        try {
            const respuesta = await fetch("/api/guardar_juego", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    juego: modoActual,
                    puntos,
                    aciertos,
                    errores
                })
            });

            if (!respuesta.ok) {
                console.warn("No se pudo guardar el puntaje.");
            }
        } catch (error) {
            console.error("Error al guardar puntaje:", error);
        }
    }

    function actualizarEstadisticas() {
        let datos = {};

        try {
            datos = JSON.parse(
                localStorage.getItem("aulaJuegos") || "{}"
            );
        } catch {
            datos = {};
        }

        datos.totalPoints = (datos.totalPoints || 0) + puntos;
        datos.totalCoins = (datos.totalCoins || 0) + Math.floor(puntos / 10);
        datos.bestScore = Math.max(datos.bestScore || 0, puntos);

        localStorage.setItem("aulaJuegos", JSON.stringify(datos));

        cargarEstadisticasJuegos();
    }

    function cargarEstadisticasJuegos() {
        let datos = {};

        try {
            datos = JSON.parse(
                localStorage.getItem("aulaJuegos") || "{}"
            );
        } catch {
            datos = {};
        }

        const total = document.getElementById("totalPoints");
        const monedas = document.getElementById("totalCoins");
        const record = document.getElementById("bestScore");

        if (total) total.textContent = datos.totalPoints || 0;
        if (monedas) monedas.textContent = datos.totalCoins || 0;
        if (record) record.textContent = datos.bestScore || 0;
    }

    function cerrarJuego() {
        detenerTemporizador();

        const contenido = contenidoActual();
        const tarjeta = tarjetaActual();

        if (contenido) contenido.hidden = true;

        if (tarjeta) {
            const boton = tarjeta.querySelector(":scope > .btn");
            if (boton) boton.hidden = false;
        }

        modoActual = null;
        preguntasJuego = [];
        preguntaActual = 0;
        bloqueado = false;
        cartasVolteadas = [];
    }

    window.iniciarModo = iniciarModo;
    window.iniciarJuego = iniciarModo;
    window.siguienteJuego = siguienteJuego;
    window.cerrarJuego = cerrarJuego;
    window.cargarEstadisticasJuegos = cargarEstadisticasJuegos;

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            cargarEstadisticasJuegos
        );
    } else {
        cargarEstadisticasJuegos();
    }

})();