export function isValidEmail(value) {
  const email =
    normalizeEmail(value);

  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    email
  );
}

export function calculateAge(birthDate) {
  if (!birthDate) return null;

  const today = new Date();
  const birth = new Date(`${birthDate}T00:00:00`);

  let age =
    today.getFullYear() -
    birth.getFullYear();

  const monthDifference =
    today.getMonth() -
    birth.getMonth();

  if (
    monthDifference < 0 ||
    (
      monthDifference === 0 &&
      today.getDate() < birth.getDate()
    )
  ) {
    age--;
  }

  return age;
}

export function validateBirthDate(birthDate) {
  if (!birthDate) {
    return "Selecciona tu fecha de nacimiento.";
  }

  const age = calculateAge(birthDate);

  if (age === null) {
    return "Selecciona una fecha válida.";
  }

  if (age < 14) {
    return "Debes tener al menos 14 años para registrarte.";
  }

  if (age > 100) {
    return "Ingresa una fecha de nacimiento válida.";
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
    noSpaces: !/\s/.test(password),
  };
}

export function isStrongPassword(password) {
  return Object.values(
    passwordChecks(password)
  ).every(Boolean);
}

export function normalizeEmail(email) {
  return email
    .trim()
    .toLowerCase();
}