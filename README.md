# 🛡️ PPE Compliance Monitoring System: AI Edge Architecture

---

## 📌 Executive Summary

This repository presents an end-to-end Machine Learning architectural solution for a centralized Personal Protective Equipment (PPE) monitoring system. This system is specifically designed for execution in an Edge Computing environment (NVIDIA Jetson Orin AGX 64 GB), targeting high-performance processing: serving 15 simultaneous 1080p CCTV camera streams at 15 FPS.

The approach taken in this repository goes beyond basic model training. The solution encompasses **advanced hardware profiling analysis**, **precision degradation evaluation (Quantization)**, and the creation of a **production-ready API Gateway** utilizing a Non-blocking I/O architecture.

---

## 🗂️ Repository Structure

This repository is divided into three main domains representing the AI development lifecycle at an Enterprise scale:

```text
ppe-compliance-system/
│
├── README.md                      # Main documentation (You are here)
│
├── 01_system_design/              # PART A: Architecture & Scale Planning
│   └── pipeline_proposal.md       # System topology proposal, latency & I/O calculations
│
├── 02_model_experiment/           # PART B: Experimentation, Quantization & Tensor Analysis
│   ├── benchmark_notebook.ipynb   # Integrated Colab Notebook (Experiment + Live API Demo)
│   ├── layer_analysis.md          # Empirical analysis of PyTorch Hooks for Layer Collapse
│   └── metrics_export.csv         # Real-world benchmark data (FP32 vs FP16 vs INT8)
│
└── 03_api_prototype/              # PART C: Production-Ready API (FastAPI)
    ├── pyproject.toml             # Modern package & linter configuration (uv, ruff)
    ├── src/                       # Source code based on Domain-Driven Design (DDD)
    │   ├── main.py
    │   ├── api/routes/
    │   └── models/
    └── tests/                     # Automated unit tests using Pytest

```

---



## 🔬 Engineering Highlights



### 1. Edge Pipeline Design (Part A)

The system is designed to withstand extreme I/O loads from 15 cameras. Dynamic batching strategies and GPU memory management are proposed to ensure the Latency Budget (≤ 66.7 ms per batch) is seamlessly met on top of the TensorRT architecture.



### 2. Quantization Evaluation & "Layer Collapse" (Part B)

Through dynamic benchmarking on the YOLOv11s architecture, it was discovered that:



* Sweet Spot (Maximum ROI): Quantization to FP16 precision successfully slashed latency massively (from 7.71 ms to 2.89 ms) while simultaneously reducing VRAM usage by ~50% (from 39.8 MB to 20.1 MB) without experiencing any mAP50-95 degradation (stable at 0.11). This makes YOLOv11s FP16 the absolute candidate for production.


* Unjustified INT8 Trade-off: Quantization to INT8 provided a time savings of 0.51 ms (down to 2.38 ms) but triggered accuracy degradation (mAP dropped to 0.09). Given that the FP16 latency is already well below the Latency Budget, FP16 is retained for detection reliability.


* Predictive Tensor Analysis: Utilizing `PyTorch Forward Hooks` injection, it was mathematically proven that the INT8 failure (clipping error) did not purely occur in the Detection Head, but was rooted in extreme Dynamic Range anomalies in the Early Backbone area (`model.1.conv`), which triggered the loss of micro-spatial features on small-sized PPE.



### 3. Production-Scale API Gateway (Part C)

The backend prototype is built using FastAPI with industry standards:

* Domain-Driven Design (DDD): Separation of Pydantic v2 schemas, routing interfaces, and business logic.

* Asynchronous Processing: Utilizing `BackgroundTasks` to delegate heavy computation (such as TensorRT inference or face extraction) to avoid blocking the HTTP queue.

* Cloudflare Tunnel Integration: Automated tunneling integration directly from within the Jupyter Notebook to expose the Swagger UI/ReDoc to the public web without session conflicts.



---



## 🚀 Quick Start Guide

### Option 1: Interactive Live Demo

You can execute the entire cycle (from model calibration to directly spawning the API server) without any local configuration.

* Open `02_model_experiment/benchmark_notebook.ipynb` using Google Colab: <br>

[https://colab.research.google.com/drive/1VTZDTQAuaP7oxl2MD_vZCucJgWOdQJWi?usp=sharing](https://colab.research.google.com/drive/1VTZDTQAuaP7oxl2MD_vZCucJgWOdQJWi?usp=sharing)

* Execute the cells from top to bottom (Run All).

* In the bottom-most cell block, the script will establish an asynchronous tunnel using Cloudflare. Click the `.trycloudflare.com/doc` link that appears in the output to interact directly with the API powered by the Colab environment.


### 🚀 Sample API Output

The system returns violation data in a structured JSON format, facilitating integration with central reporting dashboards:


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



### Option 2: Local API Execution (Local Development)

To test the backend architecture in isolation with production-standard linters:



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



Access the interactive documentation at: `http://localhost:8000/docs`



---



## ⚖️ License & Copyright


*   **Implementation Copyright:** © 2026 Felix Yustian Setiono. The entire system architecture, API source code, and experimental analysis documents within this repository are the original intellectual property of the author.
