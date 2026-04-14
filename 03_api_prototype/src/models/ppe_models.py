from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ViolationResponse(BaseModel):
    id: str = Field(..., example="viol-5f8a-9b12")
    camera_id: str = Field(..., example="cam-01-zone-a")
    timestamp: datetime
    violation_types: List[str] = Field(..., example=["no_helmet", "no_safety_vest"])
    employee_id: Optional[str] = Field(None, example="emp-102")
    employee_name: Optional[str] = Field(None, example="Felix Santoso")

class PaginatedViolations(BaseModel):
    total_count: int = Field(..., example=150)
    page: int = Field(..., example=1)
    limit: int = Field(..., example=20)
    data: List[ViolationResponse]

class ViolationSummary(BaseModel):
    by_type: dict[str, int] = Field(..., example={"no_helmet": 45, "no_mask": 12})
    by_zone: dict[str, int] = Field(..., example={"zone_a": 30, "zone_b": 27})

class EmployeeCreateResponse(BaseModel):
    message: str = Field(..., example="Karyawan terdaftar. Ekstraksi wajah diproses.")
    employee_id: str = Field(..., example="emp-103")

class ViolationSummary(BaseModel):
    by_type: dict[str, int] = Field(..., example={"no_helmet": 45, "no_mask": 12})
    by_zone: dict[str, int] = Field(..., example={"zone_a": 30, "zone_b": 27})
    # TAMBAHAN: Rekapitulasi per Shift kerja
    by_shift: dict[str, int] = Field(..., example={"shift_1": 40, "shift_2": 15, "shift_3": 20})