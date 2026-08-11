import axios from 'axios'
import { env } from '../config/env'
import { supabase } from './supabaseClient'
const api=axios.create({baseURL:env.apiUrl,timeout:30000})
api.interceptors.request.use(async config=>{const {data}=await supabase.auth.getSession(); const token=data.session?.access_token; if(token) config.headers.Authorization=`Bearer ${token}`; return config})
api.interceptors.response.use(r=>r, e=>{const detail=e.response?.data?.detail; return Promise.reject(new Error(typeof detail==='string'?detail:e.message||'Error de conexión'))})
export default api
