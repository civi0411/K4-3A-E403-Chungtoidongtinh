# Bản Thu hoạch Cá nhân (Individual Reflection)

* **Họ và Tên:** Nguyễn Nam Khánh  
* **Mã Học Viên:** `2A202602568`  
* **Lớp:** 3A · **Phòng thi:** E403  
* **Vai trò trong nhóm:** Thành viên (Data & Eval)  

---

### 1. Phần việc đảm nhiệm trong dự án
* Trực tiếp khai phá (data mining) tệp dữ liệu chatlog thật `tutor_turns.csv` của khóa K4 (3.097 dòng), trích xuất các con số định lượng chuẩn B (17,5% bấm câu mẫu, 89,3% xả lý thuyết, 0,19% hỏi gợi mở).
* Xây dựng bộ dữ liệu kiểm thử chuẩn **Golden Set 20 case thật** (`eval/golden_set.json`) bao phủ trọn vẹn qua 4 lớp chỗ khó.
* Lập trình script đo lường tự động `eval/eval_runner.py` và viết Báo cáo kết quả đo lường Lượt 1 (`eval/run_01_results.md`).

### 2. AI đã hỗ trợ tôi như thế nào trong quá trình làm việc?
* AI đóng vai trò như một trợ lý xử lý dữ liệu và viết mã phân tích:
  * Viết các đoạn script Python sử dụng thư viện `pandas` để lọc nhanh 3.097 dòng tương tác của K4 theo các trường cờ `is_preset`, `move_used`, và `has_citation`.
  * Hỗ trợ xây dựng các tiêu chí đánh giá bán tự động (LLM-as-a-judge / rule-based validation) trên 3 chiều: Accuracy, Brevity và Grounding để kiểm tra 20 case trong Golden Set.

### 3. Một bài học sâu sắc từ chính ca thất bại (Failure Case) của nhóm
* **Ca thất bại:** Ở case `GS-20` trong Golden Set ("Có giám sát / Cần đáp án"), model sinh ra các chip gợi ý dài hơn 15 từ do cố nhồi nhét cả một đoạn văn so sánh bảng dữ liệu, khiến bài test bị đánh dấu FAIL ở chiều Brevity.
* **Bài học rút ra:** **Đo lường bằng số liệu thực tế là cách duy nhất để nhìn thấy điểm mù.** Nếu chỉ nhìn bằng mắt ("vibe check"), tôi sẽ nghĩ chip giải thích dài là tốt vì đầy đủ thông tin. Nhưng khi đối chiếu với tiêu chuẩn Brevity của người học trên mobile/web, việc chip quá dài làm người học bị ngợp. Bài học lớn nhất của tôi là phải định nghĩa các chiều chất lượng kiểm chứng được bằng con số cứng (như $\le 15$ từ) trước khi đo, chứ không được chấm điểm theo cảm tính.
