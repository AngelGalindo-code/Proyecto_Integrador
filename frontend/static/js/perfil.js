document.addEventListener("DOMContentLoaded", function () {
    const formularios = document.querySelectorAll("form");

    formularios.forEach(function (formulario) {
        formulario.addEventListener("submit", function (evento) {
            const boton = formulario.querySelector("button");

            if (boton && boton.textContent === "Eliminar") {
                const respuesta = confirm("¿Seguro que querés eliminar?");

                if (respuesta == false) {
                    evento.preventDefault();
                }
            }
        });
    });
});
