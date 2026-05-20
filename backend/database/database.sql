CREATE DATABASE restaurante;
USE restaurante

CREATE TABLE usuarios(
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    numero VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL
);
CREATE TABLE reservas(
    id_reserva INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    id_usuario INT NOT NULL,
    fecha DATETIME NOT NULL,

    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
);