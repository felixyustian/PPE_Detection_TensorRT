# PPE Compliance API Prototype (Bagian C)

API ini dirancang dengan FastAPI menggunakan prinsip **Domain-Driven Design**, arsitektur *non-blocking I/O* via `BackgroundTasks`, dan divalidasi dengan `pytest`.

## Persiapan Environment (Menggunakan `uv`)

1. **Install dependensi:**
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"

### 🧪 Testing
Jalankan perintah berikut untuk memvalidasi integritas API dan skema model:
```bash
pytest tests/