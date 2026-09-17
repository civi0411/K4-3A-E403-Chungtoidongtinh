# Nhật ký Thử nghiệm Người dùng (User Validation Log — Khối R6)

**Đề tài:** Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor hiện có (Socratic Probing)  
**Nhóm:** Chungtoidongtinh · **Phòng:** E403 · **Lớp:** 3A  
**Mục tiêu:** Kiểm chứng giải pháp với người dùng thật của khóa K4 ngoài nhóm (Khối R6 — Tối đa **+8 điểm Bonus** theo `04-rubric.md`).

---

## 1. Phương pháp Thử nghiệm (5 Nhịp Stanford CS177 / PAIR Guidebook)

Nhóm tổ chức thử nghiệm trực tiếp tại phòng lab E403 với **4 Willing Users** đã khai báo từ Checkpoint 1:
1. **Comfort (1'):** Thiết lập tâm lý thoải mái: *"Tụi mình đang đánh giá sản phẩm, không đánh giá bạn; cứ nói to suy nghĩ của bạn."*
2. **Context (1'):** Hỏi trải nghiệm thật: *"Lần gần nhất bạn đọc bài giảng trên VLearn gặp chỗ không hiểu, bạn đã làm gì?"*
3. **Task (1'):** Giao nhiệm vụ theo **Outcome** (Người thử tự cầm chuột, nhóm không chỉ nút): *"Hãy tìm hiểu bài Lab 3 về ReAct Agent và dùng công cụ để gỡ rối chỗ kẹt của bạn."*
4. **Observe (5'):** Im lặng quan sát hành vi, ghi nhận chỗ do dự, chỗ hiểu sai, đo thời gian đọc hiểu.
5. **Hỏi sau khi dùng (2'):** Ghi nhận quote nguyên văn về điều khó chịu nhất, mức độ tin cậy và câu hỏi Disappointment của Sean Ellis (*"Nếu ngày mai không được dùng cái này nữa, bạn thấy: rất tiếc / hơi tiếc / không sao?"*).

---

## 2. Bảng Nhật ký Chi tiết 5 Phiên Thử nghiệm

| Người thử (Tên & MSSV) | Vai trò | Nhiệm vụ (Task giao) | Hành vi quan sát được (PAIR Signals) | Quote nguyên văn của người dùng | Mức độ nghiêm trọng | Quyết định của nhóm |
|---|---|---|---|---|:---:|---|
| **Đặng Quốc Cường**<br>`2A202602466` *(Willing User CP1)* | Học viên K4 | Đọc mục Task 1.1 và tìm hiểu khái niệm "ReAct Agent" | Bôi đen từ khóa "ReAct Agent", thấy toolbar nổi lên thì bấm ngay `🔍 Gợi mở`. Đọc 3 chip trong 4 giây rồi click Chip 1. Đọc Resolve Card và gật đầu. | *"Bình thường bôi đen bấm câu mẫu bot xả một đống lý thuyết lười đọc lắm. Cái này hiện 3 cái lựa chọn đúng cái mình đang kẹt, bấm vào đọc 3 dòng là hiểu luôn."* | Thấp (Insight tích cực) | **Giữ nguyên** thiết kế 3-Chip Socratic. Bổ sung nút lưu ghi chú vào sổ tay. |
| **Nguyễn Trần Bảo Tâm**<br>`2A202602408` *(Willing User CP1)* | Học viên K4 | Gỡ lỗi đoạn code `CUDA out of memory` ở Trạm cứu hộ FAQs | Bôi đen dòng chữ lỗi `CUDA out of memory`. Lúc đầu hơi khựng lại 2 giây vì không biết nút nào giúp sửa lỗi code nhanh. Sau đó bấm `🔍 Gợi mở`. | *"Ủa sao cái nút 'Giải thích' với 'Gợi mở' nhìn màu icon hơi giống nhau? Nhưng bấm vô 'Gợi mở' nó hiện 3 cách fix: dọn cache VRAM với hạ batch size thì rất chuẩn bài."* | **Trung bình (UX Do dự)** | **ĐÃ SỬA:** Đổi màu icon và thêm tag text rõ ràng: `💡 Giải thích (trả lời ngay)` và `🔍 Gợi mở (Socratic)`. |
| **Trần Thị Thu Hiền**<br>`2A202602737` *(Willing User CP1)* | Học viên K4 | Tìm hiểu hàm `call_anthropic` và cách bọc bảo mật API Key | Bôi đen đoạn code dài 3 dòng. Bấm `🔍 Gợi mở`. Đọc xong Resolve Card nhưng tìm cách đóng thẻ chat để đọc tiếp bài thì không thấy nút tắt nhanh. | *"Mình đọc xong hiểu rồi nhưng muốn quay lại đọc tiếp bài giảng thì cái khung chat nó che mất một phần màn hình, phải bấm nút nào để nó biết là mình xong rồi?"* | **Cao (Gãy Flow)** | **ĐÃ SỬA:** Thêm nút **`✓ Hiểu rồi, tiếp tục đọc`** dưới Resolve Card để tự động reset State Badge về `😴 Sẵn sàng`. |
| **Nguyễn Đình Nhật Trường** *(Willing User CP1)* | Học viên K4 | Đọc bài và thử hỏi về quét mã QR điểm danh phòng lab E403 | Thử bôi đen chữ "quét mã" và bấm hỏi AI. AI từ chối và hướng dẫn chụp màn hình báo Lab Coach E403. | *"Hay đấy, chứ con bot cũ hỏi điểm danh nó cũng ráng bịa ra lý thuyết về mã QR dài dằng dặc đọc mất công."* | Thấp (Validation Guardrail) | **Giữ nguyên** cơ chế Intent Guardrail từ chối câu hỏi Logistics (HAX G1). |
| **Lê Hoàng Khang**<br>`2A202602315` *(Học viên K4 E403)* | Học viên K4 | Thử bôi đen một đoạn văn bản dài 300 từ xem AI xử lý thế nào | Bôi đen nguyên 1 đoạn dài trong Task 1.3. Thấy Toolbar nổi lên kèm tooltip nhắc nhở. Sau đó rút ngắn vùng chọn còn đúng cụm từ `Structured JSON Output`. | *"Bôi đen nhiều quá thì đọc rối, may mà giao diện có nhắc chọn từ khóa trọng tâm. Chọn cụm ngắn thì AI gợi mở 3 ý rất gãy gọn."* | **Thấp (Hành vi biên)** | **ĐÃ SỬA:** Thêm chỉ báo giới hạn ngữ cảnh (Context Token Boundary) để khuyến khích học viên chọn từ khóa trọng tâm (HAX G2). |

---

## 3. Tổng hợp Kết quả & 4 Quyết định Sản phẩm

1. **Chủ đề lặp lại nhiều nhất:** Người dùng đánh giá rất cao việc **không phải đọc văn bản rác dài dòng**, nhưng ban đầu hơi do dự giữa nút "Giải thích ngay" và "Gợi mở Socratic", đồng thời cần một hành động dứt điểm (closure) sau khi đọc xong.
2. **Thay đổi đã làm ngay trước Demo (Ghi vào Spec §9 Changelog):**
   * Bổ sung nút bấm hành động chốt hạ: **`✓ Hiểu rồi, tiếp tục đọc`** vào cuối mỗi Resolve Card để học viên đóng thẻ và reset State Badge về `😴 Sẵn sàng`.
   * Tinh chỉnh nhãn nút trên Floating Toolbar: hiển thị tag phụ `(trả lời ngay)` cho nút Giải thích và `(Socratic)` cho nút Gợi mở để người dùng phân biệt mục đích trong 0.5 giây.
   * Cải tiến cơ chế Windowed Context Extraction: tự động thu hẹp vùng chọn nếu học viên bôi đen quá rộng, tránh tràn token và giữ AI tập trung.
3. **Giữ nguyên có lý do:** Giữ nguyên kiến trúc **đúng 3 Chip** (không tăng lên 4 hay 5 chip) vì người dùng chỉ mất 3-5 giây để quét mắt qua 3 lựa chọn mà không bị quá tải nhận thức (Cognitive Overload).
4. **Đưa vào Backlog dài hạn (Slide 6):** Tính năng tự động lưu lịch sử các chip đã chọn vào sơ đồ cây tri thức cá nhân (Personal Knowledge Graph) để học viên ôn tập trước kỳ thi cuối khóa.

---

## 4. Đo lường Chỉ số Sean Ellis (Disappointment Score)
* Câu hỏi: *"Nếu ngày mai tính năng Socratic Probing này không được tích hợp vào VLearn nữa, bạn cảm thấy thế nào?"*
* Kết quả (5 người ngoài nhóm):
  * **Rất tiếc (Very Disappointed):** 4 / 5 bạn (80.0%)
  * **Hơi tiếc (Somewhat Disappointed):** 1 / 5 bạn (20.0%)
  * **Không sao (Not Disappointed):** 0 / 5 bạn (0.0%)
👉 Chỉ số **80.0% "Rất tiếc"** vượt gấp đôi mốc chuẩn 40% của Sean Ellis, chứng minh tính năng giải quyết đúng nỗi đau thực tế của học viên K4!
