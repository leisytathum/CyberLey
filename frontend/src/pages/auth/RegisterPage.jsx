import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../../services/supabaseClient'

export default function RegisterPage() {
  const nav = useNavigate()
  const [form, setForm] = useState({
    nombre: '', edad: 18, genero: 'Seleccionar', ciudad: '',
    nivel_educativo: 'Seleccionar', email: '', password: '',
  })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  async function submit(e) {
    e.preventDefault()
    setError(''); setMsg('')
    if (form.genero === 'Seleccionar' || form.nivel_educativo === 'Seleccionar') {
      setError('Selecciona género y nivel educativo.'); return
    }
    setLoading(true)
    const { error } = await supabase.auth.signUp({
      email: form.email.trim(),
      password: form.password,
      options: {
        data: {
          nombre_completo: form.nombre.trim(),
          edad: Number(form.edad),
          genero: form.genero,
          ciudad: form.ciudad.trim(),
          nivel_educativo: form.nivel_educativo,
        },
      },
    })
    setLoading(false)
    if (error) { setError(error.message); return }
    setMsg('Cuenta creada correctamente. Ya puedes iniciar sesión.')
    setTimeout(() => nav('/login'), 1200)
  }

  return <div className="authPage">
    <section className="authIntro"><div className="logoCircle">C</div><h1>Únete a CyberLey</h1><p>Evalúa tus hábitos digitales y recibe una orientación de riesgo.</p></section>
    <form className="authCard" onSubmit={submit}>
      <h2>Crear cuenta</h2>
      <label>Nombre completo<input name="nombre" value={form.nombre} onChange={change} required /></label>
      <label>Edad<input name="edad" type="number" min="10" max="100" value={form.edad} onChange={change} required /></label>
      <label>Género<select name="genero" value={form.genero} onChange={change}><option>Seleccionar</option><option>Femenino</option><option>Masculino</option><option>Prefiero no decirlo</option><option>Otro</option></select></label>
      <label>Ciudad<input name="ciudad" value={form.ciudad} onChange={change} required /></label>
      <label>Nivel educativo<select name="nivel_educativo" value={form.nivel_educativo} onChange={change}><option>Seleccionar</option><option>Primaria</option><option>Secundaria</option><option>Universitario</option><option>Posgrado</option><option>Otro</option></select></label>
      <label>Correo electrónico<input name="email" type="email" value={form.email} onChange={change} required /></label>
      <label>Contraseña<input name="password" type="password" minLength="6" value={form.password} onChange={change} required /></label>
      {error && <div className="errorBox">{error}</div>}{msg && <div className="successBox">{msg}</div>}
      <button className="primary" disabled={loading}>{loading ? 'Creando…' : 'Registrarme'}</button>
      <p><Link to="/login">Volver al inicio de sesión</Link></p>
    </form>
  </div>
}
