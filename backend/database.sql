CREATE DATABASE restaurante;
USE restaurante;

CREATE TABLE platos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(255) NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    imagen VARCHAR(255)
);