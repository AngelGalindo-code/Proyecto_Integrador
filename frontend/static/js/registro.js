const boton_ingresar = document.getElementById("boton_ingresar")
const datos = document.getElementsByClassName("dato_ingreso")
const errores = document.getElementsByClassName("error")

boton_ingresar.addEventListener("click", function(event) {
    event.preventDefault()

    while (errores.length > 0) {
        errores[0].remove()
    }

    const nombre_usuario = document.getElementById("usuario").value.trim()
    const email_usuario = document.getElementById("email").value.trim()
    const telefono_usuario = document.getElementById("telefono").value.trim()

    if (nombre_usuario == "") {
        crearError("Este campo debe estar completo", datos[0])
    } else if (nombre_usuario.length <= 4 || nombre_usuario.length >= 15) {
        crearError("El nombre debe tener entre 4 a 15 letras", datos[0])
    }

    
    const regexGmail = /^[a-zA-Z0-9._-]+@gmail\.com$/i

    if (email_usuario == "") {
        crearError("Este campo debe estar completo", datos[1])
    } else if (!regexGmail.test(email_usuario)) {
        crearError("El email debe ser una cuenta de Gmail válida (ejemplo@gmail.com)", datos[1])
    }


    if (telefono_usuario == "") {
        crearError("Este campo debe estar completo", datos[2])
    } else if (isNaN(telefono_usuario)) {
      
        crearError("El telefono debe contener solo numeros", datos[2])
    }


    if (errores.length == 0) {
        event.target.form.submit()
    }
})

function crearError(mensaje, contenedor) {
    const error = document.createElement("span")
    error.textContent = mensaje
    error.classList.add("error")
    contenedor.appendChild(error)
}