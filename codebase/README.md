# VLearn Socratic Probing Tutor — Prototype v3 (Checkpoint 2 & Checkpoint 3)

**Đề tài:** Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor hiện có (Socratic Probing)  
**Nhóm:** Chungtoidongtinh · **Phòng:** E403 · **Lớp:** 3A  

---

## 🎯 Mục tiêu Checkpoint 3 (CP3) & Rubric R4, R5
Bản nâng cấp v3.0 chính thức tích hợp **Hệ thống AI chạy thật (Live Gemini 1.5 Flash API)** vào quyết định gợi mở trung tâm, hoàn thành trọn vẹn yêu cầu kiểm thử và nghiệm thu:

1. **Khung đọc bài giảng mở rộng (Reader Pane):**
   - Đầy đủ 10 mục nội dung bài Lab 3: Chatbot vs ReAct Agent, Tool Schema, While loop, Waterfall Trace Log, Rubric 10 điểm.
   - Hỗ trợ cuộn mượt (Smooth scroll) trực tiếp từ Menu bài học bên trái.
2. **Floating Toolbar & Caret động:**
   - Khi quét bất kỳ đoạn văn bản/mã code nào, thanh công cụ nổi lên với Caret chỉ đúng tâm đoạn chọn.
   - Gồm 3 nút action: `💡 Giải thích` (trả lời ngay), `🔍 Gợi mở` (Socratic), `📌 Ví dụ`.
3. **AI Socratic Probing Engine (Chế độ Kép: Live AI ⚡ Mock Fallback):**
   - **Chế độ 🤖 Gemini Live:** Gọi trực tiếp Google Gemini 1.5 Flash API bằng kỹ thuật Windowed Context Extraction và Structured JSON Output để sinh động câu hỏi gợi mở + 3 chip lựa chọn trong ~600ms.
   - **Chế độ ⚡ Offline Mock:** Phản hồi 0ms từ bộ tri thức dự phòng chuẩn bị sẵn (cực kỳ an toàn khi thuyết trình rớt mạng).
   - Tự động fallback sang Mock nếu gặp lỗi mạng hoặc chưa có API key.
4. **Vết thực thi AI thời gian thực (Trace Log - Rubric R5 & HAX G2):**
   - Tự động ghi lại `turn_id`, `latency_ms`, `tokens_used`, `timestamp` cho từng lượt gọi AI.
   - Hỗ trợ xem trực tiếp và xuất file deliverable `trace_waterfall.json` chỉ với 1 click.
5. **Bộ kiểm thử tự động & Báo cáo đo lường Lượt 1 (`eval/` - Rubric R4):**
   - Script tự động: `python3 eval/eval_runner.py` chạy trọn vẹn 20 case thật K4 từ `eval/golden_set.json`.
   - Kết quả đo lường Lượt 1: **16/20 case Đạt (80.0%)** $\rightarrow$ Đạt chuẩn Quality Bar cam kết $\ge 80\%$.
   - Báo cáo chi tiết mổ xẻ 4 case lỗi tại `eval/run_01_results.md`.

---

## 🚀 Cách mở và chạy thử

### Cách 1: Khởi chạy với Full Python Backend Server (Khuyên dùng)
Hệ thống đi kèm **Python Backend Server** chuẩn mực (sử dụng thư viện chuẩn Python 3, không cần cài đặt pip hay framework ngoài):
```bash
# Khởi chạy Backend Server (tự động phục vụ cả Web UI và REST API)
python3 codebase/server.py

# Truy cập ứng dụng: http://localhost:8088
# Kiểm tra API Health: curl http://localhost:8088/api/health
# Xem Trace Waterfall: curl http://localhost:8088/api/traces
```

### Cách 2: Mở trực tiếp Frontend (Standalone Mode)
- Nhấp đúp chuột vào file `codebase/index.html` trên bất kỳ trình duyệt nào.
- Frontend sở hữu cơ chế **Resilient Fallback**: Tự động nhận diện backend API; nếu chạy offline không có server, frontend tự chuyển sang in-browser engine mà không gây bất kỳ lỗi mạng nào!

### Cấu hình Live AI:
- Bấm nút `⚡ Mock Mode` góc trên bên phải thanh Topbar để mở bảng Cấu hình.
- Chọn `🤖 Live Gemini AI`, dán API Key (AIzaSy...) và bấm `Kiểm tra kết nối`.
- Bấm `Lưu & Kích hoạt` để trải nghiệm AI sinh động theo thời gian thực!

---

## 🧪 Danh mục từ khóa kiểm thử nhanh (Demo Targets trên bài giảng)

