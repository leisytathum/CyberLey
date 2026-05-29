from supabase import create_client, Client

# =========================
# DATOS DE SUPABASE
# =========================

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# LOGIN SIMPLE
# =========================

email = input("Correo: ")
password = input("Contraseña: ")

try:

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    user = response.user

    print("\n✅ Login exitoso")
    print(f"Usuario conectado: {user.email}")

except Exception as e:

    print("\n❌ Error")
    print(e)