const btnEnviar = document.getElementById('btn-enviar-correo');
const idReserva = document.getElementById('reserva-id').innerText.replace('#', '');

btnEnviar.addEventListener('click', async function() {
    
    // Corrergir las faltas de tildes
    btnEnviar.innerText = 'Enviando';
    btnEnviar.disabled = true; 

    try {
        
        const respuesta = await fetch(`/reservas/${idReserva}/enviarcorreo`, {  // Con '' no me lee la variable. Usarn ``
            method: 'POST'
        });

        if (respuesta.ok) {
            alert('¡Comprobante enviado con exito a tu correo electronico registrados!');
            btnEnviar.innerText = '¡Enviado con exito!';
        } else {
            alert('No se pudo enviar el correo. Intentá nuevamente más tarde.');
            btnEnviar.innerText = 'Enviar comprobante al email';
            btnEnviar.disabled = false;
        }

    } catch (error) {
        console.error('Error de red:', error);
        alert('Error de conexion con el servidor.');
        btnEnviar.innerText = 'Enviar comprobante al email';
        btnEnviar.disabled = false;
    }
});