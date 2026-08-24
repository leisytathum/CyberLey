export function Metrics({ items }) {
  return <section className="moduleMetrics">{items.map(({ label, value }) => <article className="moduleMetric" key={label}><span>{label}</span><strong>{value ?? 0}</strong></article>)}</section>;
}

export function State({ loading, error, empty, emptyText = "No hay registros para mostrar." }) {
  if (loading) return <div className="moduleSkeleton" aria-label="Actualizando contenido"><span /><span /><span /></div>;
  if (error) return <div className="warningBox">{error}</div>;
  if (empty) return <div className="moduleState">{emptyText}</div>;
  return null;
}

export function PageHeading({ eyebrow, title, children }) {
  return <div className="pageTitle"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{children}</p></div></div>;
}

export function downloadBase64(value, filename, mime = "application/octet-stream") {
  const bytes = Uint8Array.from(atob(value), character => character.charCodeAt(0));
  const url = URL.createObjectURL(new Blob([bytes], { type: mime }));
  const link = document.createElement("a"); link.href = url; link.download = filename; link.click(); URL.revokeObjectURL(url);
}
