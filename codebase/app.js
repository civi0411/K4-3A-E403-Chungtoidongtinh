// =========================================================
// VLearn Tutor (Socratic Probing) — Prototype v2
// Đề tài: Track A (VLearn Tutor) — Đề A1: Tối ưu AI Tutor
// Nhóm: Chungtoidongtinh · Phòng E403
// =========================================================

// 1. MOCK KNOWLEDGE BASE CHUẨN BÀI LAB DAY 03 & 3 CHIPS ARCHITECTURE
const MOCK_KNOWLEDGE_BASE = {
  "react agent": {
    matchedKeyword: "ReAct Agent",
    directAnswer: "ReAct Agent (Reasoning + Acting) là mô hình AI kết hợp giữa suy luận và hành động. Thay vì chỉ sinh văn bản đóng băng, Agent tự lập luận (Thought), quyết định gọi công cụ ngoài (Action) và đọc kết quả trả về (Observation) để xử lý tác vụ đa bước phức tạp.",
    extraExample: "📌 **Ví dụ thực tế:** Khi hỏi *'Thời tiết Hà Nội hôm nay và gợi ý trang phục'*, ReAct Agent sẽ gọi API OpenWeather lấy nhiệt độ 28°C rồi lập luận đưa ra gợi ý mặc áo thun thoáng mát.",
    socraticQuestion: "Bạn đang bôi đen 'ReAct Agent'. Điểm nào dưới đây là phần bạn đang cảm thấy kẹt nhất?",
    chips: [
      {
        id: 1,
        label: "1. Cơ chế vòng lặp Thought -> Action -> Observation hoạt động ra sao?",
        explanation: "ReAct Agent không sinh ngay câu trả lời cuối cùng mà lặp qua 3 nhịp: (1) **Thought** (LLM tự suy ngẫm bước cần làm); (2) **Action** (LLM phát lệnh gọi Tool, ví dụ hàm search hay query DB); (3) **Observation** (Mô hình nhận kết quả trả về từ môi trường để tư duy tiếp hoặc xuất kết quả).",
        example: "💡 **Ví dụ trực quan:** Giống như lập trình viên sửa bug: Đọc mã lỗi (Thought) ➔ Tra cứu Google / Chạy test (Action) ➔ Đọc kết quả terminal (Observation) ➔ Fix code."
      },
      {
        id: 2,
        label: "2. Sự khác biệt cốt lõi giữa Chatbot (Cấp 2) và ReAct Agent (Cấp 3)?",
        explanation: "Chatbot thông thường chỉ dựa vào tri thức đóng băng trong trọng số mô hình (weights) và không thể tương tác thế giới thực. ReAct Agent được gắn 'tay chân' là các Tool (hàm API, database, calculator), cho phép truy vấn dữ liệu thời gian thực và tự sửa lỗi nếu tool trả về exception.",
        example: "💡 **Ví dụ so sánh:** Hỏi Chatbot Cấp 2: 'Bitcoin giá bao nhiêu?' ➔ Trả lời dữ liệu cũ 2023. Hỏi ReAct Agent Cấp 3 ➔ Tự gọi `get_crypto_price('BTC')` trả về giá chính xác lúc này."
      },
      {
        id: 3,
        label: "3. Cách viết vòng lặp While và điều kiện ngắt (stop condition) trong Python?",
        explanation: "Trong file `src/react_agent.py`, vòng lặp `while iteration < max_iterations:` sẽ chạy liên tục. Điều kiện dừng là khi phản hồi của LLM không còn yêu cầu gọi công cụ (`tool_calls` rỗng), hoặc khi đạt trần an toàn `max_iterations = 5` để chống lặp vô tận tốn token.",
        example: "💻 **Code mẫu:** `if not response.tool_calls: return response.content` ➔ ngắt vòng lặp và gửi câu trả lời cuối cùng cho người dùng."
      }
    ]
  },

  "native tool calling": {
    matchedKeyword: "Native Tool Calling",
    directAnswer: "Native Tool Calling là cơ chế được huấn luyện trực tiếp vào model (Anthropic / OpenAI). Khi cần dùng công cụ, model dừng sinh text và trả về đối tượng JSON chuẩn (tên hàm + arguments) thay vì phải dùng regex tách chuỗi tự do.",
    extraExample: "📌 **Ví dụ:** Thay vì text 'Hãy gọi search_db với id=10', Claude/OpenAI trả về cấu trúc `{ name: 'search_db', arguments: { id: 10 } }`.",
    socraticQuestion: "Khi tìm hiểu Native Tool Calling, bạn muốn tháo gỡ điểm nào?",
    chips: [
      {
        id: 1,
        label: "1. Cú pháp khai báo JSON Schema cho tham số (parameters)?",
        explanation: "Tool Schema được định nghĩa theo chuẩn JSON Schema gồm 3 trường: `name` (tên hàm), `description` (hướng dẫn cho LLM hiểu khi nào dùng), và `input_schema` (kiểu dữ liệu các tham số bắt buộc).",
        example: "💻 **Mẫu khai báo:** `{ 'name': 'calculator', 'description': 'Tính biểu thức toán', 'input_schema': {'type': 'object', 'properties': {'expr': {'type': 'string'}}}}`."
      },
      {
        id: 2,
        label: "2. Cơ chế model phát hiện khi nào cần gọi Tool hay trả lời thẳng?",
        explanation: "LLM dựa vào `description` của từng tool trong prompt hệ thống. Nếu câu hỏi cần thông tin tool hỗ trợ, LLM trả về `stop_reason: tool_use`. Nếu là câu chào hỏi thông thường, nó trả lời bằng text bình thường.",
        example: "💡 **Ví dụ:** Hỏi 'Chào bạn' ➔ Text thường. Hỏi '153 * 289 bằng bao nhiêu?' ➔ LLM tự quyết định kích hoạt tool `calculator`."
      },
      {
        id: 3,
        label: "3. Xử lý lỗi khi model sinh tham số JSON sai schema?",
        explanation: "Khi parse arguments bị lỗi `JSONDecodeError` hoặc thiếu tham số bắt buộc, ta bắt exception trong code Python, đóng gói thông báo lỗi thành `tool_result` và gửi ngược lại cho LLM để nó tự sửa sai (Self-healing loop).",
        example: "🔄 **Kịch bản tự sửa:** Gửi lại message `{ role: 'tool', content: 'Lỗi: tham số expr bị thiếu dấu đóng ngoặc' }` để model tự sinh lại JSON hợp lệ."
      }
    ]
  },

  "waterfall trace log": {
    matchedKeyword: "Waterfall Trace Log",
    directAnswer: "Waterfall Trace Log là bản ghi vết thực thi trực quan ghi lại từng mắt xích hoạt động của Agent: thời điểm bắt đầu, thời lượng chạy từng nhịp suy luận, thời gian gọi tool thực tế và mức tiêu thụ token.",
    extraExample: "📌 **Ví dụ cấu trúc:** Turn 1: Thought 320ms ➔ Tool execute 150ms ➔ Observation ➔ Final answer 210ms (Tổng độ trễ: 680ms).",
    socraticQuestion: "Vết Waterfall Trace Log là yêu cầu bắt buộc của bài Lab. Bạn đang băn khoăn ở phần nào?",
    chips: [
      {
        id: 1,
        label: "1. Cấu trúc chuẩn file docs/trace_waterfall.json gồm những trường gì?",
        explanation: "File log gồm mảng các lượt gọi (turns). Mỗi item cần có: `timestamp`, `step` (Thought / Action / Observation), `tool_name`, `latency_ms` và `tokens_used`.",
        example: "📄 **Mẫu JSON:** `[{ 'step': 'Action', 'tool': 'fetch_stock', 'latency_ms': 142, 'status': 'success' }]`."
      },
      {
        id: 2,
        label: "2. Đo độ trễ (latency) từng bước trong Python bằng cách nào?",
        explanation: "Sử dụng module `time.perf_counter()` trước và sau khi gọi API LLM hoặc thực thi hàm công cụ, sau đó lấy hiệu số nhân 1000 để ra mili-giây (ms).",
        example: "💻 **Code mẫu:** `t0 = time.perf_counter(); res = run_tool(); latency = (time.perf_counter() - t0) * 1000`."
      },
      {
        id: 3,
        label: "3. Cách dùng file trace này để chấm điểm rubric bài Lab?",
        explanation: "Giảng viên và bot chấm điểm sẽ đọc file `trace_waterfall.json` để xác minh Agent của bạn thực sự tương tác với Tool hay chỉ hardcode giả lập câu trả lời.",
        example: "🎯 **Tiêu chí chấm:** File trace phải có timestamp khớp thời gian chạy test suite và có log gọi hàm thực tế."
      }
    ]
  },

  "thought action observation": {
    matchedKeyword: "Thought -> Action -> Observation",
    directAnswer: "Vòng lặp ReAct Loop (Thought -> Action -> Observation) là chu trình giúp Agent suy nghĩ (Thought), hành động qua tool (Action), và quan sát kết quả từ môi trường (Observation) cho đến khi giải xong bài toán.",
    extraExample: "📌 **Ví dụ:** Thought: 'Cần tìm dân số TP.HCM' ➔ Action: `get_population('HCM')` ➔ Observation: '9.3 triệu' ➔ Final Answer.",
    socraticQuestion: "Về chu trình ReAct Loop, điểm nghẽn của bạn đang nằm ở đâu?",
    chips: [
      {
        id: 1,
        label: "1. LLM nhận biết kết quả Observation bằng cách nào?",
        explanation: "Kết quả thực thi từ hàm Python được đưa vào danh sách hội thoại với vai trò `tool_result` (hoặc `user` message chứa kết quả), sau đó gửi toàn bộ lịch sử này cho LLM ở lượt gọi tiếp theo.",
        example: "💬 **Payload gửi tiếp:** `messages.append({'role': 'tool', 'tool_call_id': id, 'content': str(result)})`."
      },
      {
        id: 2,
        label: "2. Xử lý khi Tool trả về kết quả rỗng hoặc báo lỗi?",
        explanation: "Không nên để chương trình crash! Hãy chuyển error message thành text Observation để LLM đọc được và suy nghĩ phương án thử công cụ khác (Re-trying logic).",
        example: "🔄 **Tự hồi phục:** Observation: 'Không tìm thấy kết quả' ➔ Thought tiếp theo: 'Sẽ thử tìm kiếm bằng từ khóa đồng nghĩa'."
      },
      {
        id: 3,
        label: "3. Thiết lập điều kiện dừng tránh lặp vô tận (Infinite Loop)?",
        explanation: "Cần đặt giới hạn `max_turns = 5` và kiểm tra cờ kết thúc. Nếu sau 5 lượt vẫn chưa có đáp án, Agent sẽ chủ động dừng và thông báo cho người dùng thay vì treo máy.",
        example: "🛑 **Code:** `if turn >= MAX_TURNS: return 'Đã đạt giới hạn số bước suy luận tối đa.'`."
      }
    ]
  },

  "call_anthropic": {
    matchedKeyword: "call_anthropic",
    directAnswer: "Hàm `call_anthropic` khởi tạo client kết nối Claude API, truyền tham số model, temperature và danh sách messages để nhận về phản hồi văn bản hoặc yêu cầu gọi tool.",
    extraExample: "📌 **Ví dụ cú pháp:** `response = client.messages.create(model='claude-3-5-sonnet', temperature=0.0, messages=[...])`.",
    socraticQuestion: "Bạn bôi đen đoạn mã gọi API `call_anthropic`. Bạn muốn làm rõ điều gì?",
    chips: [
      {
        id: 1,
        label: "1. Tham số temperature ảnh hưởng thế nào đến Tool Calling?",
        explanation: "Với chatbot thông thường, temperature = 0.7 giúp văn phong phong phú. Nhưng với ReAct Agent cần sinh JSON Tool Call chuẩn xác, ta nên đặt `temperature = 0.0` để output luôn tất định và chuẩn schema.",
        example: "⚡ **Khuyến nghị:** Luôn dùng `temperature=0` khi cần sinh tham số gọi hàm."
      },
      {
        id: 2,
        label: "2. Quản lý ANTHROPIC_API_KEY bảo mật, không lộ trên GitHub?",
        explanation: "Tuyệt đối không hardcode API key vào code (HAX G2). Hãy lưu vào Colab Secrets hoặc file `.env` (thêm vào `.gitignore`) và đọc qua `os.environ.get('ANTHROPIC_API_KEY')`.",
        example: "🔒 **Bảo mật:** `client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])`."
      },
      {
        id: 3,
        label: "3. Cách bọc hàm xử lý ngoại lệ (try/except timeout, rate limit)?",
        explanation: "Nên bọc lệnh gọi bằng `try...except anthropic.RateLimitError` và triển khai cơ chế retry với thời gian chờ tăng dần (Exponential Backoff) để Agent không bị gián đoạn.",
        example: "🛠️ **Code:** `except anthropic.APIConnectionError: time.sleep(2); retry()`."
      }
    ]
  },

  "cuda out of memory": {
    matchedKeyword: "CUDA out of memory",
    directAnswer: "Lỗi CUDA OutOfMemory xảy ra khi kích thước mô hình hoặc bộ nhớ đệm activations vượt quá dung lượng VRAM card đồ họa máy tính / máy ảo Colab.",
    extraExample: "📌 **Ví dụ:** Card GPU có 15GB VRAM nhưng bạn load model 14B params cùng batch_size=8 dẫn đến tràn bộ nhớ.",
    socraticQuestion: "Bạn đang gặp mã lỗi tràn VRAM GPU. Bạn muốn giải quyết theo hướng nào?",
    chips: [
      {
        id: 1,
        label: "1. Hạ batch size và dọn dẹp cache VRAM trong PyTorch?",
        explanation: "Gọi `torch.cuda.empty_cache()` sau mỗi lượt chạy và giảm `batch_size = 1`. Đồng thời xóa các biến tensor không dùng bằng `del tensor_var; gc.collect()`.",
        example: "💻 **Code giải phóng VRAM:** `import torch; torch.cuda.empty_cache()`."
      },
      {
        id: 2,
        label: "2. Dùng kỹ thuật lượng tử hóa (Quantization 4-bit / 8-bit)?",
        explanation: "Sử dụng thư viện `bitsandbytes` với cấu hình `load_in_4bit=True` khi load model từ HuggingFace, giúp giảm dung lượng VRAM từ 16GB xuống chỉ còn ~4GB.",
        example: "⚙️ **Code:** `model = AutoModelForCausalLM.from_pretrained(model_id, load_in_4bit=True)`."
      },
      {
        id: 3,
        label: "3. Chuyển sang gọi API Cloud (Anthropic / OpenAI) không tốn VRAM?",
        explanation: "Bài Lab 3 tập trung vào ReAct logic và Tool Calling, nên việc gọi API đám mây sẽ giúp bạn không cần tốn VRAM GPU cá nhân mà vẫn chạy mượt mà.",
        example: "☁️ **Giải pháp:** Dùng trực tiếp Claude API hoặc OpenAI API theo hướng dẫn của bài Lab."
      }
    ]
  },

  "quét mã điểm danh": {
    matchedKeyword: "Quét mã điểm danh",
    isOutOfScope: true,
    rejectionReason: "Vấn đề điểm danh là quy trình vận hành (Logistics), không thuộc nội dung bài học chuyên môn (Lớp chỗ khó ③: Ngoài thẩm quyền).",
    explanation: "Chào bạn! Theo quy định của khoá học (tin nhắn M14918 trên Discord): Việc quét mã QR điểm danh bằng Microsoft Form là hệ thống độc lập, không đồng bộ lịch sử về app MyVinUni. Bạn hãy chủ động chụp lại ảnh màn hình xác nhận sau khi nộp form, và nhắn ngay cho Lab Coach trực phòng E403 để được hỗ trợ đối soát nhé!",
    citation: "Quy chế điểm danh K4 & Kênh hỗ trợ Lab Coach phòng E403"
  },

  "quantum": {
    matchedKeyword: "Quantum Computing",
    isOutOfScope: true,
    rejectionReason: "Khái niệm này không nằm trong nội dung bài học Day 03 (ReAct Agent & Tool Calling).",
    explanation: "Trợ giảng AI đồng hành học tập chỉ giải thích kiến thức thuộc phạm vi bài giảng của khoá học để đảm bảo tính chính xác và trích dẫn chuẩn. Bạn có muốn quay lại chủ đề ReAct Agent không?",
    citation: "HAX G1 & G2: Giới hạn phạm vi & Không bịa kiến thức"
  },

  "https": {
    matchedKeyword: "https",
    directAnswer: "Đoạn 'https' là tiền tố giao thức của Starter Repo trên GitHub dành cho học viên lớp K4.",
    extraExample: "📌 **Link đầy đủ:** `https://github.com/VinUni-AI20k/K4A-Day03-Lab-Chatbot-vs-ReAct-Agent`.",
    socraticQuestion: "Bạn vừa bôi nhầm chữ 'https'. Bạn đang cần hỗ trợ phần nào liên quan đến Repository bài Lab?",
    chips: [
      {
        id: 1,
        label: "1. Lấy đường link Fork đầy đủ của lớp Sáng (K4A) / Chiều (K4B)?",
        explanation: "Bạn bấm vào link repository trên bài đọc, sau đó nhấn nút 'Fork' ở góc phải trên cùng GitHub để tạo bản sao về tài khoản cá nhân trước khi clone.",
        example: "🔗 **Repo:** `VinUni-AI20k/K4A-Day03-Lab-Chatbot-vs-ReAct-Agent`."
      },
      {
        id: 2,
        label: "2. Cách cấu hình SSH key hoặc Personal Access Token khi clone?",
        explanation: "Nếu gặp lỗi Permission Denied khi clone HTTPS, hãy chạy `gh auth login` hoặc thêm SSH Public Key vào mục Settings -> SSH Keys trên GitHub.",
        example: "🔑 **Lệnh kiểm tra:** `ssh -T git@github.com`."
      },
      {
        id: 3,
        label: "3. Quy định đặt tên nhánh và commit bài Lab theo chuẩn?",
        explanation: "Nên commit thường xuyên sau mỗi Task hoàn thành với message rõ ràng: `feat(task-1): declare tool schema` để lưu vết lịch sử chấm bài.",
        example: "📝 **Mẫu commit:** `git commit -m 'feat(task-2): implement react loop'`."
      }
    ]
  },

  "tool schema": {
    matchedKeyword: "Tool Schema",
    directAnswer: "Tool Schema là bản đặc tả cấu trúc dữ liệu theo chuẩn JSON Schema, định nghĩa tên hàm, mô tả ngữ cảnh sử dụng và danh sách tham số để mô hình LLM biết chính xác khi nào và truyền dữ liệu gì vào tool.",
    extraExample: "📌 **Mẫu khai báo:** `{ 'name': 'calculator', 'description': '...', 'input_schema': {'type': 'object', 'properties': {'expr': {'type': 'string'}}}}`.",
    socraticQuestion: "Về việc khai báo Tool Schema, bạn đang gặp vướng mắc ở phần nào?",
    chips: [
      {
        id: 1,
        label: "1. Cách viết trường description để LLM không bị nhầm lẫn?",
        explanation: "Trường `description` là prompt quan trọng nhất. Cần nêu rõ: tool dùng để làm gì, khi nào NÊN dùng và khi nào KHÔNG NÊN dùng, kèm ví dụ định dạng chuỗi.",
        example: "💡 **Mẹo:** 'Dùng khi cần tính toán số học phức tạp; không dùng cho việc đếm từ đơn giản'."
      },
      {
        id: 2,
        label: "2. Quy định kiểu dữ liệu trong input_schema (string, number, array)?",
        explanation: "Sử dụng các kiểu chuẩn của JSON Schema: 'string', 'number', 'integer', 'boolean', 'array', 'object'. Luôn khai báo mảng `required` chứa các trường bắt buộc.",
        example: "📄 **Schema:** `'properties': {'student_id': {'type': 'string'}}, 'required': ['student_id']`."
      },
      {
        id: 3,
        label: "3. Khác biệt giữa Tool Schema của Claude (Anthropic) và OpenAI?",
        explanation: "Claude dùng trường `input_schema`, còn OpenAI dùng cấu trúc `parameters`. Cả hai đều tuân thủ chuẩn JSON Schema bản Draft-07.",
        example: "🔄 **Chuyển đổi:** Khi đổi SDK, chỉ cần đổi tên key `input_schema` thành `parameters`."
      }
    ]
  },

  "self-healing": {
    matchedKeyword: "Self-healing",
    directAnswer: "Self-healing (Tự sửa lỗi) là cơ chế bắt exception khi thực thi tool, đóng gói thông báo lỗi thành chuỗi Observation gửi lại cho LLM để nó tự phân tích và thử lại tham số khác mà không làm crash chương trình.",
    extraExample: "📌 **Ví dụ:** Tool báo lỗi 'KeyError: price' ➔ Observation: 'Lỗi: trường price không tồn tại' ➔ LLM tự đổi sang query trường 'cost'.",
    socraticQuestion: "Bạn đang tìm hiểu về cơ chế Self-healing loop. Điểm nào bạn muốn làm rõ?",
    chips: [
      {
        id: 1,
        label: "1. Cách bọc try...except để không làm dừng vòng lặp Agent?",
        explanation: "Trong hàm `execute_tool`, bọc toàn bộ code thực thi trong `try...except Exception as e: return f'Lỗi thực thi công cụ: {str(e)}'` thay vì để raise exception.",
        example: "💻 **Code:** Luôn trả về kiểu string để đưa vào message `tool_result`."
      },
      {
        id: 2,
        label: "2. Làm sao để LLM hiểu lỗi và không lặp lại tham số sai?",
        explanation: "Thông báo lỗi cần có tính hướng dẫn, ví dụ: 'Lỗi: ngày tháng phải theo định dạng YYYY-MM-DD'. Khi đó LLM sẽ tự đọc và format lại đúng chuẩn ở turn sau.",
        example: "💡 **Mẹo:** Trả về lỗi kèm format mong đợi."
      },
      {
        id: 3,
        label: "3. Giới hạn số lần retry tự sửa lỗi để tránh tốn token?",
        explanation: "Nên đếm số lần lỗi liên tiếp (consecutive_errors). Nếu vượt quá 3 lần, chuyển sang yêu cầu người dùng làm rõ hoặc dừng lượt suy luận.",
        example: "🛑 **Code:** `if error_count >= 3: return 'Không thể thực thi sau 3 lần thử.'`."
      }
    ]
  },

  "max_iterations": {
    matchedKeyword: "max_iterations",
    directAnswer: "Tham số `max_iterations` là cơ chế bảo vệ (circuit breaker) đặt giới hạn số lượt suy luận tối đa cho vòng lặp ReAct Loop (mặc định = 5 trong bài Lab) nhằm chống kẹt vòng lặp vô tận và cháy hạn ngạch API.",
    extraExample: "📌 **Code thực tế:** `while iteration < max_iterations: iteration += 1`.",
    socraticQuestion: "Về tham số max_iterations và điều kiện dừng, bạn đang thắc mắc điều gì?",
    chips: [
      {
        id: 1,
        label: "1. Tại sao bài Lab quy định trần max_iterations = 5?",
        explanation: "Các tác vụ trong bài Lab 3 chỉ cần từ 2 đến 4 bước (Thought -> Action -> Observation -> Final). Ngưỡng 5 là vừa đủ để Agent giải quyết bài toán và tự sửa sai 1 lần nếu cần.",
        example: "📊 **Thống kê:** 95% test cases hoàn thành trong 3 bước."
      },
      {
        id: 2,
        label: "2. Xử lý kịch bản khi chạm trần 5 bước mà chưa có kết quả?",
        explanation: "Khi vòng lặp kết thúc mà chưa nhận được `end_turn`, Agent nên trả về thông báo lịch sự: 'Đã đạt giới hạn 5 bước suy luận mà chưa có đáp án cuối cùng. Vui lòng thu hẹp câu hỏi.'",
        example: "💬 **Thông báo:** Giúp người dùng biết Agent đã dừng chứ không phải bị treo."
      },
      {
        id: 3,
        label: "3. Đo lường chi phí token khi tăng max_iterations lên cao?",
        explanation: "Mỗi turn hội thoại phải gửi lại toàn bộ lịch sử trước đó. Nếu max_iterations tăng lên 10, số lượng token đầu vào sẽ tăng theo cấp số nhân (quadratic growth).",
        example: "💰 **Tiết kiệm:** Giữ max_iterations nhỏ giúp tiết kiệm tới 60% chi phí gọi API."
      }
    ]
  },

  "ratelimit": {
    matchedKeyword: "RateLimitError",
    directAnswer: "Lỗi RateLimitError (HTTP 429) xảy ra khi số lượng requests hoặc tokens gọi lên API Anthropic vượt quá hạn ngạch cho phép theo phút (TPM / RPM) của gói tài khoản.",
    extraExample: "📌 **Mã lỗi:** `anthropic.RateLimitError: Error code: 429 - Number of request tokens has exceeded rate limit.`",
    socraticQuestion: "Bạn đang gặp mã lỗi RateLimitError 429. Bạn muốn khắc phục theo cách nào?",
    chips: [
      {
        id: 1,
        label: "1. Kỹ thuật Exponential Backoff (chờ lũy tiến và thử lại)?",
        explanation: "Bọc hàm gọi API với decorator retry hoặc vòng lặp while: nếu gặp lỗi 429, cho chương trình sleep tăng dần: 2s, 4s, 8s rồi tự động gọi lại.",
        example: "💻 **Code:** `time.sleep(2 ** attempt)`."
      },
      {
        id: 2,
        label: "2. Rút gọn context message trước khi gửi để giảm token?",
        explanation: "Chỉ giữ lại 3 turns gần nhất của Observation thay vì gửi toàn bộ dữ liệu thô (ví dụ: cắt bớt kết quả JSON quá dài từ tool).",
        example: "✂️ **Mẹo:** Cắt ngắn Observation text còn tối đa 500 ký tự."
      },
      {
        id: 3,
        label: "3. Kiểm tra hạn mức Tier tài khoản trên Anthropic Console?",
        explanation: "Truy cập console.anthropic.com -> Plans & Billing để kiểm tra Tier tài khoản của bạn (Tier 1: 50 RPM, Tier 2: 1000 RPM) và nạp thêm credit nếu cần.",
        example: "🔑 **Dashboard:** Kiểm tra biểu đồ Usage thời gian thực."
      }
    ]
  },

  "anthropic_api_key": {
    matchedKeyword: "ANTHROPIC_API_KEY",
    directAnswer: "ANTHROPIC_API_KEY là khóa bí mật xác thực tài khoản gọi Claude API. Theo nguyên tắc an toàn thông tin (HAX G2), tuyệt đối không commit key lên GitHub mà phải nạp qua biến môi trường hoặc Colab Secrets.",
    extraExample: "📌 **Cú pháp đọc:** `api_key = os.environ.get('ANTHROPIC_API_KEY')`.",
    socraticQuestion: "Bạn cần hỗ trợ cấu hình ANTHROPIC_API_KEY ở môi trường nào?",
    chips: [
      {
        id: 1,
        label: "1. Cấu hình bảo mật trên Google Colab Secrets (hình ổ khóa)?",
        explanation: "Ở thanh công cụ bên trái Google Colab, bấm vào icon hình Ổ khóa (Secrets) -> Add new secret với tên `ANTHROPIC_API_KEY`, dán key vào và bật quyền Notebook access.",
        example: "🔒 **Code Colab:** `from google.colab import userdata; key = userdata.get('ANTHROPIC_API_KEY')`."
      },
      {
        id: 2,
        label: "2. Cấu hình file .env trên máy cục bộ (VS Code / Terminal)?",
        explanation: "Tạo file `.env` cùng cấp với thư mục dự án: `ANTHROPIC_API_KEY=sk-ant-...`, sau đó thêm dòng `.env` vào file `.gitignore` để Git tự động bỏ qua.",
        example: "📄 **Thư viện:** Dùng `python-dotenv` với lệnh `load_dotenv()`."
      },
      {
        id: 3,
        label: "3. Làm gì khi lỡ commit API key lên GitHub công khai?",
        explanation: "Lập tức truy cập Anthropic Console để Revoke (hủy) key cũ và tạo key mới. Sau đó xóa commit bằng `git reset` hoặc công cụ BFG Repo-Cleaner.",
        example: "🚨 **Khẩn cấp:** Thu hồi key ngay trong vòng 5 phút để tránh bị bot quét cạn tiền."
      }
    ]
  },

  "trace_waterfall.json": {
    matchedKeyword: "trace_waterfall.json",
    directAnswer: "File `docs/trace_waterfall.json` là sản phẩm nộp bắt buộc của bài Lab 3, chứa nhật ký toàn bộ các bước suy luận Thought, Action, Observation kèm độ trễ tính bằng mili-giây để phục vụ chấm điểm tự động.",
    extraExample: "📌 **Mẫu log:** `[{ 'turn_id': 1, 'timeline': [{'phase': 'Thought', 'latency_ms': 340}], 'total_latency_ms': 634, 'status': 'PASS' }]`.",
    socraticQuestion: "Về file deliverable docs/trace_waterfall.json, bạn đang băn khoăn ở phần nào?",
    chips: [
      {
        id: 1,
        label: "1. Cấu trúc các trường bắt buộc để bot chấm điểm nhận diện?",
        explanation: "Mỗi phần tử trong JSON phải có: `turn_id` (số thứ tự), `user_query` (câu hỏi test), `timeline` (danh sách các phase), `total_latency_ms` và `status: 'PASS'`.",
        example: "📄 **Kiểm tra:** Đúng tên file tại đường dẫn `docs/trace_waterfall.json`."
      },
      {
        id: 2,
        label: "2. Cách dùng time.perf_counter() để ghi độ trễ chính xác?",
        explanation: "Bắt đầu đo: `t0 = time.perf_counter()`. Sau khi API hoặc hàm tool trả về: `latency = round((time.perf_counter() - t0) * 1000)`. Ghi giá trị này vào timeline phase.",
        example: "⏱️ **Độ chính xác:** Tính chính xác tới từng mili-giây (ms)."
      },
      {
        id: 3,
        label: "3. Tiêu chí đánh giá tính trung thực của file trace khi chấm bài?",
        explanation: "Script chấm bài sẽ kiểm tra timestamp có khớp với thời gian làm bài thực tế hay không và đối chiếu token usage với log API thật để loại bỏ các trường hợp fake log.",
        example: "💯 **Rubric:** Đạt trọn vẹn 3.0 điểm tiêu chí Trace Log."
      }
    ]
  }
};

