// Reglas de validación compartidas por login y registro (iguales al backend).
const REGLAS = {
  nombre:   { re: /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{2,50}$/, msg: "Solo letras y espacios (2 a 50 caracteres)." },
  apellido: { re: /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{2,50}$/, msg: "Solo letras y espacios (2 a 50 caracteres)." },
  documento:{ re: /^\d{6,10}$/, msg: "Solo números (6 a 10 dígitos)." },
  email:    { re: /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/, msg: "Correo electrónico inválido." },
  telefono: { re: /^\d{10}$/, msg: "Solo números (10 dígitos)." },
  password: { re: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,30}$/, msg: "Mínimo 8 caracteres, con mayúscula, minúscula y número." },
};

// Filtros de escritura: impiden teclear caracteres no permitidos.
const FILTROS = {
  letras:  /[^A-Za-zÁÉÍÓÚáéíóúÑñÜü ]/g,
  numeros: /\D/g,
  sinEspacios: /\s/g,
};

function aplicarFiltros(form) {
  form.querySelectorAll("[data-filtro]").forEach((input) => {
    input.addEventListener("input", () => {
      const limpio = input.value.replace(FILTROS[input.dataset.filtro], "");
      if (limpio !== input.value) input.value = limpio;
    });
  });
}

function validarFecha(valor) {
  if (!valor) return "La fecha de nacimiento es obligatoria.";
  const nac = new Date(valor + "T00:00:00");
  const hoy = new Date();
  if (nac > hoy) return "La fecha no puede ser futura.";
  let edad = hoy.getFullYear() - nac.getFullYear();
  const m = hoy.getMonth() - nac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) edad--;
  if (edad < 18 || edad > 120) return "Debes tener entre 18 y 120 años.";
  return "";
}

function validarCampo(input) {
  const nombre = input.name;
  const valor = input.value.trim();
  let msg = "";
  if (!valor) msg = "Este campo es obligatorio.";
  else if (nombre === "fecha_nacimiento") msg = validarFecha(valor);
  else if (REGLAS[nombre] && !REGLAS[nombre].re.test(valor)) msg = REGLAS[nombre].msg;
  mostrarError(input, msg);
  return !msg;
}

function mostrarError(input, msg) {
  input.classList.toggle("invalido", !!msg);
  const span = document.getElementById("error-" + input.name);
  if (span) span.textContent = msg;
}

function validarFormulario(form) {
  let ok = true;
  form.querySelectorAll("input").forEach((i) => { if (!validarCampo(i)) ok = false; });
  return ok;
}

function alerta(el, texto, tipo) {
  el.textContent = texto;
  el.className = "alerta " + tipo;
}
