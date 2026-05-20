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
CREATE TABLE ranking_usuarios(
    id_ranking INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    id_usuario INT NOT NULL,
    cant_cancelaciones INT,

    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
);
CREATE TABLE reseñas(
    id_comentario INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    id_usuario INT NOT NULL,
    comentario TEXT,
    valoracion INT NOT NULL,

    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
);
CREATE TABLE categorias(
    id_categoria INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nombre_categoria VARCHAR(50) NOT NULL
);
