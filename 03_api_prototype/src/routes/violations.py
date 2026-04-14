from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Query
# Pastikan ViolationSummary di ppe_schemas.py sudah memiliki field 'by_shift'
# Gunakan baris baru ini (sesuai folder models dan file ppe_models):
from src.models.ppe_models import PaginatedViolations, ViolationSummary, ViolationResponse

router = APIRouter(prefix="/api/v1/violations", tags=["Violations"])

# Mock Database untuk Prototipe
MOCK_VIOLATIONS = [
    ViolationResponse(
        id=f"viol-00{i}",
        camera_id=f"cam-0{1 if i % 2 == 0 else 2}-zone-a",
        timestamp=datetime.utcnow(),
        violation_types=["no_helmet"] if i % 2 == 0 else ["no_safety_vest"],
        employee_id="emp-102" if i % 3 == 0 else None,
        employee_name="Felix Santoso" if i % 3 == 0 else "Unknown"
    ) for i in range(1, 26)
]

@router.get("/", response_model=PaginatedViolations)
async def get_violations(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    camera_id: Annotated[Optional[str], Query()] = None,
    violation_type: Annotated[Optional[str], Query()] = None,
    # TAMBAHAN: Filter Date Range sesuai PDF
    start_date: Annotated[Optional[datetime], Query()] = None,
    end_date: Annotated[Optional[datetime], Query()] = None,
):
    """Mengambil daftar pelanggaran dengan filter dan pagination."""
    filtered_data = MOCK_VIOLATIONS

    if camera_id:
        filtered_data = [v for v in filtered_data if v.camera_id == camera_id]
    if violation_type:
        filtered_data = [v for v in filtered_data if violation_type in v.violation_types]
    
    # Logic tambahan untuk filter tanggal jika diperlukan
    if start_date:
        filtered_data = [v for v in filtered_data if v.timestamp >= start_date]
    if end_date:
        filtered_data = [v for v in filtered_data if v.timestamp <= end_date]

    start_idx = (page - 1) * limit
    paginated_data = filtered_data[start_idx : start_idx + limit]

    return PaginatedViolations(
        total_count=len(filtered_data),
        page=page,
        limit=limit,
        data=paginated_data
    )

@router.get("/summary", response_model=ViolationSummary)
async def get_violations_summary():
    """Mengambil ringkasan statistik agregat dari pelanggaran (Tipe, Zona, Shift)."""
    return ViolationSummary(
        by_type={"no_helmet": 12, "no_safety_vest": 13},
        by_zone={"area_welding": 13, "area_assembly": 12},
        # TAMBAHAN: Breakdown per Shift sesuai instruksi PDF halaman 3
        by_shift={
            "shift_1_pagi": 10,
            "shift_2_siang": 8,
            "shift_3_malam": 7
        }
    )