// 2. STATE MANAGEMENT & BADGES
let userNotes = JSON.parse(localStorage.getItem('vlearn_user_notes') || '[]');
let currentSelectedSnippet = "";
let currentRange = null;

// DOM Elements
const lecturePane = document.getElementById('lecture-pane');
const selectionTooltip = document.getElementById('selection-tooltip');
const floatingCaret = document.getElementById('floating-caret');
const btnActionExplain = document.getElementById('btn-action-explain');
const btnActionSocratic = document.getElementById('btn-action-socratic');
const btnActionExample = document.getElementById('btn-action-example');

const stateBadge = document.getElementById('state-badge');
const contextBar = document.getElementById('context-bar');
const contextText = document.getElementById('context-text');
const btnClearContext = document.getElementById('btn-clear-context');

const chatMessagesEl = document.getElementById('chat-messages');
const manualChatInput = document.getElementById('manual-chat-input');
const btnSendManual = document.getElementById('btn-send-manual');
const btnNewChat = document.getElementById('btn-new-chat');

const btnShowFlow = document.getElementById('btn-show-flow');
const flowModal = document.getElementById('flow-modal');
const btnCloseModal = document.getElementById('btn-close-modal');

const noteModal = document.getElementById('note-modal');
const noteQuotePreview = document.getElementById('note-quote-preview');
const noteTextInput = document.getElementById('note-text-input');
const btnSaveNote = document.getElementById('btn-save-note');
const btnCancelNote = document.getElementById('btn-cancel-note');
const btnCloseNoteModal = document.getElementById('btn-close-note-modal');

