import { createClient } from '@supabase/supabase-js'
import { env } from '../config/env'
if (!env.supabaseUrl || !env.supabaseKey) throw new Error('Faltan VITE_SUPABASE_URL y VITE_SUPABASE_PUBLISHABLE_KEY.')
export const supabase = createClient(env.supabaseUrl, env.supabaseKey, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
})
