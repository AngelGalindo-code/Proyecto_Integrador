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



// Iluminar estrellas
const cont_estrellas = document.getElementsByClassName("contenedor_estrellas")

for (let i = 0; i < cont_estrellas.length; i++) {
    cont_estrellas[i].addEventListener("click", function(event) {
        iluminar_estrellas(cont_estrellas[i])
    }
)}


function iluminar_estrellas(cont_estrellas){
    let n = encontrar_llamado(cont_estrellas)

    const estrellitas = cont_estrellas.getElementsByClassName("iluminable")

    for (let i=0; i<estrellitas.length; i++){
        if (i < n) {
            estrellitas[i].textContent = "★";
        } else {
            estrellitas[i].textContent = "☆";
        }
    }

}

function encontrar_llamado(cont_estrellas){ 
    let n = 0

    const estrellas = cont_estrellas.getElementsByClassName("estrellas")

    for (let i=0; i<estrellas.length; i++){
        if (estrellas[i].checked){
            n = i + 1
        }
    }
    return n
}
