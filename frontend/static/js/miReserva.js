const formCancelar = document.getElementById('form-cancelar') || document.querySelector('.form-eliminar-admin');

if (formCancelar) {
    formCancelar.addEventListener('submit', function(event) {
        //Frenamos el envío automático del formulario
        event.preventDefault();
        const confirmar = confirm('¿Estás seguro de que deseas cancelar definitivamente esta reserva?');
    
        if (confirmar) {
            formCancelar.submit(); 
        }
    });
}