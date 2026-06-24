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

//Boton Editar y Eliminar

const boton_eliminar = document.getElementsByClassName("boton_eliminar")
const boton_modificar = document.getElementsByClassName("boton_modificar")

for (let i=0; i<boton_eliminar.length; i++) {

    boton_eliminar[i].addEventListener("click", function(event) {
        abrir_formulario_resena("formulario_eliminar_resena", i)


    })

    boton_modificar[i].addEventListener("click", function(event){
        abrir_formulario_resena("formulario_modificar_resena", i)

    })

}


function abrir_formulario_resena(formulario, i){
    document.getElementsByClassName(formulario)[i].style.display = "block"
}
