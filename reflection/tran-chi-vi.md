# Bản Thu hoạch Cá nhân (Individual Reflection)

* **Họ và Tên:** Trần Chí Vĩ  
* **Mã Học Viên:** `2A202602968`  
* **Lớp:** 3A · **Phòng thi:** E403  
* **Vai trò trong nhóm:** Đội trưởng (Team Lead)  

---

### 1. Phần việc đảm nhiệm trong dự án
* Điều phối tiến độ tổng thể của nhóm qua 6 Checkpoint, đảm bảo toàn bộ các mốc nộp đúng hạn.
* Chủ trì xây dựng tài liệu `spec.md` (trọng tâm ở các mục §1 Bối cảnh, §2 Bằng chứng chuẩn B, §4 Lát cắt 1 câu & Non-goals, §8 Phân công).
* Khai báo và nộp các biểu mẫu Checkpoint 1 đến Checkpoint 5 cho Ban Tổ chức.
* Đảm nhiệm vai trò thuyết trình chính (Pitching & Demo live) tại vòng cụm và chung kết phòng E403 ở Checkpoint 6.

### 2. AI đã hỗ trợ tôi như thế nào trong quá trình làm việc?
* Tôi sử dụng AI (Gemini/Claude) như một người cộng sự tư duy phản biện (Sparring Partner). Cụ thể, tôi dùng AI để:
  * Soát lỗi logic trong lát cắt giải pháp, biến các mô tả tính năng trừu tượng thành định dạng MỘT CÂU chuẩn xác (`1 user · 1 việc · 1 quyết định AI · 1 kết quả`).
  * Phân tích các góc nhìn đối chiếu chi phí lỗi (Cost-of-error) để bảo vệ quyết định chọn mức tự động hóa `Conditional` thay vì `Automate`.
  * Soạn thảo khung sườn Slide 6 trang bám sát luật *"không có bằng chứng thì không có slide"*.

### 3. Một bài học sâu sắc từ chính ca thất bại (Failure Case) của nhóm
* **Ca thất bại:** Khi chạy thử bộ Golden Set ở Lượt 1, case `GS-02` (học viên bôi nhầm chữ `"https"` trong link Slido) khiến hệ thống hiểu nhầm đây là khái niệm an ninh mạng và hỏi người học về chứng chỉ SSL.
* **Bài học rút ra:** Là một Product Lead, tôi nhận ra rằng: **Đừng bao giờ tin rằng dữ liệu đầu vào của người dùng luôn sạch sẽ.** Trước khi để AI "suy luận thông minh", hệ thống cần có những bộ lọc kỹ thuật căn bản (như regex chặn URL hoặc bắt độ dài từ). Một sản phẩm AI xuất sắc được định nghĩa bởi cách nó xử lý graceful failure ở các góc khuất, chứ không chỉ ở những trường hợp hoàn hảo (Happy Path).