const btnToggleNotes = document.getElementById('btn-toggle-notes');
const notesDrawer = document.getElementById('notes-drawer');
const btnCloseDrawer = document.getElementById('btn-close-drawer');
const notesBadge = document.getElementById('notes-badge');
const drawerNotesCount = document.getElementById('drawer-notes-count');
const notesListContainer = document.getElementById('notes-list-container');

const quickTabs = document.querySelectorAll('.q-tab');

// State Badge Controller (😴 Sẵn sàng / ⚙️ Đang phân tích / 🔍 Socratic / ✅ Đã trả lời)
function updateStateBadge(state) {
  if (!stateBadge) return;
  stateBadge.className = 'state-pill';
  if (state === 'ready') {
    stateBadge.classList.add('state-ready');
    stateBadge.textContent = '😴 Sẵn sàng';
  } else if (state === 'analyzing') {
    stateBadge.classList.add('state-analyzing');
    stateBadge.textContent = '⚙️ Đang phân tích…';
  } else if (state === 'socratic') {
    stateBadge.classList.add('state-socratic');
    stateBadge.textContent = '🔍 Socratic';
  } else if (state === 'answered') {
    stateBadge.classList.add('state-answered');
    stateBadge.textContent = '✅ Đã trả lời';
  }
}

// Context Bar Controller
function showContextBar(text) {
  if (!contextBar || !contextText) return;
  const truncated = text.length > 55 ? text.substring(0, 52) + '...' : text;
  contextText.textContent = `“${truncated}”`;
  contextBar.style.display = 'flex';
}

