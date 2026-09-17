# 🎥 Video Demo Sản Phẩm (Thao Tác AI Chạy Thật — Checkpoint 3 & 5)

Thư mục này quản lý các video minh chứng cho hai mốc nghiệm thu kỹ thuật:
* **Checkpoint 3 (CP3):** Video 30 giây chứng minh AI chạy thật tại quyết định trung tâm (không hardcode).
* **Checkpoint 5 (CP5):** Video demo dự phòng (Backup Video 60–90 giây) phục vụ thuyết trình nếu phòng lab E403 rớt mạng.

---

## 1. Kịch bản Video 30s Checkpoint 3 (AI Chạy Thật)
* **Thời lượng chuẩn:** 30 giây (quay màn hình không cần lồng tiếng theo chuẩn `README.md` CP3).
* **Luồng thao tác thực tế:**
  1. `00s - 05s`: Mở giao diện bài giảng VLearn trên trình duyệt (`http://localhost:8088`).
  2. `06s - 12s`: Dùng chuột bôi đen cụm từ **"ReAct Agent"** trong tài liệu bài Lab Day 03. Floating Toolbar nổi lên với Caret chỉ đúng tọa độ.
  3. `13s - 20s`: Bấm nút `🔍 Gợi mở (Socratic)`. Nhìn thấy State Badge chuyển sang `⚙️ Đang phân tích…`. Backend gọi API Gemini 1.5 Flash theo thời gian thực (ghi nhận độ trễ ~680ms). Thẻ Socratic Card hiện ra với 1 câu hỏi và **3 chip lựa chọn**.
  4. `21s - 26s`: Click vào **Chip 2** (*"Khác biệt Chatbot Cấp 2 vs ReAct Agent Cấp 3"*). Thẻ Resolve Card phản hồi giải thích trúng đích trong 3 dòng.
  5. `27s - 30s`: Bấm nút **`✓ Hiểu rồi, tiếp tục đọc`** để đóng thẻ, badge reset về `😴 Sẵn sàng`. Hoàn tất chu trình Socratic.

---

## 2. Đường dẫn Video File
* **File lưu nội bộ repo:** `video/cp3_demo.mp4` (hoặc định dạng `.mov`/`.webm`).
* **Google Drive Backup Link:** *(Dành cho nộp form online)* [Link Video Drive Trực tiếp](https://drive.google.com) *(Mở quyền Public: Anyone with the link can view)*.
* **Chứng minh quyết định trung tâm gọi LLM thật:** Đối soát trực tiếp vết log thời gian thực tại file `codebase/trace_waterfall.json` tương ứng với timestamp trong video.
