//iluminar estrellas

const estrellas = document.getElementById("estrellas")
const estrellitas = document.getElementsByClassName("iluminable")

estrellas.addEventListener("click", function(event) {
    iluminar_estrellas()
})

function iluminar_estrellas(){
    let n = encontrar_llamado()
    for (let i=0; i<=5; i++){
        if (i < n) {
            estrellitas[i].textContent = "★";
        } else {
            estrellitas[i].textContent = "☆";
        }
    }

}

function encontrar_llamado(){ 
    let n = 0

    for (let i=1; i<=5; i++){
        if (document.getElementById(`estrellas${i}`).checked){
            n = i
        }
    }
    return n
}

//cerrar formulario y las validaciones

cancelar_posteo = document.getElementById("cerrar_ventana")
publicar_posteo = document.getElementById("boton_publicar")

const errores = document.getElementsByClassName("error")

cancelar_posteo.addEventListener("click", function(event) {
    cerrarResena()
})


publicar_posteo.addEventListener("click", function(event) {
      event.preventDefault()

    while (errores.length > 0) {
        errores[0].remove()
    }

    if (encontrar_llamado() == 0) {
        error_valoracion("Debe dejar una valoración", estrellas)
    }
   
    if (errores.length == 0) {
        event.target.form.submit()
        cerrarResena()
    }
})

function cerrarResena() { 
    document.getElementById("formulario_resena").style.display = "none"
}

function error_valoracion(mensaje, contenedor) {
    const error = document.createElement("span")
    error.textContent = mensaje
    error.classList.add("error")
    contenedor.appendChild(error)
}