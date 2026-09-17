# VLearn Socratic Probing Tutor — Prototype v4 (Checkpoint 4: Quality Lock)

**Đề tài:** Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor hiện có (Socratic Probing)  
**Nhóm:** Chungtoidongtinh · **Phòng:** E403 · **Lớp:** 3A  
**Đội trưởng:** Trần Chí Vĩ (`2A202602968`)  

---

## 🎯 Mục tiêu & Kết quả Nghiệm thu Checkpoint 4 (CP4)

Tại Checkpoint 4, nhóm thực hiện **Khóa phạm vi Demo (Scope Freeze)** và **Khóa ngưỡng chất lượng chính thức (Official Quality Bar)**:

### 1. Khóa Ngưỡng Chất lượng Chính thức (Official Quality Threshold)
- **Quality Bar cam kết:** $\ge 90.0\%$ Pass rate trên bộ kiểm thử 20 case thật K4 (`eval/golden_set.json`), 100% không bịa đặt nguồn ngoài bài học (Grounding).
- **Kết quả đo lường Lượt 2 (CP4 Quality Lock):**
  - **Số case đạt (PASS):** **20 / 20 case (100.0%)**
  - **Tỷ lệ Grounding & Safety:** **100%**
  - **Tỷ lệ Brevity:** **100%** (Câu hỏi $\le 2$ câu, đúng 3 chip, nhãn chip $\le 15$ từ).
  - **Báo cáo chi tiết:** Lưu tại `eval/run_02_results.md` và `eval/run_02_results.json`.

### 2. Khóa Phạm vi Kịch bản Demo (Happy Path Demo Scope)
- **Chu trình Socratic Chuẩn (4 Bước):**
  1. *BƯỚC 1:* Học viên đọc tài liệu bài Lab bên trái. Khung Chat bên phải ở trạng thái `😴 Sẵn sàng`.
  2. *BƯỚC 2:* Bôi đen từ khóa chuyên môn (VD: `ReAct Agent`). Thanh công cụ **Floating Toolbar** nổi lên với 3 nút bấm: `💡 Giải thích`, `🔍 Gợi mở (Socratic)`, `📌 Ví dụ`.
  3. *BƯỚC 3:* Bấm nút `🔍 Gợi mở (Socratic)`. AI phân tích và trả về **Socratic Card** gồm câu hỏi gợi mở chữ tím `🎯` kèm **3 chip lựa chọn** điểm nghẽn nhận thức.
  4. *BƯỚC 4:* Học viên bấm chọn 1 chip. Chip được chọn sáng tím highlight, 2 chip còn lại mờ đi. AI hiển thị **Resolve Card** màu xanh lá giải thích trúng đích kèm ví dụ. Bấm `✓ Hiểu rồi, tiếp tục đọc` để dứt điểm luồng học và đưa State Badge về `😴 Sẵn sàng`.

### 3. Khắc phục Triệt để Nhóm Lỗi (Error Analysis Fixes)
- **Case GS-02 (`https`):** Kích hoạt Regex Guardrail `^(https?:\/\/|www\.)` chặn người dùng bôi nhầm link ngoài, đưa ra hướng dẫn bôi đen lại từ khóa đúng (HAX G1/G10).
- **Case GS-16, GS-19, GS-20:** Tinh chỉnh System Prompt và kích hoạt bộ cắt tỉa nhãn chip tự động $\le 15$ từ, đảm bảo tuyệt đối không quá tải nhận thức của người học.

---

## 🚀 Hướng dẫn Cài đặt & Chạy Thực nghiệm

### Cách 1: Khởi chạy Full-stack với Python Backend Server (Khuyên dùng)
Server sử dụng thư viện chuẩn Python 3 (không cần cài pip gói ngoài):

```bash
# 1. Khởi chạy Backend Server (phục vụ cả Web UI và REST API)
python3 codebase/server.py

# 2. Mở trình duyệt truy cập:
# http://localhost:8088

# 3. Kiểm tra các endpoint quản trị:
# Health check:     curl http://localhost:8088/api/health
# Trace waterfall:  curl http://localhost:8088/api/traces
```

### Cách 2: Chạy Kiểm thử Tự động 20 Case (Rubric R4 & CP4)

```bash
# Chạy đánh giá Lượt 2 và sinh báo cáo Markdown chính thức
python3 eval/eval_runner.py --run 2

# Xem báo cáo nghiệm thu chi tiết tại:
# eval/run_02_results.md
```

### Cách 3: Cấu hình Live AI (Google Gemini 1.5 Flash API)
1. Trên giao diện web, bấm nút `⚡ Mock Mode` góc trên bên phải thanh Topbar.
2. Chọn `🤖 Live Gemini AI`, dán API Key của bạn (`AIzaSy...`) và bấm `Kiểm tra kết nối`.
3. Bấm `Lưu & Kích hoạt` để trải nghiệm AI sinh động theo thời gian thực (có huy hiệu độ trễ thực tế `680ms · Live AI`).

---

## 🧪 Danh mục Từ khóa Kiểm thử Nhanh trên Bài giảng

Bạn có thể bôi đen trực tiếp các từ khóa nổi bật trên bài Lab 3:
- **`ReAct Agent`**: Kiểm tra vòng lặp Thought ➔ Action ➔ Observation.
- **`Native Tool Calling`**: Khai báo JSON Schema và cơ chế Function Calling.
- **`Waterfall Trace Log`**: Đo độ trễ từng bước suy luận phục vụ chấm điểm Rubric R5.
- **`call_anthropic`**: Tham số temperature vs bảo mật API Key qua `.env`.
- **`Self-healing`**: Bắt exception runtime để mô hình tự sửa sai.
- **`CUDA out of memory`**: Lỗi tràn VRAM GPU và giải pháp lượng tử hóa 4-bit.
- **`https`**: Kiểm tra Intent Guardrail chặn bôi nhầm link URL ngoài (Case GS-02).
- **`quét mã điểm danh`**: Kiểm tra rào chắn từ chối câu hỏi vận hành (Logistics) theo chuẩn HAX G1.