function hideContextBar() {
  if (contextBar) contextBar.style.display = 'none';
}

if (btnClearContext) {
  btnClearContext.addEventListener('click', () => {
    hideContextBar();
    currentSelectedSnippet = "";
  });
}

// Initialize state
updateStateBadge('ready');
updateNotesCount();

// Sidebar Navigation Smooth Scroll
document.querySelectorAll('[data-scroll]').forEach(el => {
  el.addEventListener('click', (e) => {
    e.preventDefault();
    const selector = el.getAttribute('data-scroll');
    const targetSection = document.querySelector(selector);
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.querySelectorAll('.lesson-list .lesson-item').forEach(item => item.classList.remove('active-lesson'));
      if (el.classList.contains('lesson-item')) {
        el.classList.add('active-lesson');
      }
    }
  });
});

// =========================================================
// BƯỚC 2 — BÔI ĐEN ĐOẠN KHÔNG HIỂU & FLOATING TOOLBAR
// =========================================================
lecturePane.addEventListener('mouseup', handleTextSelection);

// Hỗ trợ click vào các keyword có sẵn trên bài giảng để test nhanh
document.querySelectorAll('.demo-target').forEach(el => {
  el.addEventListener('click', (e) => {
    e.stopPropagation();
    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    handleTextSelection();
  });
});

