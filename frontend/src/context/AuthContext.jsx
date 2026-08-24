import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { supabase } from "../services/supabaseClient";

const AuthContext = createContext(null);
const PROFILE_CACHE_KEY = "cyberley_profile";
const profileRequests = new Map();

function readCachedProfile(userId) {
  try {
    const saved = JSON.parse(localStorage.getItem(PROFILE_CACHE_KEY));
    return saved?.userId === userId ? saved.profile : null;
  } catch {
    return null;
  }
}

function cacheProfile(userId, profile) {
  localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify({ userId, profile }));
}

async function requestProfile(userId) {
  if (!profileRequests.has(userId)) {
    const request = supabase
      .from("perfiles")
      .select("*")
      .eq("id", userId)
      .maybeSingle()
      .then(({ data, error }) => {
        if (error) throw error;
        return data;
      })
      .finally(() => profileRequests.delete(userId));
    profileRequests.set(userId, request);
  }
  return profileRequests.get(userId);
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadProfile(user) {
    if (!user) {
      setProfile(null);
      return null;
    }
    const data = await requestProfile(user.id);
    if (data) {
      setProfile(data);
      cacheProfile(user.id, data);
    }
    return data;
  }

  useEffect(() => {
    let mounted = true;

    async function hydrate(nextSession) {
      if (!mounted) return;
      setSession(nextSession);
      if (!nextSession?.user) {
        setProfile(null);
        localStorage.removeItem(PROFILE_CACHE_KEY);
        setLoading(false);
        return;
      }

      const cached = readCachedProfile(nextSession.user.id);
      if (cached) {
        setProfile(cached);
        setLoading(false);
        loadProfile(nextSession.user).catch(() => {});
        return;
      }

      try {
        await loadProfile(nextSession.user);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    supabase.auth.getSession().then(({ data }) => hydrate(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      hydrate(nextSession);
    });

    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  const signOut = async () => {
    localStorage.removeItem(PROFILE_CACHE_KEY);
    return supabase.auth.signOut();
  };

  const value = useMemo(
    () => ({
      session,
      user: session?.user || null,
      profile,
      loading,
      signOut,
      refreshProfile: loadProfile,
    }),
    [session, profile, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
