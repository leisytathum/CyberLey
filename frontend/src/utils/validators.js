export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    value.trim()
  );
}

export function validateAge(value) {
  const age = Number(value);

  if (!Number.isInteger(age)) {
    return "La edad debe ser un número entero.";
  }

  if (age < 10) {
    return "La edad mínima permitida es 10 años.";
  }

  if (age > 100) {
    return "La edad máxima permitida es 100 años.";
  }

  return "";
}

export function passwordChecks(password) {
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
}

export function isStrongPassword(password) {
  return Object.values(
    passwordChecks(password)
  ).every(Boolean);
}