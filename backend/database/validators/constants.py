import os
from dotenv import load_dotenv

load_dotenv()

# URL base de la API
BASE_URL = '/' # Modificar

# Formato de fecha esperado por la API
FORMATO_FECHA = '%Y-%m-%d'


# Configuracion de la base de datos MySQL (levantada via docker-compose)
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306')) # Modificar
DB_USER     = os.getenv('DB_USER', '') # Modificar
DB_PASSWORD = os.getenv('DB_PASSWORD', '') # Modificar
DB_NAME     = os.getenv('DB_NAME', '') # Modificar
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Codigos de error
ERROR_CODE_INVALID_BODY        = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE   = 'invalid.max.value'
ERROR_CODE_ALUMNO_NOT_FOUND    = 'alumno.not.found'
ERROR_CODE_MATERIA_NOT_FOUND   = 'materia.not.found'