function handleTextSelection() {
  setTimeout(() => {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0) {
      currentSelectedSnippet = text;
      try {
        currentRange = selection.getRangeAt(0).cloneRange();
      } catch (err) {
        currentRange = null;
      }

      const rect = selection.getRangeAt(0).getBoundingClientRect();
      const paneRect = lecturePane.getBoundingClientRect();

      // Vị trí caret và toolbar (phía trên hoặc phía dưới tùy vị trí màn hình)
      let leftOffset = rect.left - paneRect.left + (rect.width / 2);
      const showAbove = (rect.top - paneRect.top) > 80;
      let topOffset;

      if (showAbove) {
        topOffset = rect.top - paneRect.top + lecturePane.scrollTop - 10;
        selectionTooltip.style.transform = 'translate(-50%, -100%)';
        if (floatingCaret) {
          floatingCaret.style.top = 'auto';
          floatingCaret.style.bottom = '-6px';
          floatingCaret.style.borderTop = 'none';
          floatingCaret.style.borderLeft = 'none';
          floatingCaret.style.borderRight = '1px solid var(--border-subtle)';
          floatingCaret.style.borderBottom = '1px solid var(--border-subtle)';
        }
      } else {
        topOffset = rect.bottom - paneRect.top + lecturePane.scrollTop + 10;
        selectionTooltip.style.transform = 'translate(-50%, 0)';
        if (floatingCaret) {
          floatingCaret.style.bottom = 'auto';
          floatingCaret.style.top = '-6px';
          floatingCaret.style.borderRight = 'none';
          floatingCaret.style.borderBottom = 'none';
          floatingCaret.style.borderTop = '1px solid var(--border-subtle)';
          floatingCaret.style.borderLeft = '1px solid var(--border-subtle)';
        }
      }

      // Giới hạn trong khung đọc
      leftOffset = Math.max(160, Math.min(leftOffset, paneRect.width - 160));
      selectionTooltip.style.top = `${topOffset}px`;
      selectionTooltip.style.left = `${leftOffset}px`;
      selectionTooltip.style.display = 'block';
    } else {
      hideSelectionTooltip();
    }
  }, 10);
}

