//Cerrar formulario

const cancelar_eliminar = document.getElementsByClassName("boton_cancelar_eliminar")
const cancelar_modificar = document.getElementsByClassName("boton_cancelar_modificar")

for (let i=0; i<cancelar_eliminar.length; i++) {
    cancelar_eliminar[i].addEventListener("click", function(event) {
        cerrar_resena("formulario_eliminar_resena",i)
    }
)}


for (let i=0; i < cancelar_modificar.length; i++) {
    cancelar_modificar[i].addEventListener("click", function() {
        cerrar_resena("formulario_modificar_resena", i)
    }
)}

function cerrar_resena(formulario, i) { 
    document.getElementsByClassName(formulario)[i].style.display = "none"
}