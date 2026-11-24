"use strict";

window.enviarPreguntaAlex = async function () {
    const entrada = document.getElementById("mensajeAlex");
    const enviar = document.getElementById("enviarAlex");
    const mensajes = document.getElementById("chatMensajes");

    if (!entrada || !enviar || !mensajes) {
        alert("No se encontraron los elementos del chat.");
        return;
    }

    const pregunta = entrada.value.trim();

    if (!pregunta) {
        entrada.focus();
        return;
    }

    if (enviar.disabled) return;

    entrada.value = "";
    enviar.disabled = true;

    const usuario = document.createElement("div");
    usuario.className = "mensaje usuario";
    usuario.textContent = pregunta;
    mensajes.appendChild(usuario);

    const cargando = document.createElement("div");
    cargando.className = "mensaje alex";
    cargando.textContent = "Profe Alex está pensando...";
    mensajes.appendChild(cargando);

    mensajes.scrollTop = mensajes.scrollHeight;

    try {
        const response = await fetch("/preguntar_alex", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ pregunta: pregunta })
        });

        const datos = await response.json();

        cargando.remove();

        if (!response.ok) {
            throw new Error(datos.respuesta || "Error al enviar la pregunta.");
        }

        const respuesta = datos.respuesta || "No recibí una respuesta.";

        const alex = document.createElement("div");
        alex.className = "mensaje alex";
        alex.textContent = respuesta;
        mensajes.appendChild(alex);

        mensajes.scrollTop = mensajes.scrollHeight;

        if ("speechSynthesis" in window) {
            speechSynthesis.cancel();

            const voz = new SpeechSynthesisUtterance(respuesta);
            voz.lang = "es-MX";
            speechSynthesis.speak(voz);
        }

    } catch (error) {
        if (cargando.parentNode) cargando.remove();

        const errorDiv = document.createElement("div");
        errorDiv.className = "mensaje alex";
        errorDiv.textContent = "Error: " + error.message;
        mensajes.appendChild(errorDiv);

        console.error("Error de Profe Alex:", error);

    } finally {
        enviar.disabled = false;
        entrada.focus();
        mensajes.scrollTop = mensajes.scrollHeight;
    }
};

document.addEventListener("DOMContentLoaded", function () {

    const entrada = document.getElementById("mensajeAlex");
    const micro = document.getElementById("microAlex");

    if (entrada) {
        entrada.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                window.enviarPreguntaAlex();
            }
        });
    }

    if (micro) {
        const Reconocimiento =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!Reconocimiento) {
            micro.addEventListener("click", function () {
                alert("Tu navegador no admite dictado por voz.");
            });
            return;
        }

        const reconocimiento = new Reconocimiento();
        reconocimiento.lang = "es-MX";
        reconocimiento.continuous = false;

        micro.addEventListener("click", function () {
            reconocimiento.start();
        });

        reconocimiento.onresult = function (event) {
            if (entrada) {
                entrada.value = event.results[0][0].transcript;
                window.enviarPreguntaAlex();
            }
        };
    }
});