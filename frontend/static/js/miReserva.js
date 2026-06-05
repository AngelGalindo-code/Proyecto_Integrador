function abrirModal(id){

    const modal = document.getElementById(id);

    if(modal){
        modal.classList.add('modal--open');
        modal.setAttribute('aria-hidden', 'false');
    }
}

function cerrarModal(id){

    const modal = document.getElementById(id);

    if(modal){
        modal.classList.remove('modal--open');
        modal.setAttribute('aria-hidden', 'true');

    }
}

window.addEventListener('keydown', function(event){

    if(event.key === 'Escape'){
        document.querySelectorAll('.modal--open').forEach(function(modalAbierto){
            cerrarModal(modalAbierto.id)
        });
    }
});