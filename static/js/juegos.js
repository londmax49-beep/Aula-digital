"use strict";

document.addEventListener("DOMContentLoaded", function () {

    let preguntas = [];
    let preguntasOriginales = [];
    let preguntaActual = 0;
    let puntos = 0;
    let errores = 0;
    let racha = 0;
    let modo = "quiz";
    let bloqueado = false;

    const preguntaHTML = document.getElementById("gameQuestion");
    const opcionesHTML = document.getElementById("gameOptions");
    const resultadoHTML = document.getElementById("gameResult");
    const puntosHTML = document.getElementById("gameScore");
    const canvas = document.getElementById("gameCanvas");

    async function cargarPreguntas() {

        try {

            const response = await fetch("/api/banco_juegos");

            if (!response.ok) {
                throw new Error("No se pudo cargar el banco");
            }

            const datos = await response.json();

            let banco = [];

            if (Array.isArray(datos)) {
                banco = datos;
            } else {
                Object.values(datos).forEach(function (grupo) {
                    if (Array.isArray(grupo)) {
                        banco = banco.concat(grupo);
                    }
                });
            }

            preguntasOriginales = banco.filter(p =>
                p && p.pregunta && Array.isArray(p.opciones)
            );

            if (!preguntasOriginales.length) {
                mostrarMensaje("No hay preguntas disponibles.");
                return;
            }

            iniciarJuego("quiz");

        } catch (error) {

            mostrarMensaje(
                "No se pudieron cargar las preguntas. Revisa que el servidor esté funcionando."
            );

        }
    }

    function mezclar(array) {

        const copia = array.slice();

        for (let i = copia.length - 1; i > 0; i--) {

            const j = Math.floor(Math.random() * (i + 1));

            [copia[i], copia[j]] = [copia[j], copia[i]];
        }

        return copia;
    }

    function obtenerRespuesta(p) {
        return p.correcta ?? p.respuesta ?? p.answer;
    }

    function normalizar(valor) {
        return String(valor ?? "")
            .trim()
            .toLowerCase()
            .replace(/[.,!?¿¡]/g, "");
    }

    function iniciarJuego(tipo) {

        modo = tipo || "quiz";

        preguntas = mezclar(preguntasOriginales);

        if (modo === "memoria") {
            preguntas = preguntas.slice(0, 6);
        }

        preguntaActual = 0;
        puntos = 0;
        errores = 0;
        racha = 0;
        bloqueado = false;

        actualizarPuntos();

        if (resultadoHTML) resultadoHTML.textContent = "";

        if (canvas) canvas.style.display = "none";

        mostrarPregunta();
    }

    function actualizarPuntos() {

        if (puntosHTML) {
            puntosHTML.textContent = puntos;
        }

        const rachaHTML = document.getElementById("gameStreak");

        if (rachaHTML) {
            rachaHTML.textContent = racha;
        }
    }

    function mostrarMensaje(texto) {

        if (preguntaHTML) {
            preguntaHTML.textContent = texto;
        }

        if (opcionesHTML) {
            opcionesHTML.innerHTML = "";
        }
    }

    function mostrarPregunta() {

        bloqueado = false;

        if (preguntaActual >= preguntas.length) {
            terminarJuego();
            return;
        }

        const p = preguntas[preguntaActual];

        if (preguntaHTML) {
            preguntaHTML.textContent = p.pregunta;
        }

        if (resultadoHTML) {
            resultadoHTML.textContent = "";
        }

        if (!opcionesHTML) return;

        opcionesHTML.innerHTML = "";

        let opciones = Array.isArray(p.opciones) ? p.opciones.slice() : [];

        if (modo === "verdadero") {

            const correcta = obtenerRespuesta(p);

            const esVerdadero = opciones.some(op =>
                normalizar(op) === normalizar(correcta)
            );

            opciones = esVerdadero
                ? ["Verdadero", "Falso"]
                : ["Falso", "Verdadero"];
        }

        opciones = mezclar(opciones);

        opciones.forEach(function (opcion) {

            const boton = document.createElement("button");

            boton.type = "button";
            boton.className = "game-option";
            boton.textContent = opcion;

            boton.addEventListener("click", function () {
                verificarRespuesta(opcion, boton);
            });

            opcionesHTML.appendChild(boton);
        });
    }

    function verificarRespuesta(opcion, boton) {

        if (bloqueado) return;

        bloqueado = true;

        const p = preguntas[preguntaActual];
        const correcta = obtenerRespuesta(p);

        let acertado = normalizar(opcion) === normalizar(correcta);

        if (modo === "verdadero") {

            const esVerdadero = p.opciones.some(op =>
                normalizar(op) === normalizar(correcta)
            );

            acertado = normalizar(opcion) ===
                normalizar(esVerdadero ? "Verdadero" : "Falso");
        }

        opcionesHTML.querySelectorAll("button").forEach(b => {
            b.disabled = true;
        });

        if (acertado) {

            puntos += modo === "racha" ? 20 : 10;
            racha++;

            if (boton) boton.classList.add("correcta");

            if (resultadoHTML) {
                resultadoHTML.textContent = "✅ ¡Correcto! Muy bien.";
            }

        } else {

            errores++;
            racha = 0;

            if (boton) boton.classList.add("incorrecta");

            if (resultadoHTML) {
                resultadoHTML.textContent = "❌ Respuesta incorrecta. La respuesta es: " + correcta;
            }
        }

        actualizarPuntos();

        setTimeout(function () {
            preguntaActual++;
            mostrarPregunta();
        }, 1200);
    }

    function terminarJuego() {

        mostrarMensaje("🏆 ¡Juego terminado!");

        if (resultadoHTML) {
            resultadoHTML.textContent =
                "Puntos: " + puntos +
                " | Aciertos: " + (preguntas.length - errores) +
                " | Errores: " + errores;
        }

        if (opcionesHTML) {

            const reiniciar = document.createElement("button");

            reiniciar.type = "button";
            reiniciar.textContent = "🔄 Volver a jugar";

            reiniciar.addEventListener("click", function () {
                iniciarJuego(modo);
            });

            opcionesHTML.appendChild(reiniciar);
        }

        guardarPuntaje();
    }

    async function guardarPuntaje() {

        try {

            await fetch("/api/guardar_juego", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    juego: modo,
                    puntos: puntos,
                    aciertos: preguntas.length - errores,
                    errores: errores
                })
            });

        } catch (error) {
            console.log("No se pudo guardar el puntaje.");
        }
    }

    document.querySelectorAll("[data-juego]").forEach(function (boton) {

        boton.addEventListener("click", function () {

            iniciarJuego(boton.dataset.juego);

        });
    });

    window.iniciarJuego = iniciarJuego;

    window.iniciarQuiz = () => iniciarJuego("quiz");
    window.iniciarVerdaderoFalso = () => iniciarJuego("verdadero");
    window.iniciarMemoria = () => iniciarJuego("memoria");
    window.iniciarDesafio = () => iniciarJuego("desafio");
    window.iniciarVelocidad = () => iniciarJuego("velocidad");
    window.iniciarRacha = () => iniciarJuego("racha");

    cargarPreguntas();

});