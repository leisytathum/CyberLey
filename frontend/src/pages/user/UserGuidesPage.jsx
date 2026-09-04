import { useEffect, useMemo, useState } from "react";
import { FiArrowRight, FiBookOpen, FiCheck, FiCheckCircle, FiSearch, FiShield, FiX } from "react-icons/fi";
import { toast } from "sonner";
import { State } from "../../components/common/ModuleUI";
import api from "../../services/api";

export default function UserGuidesPage() {
  const [rows, setRows] = useState([]), [loading, setLoading] = useState(true), [error, setError] = useState(""), [query, setQuery] = useState(""), [category, setCategory] = useState("todas"), [selected, setSelected] = useState(null), [saving, setSaving] = useState(false);
  useEffect(() => { api.cachedGet("/guias", {}, 0).then(({ data }) => setRows(data.items || [])).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false)); }, []);
  const categories = useMemo(() => [...new Set(rows.map((item) => item.categoria).filter(Boolean))], [rows]);
  const visibleRows = useMemo(() => { const normalized = query.trim().toLocaleLowerCase("es"); return rows.filter((item) => { const text = `${item.titulo || ""} ${item.descripcion || ""} ${item.contenido || ""}`.toLocaleLowerCase("es"); return (category === "todas" || item.categoria === category) && (!normalized || text.includes(normalized)); }); }, [category, query, rows]);

  async function completeGuide() {
    if (!selected || selected.completada) return;
    setSaving(true);
    try {
      await api.post(`/guias/${selected.id_guia}/completar`);
      const update = (item) => item.id_guia === selected.id_guia ? { ...item, completada: true } : item;
      setRows((current) => current.map(update)); setSelected((current) => ({ ...current, completada: true }));
      toast.success("Guía marcada como completada.");
    } catch (requestError) { toast.error(requestError.message); }
    finally { setSaving(false); }
  }

  if (loading) return <State loading />;
  if (error) return <State error={error} />;
  return <div className="userGuidesPage">
    <section className="userPageHero userGuidesHero"><div><span className="userSectionLabel">CENTRO DE APRENDIZAJE</span><h2>Convierte recomendaciones en hábitos seguros</h2><p>Contenido práctico creado para ayudarte a proteger tus cuentas, dispositivos e información.</p></div><div className="userHeroStat"><FiBookOpen /><strong>{rows.length}</strong><span>guías disponibles</span></div></section>
    <section className="userResourceToolbar"><label><FiSearch /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar una guía..." /></label><select value={category} onChange={(event) => setCategory(event.target.value)} aria-label="Filtrar por categoría"><option value="todas">Todas las categorías</option>{categories.map((item) => <option value={item} key={item}>{item}</option>)}</select></section>
    {!rows.length ? <State empty emptyText="No hay guías disponibles todavía." /> : !visibleRows.length ? <State empty emptyText="No encontramos guías con esos filtros." /> : <div className="userGuideGrid">{visibleRows.map((item) => <article className="userGuideCard" key={item.id_guia}><div className="userGuideCardTop"><span className="userGuideIcon"><FiShield /></span>{item.completada && <span className="userCompletedBadge"><FiCheck /> Completada</span>}</div><span className="userGuideMeta">{item.categoria || "Ciberseguridad"} · {item.nivel_recomendado || "Todos los niveles"}</span><h3>{item.titulo}</h3><p>{item.descripcion}</p><button type="button" onClick={() => setSelected(item)}>Leer guía <FiArrowRight /></button></article>)}</div>}
    {selected && <div className="moduleModal userGuideModal" onClick={() => setSelected(null)} role="presentation"><article className="moduleModalContent" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="guide-title"><button className="userModalClose" type="button" onClick={() => setSelected(null)} aria-label="Cerrar"><FiX /></button><span className="userGuideIcon"><FiBookOpen /></span><span className="userSectionLabel">{selected.categoria || "GUÍA DE SEGURIDAD"}</span><h2 id="guide-title">{selected.titulo}</h2><p className="userGuideLead">{selected.descripcion}</p>{selected.contenido && <div className="guideContent">{selected.contenido}</div>}{selected.archivo_url && <a className="userPrimaryButton" href={selected.archivo_url} target="_blank" rel="noreferrer">Abrir recurso <FiArrowRight /></a>}<footer><button type="button" className={selected.completada ? "userSecondaryButton" : "userPrimaryButton"} disabled={saving || selected.completada} onClick={completeGuide}><FiCheckCircle /> {selected.completada ? "Guía completada" : saving ? "Guardando..." : "Marcar como completada"}</button></footer></article></div>}
  </div>;
}
