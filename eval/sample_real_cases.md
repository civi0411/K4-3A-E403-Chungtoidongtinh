# 5 Ví Dụ Thực Tế Minh Hoạ (Safe Sample Cases)

> 🔒 **Tuân thủ bảo mật:** Dữ liệu trích dẫn ngắn (dưới 2 câu mỗi ví dụ), đã ẩn danh học viên (`S####`), dẫn nguồn qua mã lượt (`T#####`). Tuyệt đối không chứa thông tin cá nhân.

---

### Case 1 · Bôi đen nhầm link, bot xả bài giảng 455 chữ
* **Mã lượt:** `T10372` | **Học viên:** `S0253` | **Bài học:** Day 01 (AI Foundation)
* **Đoạn học viên bôi đen:** `"https"` (trong link Slido trên slide trang 4).
* **Câu hỏi mẫu bấm sẵn:** *"Giải thích rõ đoạn này giúp mình."*
* **Hành vi Tutor hiện tại (Thất bại - 455 ký tự):**
  > *"Chào [HV], trong ngữ cảnh bài học, 'https' (Hypertext Transfer Protocol Secure) là giao thức bảo mật..."*
  *(Học viên chỉ bôi nhầm chữ trong link, nhưng bot xả cả bài giảng lý thuyết mạng).*
* **Hành vi Socratic Probing kỳ vọng (Thành công):**
  > *"Chào bạn, đoạn bạn chọn chỉ có chữ 'https'. Bạn đang muốn mở link Slido ở trang 4 hay muốn hỏi về giao thức mạng?"*
  *(Kèm 2 nút bấm: [Mở link Slido] / [Hỏi về giao thức])*

---

### Case 2 · Bôi đen 1 từ viết tắt, bot xả bức tường chữ 1.069 ký tự
* **Mã lượt:** `T10378` | **Học viên:** `S0456` | **Bài học:** Object Detection
* **Đoạn học viên bôi đen:** `"CVAT"`
* **Câu hỏi mẫu bấm sẵn:** *"Giải thích rõ đoạn này giúp mình."*
* **Hành vi Tutor hiện tại (Thất bại - 1.069 ký tự):**
  > Xả nguyên văn định nghĩa từ slide trang 18, giải thích công cụ CVAT là gì, chức năng ra sao... cực kỳ dài dòng trong khi học viên đã đọc slide rồi.
* **Hành vi Socratic Probing kỳ vọng (Thành công):**
  > *"Chào bạn, về công cụ CVAT ở trang 18, bạn đang vướng ở phần nào để mình hỗ trợ nhanh?"*
  *(Kèm 2 lựa chọn gợi mở: A. Cách cài đặt & chạy server | B. Quy tắc gán nhãn Bounding Box)*

---

### Case 3 · Bôi đen số liệu bảng, bot xả 871 ký tự
* **Mã lượt:** `T10419` | **Học viên:** `S1335` | **Bài học:** Data Lifecycle
* **Đoạn học viên bôi đen:** `"3,6"` (một con số trong bảng dữ liệu)
* **Câu hỏi mẫu bấm sẵn:** *"Giải thích rõ đoạn này giúp mình."*
* **Hành vi Tutor hiện tại (Thất bại - 871 ký tự):**
  > Tự động suy đoán và xả một bài luận về ý nghĩa của các con số thống kê.
* **Hành vi Socratic Probing kỳ vọng (Thành công):**
  > *"Bạn đang quan tâm đến con số '3,6' ở dòng dữ liệu nào trong bảng trang này?"*

---

### Case 4 · Bôi đen khái niệm cốt lõi, bot giảng lại slide
* **Mã lượt:** `T10382` | **Học viên:** `S0378` | **Bài học:** Day 01
* **Đoạn học viên bôi đen:** `"Self-attention Demo on Google Colab"`
* **Câu hỏi mẫu bấm sẵn:** *"Giải thích rõ đoạn này giúp mình."*
* **Hành vi Tutor hiện tại (Thất bại - 573 ký tự):**
  > Giảng lại định nghĩa Self-attention là gì.
* **Hành vi Socratic Probing kỳ vọng (Thành công):**
  > *"Bạn đang muốn chạy thử file Colab Demo hay muốn làm rõ cơ chế tính trọng số attention giữa các token?"*

---

### Case 5 · Bôi đen từ khoá "LiDAR", bot xả 919 ký tự
* **Mã lượt:** `T10437` | **Học viên:** `S1335` | **Bài học:** Data
* **Đoạn học viên bôi đen:** `"LiDAR"`
* **Câu hỏi mẫu bấm sẵn:** *"Giải thích rõ đoạn này giúp mình."*
* **Hành vi Tutor hiện tại (Thất bại - 919 ký tự):**
  > Giảng giải từ nguyên lý phát tia laser đến lịch sử công nghệ LiDAR.
* **Hành vi Socratic Probing kỳ vọng (Thành công):**
  > *"Trong bài học về xe tự lái, bạn muốn so sánh LiDAR với Camera hay cách xử lý dữ liệu Point Cloud?"*
