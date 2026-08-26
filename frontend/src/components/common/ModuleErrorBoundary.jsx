import { Component } from "react";

export default class ModuleErrorBoundary extends Component {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error, details) {
    console.error("[CyberLey módulo]", error, details);
  }

  render() {
    if (this.state.failed) {
      return (
        <section className="moduleState">
          <h2>No fue posible mostrar este módulo</h2>
          <p>La navegación sigue disponible. Puedes recargarlo sin cerrar sesión.</p>
          <button className="moduleButton" onClick={() => window.location.reload()}>
            Recargar módulo
          </button>
        </section>
      );
    }
    return this.props.children;
  }
}
