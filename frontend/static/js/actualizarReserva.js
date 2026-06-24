const formModificar = document.getElementById('form-modificar');
const datosContenedores = document.getElementsByClassName('dato_ingreso');

formModificar.addEventListener('submit', function(event) {
    event.preventDefault();

    const erroresViejos = document.querySelectorAll('.error-mensaje');
    erroresViejos.forEach(error => error.remove());

    const nombre = document.getElementById('nombre').value.trim();
    const fechaInput = document.getElementById('fecha').value;
    const personas = parseInt(document.getElementById('cantidad_personas').value);

    let tieneErrores = false;

    if (nombre.length < 3) {
        crearError("El nombre debe tener al menos 3 letras.", datosContenedores[0]);
        tieneErrores = true;
    }
    if (fechaInput) {
        const fechaReserva = new Date(fechaInput + "T00:00:00");
        const fechaHoy = new Date();
        fechaHoy.setHours(0,0,0,0); 

        if (fechaReserva < fechaHoy) {
            crearError("La fecha no puede ser anterior al día de hoy.", datosContenedores[1]);
            tieneErrores = true;
        }
    }

    if (personas <= 0 || personas > 30) {
        crearError("La cantidad de personas debe ser entre 1 y 30.", datosContenedores[4]);
        tieneErrores = true;
    }
    if (!tieneErrores) {
        const boton = document.getElementById('btn-guardar-cambios');
        if (boton) {
            boton.disabled = true;
            boton.innerText = "Guardando...";
        }
        formModificar.submit(); 
    }
});
function crearError(mensaje, contenedor) {
    const errorSpan = document.createElement("span");
    errorSpan.textContent = mensaje;
    errorSpan.classList.add("error-mensaje"); 
    errorSpan.style.color = "red";
    errorSpan.style.fontSize = "12px";
    errorSpan.style.display = "block";
    errorSpan.style.marginTop = "5px";
    contenedor.appendChild(errorSpan);
}