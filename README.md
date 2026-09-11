# Stock de Insumos — API local v2.1

Backend local en **FastAPI + SQLite** + frontend mobile-first servido en `/`.
Maneja insumos, movimientos (entradas / salidas / ajustes), pedidos, alertas de
bajo stock, configuracion (FX, servicios, umbral) e importacion / exportacion
de datos.

Por default la API **no pide login** (uso local en una sola maquina). Se puede
reactivar la autenticacion seteando `AUTH_DISABLED=0` antes de levantar uvicorn.

> **No toca los archivos originales.** Excel, HTML viejo y `fotos_insumos/`
> quedan tal cual. Para revertir, borra la carpeta `api/`.

---

## Estructura

```
STOCK DE INSUMOS/
├── Stock_Insumos_App.html              (sin tocar - tu app original)
├── Stock_Insumos_Dashboard.xlsx        (sin tocar - fuente de la migracion)
├── Plantilla_Importar_Insumos.xlsx     (sin tocar - usada por /plantilla)
├── fotos_insumos/                      (sin tocar - servido en /fotos)
└── api/
    ├── main.py            # FastAPI + endpoints
    ├── auth.py            # JWT + bcrypt + AUTH_DISABLED (default 1)
    ├── database.py        # SQLAlchemy → sqlite
    ├── models.py          # Insumo, Movimiento, Pedido, Config, Usuario
    ├── schemas.py         # Pydantic v2
    ├── migrate.py         # Crea esquema + ALTER TABLE idempotente + seed admin
    ├── requirements.txt
    ├── stock.db           # se crea / actualiza al correr migrate.py
    ├── uploads/           # fotos subidas via API
    └── static/
        └── index.html     # frontend SPA mobile-first conectado a la API
```

## Levantar la API

```powershell
cd "C:\Users\Bioingenieria\Documents\Claude\Projects\STOCK DE INSUMOS\api"
pip install -r requirements.txt
python migrate.py
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Despues abri en el navegador:
- **Frontend nuevo (SPA mobile)** → http://localhost:8000/    ← entra directo, sin login
- **Docs interactivos**          → http://localhost:8000/docs
- **HTML viejo (sigue intacto)** → doble-click en `Stock_Insumos_App.html`

> ⚠ **No abras** `api/static/index.html` con doble-click — al cargarlo como
> `file://` el navegador no puede hablar con la API y vas a ver "Failed to
> fetch". Siempre entra por `http://localhost:8000/`.

## Login deshabilitado por default

Para uso local la API arranca con **auth deshabilitada** (`AUTH_DISABLED=1`).
El frontend entra directo y todos los movimientos quedan firmados con el
usuario virtual `local` (rol admin).

Para **reactivar** el login (util si la API queda expuesta en la red):

```powershell
$env:AUTH_DISABLED = "0"
$env:JWT_SECRET = "una-frase-secreta-larga-aleatoria"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Con `AUTH_DISABLED=0`, los endpoints exigen un JWT. La primera vez que corres
`migrate.py` se crea un usuario admin con:

| Campo      | Valor        |
| ---------- | ------------ |
| usuario    | `admin`      |
| contrasena | `admin1234`  |

Cambialo despues via `POST /auth/users`.

## Variables de entorno

| Variable           | Default        | Para que sirve                          |
| ------------------ | -------------- | --------------------------------------- |
| `AUTH_DISABLED`    | `1` (apagada)  | Si es `0`, exige JWT en cada request.   |
| `JWT_SECRET`       | dev secret     | Solo se usa con `AUTH_DISABLED=0`.      |
| `JWT_EXPIRE_HOURS` | `12`           | Vida del token (horas).                 |

---

## Endpoints (resumen)

### Auth
- `POST /auth/login`, `GET /auth/me`, `GET/POST /auth/users` (estos dos ultimos requieren rol admin si auth esta on)

### Insumos
- `GET /insumos`, `GET /insumos/bajo-stock`, `GET /insumos/{id}`
- `POST /insumos`, `PATCH /insumos/{id}` (cambios de stock generan AJUSTE automatico)
- `DELETE /insumos/{id}` (admin), `GET/POST /insumos/{id}/foto`

### Movimientos
- `GET /movimientos` (filtros: `q`, `tipo`, `servicio`, `insumo_id`, `desde`, `hasta`, `limit`)
- `POST /movimientos`, `GET/POST /insumos/{id}/movimientos`, `DELETE /movimientos/{id}`
- Tipos: `IN` (suma), `OUT` (resta), `AJUSTE` (setea stock absoluto)

### Pedidos
- `GET/POST /pedidos`, `DELETE /pedidos/{id}`, `GET /pedidos/sugerencia`

### Config
- `GET /config`, `PUT /config`

### Import / Export
- `GET /plantilla`, `POST /import/excel` (admin)
- `GET /backup`, `POST /backup?mode=merge|replace` (admin)

---

## Migracion / upgrades

`python migrate.py` es seguro de correr cuantas veces quieras:
- Crea las tablas que falten.
- Corre `ALTER TABLE` solo si la columna nueva no existe (`stock_minimo` en
  `insumos`, `usuario` en `movimientos`).
- Crea el usuario admin solamente si la tabla `usuarios` esta vacia.
- Si el Excel original existe, hace upsert por nombre. Si no existe, lo saltea
  sin error.

## Como revertir
Borra la carpeta `api/`. Tu Excel, el HTML viejo y las fotos no se tocaron.
