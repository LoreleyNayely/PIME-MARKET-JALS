
# 🛒 PYME Market - Sistema de Microservicios

Este sistema se compone de 4 microservicios desarrollados en **FastAPI**, y una **interfaz frontend en React**, organizados con una arquitectura limpia y desacoplada. Cada microservicio cuenta con su **propia base de datos** y configuración independiente.

---

## 🚀 Microservicios

| Servicio  | Puerto | Descripción                                                                    |
| --------- | ------ | ------------------------------------------------------------------------------ |
| Auth      | 8000   | Registro, login, generación y validación de tokens JWT, hashing de contraseñas |
| Productos | 8001   | CRUD completo de productos                                                     |
| Orders    | 8002   | Gestión de pedidos, carrito y generación de comprobantes                       |
| Chat      | 8003   | Comunicación en tiempo real vía WebSocket y almacenamiento de mensajes         |

---

## ✅ Requisitos Previos

* Python 3.10+
* Node.js 18+
* PostgreSQL (o base de datos definida por cada microservicio)
* Git
* PowerShell (en Windows) o Terminal (Linux/macOS)

---

## 📦 Estructura de carpetas

```
PYME-MARKET/
│
├── pyme-market-auth/      # Microservicio de autenticación
├── pyme-market-products/  # Microservicio de productos
├── pyme-market-orders/    # Microservicio de órdenes
├── pyme-market-chat/      # Microservicio de chat
└── pyme-market/              # Proyecto en React
```

---

## ⚙️ Levantamiento de un microservicio

### 1. Clonar el repositorio (si no lo has hecho)

```bash
git clone (https://github.com/LoreleyNayely/PIME-MARKET-JALS.git)
```

Debes repetir los siguientes pasos en **cada carpeta de microservicio** (`pyme-market-auth`, `pyme-market-products`, etc.).
### 1 . Ingresar a la carpeta correspondiente del microservicio

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno

* **Windows (PowerShell):**

  ```bash
  .\venv\Scripts\Activate.ps1
  ```

* **Linux/macOS:**

  ```bash
  source venv/bin/activate
  ```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear archivo `.env`

Dentro del directorio del microservicio, crea un archivo `.env` con la configuración adecuada. Por ejemplo:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/db_auth
SECRET_KEY=clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ Cambia los valores según corresponda para cada microservicio.

---

## 🧱 Probar conexión en la base de datos postgres y crear solo las tablas, tener en cuente que se debe considerar las variables de entorno 

## ▶️ Levantar el microservicio

Una vez creadas las tablas:

```bash
uvicorn app.main:app --port <puerto_correspondiente> --reload
```

Ejemplos:

```bash
uvicorn app.main:app --port 8000 --reload  # Auth
uvicorn app.main:app --port 8001 --reload  # Productos
uvicorn app.main:app --port 8002 --reload  # Orders
uvicorn app.main:app --port 8003 --reload  # Chat
```

---

## 🖥️ Frontend

### 1. Ir a la carpeta `pyme-market`:

```bash
cd ../pyme-market
```

### 2. Instalar dependencias:

```bash
npm install
```

### 3. Levantar React:

```bash
npm run dev
```

---

## 🧪 Tests

Cada microservicio puede tener tests con `pytest`. Para ejecutarlos:

```bash
pytest
```

---


