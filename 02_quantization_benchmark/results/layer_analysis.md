# Layer Collapse Analysis: Transisi FP32 ke INT8

## A. Pendekatan Identifikasi Layer Sensitif
Untuk mengidentifikasi *layer* mana yang memicu *collapse* (degradasi akurasi) selama proses kuantisasi ke INT8, pendekatan yang digunakan adalah **Predictive Sensitivity Analysis** di level arsitektur PyTorch (*pre-export*). 

Pendekatan ini menggunakan `torch.nn.modules.module.register_forward_hook` untuk menyadap (*intercept*) tensor keluaran (aktivasi) dari setiap blok konvolusi (`nn.Conv2d`) saat model melakukan *forward pass*. Metrik utama yang diukur adalah **Dynamic Range** (selisih antara nilai aktivasi maksimum dan minimum) pada masing-masing *layer*. *Layer* dengan rentang dinamis yang ekstrem adalah target utama yang akan mengalami presisi meluap (*clipping error*) saat dipaksa masuk ke dalam kalibrasi INT8.

## B. Bukti Empiris Layer yang Terdegradasi (Collapse)
Berdasarkan ekstraksi *hooks* pada arsitektur YOLOv11s, data empiris menunjukkan temuan arsitektural yang bertolak belakang dengan intuisi umum. *Layer* yang paling rentan justru **bukan** berada di *Detection Head* (cabang regresi koordinat), melainkan terpusat di area **Early Backbone**:

1. **`model.1.conv`** (Dynamic Range: 288.40)
2. **`model.2.cv1.conv`** (Dynamic Range: 173.35)

Terlihat adanya jurang disparitas rentang nilai yang sangat masif; *layer-layer* awal ini memiliki rentang aktivasi hingga 10x lipat lebih ekstrem dibandingkan *layer* setelahnya (sebagai perbandingan, `model.2.cv2.conv` memiliki rentang dinamis yang langsung stabil di angka 26.03).

## C. Mengapa Early Backbone Sangat Rentan?
Kerentanan ini berakar pada fondasi matematis dari *Post-Training Quantization* (PTQ). Kuantisasi INT8 memetakan nilai *floating-point* (FP32) yang kontinu ke dalam ruang diskrit 8-bit yang hanya memiliki 256 nilai diskrit (-128 hingga 127). Skala pemetaan (*Scale Factor*, $S$) dihitung menggunakan persamaan:

$$S = \frac{X_{max} - X_{min}}{255}$$

1. **Karakteristik Ekstraksi Gradien Ekstrem:** *Layer* awal pada jaringan YOLO (`model.1.conv`) bertugas mengekstrak fitur dasar (*low-level features*) langsung dari piksel gambar mentah, seperti tingkat kontras tinggi, tepian tajam, atau perubahan warna drastis. Benda-benda seperti rompi keselamatan (*safety vest*) yang memantulkan cahaya neon atau helm proyek berwarna mencolok di bawah sinar matahari pabrik sering kali menghasilkan lonjakan nilai aktivasi (*outliers*) yang luar biasa besar di *layer* pembuka ini.
2. **Clipping pada Fitur Dasar:** Kehadiran aktivasi *outliers* yang mencapai nilai 288.40 ini memaksa skala pemetaan $S$ melebar secara ekstrem untuk menampung batas atas. Akibatnya, nilai-nilai aktivasi kecil—yang sebenarnya merepresentasikan tekstur halus atau batas tepi objek berukuran kecil di latar belakang—akan terhimpit, tidak mendapat tempat di ruang 8-bit, dan terpotong (*clipped*) menjadi nol. 

## D. Implikasi Terhadap Akurasi Keseluruhan (Cascading Failure)
Degradasi yang terjadi secara prematur di area *Early Backbone* ini memicu fenomena **Cascading Failure** (kegagalan beruntun) di dalam sisa *pipeline* deteksi:

* **Korupsi Fitur Fundamental:** Karena *layer* awal bertugas menyuplai *feature maps* (peta fitur) untuk seluruh sisa jaringan di bawahnya, *clipping error* di fase awal ini berarti *layer-layer* di area leher (*Neck*) dan akhir jaringan (*Detection Head*) secara inheren menerima data yang sudah korup atau kehilangan resolusi informasi spasialnya.
* **Kegagalan Deteksi Objek Kecil:** Hilangnya detail halus di awal jaringan menyebabkan model secara komputasional menjadi buta terhadap fitur spasial mikro. Objek krusial seperti kacamata pelindung (*goggles*) atau tali masker yang mungkin hanya menempati rasio sebagian kecil piksel dalam rekaman CCTV 1080p, tidak dapat lagi direkonstruksi oleh *Detection Head*. Ini berujung langsung pada penurunan angka *Recall* dan mAP secara keseluruhan pada presisi INT8.