function hideSelectionTooltip() {
  if (selectionTooltip) selectionTooltip.style.display = 'none';
}

document.addEventListener('mousedown', (e) => {
  if (!selectionTooltip.contains(e.target) && !lecturePane.contains(e.target)) {
    hideSelectionTooltip();
  }
});

// Event listeners cho 3 nút action trên Floating Toolbar
if (btnActionExplain) {
  btnActionExplain.addEventListener('click', () => {
    const text = currentSelectedSnippet;
    hideSelectionTooltip();
    showContextBar(text);
    triggerDirectFlow(text, false);
  });
}

if (btnActionSocratic) {
  btnActionSocratic.addEventListener('click', () => {
    const text = currentSelectedSnippet;
    hideSelectionTooltip();
    showContextBar(text);
    triggerSocraticFlow(text);
  });
}

if (btnActionExample) {
  btnActionExample.addEventListener('click', () => {
    const text = currentSelectedSnippet;
    hideSelectionTooltip();
    showContextBar(text);
    triggerDirectFlow(text, true);
  });
}

// =========================================================
// BƯỚC 3A — CHỌN 💡 GIẢI THÍCH HOẶC 📌 VÍ DỤ (TRẢ LỜI NGAY)
// =========================================================
function triggerDirectFlow(snippet, isExample = false) {
  removeEmptyState();

  const intentTag = isExample ? '📌 Ví dụ' : '💡 Trả lời ngay';
  const intentClass = 'intent-direct';
  const userText = isExample ? 'Cho mình xem ví dụ cụ thể về đoạn này' : 'Giải thích trực tiếp giúp mình đoạn này';

  appendUserBubbleWithContext(snippet, intentTag, intentClass, userText);
  updateStateBadge('analyzing');

  const waitingRow = appendWaitingIndicator();

  setTimeout(() => {
    waitingRow.remove();
    const data = resolveKnowledge(snippet);

    if (data.isOutOfScope) {
      appendRejectionMessage(data);
      updateStateBadge('answered');
      return;
    }

    appendDirectCard(data, snippet, isExample);
    updateStateBadge('answered');
  }, 900);
}

function appendDirectCard(data, snippet, isExample) {
  const row = document.createElement('div');
  row.className = 'msg-row';
  const cardId = 'direct-' + Date.now();

  const contentText = isExample ? data.extraExample : data.directAnswer;

  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble">
      <div class="direct-card" id="${cardId}">
        <div class="direct-header">💡 Câu trả lời trực tiếp</div>
        <div class="direct-content">${contentText}</div>
        <div class="direct-actions">
          <button class="btn-direct-check">✓ Đã hiểu</button>
          <button class="btn-direct-example">📌 Thêm ví dụ</button>
          <button class="btn-save-to-note" style="margin-left: auto;">📌 Lưu vào Ghi chú</button>
        </div>
      </div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();

  const cardEl = document.getElementById(cardId);
  const btnCheck = cardEl.querySelector('.btn-direct-check');
  const btnMoreExample = cardEl.querySelector('.btn-direct-example');
  const btnSave = cardEl.querySelector('.btn-save-to-note');

  // Nút tương tác: ✓ Đã hiểu -> ✓ Đã đánh dấu
  btnCheck.addEventListener('click', () => {
    btnCheck.classList.toggle('checked');
    if (btnCheck.classList.contains('checked')) {
      btnCheck.textContent = '✓ Đã đánh dấu';
    } else {
      btnCheck.textContent = '✓ Đã hiểu';
    }
  });

  // Nút tương tác: 📌 Thêm ví dụ -> gửi thêm ví dụ ngay trong chat
  btnMoreExample.addEventListener('click', () => {
    const extraExampleRow = document.createElement('div');
    extraExampleRow.className = 'msg-row';
    extraExampleRow.innerHTML = `
      <div class="msg-avatar">✨</div>
      <div class="msg-bubble bot-bubble">
        <div style="font-size: 11.5px; font-weight: 700; color: #0284c7; margin-bottom: 4px;">📌 Ví dụ bổ sung về ${escapeHtml(data.matchedKeyword || 'khái niệm')}</div>
        <div style="font-size: 13px; line-height: 1.6;">${data.extraExample}</div>
      </div>
    `;
    chatMessagesEl.appendChild(extraExampleRow);
    scrollToBottom();
  });

  btnSave.addEventListener('click', () => {
    saveAIExplanationToNote(snippet, contentText);
  });
}

// =========================================================
// BƯỚC 3B — CHỌN 🔍 GỢI MỞ (SOCRATIC LOOP)
// =========================================================
function triggerSocraticFlow(snippet) {
  removeEmptyState();

  appendUserBubbleWithContext(snippet, '🔍 Socratic', 'intent-socratic', 'Gợi mở tư duy giúp mình đoạn này');
  updateStateBadge('analyzing');

  const waitingRow = appendWaitingIndicator();

  setTimeout(() => {
    waitingRow.remove();
    const data = resolveKnowledge(snippet);

    if (data.isOutOfScope) {
      appendRejectionMessage(data);
      updateStateBadge('answered');
      return;
    }

    appendSocraticCard(data, snippet);
    updateStateBadge('socratic');
  }, 900);
}

