# Login / Registro (Flask + HTML/JS + CSV)

## Ejecutar (Windows, PowerShell)
```powershell
cd C:\Users\Usuario\Documents\luisk\Py\login
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Abrir: http://127.0.0.1:5000

## Estructura
```
app.py              Backend (API + sirve el frontend)
frontend/           login.html, registro.html, bienvenida.html, styles.css, validaciones.js
data/usuarios.csv   Se crea al registrar el primer usuario
```

## Reglas de validación (frontend y backend)
| Campo | Regla |
|---|---|
| Nombre / Apellido | Solo letras (con tildes/ñ) y espacios, 2–50 |
| Documento | Solo números, 6–10 dígitos |
| Fecha de nacimiento | Fecha válida, no futura, edad 18–120 |
| Email | Formato correo, sin espacios |
| Contraseña | 8–30, al menos 1 mayúscula, 1 minúscula, 1 número |
| Teléfono | Solo números, 10 dígitos |

- Los campos de letras/números bloquean caracteres no permitidos al escribir.
- Email y documento no se pueden repetir (HTTP 409).
- La contraseña se guarda con hash (no en texto plano).
- `/bienvenida` sin sesión redirige a `/login`.

## API
| Método | Ruta | Respuesta |
|---|---|---|
| POST | /api/registro | 201 ok · 400 validación · 409 duplicado |
| POST | /api/login | 200 ok · 400 datos inválidos · 401 credenciales |
| GET | /api/me | 200 con sesión · 401 sin sesión |
| POST | /api/logout | 200 |

Todos los elementos tienen `data-testid` para automatizar con Playwright
(ej. `login-email`, `login-submit`, `registro-documento`, `bienvenida-nombre`).
