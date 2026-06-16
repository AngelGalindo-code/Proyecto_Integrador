// Funcionalidad al boton de cancelar el envio de formulario:

const formCancelar = document.getElementById('form-cancelar');

formCancelar.addEventListener('submit', async function(event) {
    
    event.preventDefault();
    const confirmar = confirm('¿Estás seguro de que deseas cancelar definitivamente esta reserva?');
    if (!confirmar) return;

    const url = formCancelar.action;

    try {
        const respuesta = await fetch(url, {
            method: 'POST' 
        });

        // Status code == 200
        if (respuesta.ok) {
            alert('Reserva eliminada correctamente.');
            
            window.location.href = '/'; // Lo manda al inicio
        } else {
            alert('Error de servidor');
        }

    } catch (error) {
        console.error('Error de servidor:', error);
        alert('No se pudo conectar con el servidor. Revisá tu conexión.');
    }
});