# Pipeline Proposal & Tech Stack Justification

## A. Pipeline Proposal: Cascade & Conditional Inference Architecture

Menghadapi beban komputasi 15 aliran video 1080p secara simultan pada satu perangkat *edge* menuntut efisiensi arsitektur yang ekstrem. Arsitektur konvensional yang memproses deteksi wajah pada setiap individu di setiap *frame* akan langsung memicu *bottleneck*. Oleh karena itu, saya merancang *pipeline* berbasis **Cascade & Conditional Inference** menggunakan ekosistem NVIDIA DeepStream:

1. **Hardware-Accelerated Ingestion:** 15 *stream* RTSP ditarik dan langsung di-*decode* oleh *Dedicated Hardware Decoder* (NVDEC) pada Jetson Orin. *Frame* hasil *decode* tetap berada di memori GPU (*Zero-Memory Copy*).
2. **Batch Multiplexing:** `nvstreammux` menggabungkan 15 *frame* (satu dari tiap kamera) menjadi satu *batch* tensor berseri untuk memaksimalkan utilisasi *Tensor Cores*.
3. **Primary Inference (PGIE):** Model YOLOv11s mendeteksi kelas pekerja (`Person`) beserta atribut kepatuhan keselamatannya (masker, helm, rompi, dll).
4. **Hardware-Accelerated Tracking:** Modul `nvtracker` menggunakan algoritma NvDCF (varian NVIDIA dari DeepSORT) untuk memberikan ID pelacakan temporal pada setiap pekerja. Ini mencegah sistem menghitung pelanggaran yang sama berulang kali pada detik yang berbeda.
5. **Conditional Secondary Inference (SGIE):** *Ini adalah inti dari efisiensi pipeline.* Model *Face Recognition* **hanya** dipicu secara kondisional. Jika *Primary Inference* mendeteksi ketiadaan APD pada seorang pekerja, sistem akan memotong (*crop*) *bounding box* wajah pekerja tersebut dan mengumpankannya ke SGIE untuk identifikasi. Jika pekerja patuh, komputasi pengenalan wajah dilewati sepenuhnya (*bypassed*).
6. **Asynchronous Message Broker:** *Metadata* pelanggaran diubah menjadi format JSON oleh `nvmsgconv` dan dipublikasikan ke *broker* lokal (Kafka/Redis) untuk diserap oleh layanan FastAPI secara asinkron tanpa memblokir *pipeline* video utama.

---

## B. Tech Stack Justification

| Komponen | Pilihan Teknologi | Justifikasi Teknis |
| :--- | :--- | :--- |
| **Video Analytics Framework** | **NVIDIA DeepStream SDK** | Pendekatan standar menggunakan OpenCV + PyTorch/Multiprocessing akan gagal karena *memory copy overhead* (CPU RAM ↔ GPU VRAM) yang masif. DeepStream mempertahankan seluruh *buffer* video di ekosistem GPU sejak *decode* hingga *encode*, memungkinkan Jetson Orin menangani 225 FPS kumulatif tanpa membebani utilisasi CPU. |
| **Primary Detection Model** | **YOLOv11s (TensorRT FP16)** | Meskipun lampiran menyediakan *pre-trained* model YOLOv8, desain ini secara strategis mengadopsi YOLOv11s. Keputusan ini didasarkan pada lonjakan efisiensi arsitektur YOLOv11 yang menawarkan latensi sangat rendah (~2.89 ms) dengan mAP yang andal di *edge device* (dibuktikan secara empiris pada Analisis Bagian B). Ini memastikan *pipeline* tidak hanya mengejar target FPS, tetapi juga mutakhir secara arsitektur. |
| **Inference Optimizer** | **NVIDIA TensorRT** | TensorRT melakukan fusi *layer* secara agresif dan mengkalibrasi presisi kernel ke FP16 secara spesifik untuk GPU Orin/T4, memaksimalkan *throughput* pada *Tensor Cores* dan menurunkan latensi secara eksponensial dibandingkan eksekusi PyTorch *native*. |
| **Secondary Inference Model**| **InsightFace (buffalo_sc)** | Model *buffalo_sc* adalah versi sangat ringan yang tangguh menangani oklusi wajah parsial (misalnya saat pekerja memakai helm atau sebagian wajah tertutup masker), sangat cocok untuk *edge deployment*. |
| **Database Analytics** | **ClickHouse** | Data analitik pergerakan/pelanggaran dari 15 kamera akan menghasilkan *time-series event log* dengan kardinalitas tinggi. ClickHouse sangat superior untuk *Online Analytical Processing* (OLAP) dengan kecepatan agregasi yang jauh lebih tangguh daripada basis data relasional standar saat merender data untuk *dashboard*. |
| **API Framework** | **FastAPI (via uv & ruff)** | Integrasi asinkron (*ASGI*) FastAPI sangat efisien menangani I/O *bound tasks* seperti menerima aliran pesan dari DeepStream. Penggunaan `uv` mempercepat resolusi *environment* secara drastis, dan `ruff` memastikan kualitas *clean code* untuk skala *production*. |
