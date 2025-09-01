# 🏪 COSATECA

[![Django](https://img.shields.io/badge/Django-5.2.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/)

## 📖 Descripción

**COSATECA** es una plataforma web desarrollada en Django que facilita la gestión y alquiler de objetos comunitarios. El sistema permite a los usuarios descubrir, reservar y gestionar herramientas, equipos y objetos diversos disponibles en diferentes almacenes comunitarios, promoviendo la economía circular y el uso sostenible de recursos.

### ✨ Características Principales

- 🏢 **Gestión de Almacenes**: Administración completa de almacenes con ubicación geográfica y horarios
- 📦 **Catálogo de Objetos**: Sistema de catalogación con categorías, condiciones y huella de carbono
- 👥 **Gestión de Usuarios**: Sistema de autenticación con roles diferenciados (usuarios, gestores, administradores)
- 📅 **Sistema de Reservas**: Alquiler de objetos con control de fechas y disponibilidad
- ⭐ **Sistema de Valoraciones**: Calificación y comentarios de objetos y almacenes
- 🚨 **Sistema de Denuncias**: Moderación de contenido con categorización de reportes
- 💚 **Lista de Deseos**: Funcionalidad para guardar objetos favoritos
- 🌱 **Impacto Ambiental**: Tracking de huella de carbono de los objetos

## 🏗️ Arquitectura del Sistema

### Aplicaciones Django

- **`core`**: Modelos base y funcionalidades compartidas
- **`usuario`**: Gestión de usuarios, autenticación y perfiles
- **`almacen`**: Gestión de almacenes, ubicaciones y horarios
- **`objeto`**: Catálogo de objetos, valoraciones y denuncias
- **`alquiler`**: Sistema de reservas y alquileres

### Modelos Principales

```
Usuario (AbstractUser)
├── Gestor (hereda de Usuario)
└── Administrador (permisos de Django)

Almacen
├── Localizacion (OneToOne)
├── Horario (ForeignKey)
└── Objeto (ForeignKey)

Objeto
├── ObjetoValoracion (ForeignKey)
└── ObjetoValoracionDenuncia (ForeignKey)

Alquiler
├── Usuario (ForeignKey)
└── Objeto (ForeignKey)
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/COSATECA-TFG/Cosateca.git
cd Cosateca
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
CLOUD_NAME='tu_cloudinary_name'
CLOUD_API_KEY='tu_cloudinary_api_key'
CLOUD_API_SECRET='tu_cloudinary_api_secret'
```

### 5. Configurar Base de Datos

Asegúrate de tener PostgreSQL ejecutándose y actualiza la configuración en `settings.py` si es necesario.

### 6. Ejecutar Migraciones

```bash
cd cosateca
python manage.py migrate
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor

```bash
python manage.py runserver
```

El proyecto estará disponible en `http://localhost:8000/`

## 📋 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| Django | 5.2.1 | Framework web principal |
| psycopg2-binary | 2.9.10 | Conector PostgreSQL |
| cloudinary | 1.44.1 | Gestión de imágenes en la nube |
| django-cloudinary-storage | 0.3.0 | Integración Cloudinary con Django |
| Pillow | 11.2.1 | Procesamiento de imágenes |
| python-dotenv | 1.1.1 | Gestión de variables de entorno |

## 🛠️ Estructura del Proyecto

```
cosateca/
├── manage.py                 # Script de gestión de Django
├── cosateca/                 # Configuración principal
│   ├── settings.py          # Configuraciones
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuración WSGI
├── core/                     # Aplicación core
│   ├── models.py            # Modelos base
│   └── decorators.py        # Decoradores personalizados
├── usuario/                  # Gestión de usuarios
│   ├── models.py            # Usuario, Gestor
│   ├── views.py             # Vistas de autenticación
│   └── forms.py             # Formularios de usuario
├── almacen/                  # Gestión de almacenes
│   ├── models.py            # Almacen, Localizacion, Horario
│   └── views.py             # Vistas de almacenes
├── objeto/                   # Catálogo de objetos
│   ├── models.py            # Objeto, ObjetoValoracion
│   └── views.py             # Vistas de objetos
├── alquiler/                 # Sistema de reservas
│   ├── models.py            # Alquiler
│   └── views.py             # Vistas de alquileres
└── media/                    # Archivos multimedia
```

## 🧪 Testing

Para ejecutar las pruebas:

```bash
python manage.py test
```

Para ejecutar pruebas de una aplicación específica:

```bash
python manage.py test almacen
python manage.py test usuario
python manage.py test objeto
python manage.py test alquiler
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

**Proyecto COSATECA** - Universidad de Sevilla
- 🔗 GitHub: [COSATECA-TFG](https://github.com/COSATECA-TFG)

## 🙏 Agradecimientos

- [Django Project](https://djangoproject.com/) por el excelente framework
- [Cloudinary](https://cloudinary.com/) por el servicio de gestión de imágenes
- Universidad de Sevilla por el apoyo académico
