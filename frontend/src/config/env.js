export const env = {
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
  apiUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
}
if (!env.supabaseUrl || !env.supabaseKey) console.warn('[CyberLey] Falta configurar Supabase en frontend/.env')
