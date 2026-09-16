# AI SPEC — Tutor Probing: Gợi mở đúng chỗ vướng · Nhóm Chungtoidongtinh · Phòng E403
Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job
- **Job executor + workflow:** Học viên đang tự học / ôn bài trên VLearn. Workflow: Đọc tài liệu/slide → gặp đoạn khó hiểu → bôi đen đoạn văn → bấm câu mẫu có sẵn ("giải thích đoạn bôi đen") hoặc gõ câu hỏi → đọc câu trả lời của AI Tutor.
- **Core JTBD:** Hiểu rõ một khái niệm khó trong bài giảng ngay khi đang tự học để hoàn thành bài tập/quiz.
- **Problem statement:** Học viên khi bôi đen đoạn bài giảng bấm câu mẫu thường nhận về một bài giảng lại lý thuyết dài dòng chung chung, không đúng chỗ mình đang kẹt, khiến học viên nản lòng và phải chuyển sang hỏi bạn hoặc bỏ qua.
- **Evidence (chuẩn B từ data chatlog 13.494 lượt trong `data/vlearn-pack`):**
  - Số liệu mining:
    - 22,7% câu hỏi là câu mẫu bấm sẵn (`is_preset = True`: "giải thích đoạn bôi đen", "tóm tắt nội dung chính").
    - 89,8% (12.127/13.494) câu trả lời của Tutor xả lý thuyết một chiều (`move_used = review_concept`).
    - Gần như KHÔNG BAO GIỜ hỏi ngược để dò mức hiểu: `move_used = ask_probing_question` chỉ có 28/13.494 lượt (0,2%).
    - 28% câu trả lời không có trích dẫn tài liệu (`has_citation = False`).
  - Ví dụ nguyên văn:
    1. `T00867`: Học viên bấm câu mẫu, Tutor xả tràng dài khái niệm không gắn với điểm vướng cụ thể.
    2. `T00120`: Câu trả lời lặp lại nguyên văn slide nhưng không giải thích được vì sao.
    3. `T00452`: Học viên hỏi ngắn "đoạn này nghĩa là sao", Tutor trả lời 1.200 ký tự lý thuyết chung.

## §2. Impact & quyết định chọn
- **Bảng impact 3 ứng viên:**
  | Ứng viên | Bao nhiêu người gặp | Tần suất | Mỗi lần tốn gì | Khả thi build trong hackathon |
  |---|---|---|---|---|
  | **1. Tutor hỏi gợi mở khi gặp câu hỏi mẫu (Chọn)** | ~22,7% lượt hỏi (hơn 3.000 lượt trong dataset) | Rất cao khi học viên tự học | 5-10 phút đọc văn bản thừa mà không hiểu bài | Rất cao (chỉnh Prompt + Flow phân loại câu hỏi) |
  | 2. Chặn câu hỏi ngoài phạm vi bài học | ~8-10% lượt hỏi | Trung bình | Tutor bịa thông tin, học viên học sai kiến thức | Trung bình |
  | 3. Bản đồ lỗ hổng kiến thức cho giảng viên | 5-10 giảng viên/TA | Cuối mỗi buổi học | TA tốn 1-2 tiếng tổng hợp tay | Cần thêm dữ liệu aggregate, tốn thời gian |
- **Ứng viên ĐÃ LOẠI:** Ứng viên 3 (vì ít user tiếp cận trực tiếp trong phòng thi, khó làm validation user test ở CP5) và Ứng viên 2 (tần suất thấp hơn câu hỏi mẫu).
- **Ứng viên CHỌN:** Ứng viên 1 vì chiếm 22,7% toàn bộ câu hỏi trên nền tảng, giải quyết đúng nỗi đau trực tiếp của học viên đang ngồi trong phòng E403.

## §3. Giải pháp tương tự đã nghiên cứu
- **Khanmigo (Khan Academy):** Dùng Socratic method — không bao giờ đưa ngay đáp án mà luôn hỏi ngược 1 câu ngắn để học sinh tự suy nghĩ. Đáng học: Luôn giữ câu hỏi ngắn dưới 2 câu. Đáng né: Hỏi quá nhiều vòng làm học viên ức chế khi đang cần câu trả lời gấp.
- **ChatGPT Study Mode:** Giải thích kèm gợi ý các câu hỏi tiếp theo. Đáng học: Chia nhỏ câu trả lời thành từng bước ngắn.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một học viên bôi đen đoạn bài giảng và bấm câu hỏi mẫu, Tutor phản hồi bằng một câu hỏi gợi mở ngắn để xác định đúng chỗ vướng thay vì xả lý thuyết dài, giúp học viên chỉ rõ được điểm mình chưa hiểu.
- **Non-goals (3 thứ KHÔNG build):**
  1. Không build lại giao diện VLearn mới (chỉ can thiệp logic trả lời của AI Tutor).
  2. Không cố giải toàn bộ câu hỏi mở rộng ngoài phạm vi bài giảng.
  3. Không bắt học viên phải trả lời probing question nếu học viên muốn xem đáp án ngay (cho phép bỏ qua để nhận giải thích nhanh).