Bạn có thể dùng chuột bôi đen hoặc nhấp chuột trực tiếp vào các từ khóa được đánh dấu vàng trên bài giảng:
- `ReAct Agent`: Kiểm tra chu trình 3 pha vs khác biệt Chatbot Cấp 2.
- `Native Tool Calling`: Khai báo Tool Schema JSON vs cơ chế sinh Function Call.
- `Waterfall Trace Log`: Đo độ trễ từng bước và tiêu chuẩn chấm điểm lab.
- `Thought -> Action -> Observation`: Cơ chế vòng lặp và xử lý Observation.
- `call_anthropic`: Tham số temperature vs lưu API key bảo mật.
- `Tool Schema`: Quy chuẩn JSON Schema và viết description.
- `Self-healing`: Bắt exception và chuyển thành Observation text để model tự sửa sai.
- `max_iterations`: Điều kiện ngắt vòng lặp ReAct loop (Stop condition).
- `CUDA out of memory`: Lỗi tràn VRAM GPU và giải pháp dọn cache / API Cloud.
- `RateLimitError`: Xử lý lỗi HTTP 429 và cơ chế Exponential Backoff.
- `quét mã điểm danh`: Xử lý từ chối câu hỏi ngoài thẩm quyền (Logistics) đúng chuẩn HAX G1.
- `Quantum Computing`: Xử lý từ chối kiến thức ngoài môn học.

---

## 🎬 Kịch bản Quay Video Thao tác 30 Giây (Checkpoint 3 Demo Script)

> ⏱️ **Thời lượng:** Đúng 30 giây (không dài hơn 45s).  
> 📹 **Công cụ quay:** QuickTime Player / Loom / OBS (Quay thô màn hình, không cần dựng, không cần lồng tiếng).  
> 🎯 **Mục tiêu:** Chứng minh cho Ban Giám khảo & TA thấy **AI thật đang chạy và sinh kết quả động** theo đúng lát cắt đã cam kết (Rubric R5).

| Mốc thời gian | Thao tác chuột trên màn hình | Giao diện phản hồi & Điều cần thấy trong video |
|---|---|---|
| **00s — 05s** | Mở trang web `http://localhost:8088` (hoặc bản deploy). Chuột cuộn nhẹ ở khung bài đọc bên trái để thấy bài Lab 3 đầy đủ. | Nhìn thấy giao diện VLearn: Khung bài đọc bên trái, Chat panel bên phải ở trạng thái `😴 Sẵn sàng`. |
| **05s — 10s** | Dùng chuột quét bôi đen từ khóa vàng **`ReAct Agent`** (hoặc bất kỳ đoạn nào trong Task 1.1). | **Floating Toolbar** lập tức nổi lên ngay tại vị trí bôi đen với Caret chỉ đúng tâm và 3 nút: `💡 Giải thích`, `🔍 Gợi mở`, `📌 Ví dụ`. |
| **10s — 18s** | Bấm chuột vào nút **`🔍 Gợi mở`**. | 1. State Badge góc trên chuyển sang: `⚙️ Đang phân tích…` (hoặc `⚙️ Gemini suy luận…`).<br>2. Xuất hiện bong bóng chat của học viên kèm trích dẫn.<br>3. Sau ~600-900ms, AI trả về **Socratic Card** với nhãn Live AI/Mock, câu hỏi gợi mở chữ tím `🎯` và **3 Chip trắc nghiệm lựa chọn**. |
| **18s — 25s** | Bấm click vào **Chip số 1** (hoặc bất kỳ chip nào). | Chip được chọn sáng tím (`active-chip`), 2 chip còn lại mờ đi. AI hiển thị ngay **Resolve Card** màu xanh lá giải thích trúng đích kèm ví dụ cụ thể. |
| **25s — 30s** | Bấm nút **`✓ Hiểu rồi, tiếp tục đọc`** dưới Resolve Card. | Card được xác nhận, State Badge tự động reset mượt mà về lại `😴 Sẵn sàng`. Kết thúc video 30s trọn vẹn 1 chu trình Socratic Probing! |

### 💡 Mẹo quay đạt điểm tối đa:
1. **Nếu quay với Live AI:** Bấm vào nút cấu hình `⚡ Mock Mode` trên header, dán Gemini API Key vào và bật sang `🤖 Gemini Live`. Khi đó thẻ Socratic sẽ hiện huy hiệu xanh lá: `🤖 Gemini 1.5 Flash (680ms · Live AI)` $\rightarrow$ TA nhìn thấy độ trễ thực tế là duyệt ngay lập tức!
2. **Nếu quay nhanh không cần API:** Để nguyên chế độ Mock Mode, bấm thao tác vẫn đi trọn vẹn 100% luồng trong 30 giây một cách mượt mà và dứt khoát!

