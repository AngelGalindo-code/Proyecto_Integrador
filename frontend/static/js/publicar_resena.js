//iluminar estrellas y las validaciones

const estrellas = document.getElementById("estrellas")
const estrellitas = document.getElementsByClassName("iluminable")


estrellas.addEventListener("click", function(event) {
    iluminar_estrellas()
    //faltan los posibles errores
})

function iluminar_estrellas(){
    let n = encontrar_llamado()
    for (let i=0; i<=5; i++){
        if (i < n) {
            estrellitas[i].textContent = "★";
        } else {
            estrellitas[i].textContent = "☆";
        }
    }

}

function encontrar_llamado(){ 
    let n = 0

    for (let i=1; i<=5; i++){
        if (document.getElementById(`estrellas${i}`).checked){
            n = i
        }
    }
    return n
}