function appendSocraticCard(data, snippet) {
  const row = document.createElement('div');
  row.className = 'msg-row';
  const cardId = 'socratic-' + Date.now();

  const chips = data.chips || [];

  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble">
      <div class="socratic-card-v2" id="${cardId}">
        <div class="socratic-v2-header">🔍 Gợi mở Socratic</div>
        <div class="socratic-v2-question">
          <span>🎯</span>
          <span>${escapeHtml(data.socraticQuestion)}</span>
        </div>
        <div class="chips-container">
          ${chips.map((chip, idx) => `
            <button class="chip-btn" data-idx="${idx}">
              <span class="chip-num">${chip.id}</span>
              <span>${escapeHtml(chip.label)}</span>
            </button>
          `).join('')}
        </div>
      </div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();

  const cardEl = document.getElementById(cardId);
  const chipButtons = cardEl.querySelectorAll('.chip-btn');

  // =========================================================
  // BƯỚC 4 — CLICK CHIP LỰA CHỌN (CHỐT HẠ KIẾN THỨC)
  // =========================================================
  chipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.getAttribute('data-idx'), 10);
      const selectedChip = chips[idx];

      // Giao diện phản hồi: Chip được chọn chuyển tím highlight, 2 chip còn lại mờ đi và bị disable
      chipButtons.forEach(otherBtn => {
        if (otherBtn === btn) {
          otherBtn.classList.add('active-chip');
        } else {
          otherBtn.classList.add('disabled-chip');
        }
        otherBtn.disabled = true;
      });

      // Khung chat: User bubble hiển thị nội dung chip vừa chọn
      appendSimpleUserBubble(selectedChip.label);

      // Hiển thị thông báo: "Đang phân tích ngữ cảnh…"
      updateStateBadge('analyzing');
      const waitingRow = appendWaitingIndicator();

      // Phản hồi từ AI (~800 ms sau)
      setTimeout(() => {
        waitingRow.remove();
        appendResolveCard(selectedChip, snippet);
        updateStateBadge('answered');
      }, 800);
    });
  });
}

function appendResolveCard(selectedChip, snippet) {
  const row = document.createElement('div');
  row.className = 'msg-row';
  const resolveId = 'resolve-' + Date.now();

  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble">
      <div class="resolve-card-v2" id="${resolveId}">
        <div class="resolve-header">🎯 Giải thích đúng trọng tâm</div>
        <div class="resolve-content">${selectedChip.explanation}</div>
        <div class="resolve-example-box">${selectedChip.example}</div>
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 8px;">
          <button class="btn-resolve-done">✓ Hiểu rồi, tiếp tục đọc</button>
          <button class="btn-save-to-note">📌 Lưu vào Ghi chú</button>
        </div>
      </div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();

  const cardEl = document.getElementById(resolveId);
  const btnDone = cardEl.querySelector('.btn-resolve-done');
  const btnSave = cardEl.querySelector('.btn-save-to-note');

  // Nút tương tác: ✓ Hiểu rồi, tiếp tục đọc — bấm vào sẽ reset state badge về trạng thái 😴 Sẵn sàng
  btnDone.addEventListener('click', () => {
    btnDone.disabled = true;
    btnDone.textContent = '✓ Đã ghi nhận, tiếp tục đọc';
    btnDone.style.opacity = '0.7';
    updateStateBadge('ready');
  });

  btnSave.addEventListener('click', () => {
    saveAIExplanationToNote(snippet, selectedChip.explanation + "\n\n" + selectedChip.example);
  });
}

// =========================================================
// BONUS — XỬ LÝ KHI GÕ CÂU HỎI TỰ DO (INPUT PHÍA DƯỚI)
// =========================================================
btnSendManual.addEventListener('click', handleManualInput);
manualChatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleManualInput();
});

function handleManualInput() {
  const text = manualChatInput.value.trim();
  if (!text) return;
  manualChatInput.value = '';

  removeEmptyState();
  appendSimpleUserBubble(text);

  updateStateBadge('analyzing');
  const waitingRow = appendWaitingIndicator();

  setTimeout(() => {
    waitingRow.remove();
    appendManualGuidanceCard(text);
    updateStateBadge('ready');
  }, 600);
}

function appendManualGuidanceCard(userQuery) {
  const row = document.createElement('div');
  row.className = 'msg-row';
  const guideId = 'guide-' + Date.now();

  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble">
      <div class="guidance-card" id="${guideId}">
        <div class="guidance-header">💡 Gợi ý học tập thông minh</div>
        <div class="guidance-content">
          Bạn vừa đặt câu hỏi thô: <em>"${escapeHtml(userQuery)}"</em> mà chưa gắn với ngữ cảnh cụ thể.<br>
          Để Trợ giảng AI hiểu rõ bạn đang gặp khó khăn ở vị trí nào trong bài giảng và tránh trả lời lý thuyết chung chung:
          <ul style="margin: 6px 0 6px 18px; line-height: 1.6;">
            <li><strong>Cách tối ưu:</strong> Hãy dùng chuột <strong>bôi đen trực tiếp đoạn lý thuyết hoặc dòng code</strong> ở bài giảng bên trái.</li>
            <li>Hoặc bạn có thể bấm nút dưới đây để kích hoạt luồng <strong>Gợi mở Socratic</strong> về bài Lab Day 03:</li>
          </ul>
        </div>
        <button class="btn-suggest-socratic">🔍 Kích hoạt Gợi mở Socratic về bài Lab</button>
      </div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();

  const cardEl = document.getElementById(guideId);
  const btnSuggest = cardEl.querySelector('.btn-suggest-socratic');
  btnSuggest.addEventListener('click', () => {
    btnSuggest.disabled = true;
    showContextBar("ReAct Agent (Khung lý thuyết Day 03)");
    triggerSocraticFlow("ReAct Agent");
  });
}

// =========================================================
// HELPER FUNCTIONS CHO CHAT & BUBBLES
// =========================================================
function removeEmptyState() {
  const emptyState = document.getElementById('ai-empty-state');
  if (emptyState) emptyState.remove();
}

function appendUserBubbleWithContext(snippet, intentTag, intentClass, mainText) {
  const row = document.createElement('div');
  row.className = 'msg-row user-row';
  const truncSnippet = snippet.length > 50 ? snippet.substring(0, 48) + '...' : snippet;

  row.innerHTML = `
    <div class="msg-avatar user-avatar user-avatar-msg">VĨ</div>
    <div class="msg-bubble user-bubble">
      <div class="user-context-pill">
        <span>📌 “${escapeHtml(truncSnippet)}”</span>
        <span class="user-intent-tag ${intentClass}">${intentTag}</span>
      </div>
      <div>${escapeHtml(mainText)}</div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();
}

function appendSimpleUserBubble(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user-row';
  row.innerHTML = `
    <div class="msg-avatar user-avatar user-avatar-msg">VĨ</div>
    <div class="msg-bubble user-bubble">
      <div>${escapeHtml(text)}</div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();
}

function appendWaitingIndicator() {
  const row = document.createElement('div');
  row.className = 'msg-row';
  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble">
      <div class="analyzing-container">
        <span>Đang phân tích ngữ cảnh…</span>
        <span class="typing-dots">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </span>
      </div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();
  return row;
}

