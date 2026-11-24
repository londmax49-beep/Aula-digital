(function () {
    "use strict";

    function protegerNavegacion() {
        // Crear una entrada de protección en el historial
        history.pushState(
            { aulaDigital: true },
            "",
            location.href
        );

        window.addEventListener("popstate", function () {
            // Volver a crear la entrada para dificultar salir
            history.pushState(
                { aulaDigital: true },
                "",
                location.href
            );
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            protegerNavegacion
        );
    } else {
        protegerNavegacion();
    }
})();