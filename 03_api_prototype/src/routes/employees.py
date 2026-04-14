import uuid
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from src.schemas.ppe_schemas import EmployeeCreateResponse

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])

async def extract_face_embedding(employee_id: str, image_bytes: bytes):
    """Simulasi proses ekstraksi wajah asinkron (komputasi GPU)."""
    await asyncio.sleep(2) # Mensimulasikan delay inferensi
    print(f"[BACKGROUND TASK] Selesai ekstrak embedding untuk: {employee_id}")

@router.post("/", response_model=EmployeeCreateResponse, status_code=201)
async def create_employee(
    background_tasks: BackgroundTasks,
    name: str = Form(..., description="Nama karyawan"),
    department: str = Form(..., description="Departemen"),
    photo: UploadFile = File(..., description="Foto wajah referensi")
):
    """Mendaftarkan karyawan baru dan memproses fitur wajah di latar belakang."""
    if not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar.")
    
    image_bytes = await photo.read()
    new_emp_id = f"emp-{str(uuid.uuid4())[:8]}"
    
    # Delegasi tugas berat ke background
    background_tasks.add_task(extract_face_embedding, new_emp_id, image_bytes)
    
    return EmployeeCreateResponse(
        message="Karyawan terdaftar. Ekstraksi wajah diproses di latar belakang.",
        employee_id=new_emp_id
    )