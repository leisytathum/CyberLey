import { createRoot } from "react-dom/client";
import { Toaster } from "sonner";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

import "./styles/global.css";
import "./styles/auth.css";
import "./styles/user.css";
import "./styles/loading.css";

createRoot(document.getElementById("root")).render(
  <ThemeProvider>
    <AuthProvider>
      <App />

      <Toaster
        richColors
        position="top-right"
        closeButton
      />
    </AuthProvider>
  </ThemeProvider>
);
