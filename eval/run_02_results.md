# Báo cáo Đo lường Lượt 2 (Eval Run 02) — Checkpoint 4 (Quality Lock)
**Dự án:** VLearn Tutor (Socratic Probing Engine)  
**Nhóm:** Chungtoidongtinh · **Lớp:** 3A · **Phòng:** E403  
**Thời điểm đo:** 17/09/2026 · 15:32:37  
**Kỹ thuật:** 3-Layer Agent Router (Layer 0 Guardrails + Layer 1 RAG-lite + Layer 2 Live Gemini 1.5 Flash API)  
**Tập dữ liệu:** 20 case thật trích từ chatlog K4 (`eval/golden_set.json`), đầy đủ 4 lớp chỗ khó.  
**Script tự động:** `python3 eval/eval_runner.py --run 2`

---

## 1. Ngưỡng Chất lượng Chính thức (Official Quality Threshold — Khóa tại CP4)

Theo quy chuẩn nghiệm thu Checkpoint 4 (Lock Scope & Quality Bar):
- **Quality Bar cam kết ban đầu:** $\ge 80\%$ case đạt chuẩn cả 3 chiều.
- **Ngưỡng chất lượng khóa chính thức tại CP4:** **$\ge 90.0\%$ Pass Rate** trên tập Golden Set.
- **Tiêu chí Grounding:** **100%** không bịa đặt nguồn ngoài tài liệu bài giảng.

---

## 2. Bảng Kết quả Chi tiết 20 Case Golden Set (Lượt 2)

| Mã Case | Turn ID | Đoạn bôi đen | Lớp chỗ khó | Chiều 1: Accuracy | Chiều 2: Brevity | Chiều 3: Grounding | Kết quả | Trạng thái khắc phục từ CP3 |
|---|---|---|---|:---:|:---:|:---:|:---:|---|
| **GS-01** | `T10371` | "Object Detection" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-02** | `T10372` | "https" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | 🎉 **ĐÃ FIX (CP4)**: Guardrail Regex chặn URL `https` |
| **GS-03** | `T10378` | "CVAT" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-04** | `T10382` | "Self-attention Demo on Go..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-05** | `T10415` | "annotation guideline" | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-06** | `T10419` | "3,6" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-07** | `T10422` | "Cỗ máy đoán token LLM là ..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-08** | `T10437` | "LiDAR" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-09** | `T10453` | "AI, ML, DL và Data lifecycle" | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-10** | `T10457` | "(Đang học phần “Lịch sử A..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-11** | `T10475` | "annotation guideline" | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-12** | `T10476` | "Giới hạn: không ai có thể..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-13** | `T10495` | "ML" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-14** | `T10503` | "ef call_anthropic( prompt..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-15** | `T10518` | "Transformer Explainer" | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-16** | `T10530` | "Xe tự lái nhận ra người đ..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | 🎉 **ĐÃ FIX (CP4)**: Trích xuất trọng tâm bài toán người đi bộ |
| **GS-17** | `T10531` | "không có" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-18** | `T10532` | "đáp" | ② Mơ hồ / thiếu thông tin | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | Ổn định từ Lượt 1 |
| **GS-19** | `T10534` | "LLM ⊂ DL ⊂ ML ⊂ AI. Nói “..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | 🎉 **ĐÃ FIX (CP4)**: Ranh giới chính xác giữa LLM và AI |
| **GS-20** | `T10550` | "Có giám sát ■ Cần đáp án ..." | ④ Đặc thù domain | ✅ Đạt | ✅ Đạt | ✅ Đạt | **PASS** | 🎉 **ĐÃ FIX (CP4)**: Cắt tỉa nhãn chip tự động $\le 15$ từ |

---

## 3. Tổng hợp Chỉ số Đo lường Lượt 2 & Đối chiếu Ngưỡng Khóa

```
┌─────────────────────────────────────────────────────────────┐
│  TỔNG SỐ CASE KIỂM THỬ:               20 / 20 Case          │
│  SỐ CASE ĐẠT CHUẨN (PASS):            20 / 20 Case          │
│  TỶ LỆ ĐẠT THỰC TẾ LƯỢT 2:            100.0%                │
│  NGƯỠNG CHẤT LƯỢNG KHÓA (CP4):        >= 90.0%              │
│  ĐÁNH GIÁ:                            🎉 VƯỢT CHỈ TIÊU      │
│  TỶ LỆ KHÔNG BỊA NGUỒN (GROUNDING):   100%                  │
└─────────────────────────────────────────────────────────────┘
```

### So sánh Đối chiếu Tiến bộ Kỹ thuật (CP3 vs CP4):
- **Lượt 1 (CP3 Baseline):** 16/20 đạt (80.0%) — Vướng 4 ca lỗi về URL regex và độ dài nhãn.
- **Lượt 2 (CP4 Quality Lock):** **20/20 đạt (100.0%)** — Khắc phục triệt để 100% các nhóm lỗi đã phát hiện.
- **Kết luận:** Hệ thống đã khóa vững chắc chất lượng theo chuẩn Rubric R4 & R5, sẵn sàng bước vào vòng thử nghiệm người dùng thật (CP5) và Demo trực tiếp (CP6).
