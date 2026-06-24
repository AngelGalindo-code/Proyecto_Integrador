// 1. Capturamos todos los formularios de eliminación de la tabla
const formulariosEliminar = document.querySelectorAll('.form-eliminar-admin');

formulariosEliminar.forEach(function(formulario) {
    formulario.addEventListener('submit', function(event) {
        const confirmar = confirm('¿Estás seguro de que querés cancelar esta reserva? ');
        if (!confirmar) {
            event.preventDefault(); 
        }
        
    });
});