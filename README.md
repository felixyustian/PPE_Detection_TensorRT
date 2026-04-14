# 🛡️ PPE Compliance Monitoring System: AI Edge Architecture



---



## 📌 Executive Summary



Repositori ini menyajikan solusi rekayasa arsitektur *Machine Learning* *end-to-end* untuk sistem pemantauan Alat Pelindung Diri (APD/PPE) terpusat. Sistem ini dirancang secara spesifik untuk dieksekusi di lingkungan *Edge Computing* (NVIDIA Jetson Orin AGX 64 GB), dengan target pemrosesan berkinerja tinggi: melayani 15 aliran kamera CCTV 1080p secara simultan pada 15 FPS.



Pendekatan yang diambil dalam repositori ini melampaui sekadar pelatihan model. Solusi ini mencakup **analisis profil perangkat keras tingkat lanjut**, **evaluasi degradasi presisi (Quantization)**, dan pembuatan **API Gateway produksi** menggunakan arsitektur *Non-blocking I/O*.



---



## 🗂️ Struktur Repositori



Repositori ini dibagi menjadi tiga domain utama yang merepresentasikan siklus hidup (*lifecycle*) pengembangan AI di skala *Enterprise*:



```text

synapsis-ppe-assessment/

│

├── README.md                      # Dokumentasi utama (Anda di sini)

│

├── 01_system_design/              # BAGIAN A: Arsitektur & Perencanaan Skala

│   └── pipeline_proposal.md       # Proposal topologi sistem, hitungan latensi & I/O

│

├── 02_model_experiment/           # BAGIAN B: Eksperimen, Kuantisasi & Analisis Tensor

│   ├── benchmark_notebook.ipynb   # Colab Notebook terintegrasi (Eksperimen + Live API Demo)

│   ├── layer_analysis.md          # Analisis empiris PyTorch Hooks untuk Layer Collapse

│   └── metrics_export.csv         # Data benchmark riil (FP32 vs FP16 vs INT8)

│

└── 03_api_prototype/              # BAGIAN C: Production-Ready API (FastAPI)

    ├── pyproject.toml             # Konfigurasi package & linter modern (uv, ruff)

    ├── src/                       # Source code berbasis Domain-Driven Design (DDD)

    │   ├── main.py

    │   ├── api/routes/

    │   └── models/

    └── tests/                     # Unit test otomatis menggunakan Pytest

```



---



## 🔬 Sorotan Rekayasa (Engineering Highlights)



### 1. Desain Pipeline Edge (Bagian A)

Sistem dirancang untuk menahan beban I/O ekstrem dari 15 kamera. Strategi batching dinamis dan manajemen memori GPU diusulkan agar batas anggaran latensi (Latency Budget) ≤ 66.7 ms per batch dapat terpenuhi dengan mulus di atas arsitektur TensorRT.



### 2. Evaluasi Kuantisasi & "Layer Collapse" (Bagian B)

Melalui benchmarking dinamis pada arsitektur YOLOv11s, ditemukan bahwa:



* Sweet Spot (ROI Maksimal): Kuantisasi ke presisi FP16 berhasil memangkas latensi secara masif (dari 7.71 ms menjadi 2.89 ms) sekaligus mereduksi penggunaan VRAM hingga ~50% (dari 39.8 MB menjadi 20.1 MB) tanpa mengalami degradasi mAP50-95 sama sekali (stabil di 0.11). Ini menjadikan YOLOv11s FP16 sebagai kandidat absolut untuk produksi.



* Unjustified INT8 Trade-off: Kuantisasi ke INT8 memberikan penghematan waktu sebesar 0.51 ms (turun ke 2.38 ms), namun memicu degradasi akurasi (mAP turun ke 0.09). Mengingat latensi FP16 sudah sangat jauh di bawah batas Latency Budget, FP16 dipertahankan demi keandalan deteksi.



* Predictive Tensor Analysis: Menggunakan injeksi `PyTorch Forward Hooks`, dibuktikan secara matematis bahwa kegagalan INT8 (clipping error) tidak murni terjadi di Detection Head, melainkan berakar dari anomali Dynamic Range ekstrem di area Early Backbone (`model.1.conv`), yang memicu hilangnya fitur spasial mikro pada APD berukuran kecil.



### 3. API Gateway Skala Produksi (Bagian C)

Purwarupa backend dibangun menggunakan FastAPI dengan standar industri:



* Domain-Driven Design (DDD): Pemisahan skema Pydantic v2, antarmuka routing, dan logika bisnis.



* Asynchronous Processing: Menggunakan `BackgroundTasks` untuk mendelegasikan komputasi berat (seperti inferensi TensorRT atau ekstraksi wajah) agar tidak memblokir antrean HTTP.



* Cloudflare Tunnel Integration: Integrasi tunneling otomatis langsung dari dalam Jupyter Notebook untuk mengekspos Swagger UI/ReDoc ke web publik tanpa bentrok sesi.



---



## 🚀 Panduan Eksekusi (Quick Start)

### Opsi 1: Interactive Live Demo

Anda dapat menjalankan keseluruhan siklus (mulai dari kalibrasi model hingga memunculkan server API secara langsung) tanpa melakukan konfigurasi lokal.



* Buka `02_model_experiment/benchmark_notebook.ipynb` menggunakan Google Colab: <br>

[https://colab.research.google.com/drive/1VTZDTQAuaP7oxl2MD_vZCucJgWOdQJWi?usp=sharing](https://colab.research.google.com/drive/1VTZDTQAuaP7oxl2MD_vZCucJgWOdQJWi?usp=sharing)



* Jalankan eksekusi dari atas ke bawah (Run All).



* Di cell block paling bawah, skrip akan membangun sebuah terowongan asinkron menggunakan Cloudflare. Klik tautan `.trycloudflare.com/doc` yang muncul di output untuk berinteraksi langsung dengan API yang ditenagai oleh environment Colab tersebut.



### 🚀 Contoh Output API

Sistem mengembalikan data pelanggaran dalam format JSON yang terstruktur, memudahkan integrasi dengan dasbor pelaporan pusat:



```json

// Sample Response dari GET /api/v1/violations

[

  {

    "id": "v01",

    "camera_id": "cam-01",

    "violation_types": ["no_helmet"]

  },

  {

    "id": "v02",

    "camera_id": "cam-02",

    "violation_types": ["no_safety_vest"]

  }

]

```



### Opsi 2: Eksekusi API secara Lokal (Local Development)

Untuk menguji arsitektur backend secara terisolasi dengan linter standar produksi:



```Bash

# 1. Masuk ke direktori API

cd 03_api_prototype



# 2. Setup virtual environment menggunakan manajer paket `uv`

uv venv

source .venv/bin/activate  # Untuk Windows: .venv\Scripts\activate

uv pip install -e ".[dev]"



# 3. Jalankan unit tests

pytest tests/



# 4. Jalankan server lokal

uvicorn src.main:app --reload

```



Akses dokumentasi interaktif di: `http://localhost:8000/docs`



---



## ⚖️ Lisensi & Hak Cipta (License & Copyright)



*   **Hak Cipta Implementasi:** © 2026 Felix Yustian Setiono. Seluruh arsitektur sistem, kode API (*source code*), dan dokumen analisis eksperimen dalam repositori ini adalah hak kekayaan intelektual asli milik penulis.
