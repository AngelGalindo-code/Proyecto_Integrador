const inputFecha = document.querySelector(".fecha input");
const inputComensales = document.querySelector(".comensales input");
const inputNombre = document.querySelector(".nombre input");
const inputNumero = document.querySelector(".numero input");
const botonReserva = document.querySelector("button"); 
const bloqueSector = document.querySelector("section");
const comensalesMaximas = 12;
const comensalesMinimos = 1;

inputFecha.addEventListener("focus", function(){
    if (inputFecha.value === ""){
        this.type = "datetime-local";
    }
});
inputFecha.addEventListener("blur", function(){
    if (inputFecha.value === ""){
        this.type = "text";
    }
});

botonReserva.style.marginBottom = "2px";
bloqueSector.style.height = "600px";

botonReserva.addEventListener("click", function(evento) {
    evento.preventDefault();
    let inputsInvalidos = [];
    if (inputFecha.value === ""){
        inputsInvalidos.push("Fecha");
    }
    if (inputComensales.value === ""){
        inputsInvalidos.push("N° de comensales");
    } else if (inputComensales.value < comensalesMinimos || inputComensales.value > comensalesMaximas){
        inputsInvalidos.push("N° de comensales (1-12 personas)");
    }
    if (inputNombre.value === ""){
        inputsInvalidos.push("Nombre");
    } else if (!/^[a-zA-Z\s]+$/.test(inputNombre.value)){
        inputsInvalidos.push("Nombre Invalido")
    }
    if (inputNumero.value === ""){
        inputsInvalidos.push("Telefono");
    } else if (!/^\d+$/.test(inputNumero.value) || inputNumero.value.length !== 10){
        inputsInvalidos.push("Telefono invalido");
    }
    let mesajeGeneral = document.getElementById("error-general");
    if (inputsInvalidos.length > 0){
        if (!mesajeGeneral){
            mesajeGeneral = document.createElement("p");
            mesajeGeneral.id = "error-general";
            mesajeGeneral.style.color = "red"
            mesajeGeneral.style.fontSize = "13px";
            mesajeGeneral.style.textAlign = "center";
            botonReserva.after(mesajeGeneral);
        }
        mesajeGeneral.textContent = "Completar: " + inputsInvalidos.join(" | ");
    } else {
        if (mesajeGeneral) {
            mesajeGeneral.remove();
        }
    }
});