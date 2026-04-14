from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import violations, employees

app = FastAPI(
    title="PPE Compliance REST API",
    description="API Gateway untuk Sistem Pemantauan APD PT Synapsis",
    version="1.0.0",
)

# Konfigurasi CORS agar bisa diakses oleh frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(violations.router)
app.include_router(employees.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint untuk orkestrator (misal: Kubernetes/Docker) mengecek status layanan."""
    return {"status": "ok", "service": "synapsis-ppe-api"}