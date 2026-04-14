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
