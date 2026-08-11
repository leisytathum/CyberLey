import {
  FiCheckCircle,
  FiCircle,
} from "react-icons/fi";

import {
  passwordChecks,
} from "../../utils/validators";

export default function PasswordStrength({
  password,
}) {
  const checks = passwordChecks(password);

  const items = [
    ["length", "Al menos 8 caracteres"],
    ["uppercase", "Una letra mayúscula"],
    ["lowercase", "Una letra minúscula"],
    ["number", "Un número"],
    ["special", "Un símbolo"],
  ];

  if (!password) return null;

  return (
    <div className="passwordRequirements">
      <span>La contraseña debe incluir:</span>

      {items.map(([key, label]) => {
        const completed = checks[key];

        return (
          <div
            key={key}
            className={
              completed
                ? "passwordRequirement completed"
                : "passwordRequirement"
            }
          >
            {completed ? (
              <FiCheckCircle />
            ) : (
              <FiCircle />
            )}

            {label}
          </div>
        );
      })}
    </div>
  );
}