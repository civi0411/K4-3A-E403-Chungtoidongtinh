# Thành phần Dữ liệu & Kiểm thử (Eval Pack)

Thư mục này chứa **bằng chứng số liệu mining (Evidence chuẩn B)** và **Bộ Golden Set (≥20 case)** dùng để kiểm thử prototype theo đúng yêu cầu của Rubric **R1 (15 điểm)** và **R4 (15 điểm)**.

> 🔒 **Quy định bảo mật:** Không commit nguyên vẹn toàn bộ file dữ liệu thô `tutor_turns.csv` (36MB) vào repo public theo quy chế của khoá học. Toàn bộ các ca kiểm thử ở đây đều được trích dẫn ngắn kèm mã `turn_id` (`T#####`) để đối chiếu kiểm chứng.

---

## 1. Bằng chứng số liệu Mining (Evidence chuẩn B)

* **Nguồn dữ liệu:** Hệ thống VLearn Tutor (`data/vlearn-pack/chatlog/tutor_turns.csv`).
* **Phạm vi phân tích:** Khoá K4 (`cohort_hint = K4`), thời gian từ 09/09/2026 đến 15/09/2026.
* **Phương pháp đếm:** Quét toàn bộ 3.097 dòng chatlog của K4, phân loại theo cờ `is_preset`, `move_used`, và `has_citation`.

| Chỉ số đo lường | Số lượng | Tỷ lệ (%) | Ý nghĩa thực tế |
|---|---|---|---|
| **Tổng lượt hỏi đáp K4** | **3.097** | 100% | Toàn bộ tương tác của học viên khoá 4 |
| **Bấm câu hỏi mẫu (`is_preset`)** | **542** | **17,5%** | Học viên bôi đen bấm câu có sẵn ("giải thích đoạn này") |
| **Tutor xả lý thuyết (`review_concept`)** | **2.767** | **89,3%** | Bot chỉ độc thoại giảng bài dài, không tương tác 2 chiều |
| **Tutor hỏi gợi mở (`ask_probing_question`)** | **6** | **0,19%** | Cả khoá chỉ có đúng 6 lần bot biết hỏi ngược học viên |
| **Trả lời KHÔNG trích dẫn trang** | **839** | **27,1%** | Trả lời không căn cứ, không dẫn nguồn `[trang N]` |

---

## 2. Cấu trúc bộ Golden Set (`eval/golden_set.json`)

Bộ Golden Set gồm **20 case thật trích từ chatlog K4**, phân loại theo cấu trúc 4 lớp chỗ khó:

* **Lớp ① Nguồn sự thật (4 case):** Bôi đen đoạn nằm ngoài tài liệu hoặc không có căn cứ.
* **Lớp ② Mơ hồ / Thiếu thông tin (8 case):** Bôi đen 1 từ cụt ngủn (ví dụ bôi mỗi chữ `"https"`, bôi mỗi chữ `"CVAT"`) bấm câu hỏi mẫu.
* **Lớp ③ Ngoài phạm vi / Thẩm quyền (3 case):** Hỏi đáp án bài tập, hỏi code lab mà chưa làm.
* **Lớp ④ Đặc thù domain (5 case):** Khái niệm kỹ thuật dễ gây hiểu nhầm (Self-attention, Object detection, Loss function).

### Trích dẫn 3 case tiêu biểu trong `golden_set.json`:
1. `GS-02` (`T10372`): Học viên bôi đen nhầm chữ `"https"` trong link Slido $\rightarrow$ Tutor cũ xả bài lý thuyết 455 ký tự về giao thức mạng $\rightarrow$ *Kỳ vọng: Hỏi lại xem học viên có chọn nhầm không.*
2. `GS-03` (`T10378`): Học viên bôi đen từ viết tắt `"CVAT"` $\rightarrow$ Tutor cũ xả 1.069 ký tự $\rightarrow$ *Kỳ vọng: Đưa 2 lựa chọn gợi mở (Cài đặt vs Gán nhãn).*
3. `GS-04` (`T10382`): Học viên bôi đen `"Self-attention Demo"` $\rightarrow$ Tutor cũ giải thích chung chung $\rightarrow$ *Kỳ vọng: Hỏi gợi mở về cơ chế attention trong Transformer.*

---

## 3. Tiêu chí đánh giá chất lượng (Quality Bar)

Để đo lường ở CP3 và CP4, hệ thống đánh giá theo 3 chiều:
1. **Tỷ lệ hỏi trúng điểm nghẽn (Accuracy):** Người ngoài nhóm đọc câu hỏi gợi mở đánh giá xem có trúng từ khoá đoạn bôi đen không.
2. **Độ ngắn gọn (Brevity):** Câu hỏi gợi mở $\le$ 2 câu + kèm tối đa 2 lựa chọn A/B.
3. **Tính trung thực (Groundedness):** 100% không bịa đặt kiến thức ngoài trang tài liệu.

* **Quality bar cam kết (chốt tại CP4):** $\ge$ 80% case trong Golden Set được phản hồi bằng câu hỏi gợi mở đạt chuẩn, không xả lý thuyết một chiều.
