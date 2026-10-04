"""Backend sencillo: registro y login de usuarios guardados en CSV."""
import csv
import os
import re
from datetime import date

from flask import Flask, jsonify, request, send_from_directory, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONT_DIR = os.path.join(BASE_DIR, "frontend")
CSV_PATH = os.path.join(BASE_DIR, "data", "usuarios.csv")
CAMPOS = ["nombre", "apellido", "documento", "fecha_nacimiento", "email", "telefono", "password_hash"]

app = Flask(__name__, static_folder=None)
app.secret_key = "clave-solo-para-pruebas-locales"

# ---------- Reglas de validación (las mismas que el frontend) ----------
RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{2,50}$")
RE_DOCUMENTO = re.compile(r"^\d{6,10}$")
RE_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$")
RE_TELEFONO = re.compile(r"^\d{10}$")
RE_PASSWORD = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,30}$")


def validar_registro(d):
    errores = {}
    for campo in ("nombre", "apellido"):
        if not RE_NOMBRE.match(d.get(campo, "").strip()):
            errores[campo] = "Solo letras y espacios (2 a 50 caracteres)."
    if not RE_DOCUMENTO.match(d.get("documento", "")):
        errores["documento"] = "Solo números (6 a 10 dígitos)."
    try:
        nac = date.fromisoformat(d.get("fecha_nacimiento", ""))
        hoy = date.today()
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
        if nac > hoy:
            errores["fecha_nacimiento"] = "La fecha no puede ser futura."
        elif edad < 18 or edad > 120:
            errores["fecha_nacimiento"] = "Debes tener entre 18 y 120 años."
    except ValueError:
        errores["fecha_nacimiento"] = "Fecha inválida."
    if not RE_EMAIL.match(d.get("email", "").strip()):
        errores["email"] = "Correo electrónico inválido."
    if not RE_PASSWORD.match(d.get("password", "")):
        errores["password"] = "Mínimo 8 caracteres, con mayúscula, minúscula y número."
    if not RE_TELEFONO.match(d.get("telefono", "")):
        errores["telefono"] = "Solo números (10 dígitos)."
    return errores


# ---------- CSV ----------
def leer_usuarios():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def guardar_usuario(u):
    nuevo = not os.path.exists(CSV_PATH)
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        w.writerow(u)


# ---------- API ----------
@app.post("/api/registro")
def registro():
    d = request.get_json(silent=True) or {}
    errores = validar_registro(d)
    if errores:
        return jsonify(ok=False, errores=errores), 400

    email = d["email"].strip().lower()
    usuarios = leer_usuarios()
    if any(u["email"] == email for u in usuarios):
        return jsonify(ok=False, errores={"email": "Este correo ya está registrado."}), 409
    if any(u["documento"] == d["documento"] for u in usuarios):
        return jsonify(ok=False, errores={"documento": "Este documento ya está registrado."}), 409

    guardar_usuario({
        "nombre": d["nombre"].strip(),
        "apellido": d["apellido"].strip(),
        "documento": d["documento"],
        "fecha_nacimiento": d["fecha_nacimiento"],
        "email": email,
        "telefono": d["telefono"],
        "password_hash": generate_password_hash(d["password"]),
    })
    return jsonify(ok=True, mensaje="Usuario registrado correctamente."), 201


@app.post("/api/login")
def login():
    d = request.get_json(silent=True) or {}
    email = d.get("email", "").strip().lower()
    password = d.get("password", "")
    if not RE_EMAIL.match(email) or not password:
        return jsonify(ok=False, mensaje="Ingresa un correo y contraseña válidos."), 400

    usuario = next((u for u in leer_usuarios() if u["email"] == email), None)
    if not usuario or not check_password_hash(usuario["password_hash"], password):
        return jsonify(ok=False, mensaje="Correo o contraseña incorrectos."), 401

    session["usuario"] = f'{usuario["nombre"]} {usuario["apellido"]}'
    return jsonify(ok=True, nombre=session["usuario"])


@app.get("/api/me")
def me():
    if "usuario" not in session:
        return jsonify(ok=False), 401
    return jsonify(ok=True, nombre=session["usuario"])


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


# ---------- Frontend ----------
@app.get("/")
def raiz():
    return redirect("/login")


@app.get("/login")
def pagina_login():
    return send_from_directory(FRONT_DIR, "login.html")


@app.get("/registro")
def pagina_registro():
    return send_from_directory(FRONT_DIR, "registro.html")


@app.get("/bienvenida")
def pagina_bienvenida():
    if "usuario" not in session:
        return redirect("/login")
    return send_from_directory(FRONT_DIR, "bienvenida.html")


@app.get("/static/<path:archivo>")
def estaticos(archivo):
    return send_from_directory(FRONT_DIR, archivo)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
