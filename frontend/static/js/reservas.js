const formulariosEliminar = document.querySelectorAll('.form-eliminar-admin');

formulariosEliminar.forEach(function(formulario) {
    
    formulario.addEventListener('submit', async function(event) {
        
        event.preventDefault();
        const confirmar = confirm('¿Seguro que queres cancelar esta reserva?');

        if (!confirmar) return; 
        const url = formulario.action;

        try {
            const respuesta = await fetch(url, {
                method: 'POST'
            });

            if (respuesta.ok) {
                alert('Reserva cancelada con exito.');
                const filaTabla = formulario.closest('tr');
                
                filaTabla.remove(); 

            } else {
                alert('Error en el servidor al intentar eliminar la reserva.');
            }

        } catch (error) {
            console.error('Error de red:', error);
            alert('Error de conexion con el servidor.');
        }
    });
});

// Arreglar las tildes