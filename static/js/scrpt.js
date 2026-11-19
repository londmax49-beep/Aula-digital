"use strict";

document.addEventListener("DOMContentLoaded", function () {

    const boton = document.getElementById("botonAlex");
    const chat = document.getElementById("chatAlex");
    const entrada = document.getElementById("mensajeAlex");
    const enviar = document.getElementById("enviarAlex");
    const mensajes = document.getElementById("chatMensajes");
    const micro = document.getElementById("microAlex");

    if (!boton || !chat) {
        console.error("No se encontraron los elementos de Profe Alex.");
        return;
    }

    // ESTADO INICIAL DEL CHAT
    chat.style.setProperty("display", "none", "important");

    // BOTÓN FLOTANTE: ABRIR Y CERRAR
    boton.addEventListener("click", function (event) {

        event.preventDefault();
        event.stopPropagation();

        const oculto = getComputedStyle(chat).display === "none";

        if (oculto) {
            chat.style.setProperty("display", "flex", "important");
            chat.style.visibility = "visible";
            chat.style.opacity = "1";

            if (entrada) {
                setTimeout(function () {
                    entrada.focus();
                }, 150);
            }
        } else {
            chat.style.setProperty("display", "none", "important");
        }

    });

    // AGREGAR MENSAJE
    function agregarMensaje(texto, tipo) {

        if (!mensajes) return null;

        const div = document.createElement("div");

        div.className = "mensaje " + tipo;
        div.textContent = texto;

        mensajes.appendChild(div);
        mensajes.scrollTop = mensajes.scrollHeight;

        return div;
    }

    // HACER QUE ALEX HABLE
    function hablar(texto) {

        if (!("speechSynthesis" in window)) return;

        window.speechSynthesis.cancel();

        const voz = new SpeechSynthesisUtterance(texto);

        voz.lang = "es-MX";
        voz.rate = 0.95;
        voz.pitch = 1;
        voz.volume = 1;

        const voces = window.speechSynthesis.getVoices();

        const vozEspanol =
            voces.find(v => v.lang.toLowerCase() === "es-mx") ||
            voces.find(v => v.lang.toLowerCase().startsWith("es"));

        if (vozEspanol) {
            voz.voice = vozEspanol;
        }

        window.speechSynthesis.speak(voz);
    }

    // ENVIAR PREGUNTA A FLASK
    async function preguntar() {

        if (!entrada || !enviar) return;

        const pregunta = entrada.value.trim();

        if (!pregunta || enviar.disabled) return;

        entrada.value = "";
        enviar.disabled = true;

        agregarMensaje(pregunta, "usuario");

        const cargando = agregarMensaje(
            "🤖 Profe Alex está pensando...",
            "alex"
        );

        try {

            const response = await fetch(
                window.AULA_URL_ALEX || "/preguntar_alex",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        pregunta: pregunta
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Error del servidor: " + response.status);
            }

            const datos = await response.json();

            cargando.remove();

            const texto =
                datos.respuesta ||
                datos.mensaje ||
                "No pude encontrar una respuesta.";

            agregarMensaje(texto, "alex");

            hablar(texto);

        } catch (error) {

            cargando.remove();

            agregarMensaje(
                "No pude conectarme con el servidor. Intenta nuevamente.",
                "alex"
            );

            console.error("Error de Profe Alex:", error);

        } finally {

            enviar.disabled = false;

            if (entrada) {
                entrada.focus();
            }
        }
    }

    // BOTÓN ENVIAR
    enviar.addEventListener("click", function (event) {
        event.preventDefault();
        preguntar();
    });

    // ENVIAR CON ENTER
    entrada.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {
            event.preventDefault();
            preguntar();
        }
    });

    // DICTADO POR VOZ
    if (micro) {

        const Reconocimiento =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (Reconocimiento) {

            const reconocimiento = new Reconocimiento();

            reconocimiento.lang = "es-MX";
            reconocimiento.continuous = false;
            reconocimiento.interimResults = false;

            micro.addEventListener("click", function () {

                try {
                    reconocimiento.start();
                    micro.textContent = "🔴";
                } catch (error) {
                    console.warn("El reconocimiento ya está activo.");
                }

            });

            reconocimiento.onresult = function (event) {

                entrada.value = event.results[0][0].transcript;
                micro.textContent = "🎤";

                preguntar();
            };

            reconocimiento.onerror = function () {
                micro.textContent = "🎤";
            };

            reconocimiento.onend = function () {
                micro.textContent = "🎤";
            };

        } else {

            micro.addEventListener("click", function () {

                agregarMensaje(
                    "Tu navegador no admite dictado por voz.",
                    "alex"
                );

            });
        }
    }

});