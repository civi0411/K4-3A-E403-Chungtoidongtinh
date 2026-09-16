# CANVAS 5 TIÊU CHÍ — Checkpoint 1 (Nhóm Chungtoidongtinh · Phòng E403)

**Đề tài:** Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor hiện có (Socratic Probing)
**Đội trưởng:** Trần Chí Vĩ (Mã HV: `2A202602968`)
**Repo:** `https://github.com/civi0411/K4-3A-E403-Chungtoidongtinh`

---

**1. Pain cụ thể (Ai — đang làm gì — vướng đâu — hậu quả gì):**
- **Ai:** Học viên khoá K4 đang tự học trên VLearn.
- **Đang làm gì:** Đọc tài liệu slide, gặp chỗ khó hiểu.
- **Vướng đâu:** Không thể bôi đen để hỏi ngay tại chỗ mà phải gõ lại vào ô chat, và khi bấm câu mẫu thường nhận về một bài giảng lại lý thuyết dài dòng chung chung lặp lại nội dung slide, không đúng chỗ mình đang kẹt.
- **Hậu quả gì:** Khiến học viên nản lòng và phải chuyển sang hỏi bạn hoặc bỏ qua.

**2. Bằng chứng (Áp dụng tiêu chuẩn B - Mining data):**
- **Đếm được:** Mining 35 lượt chatlog K4
  - 17,5% câu hỏi là câu mẫu bấm sẵn.
  - 89,3% Tutor chỉ biết xả lý thuyết dài.
  - Chỉ đúng 6 lượt Tutor biết dùng câu hỏi gợi mở.
- **Ví dụ nguyên văn:** Lượt T10372 bôi nhầm link bot xả 455 chữ; T10378 bôi "CVAT" bot xả 1.069 chữ bức tường. Phương pháp đếm: Trích xuất bằng code Python phân loại trực tiếp độ dài và cấu trúc câu trả lời của AI.

**3. Problem statement + Impact:**
- **Problem Statement:** Làm rõ ngay chỗ vừa đọc không hiểu trong bài giảng bằng phương pháp gợi mở Socratic Probing, không để học viên đọc văn bản rác.
- **Impact / Cost-of-error:** Tránh đọc văn bản rác gây mất thời gian và hiểu sai kiến thức (chi phí lỗi trung bình).
- **Phân công 4 thành viên:** 
  - Trần Chí Vĩ: Lead, nộp CP, chủ trì spec.md, demo.
  - Nguyễn Nam Khánh: Mining data, Golden set, eval.
  - Nguyễn Phi Nhật: Prompt system, prototype code.
  - Hoàng Minh Tuấn: 4 lớp chỗ khó, testing R6, slide.

**4. Lát cắt prototype được (MỘT CÂU):**
"Một học viên bôi đen đoạn bài giảng và bấm câu hỏi mẫu, Tutor phản hồi bằng một câu hỏi gợi mở ngắn kèm 2 lựa chọn trọng tâm thay vì xả lý thuyết dài, giúp học viên chỉ rõ được điểm mình chưa hiểu." (Automation: Mức Conditional - Câu chi tiết trả lời ngay; Câu mơ hồ kích hoạt gợi mở Socratic).

**5. User sẵn sàng thử (Willing users):**
Nhóm đã chốt 4 willing users ngoài nhóm sẽ dùng thử prototype trước demo CP5:
1. Đặng Quốc Cường - 2A202602466 (Học viên K4)
2. Nguyễn Trần Bảo Tâm - 2A202602408 (Học viên K4)
3. Trần Thị Thu Hiền - 2A202602737 (Học viên K4)
4. Nguyễn Đình Nhật Trường (Học viên K4)
