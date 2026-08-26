import axios from 'axios'
import { env } from '../config/env'
import { supabase } from './supabaseClient'
const api=axios.create({baseURL:env.apiUrl,timeout:30000})
const getCache=new Map()
const inFlightGets=new Map()
api.interceptors.request.use(async config=>{const {data}=await supabase.auth.getSession(); const token=data.session?.access_token; if(token) config.headers.Authorization=`Bearer ${token}`; if((config.method||'get').toLowerCase()!=='get')getCache.clear(); return config})
api.interceptors.response.use(r=>r, e=>{const detail=e.response?.data?.detail;if(!e.response){const message=e.code==='ECONNABORTED'?'El servidor tardó demasiado en responder.':'No se pudo conectar con el backend. Verifica que FastAPI esté ejecutándose.';return Promise.reject(new Error(message))}return Promise.reject(new Error(typeof detail==='string'?detail:e.message||'Error de conexión'))})
const rawGet=api.get.bind(api)
api.cachedGet=async(url,config={},ttl=60000)=>{const {data}=await supabase.auth.getSession();const userId=data.session?.user?.id||"anon";const key=`${userId}:${url}:${JSON.stringify(config.params||{})}`;const saved=getCache.get(key);if(saved&&Date.now()-saved.at<ttl)return saved.response;if(inFlightGets.has(key))return inFlightGets.get(key);const request=rawGet(url,config).then(response=>{getCache.set(key,{at:Date.now(),response});return response}).finally(()=>inFlightGets.delete(key));inFlightGets.set(key,request);if(saved){request.catch(()=>{});return saved.response}return request}
api.get=(url,config)=>api.cachedGet(url,config)
export default api
