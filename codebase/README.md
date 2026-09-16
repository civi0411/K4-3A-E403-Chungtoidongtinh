# VLearn Socratic Probing Tutor — Prototype v2 Mock (Checkpoint 2)

**Đề tài:** Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor hiện có (Socratic Probing)  
**Nhóm:** Chungtoidongtinh · **Phòng:** E403 · **Lớp:** 3A  

---

## 🎯 Mục tiêu Checkpoint 2 (CP2)
Theo quy chế cuộc thi Mini Hackathon AI, Checkpoint 2 yêu cầu **Bản mock bấm được cho thấy luồng hoạt động từ đầu đến cuối** (Chưa cần AI chạy thật).

Prototype v2 này tái hiện **100% giao diện VLearn thực tế ở quy mô lớn, đầy đủ, chuyên sâu** (Toàn bộ Bài Lab 3: Chatbot vs ReAct Agent từ Mục 1 đến Mục 10), bao gồm:
1. **Khung đọc bài giảng mở rộng (Reader Pane):**
   - Đầy đủ 10 mục nội dung: Brief lý thuyết, Setup repo, Task 1.1 (Đánh giá Chatbot), Task 1.2 (Tool Schema JSON), Task 2.1 (Tool Executor Python), Task 2.2 (ReAct Loop), Task 3.1 (Waterfall Trace Log), Task 3.2 (Đóng gói Repo), Trạm cứu hộ sự cố FAQs, và Bảng Rubric 10 điểm.
   - Hỗ trợ cuộn mượt (Smooth scroll) trực tiếp từ Menu bài học bên trái.
2. **Floating Toolbar & Caret động:**
   - Khi quét bất kỳ đoạn văn bản/mã code nào, thanh công cụ nổi lên với Caret chỉ đúng tâm đoạn chọn.
   - Gồm 3 action buttons:
     - `💡 Giải thích` (tag: trả lời ngay)
     - `🔍 Gợi mở` (tag: Socratic)
     - `📌 Ví dụ` (tag: trả lời ngay)
3. **Trợ giảng AI Socratic Probing với kiến trúc 3 Chip:**
   - Khi chọn `🔍 Gợi mở`: AI hỏi lại 1 câu hỏi ngược chữ tím kèm icon `🎯` và **3 chip lựa chọn nhanh** các điểm nghẽn phổ biến.
   - Học viên click chip $\rightarrow$ Chip được chọn sáng tím (`active-chip`), 2 chip còn lại mờ đi $\rightarrow$ AI hiển thị **Resolve Card** giải thích trúng đích kèm ví dụ cụ thể.
   - Nút `✓ Hiểu rồi, tiếp tục đọc` cho phép reset trạng thái về `😴 Sẵn sàng`.
4. **State Machine 4 trạng thái (Dynamic State Badge):**
   - `😴 Sẵn sàng` ➔ `⚙️ Đang phân tích…` ➔ `🔍 Socratic` ➔ `✅ Đã trả lời` ➔ reset về `😴 Sẵn sàng`.
5. **Context Bar & Xử lý câu hỏi tự do (Bonus):**
   - Context Bar nổi phía trên chat hiển thị trích dẫn đang chọn kèm nút xóa nhanh `✕`.
   - Nếu gõ câu hỏi thô vào ô input: AI hiển thị Guidance Card hướng dẫn bôi đen hoặc gợi ý bấm nút mở luồng Socratic.

---

## 🚀 Cách mở và chạy thử
1. Dự án xây dựng bằng **Vanilla HTML5, CSS3 và JavaScript** (Zero-dependencies, không cần `npm`).
2. **Mở trực tiếp:** Nhấp đúp chuột vào file `index.html` hoặc mở bằng bất kỳ trình duyệt nào (Chrome, Safari, Edge).
3. Hoặc chạy local server:
   ```bash
   python3 -m http.server 8088 --directory codebase
   # Mở trình duyệt: http://localhost:8088
   ```

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
