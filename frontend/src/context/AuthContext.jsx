import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { supabase } from '../services/supabaseClient'
const AuthContext=createContext(null)
export function AuthProvider({children}){
 const [session,setSession]=useState(null),[profile,setProfile]=useState(null),[loading,setLoading]=useState(true)
 const loadProfile=async user=>{ if(!user){setProfile(null);return} const {data,error}=await supabase.from('perfiles').select('*').eq('id',user.id).maybeSingle(); if(error) console.warn('[CyberLey] perfil:',error.message); setProfile(data||null)}
 useEffect(()=>{let mounted=true; supabase.auth.getSession().then(async({data})=>{if(!mounted)return; setSession(data.session); await loadProfile(data.session?.user); setLoading(false)}); const {data:listener}=supabase.auth.onAuthStateChange(async(_e,s)=>{setSession(s);await loadProfile(s?.user);setLoading(false)}); return()=>{mounted=false;listener.subscription.unsubscribe()}},[])
 const signOut=()=>supabase.auth.signOut()
 const value=useMemo(()=>({session,user:session?.user||null,profile,loading,signOut,refreshProfile:()=>loadProfile(session?.user)}),[session,profile,loading])
 return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext)