function appendRejectionMessage(data) {
  const row = document.createElement('div');
  row.className = 'msg-row';
  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble bot-bubble" style="border-left: 3px solid #ef4444;">
      <div style="font-size: 11px; font-weight: 700; color: #ef4444; margin-bottom: 4px;">🔴 HAX G1: Ngoài thẩm quyền / Giới hạn phạm vi</div>
      <p><strong>${escapeHtml(data.rejectionReason)}</strong></p>
      <p style="margin-top: 6px; font-size: 13px; line-height: 1.55;">${escapeHtml(data.explanation)}</p>
      <div style="margin-top: 8px; font-size: 11.5px; color: #64748b;">🛡️ <strong>Nguyên tắc:</strong> ${escapeHtml(data.citation)}</div>
    </div>
  `;
  chatMessagesEl.appendChild(row);
  scrollToBottom();
}

function resolveKnowledge(snippet) {
  const normalized = (snippet || "").toLowerCase();
  for (const key in MOCK_KNOWLEDGE_BASE) {
    if (normalized.includes(key)) {
      return MOCK_KNOWLEDGE_BASE[key];
    }
  }

  // Fallback linh hoạt cho đoạn bôi đen bất kỳ
  const trunc = snippet.length > 35 ? snippet.substring(0, 32) + '...' : snippet;
  return {
    matchedKeyword: trunc,
    directAnswer: `Đoạn "${trunc}" là một thành phần trọng tâm trong bài giảng Day 03, phục vụ việc xây dựng và hoàn thiện vòng lặp ReAct Agent.`,
    extraExample: `📌 **Ví dụ ứng dụng:** Khi triển khai trong code Python, "${trunc}" được gọi tuần tự cùng với các công cụ trong pipeline.`,
    socraticQuestion: `Bạn đang muốn làm rõ khía cạnh nào của đoạn: "${trunc}"?`,
    chips: [
      {
        id: 1,
        label: "1. Nguyên lý hoạt động và bản chất lý thuyết?",
        explanation: `Về mặt lý thuyết, "${trunc}" định hình cách thức các mô hình ngôn ngữ lớn tương tác với môi trường bên ngoài.`,
        example: "📖 Xem thêm chi tiết trong Slide bài giảng Day 03."
      },
      {
        id: 2,
        label: "2. Cách triển khai thực tế trên mã nguồn bài Lab?",
        explanation: `Khi lập trình trong bài Lab, nội dung "${trunc}" tương ứng với các cấu hình tham số trong file src/react_agent.py.`,
        example: "💻 Kiểm tra cú pháp tại file Starter Repo của lớp."
      },
      {
        id: 3,
        label: "3. Các lỗi runtime thường gặp và cách kiểm tra?",
        explanation: `Các sự cố thường xoay quanh việc sai lệch schema JSON hoặc timeout đường truyền ngoại vi.`,
        example: "🔍 Đối soát vết lỗi tại file docs/trace_waterfall.json."
      }
    ]
  };
}

// Reset Chat về trạng thái khởi đầu
if (btnNewChat) {
  btnNewChat.addEventListener('click', () => {
    hideContextBar();
    updateStateBadge('ready');
    chatMessagesEl.innerHTML = `
      <div class="ai-empty-state" id="ai-empty-state">
        <h2 class="empty-greeting">Tối nay học gì đây VĨ?</h2>
        <p class="empty-sub">Đang mở: 📋 THÔNG TIN BRIEF & BỐI CẢNH LÝ THUYẾT</p>
        <div class="guide-steps-card">
          <div class="guide-title">🚀 Hướng dẫn 4 bước học tập thông minh:</div>
          <div class="step-item">
            <span class="step-badge">1</span>
            <div><strong>Đọc bài giảng:</strong> Theo dõi tài liệu và code bài Lab bên trái.</div>
          </div>
          <div class="step-item">
            <span class="step-badge">2</span>
            <div><strong>Bôi đen chỗ khó:</strong> Dùng chuột bôi đen đoạn khái niệm/mã lỗi.</div>
          </div>
          <div class="step-item">
            <span class="step-badge">3</span>
            <div><strong>Chọn công cụ:</strong> Bấm <strong>💡 Giải thích</strong> để nhận câu trả lời thẳng, hoặc <strong>🔍 Gợi mở</strong> để vào luồng Socratic.</div>
          </div>
          <div class="step-item">
            <span class="step-badge">4</span>
            <div><strong>Click chip lựa chọn:</strong> Chọn 1 trong 3 chip gợi ý để AI giải thích trúng đích điểm kẹt!</div>
          </div>
        </div>
      </div>
    `;
  });
}

// =========================================================
// QUICK DEMO TABS (Cho Ban Giám Khảo & Rubric R3)
// =========================================================
quickTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    quickTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const flow = tab.getAttribute('data-flow');
    if (flow === 'happy') {
      showContextBar("ReAct Agent");
      triggerSocraticFlow("ReAct Agent");
    } else if (flow === 'direct') {
      showContextBar("ReAct Agent");
      triggerDirectFlow("ReAct Agent", false);
    } else if (flow === 'code') {
      showContextBar("call_anthropic");
      triggerSocraticFlow("call_anthropic");
    } else if (flow === 'failure') {
      showContextBar("quét mã điểm danh");
      triggerDirectFlow("quét mã điểm danh", false);
    } else if (flow === 'bypass') {
      showContextBar("ReAct Agent");
      triggerDirectFlow("ReAct Agent", true);
    }
  });
});

// Flow Modal
if (btnShowFlow) {
  btnShowFlow.addEventListener('click', () => { flowModal.style.display = 'flex'; });
}
if (btnCloseModal) {
  btnCloseModal.addEventListener('click', () => { flowModal.style.display = 'none'; });
}
if (flowModal) {
  flowModal.addEventListener('click', (e) => { if (e.target === flowModal) flowModal.style.display = 'none'; });
}

// =========================================================
// NOTES & HIGHLIGHTS STORAGE
// =========================================================
window.saveAIExplanationToNote = function(quoteText, explanationText) {
  const noteItem = {
    id: Date.now(),
    type: 'ai_saved',
    quote: quoteText || 'Đoạn bài học đã chọn',
    comment: explanationText,
    timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
  };
  userNotes.unshift(noteItem);
  saveNotesToStorage();
  alert("✅ Đã lưu lời giải thích của AI vào Sổ Ghi Chú cá nhân của bạn!");
};

function saveNotesToStorage() {
  localStorage.setItem('vlearn_user_notes', JSON.stringify(userNotes));
  updateNotesCount();
  renderNotesDrawer();
}

function updateNotesCount() {
  const count = userNotes.length;
  if (notesBadge) notesBadge.textContent = count;
  if (drawerNotesCount) drawerNotesCount.textContent = count;
}

if (btnToggleNotes) {
  btnToggleNotes.addEventListener('click', () => {
    renderNotesDrawer();
    notesDrawer.style.display = 'flex';
  });
}
if (btnCloseDrawer) {
  btnCloseDrawer.addEventListener('click', () => { notesDrawer.style.display = 'none'; });
}

function renderNotesDrawer() {
  if (!notesListContainer) return;
  if (userNotes.length === 0) {
    notesListContainer.innerHTML = '<div class="empty-notes-hint">Chưa có ghi chú nào. Hãy bôi đen bài giảng để tô màu hoặc ghi chú nhé!</div>';
    return;
  }

  notesListContainer.innerHTML = userNotes.map(n => `
    <div class="note-card-item">
      <div class="note-card-header">
        <span>${n.type === 'highlight' ? '🟡 Highlight' : (n.type === 'ai_saved' ? '✨ Lời giải thích AI' : '📝 Ghi chú cá nhân')}</span>
        <span>${n.timestamp}</span>
      </div>
      <div class="note-card-text">${escapeHtml(n.comment)}</div>
      <div class="note-card-quote">“${escapeHtml(n.quote)}”</div>
    </div>
  `).join('');
}

// Note Modal
if (btnCancelNote) btnCancelNote.addEventListener('click', () => { noteModal.style.display = 'none'; });
if (btnCloseNoteModal) btnCloseNoteModal.addEventListener('click', () => { noteModal.style.display = 'none'; });

// =========================================================
// UTILITIES
// =========================================================
function scrollToBottom() {
  if (chatMessagesEl) {
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}
