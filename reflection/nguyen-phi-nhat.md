# Bản Thu hoạch Cá nhân (Individual Reflection)

* **Họ và Tên:** Nguyễn Phi Nhật  
* **Mã Học Viên:** `2A202602658`  
* **Lớp:** 3A · **Phòng thi:** E403  
* **Vai trò trong nhóm:** Thành viên (Tech & Prototype)  

---

### 1. Phần việc đảm nhiệm trong dự án
* Thiết kế kiến trúc kỹ thuật cho Prototype v3: Xây dựng cơ chế gọi API thật (Google Gemini 1.5 Flash) kết hợp với bộ tri thức Offline Mock dự phòng (Hybrid Mode).
* Thiết kế System Prompt và cấu trúc ép kiểu đầu ra **Structured JSON Output** để LLM luôn trả về đúng 1 câu hỏi Socratic và 3 Chip lựa chọn chuẩn định dạng.
* Lập trình frontend tương tác trên Vanilla HTML/CSS/JS: Floating Toolbar với Caret động bám theo tọa độ bôi đen, State Machine 4 trạng thái và module Trace Logger xuất file `trace_waterfall.json`.

### 2. AI đã hỗ trợ tôi như thế nào trong quá trình làm việc?
* AI (Gemini Code Assist / Cursor) là công cụ tăng tốc lập trình cốt lõi của tôi:
  * Sinh nhanh các hàm tính toán tọa độ DOM (`getBoundingClientRect`) để căn chỉnh Caret mũi tên luôn chỉ chính xác vào tâm của đoạn văn bản được bôi đen.
  * Tối ưu hóa cấu trúc prompt bằng kỹ thuật Windowed Context Extraction: thay vì gửi toàn bộ 10 trang bài giảng làm tăng độ trễ, AI gợi ý chỉ trích xuất tiêu đề Task và ngữ cảnh 150 từ xung quanh, giúp giảm hơn 85% input token và đưa tốc độ phản hồi về mức dưới 800ms.

### 3. Một bài học sâu sắc từ chính ca thất bại (Failure Case) của nhóm
* **Ca thất bại:** Ở case `GS-19` ("LLM ⊂ DL ⊂ ML ⊂ AI"), mô hình AI bị trôi dạt ngữ cảnh (Context Drift), thay vì hỏi sâu vào điểm nhầm lẫn giữa việc gọi "AI" thay vì "LLM", mô hình lại sinh câu hỏi lặp lại định nghĩa hình cây cơ bản.
* **Bài học rút ra:** **Prompt dài không đồng nghĩa với Prompt tốt.** Ban đầu tôi cố viết một System Prompt rất dài với nhiều ví dụ Few-shot, nhưng điều đó khiến mô hình bị xao nhãng khỏi nhiệm vụ chính. Khi tôi rút gọn prompt, tập trung vào nhiệm vụ Socratic Scaffolding và áp dụng cấu trúc JSON Schema chặt chẽ, mô hình hoạt động ổn định và chính xác hơn hẳn. Kỹ thuật bọc ngữ cảnh chuẩn quan trọng hơn độ dài của câu lệnh.
