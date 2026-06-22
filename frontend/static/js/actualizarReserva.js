const formModificar = document.getElementById('form-modificar');


formModificar.addEventListener('submit', async function(event) {
    
    event.preventDefault();
    const url = formModificar.action;
    const datosFormulario = new FormData(formModificar);

    try {
        const respuesta = await fetch(url, {
            method: 'POST',
            body: datosFormulario 
        });
        if (respuesta.ok) {
            alert('¡Reserva modificada con exito!');
            window.location.href = respuesta.url; 
        } else {
            alert('Hubo un problema en el servidor al intentar modificar la reserva.');
        }

    } catch (error) {
        console.error('Error de servidor:', error);
        alert('No se pudo conectar con el servidor. Revise tu conexion de internet.');
    }
});