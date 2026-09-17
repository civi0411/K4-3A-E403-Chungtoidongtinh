# Bản Thu hoạch Cá nhân (Individual Reflection)

* **Họ và Tên:** Hoàng Minh Tuấn  
* **Mã Học Viên:** `2A202602758`  
* **Lớp:** 3A · **Phòng thi:** E403  
* **Vai trò trong nhóm:** Thành viên (Product & Testing)  

---

### 1. Phần việc đảm nhiệm trong dự án
* Thiết kế Taxonomy 4 lớp chỗ khó (§5) và xây dựng 9 kịch bản rủi ro cụ thể cho hệ thống theo HAX Playbook.
* Lựa chọn và trỏ trực tiếp 4 nguyên tắc HAX (**G1, G2, G8, G10**) cùng nguyên tắc PAIR vào từng thành phần UI tương tác trên prototype.
* Điều phối và trực tiếp thực hiện 4 phiên thử nghiệm người dùng tại phòng lab E403 theo chuẩn Stanford CS177, ghi chép nhật ký và phỏng vấn chỉ số Sean Ellis (`validation/README.md` — Khối R6).
* Soạn thảo và hoàn thiện nội dung bộ Slide thuyết trình 6 trang (`demo-slides.md`).

### 2. AI đã hỗ trợ tôi như thế nào trong quá trình làm việc?
* AI hỗ trợ tôi đóng vai trò "Red Team" (người tìm lỗi) và hỗ trợ thiết kế trải nghiệm người dùng:
  * Đóng vai trò học viên quậy phá (Adversarial User) để thử nghiệm các câu lệnh tấn công Jailbreak, bôi đen từ viết tắt kỳ lạ, hoặc hỏi câu hỏi ngoài thẩm quyền để kiểm tra độ vững vàng của các rào chắn Guardrails.
  * Hỗ trợ chưng cất các ghi chép thô từ phiên thử nghiệm người dùng thành các insight sản phẩm súc tích, phân biệt rõ giữa lời nói xã giao và tín hiệu hành vi thật sự theo PAIR 5.1.

### 3. Một bài học sâu sắc từ chính ca thất bại (Failure Case) của nhóm
* **Ca thất bại:** Trong phiên thử nghiệm với bạn Trần Thị Thu Hiền (2A202602737), bạn đọc xong lời giải thích trên thẻ Resolve Card nhưng loay hoay không biết làm sao để đóng khung chat quay lại đọc tiếp bài giảng, khiến mạch học bị nghẽn (gãy flow tương tác).
* **Bài học rút ra:** **"Hành động dứt điểm" (Closure) quan trọng không kém gì "Hành động mở đầu".** Trước đó nhóm chỉ chăm chăm tối ưu hóa việc làm sao để floating toolbar hiện lên mượt mà và AI hỏi thật hay, nhưng lại quên mất việc người học cần một lối thoát tự nhiên sau khi đã hiểu bài. Sau buổi test, tôi đã đề xuất thêm ngay nút `✓ Hiểu rồi, tiếp tục đọc` để người học tự tin quay lại bài học. Trải nghiệm người dùng AI phải luôn đặt quyền kiểm soát (User Control) vào tay con người.