- **Mức prototype nhắm tới:** [x] Working — Frontend đơn giản mô phỏng khung chat VLearn, Backend gọi API LLM thật với System Prompt phân loại và sinh câu hỏi probing.
- **Automation:** [x] Conditional (Có điều kiện) — Phân loại input: Nếu câu hỏi chi tiết $\rightarrow$ Trả lời ngay có trích dẫn `[trang N]`; Nếu câu mẫu hoặc mơ hồ $\rightarrow$ Kích hoạt probing question ngắn.
  - *Lý do theo cost-of-error:* Trả lời lý thuyết dài dòng khi chưa rõ ý học viên khiến học viên tốn thời gian đọc rác hoặc hiểu sai (cost-of-error trung bình).

- **§4b. Nguyên tắc áp dụng (HAX/PAIR):**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ hệ thống làm được gì** | Dòng thông báo đầu khung chat: "Tutor đồng hành: Mình sẽ hỏi gợi mở để giúp bạn tự gỡ điểm nghẽn, hoặc bạn có thể yêu cầu tóm tắt nhanh." |
  | **G2 — Làm rõ làm tốt đến đâu** | Cảnh báo: "Câu trả lời dựa trên nội dung bài giảng hiện tại, kèm trích dẫn trang cụ thể." |
  | **G8 — Gạt bỏ dễ dàng** | Có nút "Bỏ qua & Xem giải thích đầy đủ" nếu học viên không muốn trả lời câu hỏi gợi mở. |
  | **G10 — Thu hẹp phạm vi khi nghi ngờ** | Khi input là câu mẫu cụt ("giải thích đoạn bôi đen"), không đoán bừa mà chỉ hỏi 1 câu tập trung vào từ khoá chính của đoạn bôi đen. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
*(Hoàn thiện chi tiết trước CP4)*

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Học viên bôi đen đoạn $\rightarrow$ bấm câu mẫu $\rightarrow$ Tutor hỏi lại 1 câu trúng chỗ mập mờ $\rightarrow$ Học viên trả lời ngắn $\rightarrow$ Tutor chốt đáp án đúng trọng tâm kèm trích dẫn `[trang N]`.
- **Low-confidence:** Học viên trả lời câu probing mơ hồ $\rightarrow$ Tutor đưa ra 2 lựa chọn (A hoặc B) để học viên chọn.
- **Failure / Không căn cứ:** Đoạn bôi đen không có trong tài liệu $\rightarrow$ Tutor từ chối lịch sự và hướng dẫn vị trí bài giảng liên quan.
- **Correction:** Học viên bấm nút "Xem giải thích ngay" $\rightarrow$ Bỏ qua bước gợi mở và nhận câu trả lời tổng quan.

## §7. Kiểm thử
- **Chiều chất lượng:** Tỷ lệ hỏi trúng điểm nghẽn (người ngoài nhóm đánh giá được), Tỷ lệ câu hỏi ngắn gọn (≤2 câu), Tỷ lệ có trích dẫn đúng trang (`[trang N]`).
- **Golden set:** ≥20 case trích từ `data/vlearn-pack/chatlog/tutor_turns.csv`.
- **Quality bar (dự kiến):** ≥80% case câu mẫu được phản hồi bằng câu hỏi gợi mở phù hợp; 100% không bịa kiến thức ngoài trang.

## §8. Phân công & kế hoạch
- **Phân công chi tiết:**
  - Trần Chí Vĩ: Quản lý chung, viết `spec.md`, nộp các Checkpoint, thuyết trình demo CP6.
  - Nguyễn Nam Khánh: Mining data `tutor_turns.csv`, xây dựng Golden Set 20 case, chạy đo lường (`eval/`).
  - Nguyễn Phi Nhật: Thiết kế Prompt, xây dựng Prototype frontend/backend gọi AI thật (`codebase/`).
  - Hoàng Minh Tuấn: Xây dựng kịch bản 4 lớp chỗ khó, kiểm thử HAX/PAIR, điều phối testing R6, làm slide PDF.
- **Willing users (Khai báo từ CP1):**
  - Người 1: [Họ tên & MSSV bạn bàn bên cạnh]
  - Người 2: [Họ tên & MSSV bạn bàn bên cạnh]

## §9. Changelog
*(Cập nhật khi có feedback từ validation)*
