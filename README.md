# Sistema de Gestión de Reservas - Los Horneros

## Descripción General

El Sistema de Gestión de Reservas - Los Horneros es una plataforma web diseñada para automatizar el proceso de reservas, administración del menú y seguimiento de métricas operativas del restaurante.

La aplicación está dividida en dos servicios independientes, Frontend y Backend, desplegados mediante Docker para garantizar portabilidad, escalabilidad y facilidad de instalación.

---

# Arquitectura del Sistema

La solución se compone de dos módulos principales que se comunican mediante una API RESTful.

## Frontend (Puerto 8080)

Aplicación desarrollada con Flask encargada de la interacción con los usuarios.

### Funcionalidades

* Renderizado de plantillas HTML mediante Jinja2.
* Gestión de formularios de reservas.
* Comunicación con la API Backend mediante Requests.
* Generación dinámica de códigos QR.
* Envío de correos electrónicos con información de reservas.

## Backend (Puerto 10599)

API RESTful responsable de la lógica de negocio y el acceso a los datos.

### Funcionalidades

* Gestión de reservas.
* Gestión de usuarios.
* Administración de platos y categorías.
* Registro de reseñas.
* Generación de métricas para administración.
* Conexión segura a MySQL mediante SSL.

---

# Características Principales

## Despliegue Contenerizado

* Uso de Docker para aislar dependencias.
* Configuración centralizada mediante variables de entorno.
* Fácil despliegue en distintos entornos.

## Dashboard Administrativo

Visualización de métricas relevantes para la gestión del restaurante:

* Comensales del día.
* Reservas activas.
* Índice de cancelaciones.
* Información estadística general.

## Sistema de Confirmación por QR

El sistema genera un código QR único para cada reserva:

1. El cliente realiza una reserva.
2. Se genera un QR asociado a dicha reserva.
3. El QR se envía por correo electrónico.
4. El personal escanea el código al momento del ingreso.
5. La asistencia queda registrada automáticamente.

---

# Tecnologías Utilizadas

## Frontend

* Python
* Flask
* Jinja2
* Requests
* Pillow

## Backend

* Python
* Flask
* PyMySQL
* MySQL (Aiven Cloud)

## Infraestructura

* Docker
* Docker Compose

---

# Estructura del Proyecto

```text
Proyecto_Integrador/
│
├── backend/
│   ├── certificates/
│   │   └── ca.pem
│   │
│   ├── database/
│   │   ├── conexion.py
│   │   ├── queries.py
│   │   ├── database.sql
│   │   └── queries_entidades/
│   │
│   ├── routes/
│   │
│   ├── .env
│   └── app.py
│
├── frontend/
│   ├── decorators/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   ├── validaciones/
│   │
│   ├── app.py
│   ├── constantes.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── .dockerignore
├── .env
├── .gitignore
└── docker-compose.yml
```

---

# Descripción de Directorios

| Directorio            | Descripción                              |
| --------------------- | ---------------------------------------- |
| backend/routes        | Endpoints de la API RESTful.             |
| backend/database      | Conexión y consultas a la base de datos. |
| backend/certificates  | Certificados SSL para conexión segura.   |
| frontend/routes       | Rutas y vistas de la aplicación web.     |
| frontend/templates    | Plantillas HTML renderizadas con Jinja2. |
| frontend/static       | Archivos CSS, JavaScript e imágenes.     |
| frontend/decorators   | Decoradores personalizados.              |

---

# Requisitos Previos

Para ejecutar el proyecto localmente es necesario contar con:

* Docker Engine 20.10 o superior.
* Docker Compose v2.

El sistema fue desarrollado y probado sobre GNU/Linux Ubuntu.

---

# Configuración del Entorno

Crear un archivo `.env` con las variables de entorno necesarias.

## Ejemplo

```env
# Base de Datos
DB_HOST=mysql-loshorneros-los-horneros-db.l.aivencloud.com
DB_PORT=10599
DB_USER=avnadmin
DB_PASSWORD=password_enviado_por_privado
DB_NAME=defaultdb

# Seguridad
SECRET_KEY=tu_secret_key

# Correo
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
```

> Importante: No subir el archivo `.env` al repositorio.

---

# Despliegue Local

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_Integrador
```

## 2. Agregar permisos para Docker

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 3. Construir e iniciar los contenedores

```bash
docker compose up -d --build
```

## 4. Verificar el estado de los servicios

```bash
docker compose ps
```

## 5. Visualizar logs

```bash
docker compose logs -f
```

## 6. Visualizar logs del Frontend

```bash
docker compose logs -f frontend
```

---

# Puertos Utilizados

| Servicio | Puerto |
| -------- | ------ |
| Frontend | 8080   |
| Backend  | 10599  |

---

# Flujo General de Reserva

1. El usuario accede al sistema.
2. Completa el formulario de reserva.
3. El Frontend envía la solicitud al Backend.
4. El Backend registra la reserva en MySQL.
5. Se genera un código QR único.
6. El personal valida la reserva escaneando el código.
7. La asistencia queda registrada en el sistema.

---

# Autor

Proyecto Integrador – Sistema de Gestión de Reservas para Restaurante Los Horneros.
