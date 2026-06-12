const form = document.getElementById('registroForm');


form.addEventListener('submit', function(event) {
   
    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const telefono = document.getElementById('telefono').value;

   
    if (nombre === "" || email === "" || telefono === "") {
        event.preventDefault(); 
        alert("Por favor, completa todos los campos antes de ingresar.");
    }
});