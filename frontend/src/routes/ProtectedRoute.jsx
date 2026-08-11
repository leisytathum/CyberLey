import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function ProtectedRoute({roles}){const {user,profile,loading}=useAuth(); if(loading)return <div className="center">Cargando sesión…</div>; if(!user)return <Navigate to="/login" replace/>; if(roles?.length && !roles.includes(profile?.rol)) return <Navigate to="/usuario" replace/>; return <Outlet/>}
