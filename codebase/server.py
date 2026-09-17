#!/usr/bin/env python3
"""
=============================================================================
VLearn Socratic Tutor — Backend Server (Track A1)
Nhóm: Chungtoidongtinh · Phòng: E403 · Lớp: 3A
Đội trưởng: Trần Chí Vĩ (2A202602968)
-----------------------------------------------------------------------------
Kiến trúc 3-Layer Agent Router:
1. Layer 0: Intent Guardrails (URL, Logistics, Đòi giải bài hộ, Prompt Injection)
2. Layer 1: RAG-lite Mock KB (30+ concepts Day 01-03, fuzzy matching, 0ms, 0 tokens)
3. Layer 2: Live AI Socratic Engine (OpenRouter/Gemini 1.5 Flash API)
4. Layer 3: Multi-turn Socratic Probing (/api/socratic-followup — Vòng 2 đào sâu)
5. Trace Waterfall Logger (Rubric R5 & HAX G2: lưu latency, tokens, steps)
=============================================================================
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Cấu hình thư mục
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACE_LOG_PATH = os.path.join(BASE_DIR, "trace_waterfall.json")
PORT = int(os.environ.get("PORT", 8088))

# Tự động tải .env từ thư mục gốc nếu có
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")
if os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

# =============================================================================
# 1. RAG-LITE KNOWLEDGE BASE (30+ Concepts Day 01 - Day 03 Curriculum)
# =============================================================================
MOCK_KNOWLEDGE = {
    # --- DAY 03: AGENT & TOOL CALLING ---
    "react agent": {
        "keyword": "ReAct Agent",
        "direct_answer": "ReAct Agent (Reasoning + Acting) là mô hình AI kết hợp giữa suy luận và hành động. Thay vì chỉ sinh văn bản đóng băng, Agent tự lập luận (Thought), quyết định gọi công cụ ngoài (Action) và đọc kết quả trả về (Observation) để xử lý tác vụ đa bước phức tạp.",
        "extra_example": "📌 Ví dụ thực tế: Khi hỏi 'Thời tiết Hà Nội hôm nay và gợi ý trang phục', ReAct Agent sẽ gọi API OpenWeather lấy nhiệt độ 28°C rồi lập luận đưa ra gợi ý mặc áo thun thoáng mát.",
        "socratic_question": "Bạn đang bôi đen 'ReAct Agent'. Điểm nào dưới đây là phần bạn đang cảm thấy kẹt nhất?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cơ chế vòng lặp Thought -> Action -> Observation hoạt động ra sao?",
                "explanation": "ReAct Agent không sinh ngay câu trả lời cuối cùng mà lặp qua 3 nhịp: (1) Thought (LLM tự suy ngẫm bước cần làm); (2) Action (LLM phát lệnh gọi Tool); (3) Observation (Mô hình nhận kết quả trả về từ môi trường để tư duy tiếp hoặc xuất kết quả).",
                "example": "💡 Ví dụ trực quan: Giống như lập trình viên sửa bug: Đọc mã lỗi (Thought) ➔ Chạy test (Action) ➔ Đọc kết quả terminal (Observation) ➔ Fix code."
            },
            {
                "id": 2,
                "label": "2. Sự khác biệt cốt lõi giữa Chatbot (Cấp 2) và ReAct Agent (Cấp 3)?",
                "explanation": "Chatbot thông thường chỉ dựa vào tri thức đóng băng trong trọng số mô hình và không thể tương tác thế giới thực. ReAct Agent được gắn 'tay chân' là các Tool (hàm API, database, calculator), cho phép truy vấn dữ liệu thời gian thực và tự sửa lỗi.",
                "example": "💡 Ví dụ so sánh: Hỏi Chatbot Cấp 2: 'Bitcoin giá bao nhiêu?' ➔ Trả lời dữ liệu cũ 2023. Hỏi ReAct Agent Cấp 3 ➔ Tự gọi get_crypto_price('BTC') trả về giá chính xác lúc này."
            },
            {
                "id": 3,
                "label": "3. Cách viết vòng lặp While và điều kiện ngắt trong Python?",
                "explanation": "Trong file src/react_agent.py, vòng lặp while iteration < max_iterations: sẽ chạy liên tục. Điều kiện dừng là khi phản hồi của LLM không còn yêu cầu gọi công cụ, hoặc khi đạt trần an toàn max_iterations = 5 để chống lặp vô tận.",
                "example": "💻 Code mẫu: if not response.tool_calls: return response.content ➔ ngắt vòng lặp và gửi câu trả lời cuối cùng."
            }
        ]
    },
    "native tool calling": {
        "keyword": "Native Tool Calling",
        "direct_answer": "Native Tool Calling là cơ chế được huấn luyện trực tiếp vào model. Khi cần dùng công cụ, model dừng sinh text và trả về đối tượng JSON chuẩn (tên hàm + arguments) thay vì phải dùng regex tách chuỗi tự do.",
        "extra_example": "📌 Ví dụ: Thay vì text 'Hãy gọi search_db với id=10', Claude/OpenAI trả về cấu trúc { name: 'search_db', arguments: { id: 10 } }.",
        "socratic_question": "Khi tìm hiểu Native Tool Calling, bạn muốn tháo gỡ điểm nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cú pháp khai báo JSON Schema cho tham số?",
                "explanation": "Tool Schema được định nghĩa theo chuẩn JSON Schema gồm 3 trường: name (tên hàm), description (hướng dẫn cho LLM hiểu khi nào dùng), và input_schema (kiểu dữ liệu các tham số bắt buộc).",
                "example": "💻 Mẫu khai báo: { 'name': 'calculator', 'description': 'Tính toán số học', 'input_schema': {...} }."
            },
            {
                "id": 2,
                "label": "2. Cơ chế model phát hiện khi nào cần gọi Tool hay trả lời thẳng?",
                "explanation": "LLM dựa vào description của từng tool trong prompt hệ thống. Nếu câu hỏi cần thông tin tool hỗ trợ, LLM trả về stop_reason: tool_use. Nếu là câu chào hỏi thông thường, nó trả lời bằng text bình thường.",
                "example": "💡 Ví dụ: Hỏi 'Chào bạn' ➔ Text thường. Hỏi '153 * 289' ➔ Kích hoạt tool calculator."
            },
            {
                "id": 3,
                "label": "3. Xử lý lỗi khi model sinh tham số JSON sai schema?",
                "explanation": "Khi parse arguments bị lỗi JSONDecodeError hoặc thiếu tham số bắt buộc, ta bắt exception trong code Python, đóng gói thông báo lỗi thành tool_result và gửi ngược lại cho LLM để nó tự sửa sai (Self-healing loop).",
                "example": "🔄 Kịch bản tự sửa: Gửi lại message { role: 'tool', content: 'Lỗi: tham số thiếu dấu đóng ngoặc' } để model tự sinh lại JSON hợp lệ."
            }
        ]
    },
    "waterfall trace log": {
        "keyword": "Waterfall Trace Log",
        "direct_answer": "Waterfall Trace Log là bản ghi vết thực thi trực quan ghi lại từng mắt xích hoạt động của Agent: thời điểm bắt đầu, thời lượng chạy từng nhịp suy luận, thời gian gọi tool thực tế và mức tiêu thụ token.",
        "extra_example": "📌 Ví dụ cấu trúc: Turn 1: Thought 320ms ➔ Tool execute 150ms ➔ Observation ➔ Final answer 210ms (Tổng độ trễ: 680ms).",
        "socratic_question": "Vết Waterfall Trace Log là yêu cầu bắt buộc của bài Lab. Bạn đang băn khoăn ở phần nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cấu trúc chuẩn file docs/trace_waterfall.json gồm những trường gì?",
                "explanation": "File log gồm mảng các lượt gọi (turns). Mỗi item cần có: timestamp, step (Thought / Action / Observation), tool_name, latency_ms và tokens_used.",
                "example": "📄 Mẫu JSON: [{ 'step': 'Action', 'tool': 'fetch_stock', 'latency_ms': 142, 'status': 'success' }]."
            },
            {
                "id": 2,
                "label": "2. Đo độ trễ (latency) từng bước trong Python bằng cách nào?",
                "explanation": "Sử dụng module time.perf_counter() trước và sau khi gọi API LLM hoặc thực thi hàm công cụ, sau đó lấy hiệu số nhân 1000 để ra mili-giây (ms).",
                "example": "💻 Code mẫu: t0 = time.perf_counter(); res = run_tool(); latency = (time.perf_counter() - t0) * 1000."
            },
            {
                "id": 3,
                "label": "3. Cách dùng file trace này để chấm điểm rubric bài Lab?",
                "explanation": "Giảng viên và bot chấm điểm sẽ đọc file trace_waterfall.json để xác minh Agent của bạn thực sự tương tác với Tool hay chỉ hardcode giả lập câu trả lời.",
                "example": "🎯 Tiêu chí chấm: File trace phải có timestamp khớp thời gian chạy test suite và có log gọi hàm thực tế."
            }
        ]
    },
    "tool schema": {
        "keyword": "Tool Schema",
        "direct_answer": "Tool Schema là bản đặc tả cấu trúc dữ liệu theo chuẩn JSON Schema mô tả tên hàm, mô tả chức năng và định dạng các tham số đầu vào để LLM sinh lời gọi hàm chuẩn xác.",
        "extra_example": "📌 Ví dụ: Định nghĩa kiểu dữ liệu 'number', 'string' và danh sách tham số 'required'.",
        "socratic_question": "Bạn muốn làm rõ khía cạnh nào khi khai báo Tool Schema?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cách viết description để LLM không gọi nhầm công cụ?",
                "explanation": "Description cần nêu rõ khi nào nên gọi tool và ví dụ cụ thể, tránh mô tả mơ hồ khiến model gọi lung tung.",
                "example": "💡 Viết chuẩn: 'Dùng khi cần tra cứu giá cổ phiếu thời gian thực theo mã ticker'."
            },
            {
                "id": 2,
                "label": "2. Khai báo tham số bắt buộc (required) vs tùy chọn (optional)?",
                "explanation": "Đặt tên trường trong mảng 'required': ['ticker'] để model bắt buộc phải truyền giá trị, nếu không model có thể bỏ sót.",
                "example": "💻 JSON: { 'type': 'object', 'properties': {...}, 'required': ['ticker'] }."
            },
            {
                "id": 3,
                "label": "3. Cấu trúc kiểu dữ liệu phức tạp: Array hoặc Object lồng nhau?",
                "explanation": "Dùng type: 'array' kèm trường 'items': {'type': 'string'} khi một tham số nhận danh sách nhiều giá trị.",
                "example": "💻 JSON: { 'type': 'array', 'items': { 'type': 'string' } }."
            }
        ]
    },
    "self-healing": {
        "keyword": "Self-healing",
        "direct_answer": "Self-healing Loop là cơ chế cho phép Agent tự phục hồi khi gặp lỗi runtime: thay vì crash chương trình, exception được bắt lại, chuyển thành chuỗi Observation gửi cho LLM tự sửa mã hoặc tham số.",
        "extra_example": "📌 Ví dụ: Model sinh thiếu dấu ngoặc JSON -> Try/Catch bắt lỗi -> Gửi thông báo 'Lỗi cú pháp' -> Model sinh lại JSON đúng.",
        "socratic_question": "Bạn đang vướng ở khâu nào của cơ chế Self-healing?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cấu trúc khối try/except bắt lỗi runtime trong Python?",
                "explanation": "Bọc lệnh thực thi tool trong try: res = func(**args) except Exception as e: res = f'Lỗi: {str(e)}' để biến lỗi thành text.",
                "example": "💻 Code: except Exception as err: return {'status': 'error', 'message': str(err)}."
            },
            {
                "id": 2,
                "label": "2. Định dạng error prompt gửi ngược lại cho LLM sửa sai?",
                "explanation": "Gửi tin nhắn có role là 'tool' chứa thông báo lỗi rõ ràng để model hiểu chính xác tham số nào đang bị sai.",
                "example": "🔄 Mẫu: { 'role': 'tool', 'content': 'Tham số date không đúng định dạng YYYY-MM-DD' }."
            },
            {
                "id": 3,
                "label": "3. Thiết lập trần max_retries để tránh vòng lặp sửa lỗi vô tận?",
                "explanation": "Cần đặt biến đếm retry_count. Nếu sau 3 lần sửa vẫn lỗi thì thoát vòng lặp và thông báo cho người dùng.",
                "example": "🛡️ Code: if retries >= 3: return 'Không thể hoàn thành tác vụ do lỗi liên tục'."
            }
        ]
    },
    "max_iterations": {
        "keyword": "max_iterations",
        "direct_answer": "max_iterations là ngưỡng chặn an toàn số vòng lặp tối đa của vòng lặp While trong Agent, ngăn ngừa tình huống LLM bị kẹt trong vòng lặp vô tận gây tốn token và treo hệ thống.",
        "extra_example": "📌 Ví dụ: Đặt max_iterations = 5. Nếu sau 5 bước mà Agent vẫn chưa đưa ra Final Answer thì chủ động dừng.",
        "socratic_question": "Khi thiết lập max_iterations, bạn đang băn khoăn điều gì?",
        "chips": [
            {
                "id": 1,
                "label": "1. Chọn giá trị max_iterations bao nhiêu là hợp lý?",
                "explanation": "Thông thường với bài Lab Agent, giá trị từ 3 đến 5 là tối ưu, đủ cho các bài toán tra cứu 2-3 công cụ liên tiếp.",
                "example": "💡 Khuyến nghị: max_iterations = 5 để cân bằng giữa hoàn thành bài tập và an toàn ngân sách."
            },
            {
                "id": 2,
                "label": "2. Xử lý thông báo trả về khi chạm ngưỡng dừng an toàn?",
                "explanation": "Khi iteration >= max_iterations, cần trả về thông báo giải thích Agent đã dùng hết lượt thử kèm kết quả quan sát gần nhất.",
                "example": "⚠️ Output: 'Đã đạt giới hạn 5 bước suy luận nhưng chưa thể kết luận dứt điểm'."
            },
            {
                "id": 3,
                "label": "3. Cơ chế kiểm tra điều kiện thoát sớm (early stop)?",
                "explanation": "Kiểm tra nếu response không còn yêu cầu gọi tool (len(tool_calls) == 0) thì ngắt vòng lặp ngay lập tức.",
                "example": "💻 Code: if not response.tool_calls: break."
            }
        ]
    },
    "call_anthropic": {
        "keyword": "call_anthropic",
        "direct_answer": "Hàm call_anthropic là hàm wrapper chuẩn trong bài Lab để gửi request đến Anthropic Claude API với các tham số cốt lõi như model, prompt, temperature và max_tokens.",
        "extra_example": "📌 Ví dụ: def call_anthropic(prompt: str, model: str = 'claude-3-5-sonnet', temperature: float = 0.0).",
        "socratic_question": "Bạn muốn làm rõ khía cạnh kỹ thuật nào của hàm call_anthropic?",
        "chips": [
            {
                "id": 1,
                "label": "1. Ý nghĩa của tham số temperature trong hàm?",
                "explanation": "Temperature = 0.0 giúp model phản hồi logic, nhất quán và gọi tool chuẩn xác nhất; giá trị cao hơn sẽ làm tăng tính ngẫu nhiên.",
                "example": "🎯 Với Agentic AI: Luôn đặt temperature = 0.0 để tránh model hallucinate cú pháp JSON."
            },
            {
                "id": 2,
                "label": "2. Cách quản lý API Key an toàn qua file .env?",
                "explanation": "Tuyệt đối không hardcode API key vào mã nguồn; đọc key qua os.environ.get('ANTHROPIC_API_KEY') và thêm .env vào .gitignore.",
                "example": "🔒 Code: api_key = os.environ.get('ANTHROPIC_API_KEY')."
            },
            {
                "id": 3,
                "label": "3. Bọc ngoại lệ bắt lỗi kết nối và RateLimitError?",
                "explanation": "Sử dụng try/except bọc lời gọi API để bắt các mã lỗi HTTP 429 hoặc timeout và kích hoạt cơ chế retry backoff.",
                "example": "⏳ Code: except anthropic.RateLimitError: time.sleep(2); retry()."
            }
        ]
    },
    "ratelimiterror": {
        "keyword": "RateLimitError",
        "direct_answer": "RateLimitError (HTTP 429) xảy ra khi số lượng request (RPM) hoặc số lượng token tiêu thụ (TPM) vượt quá hạn mức được nhà cung cấp API cho phép trong một đơn vị thời gian.",
        "extra_example": "📌 Ví dụ: Gửi 15 request liên tiếp trong 1 phút trên gói Free Tier dẫn đến lỗi HTTP 429 Too Many Requests.",
        "socratic_question": "Khi xử lý lỗi RateLimitError, giải pháp nào bạn muốn tìm hiểu?",
        "chips": [
            {
                "id": 1,
                "label": "1. Thuật toán Exponential Backoff kèm Jitter hoạt động ra sao?",
                "explanation": "Tăng gấp đôi thời gian chờ sau mỗi lần lỗi (1s -> 2s -> 4s) cộng thêm một khoảng ngẫu nhiên nhỏ để tránh xung đột request.",
                "example": "⏱️ Công thức: wait_time = base_delay * (2 ** retry) + random_jitter."
            },
            {
                "id": 2,
                "label": "2. Cơ chế Token Bucket để kiểm soát tốc độ gửi request?",
                "explanation": "Giới hạn số request tối đa trong mỗi giây bằng cách duy trì bộ đếm token cấp phép trước khi thực sự gọi API.",
                "example": "🚰 Khái niệm: Giống như vòi nước nhỏ giọt đều đặn vào xô, chỉ múc khi có nước."
            },
            {
                "id": 3,
                "label": "3. Chuyển đổi sang API Key dự phòng hoặc nhà cung cấp khác?",
                "explanation": "Khi gặp mã 429 liên tục, hệ thống tự động chuyển sang key thứ hai hoặc chuyển từ Claude sang OpenAI/Gemini.",
                "example": "🔄 Fallback: if err.status_code == 429: switch_to_backup_provider()."
            }
        ]
    },
    "temperature": {
        "keyword": "Temperature",
        "direct_answer": "Temperature là siêu tham số kiểm soát độ ngẫu nhiên của phân phối xác suất token. Giá trị thấp (0.0-0.2) cho câu trả lời nhất quán và logic; giá trị cao (0.7-1.0) tăng tính đa dạng và sáng tạo.",
        "extra_example": "📌 Ví dụ: Khi trích xuất JSON hoặc gọi Tool, dùng temperature = 0. Khi viết thơ hoặc brainstorm ý tưởng, dùng temperature = 0.8.",
        "socratic_question": "Bạn muốn làm rõ tác động của Temperature trong bài Lab nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Tại sao xây dựng ReAct Agent luôn để temperature = 0?",
                "explanation": "Agent cần gọi tool chính xác và phân tích dữ liệu khách quan. Temperature > 0 có thể làm sai lệch schema JSON hoặc tên tham số.",
                "example": "🎯 Kinh nghiệm: Luôn cố định temperature = 0 cho mọi tác vụ Agentic suy luận."
            },
            {
                "id": 2,
                "label": "2. Mối quan hệ giữa Temperature và Top-p (Nucleus Sampling)?",
                "explanation": "Temperature làm phẳng hoặc làm nhọn phân phối xác suất; trong khi Top-p cắt đuôi các token có xác suất cộng dồn thấp.",
                "example": "📊 Thông số chuẩn: Thông thường chỉ điều chỉnh một trong hai, giữ thông số còn lại ở mặc định."
            },
            {
                "id": 3,
                "label": "3. Nguy cơ ảo giác (Hallucination) khi tăng temperature?",
                "explanation": "Khi nhiệt độ cao, model sẵn sàng chọn các token có xác suất xuất hiện rất thấp, dễ dẫn đến việc bịa đặt thông tin không có thật.",
                "example": "⚠️ Cảnh báo: Temperature 1.0 có thể khiến bot bịa ra tên tham số tool không hề tồn tại."
            }
        ]
    },
    "cuda out of memory": {
        "keyword": "CUDA out of memory",
        "direct_answer": "CUDA Out of Memory (OOM) là lỗi xảy ra khi bộ nhớ VRAM của GPU không đủ để chứa trọng số mô hình (weights), trạng thái kích hoạt (activations) hoặc kích thước batch dữ liệu đầu vào.",
        "extra_example": "📌 Ví dụ: Tải mô hình Llama 7B (cần ~14GB VRAM) lên card RTX 3060 (12GB VRAM) dẫn đến RuntimeError: CUDA out of memory.",
        "socratic_question": "Bạn muốn tháo gỡ lỗi CUDA Out of Memory theo hướng nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Hạ batch_size và áp dụng Gradient Accumulation?",
                "explanation": "Giảm kích thước batch nhỏ lại (ví dụ từ 32 xuống 4) và cộng dồn gradient qua nhiều bước để tiết kiệm bộ nhớ VRAM tức thời.",
                "example": "📉 Code: batch_size = 4; accumulation_steps = 8 (tương đương batch 32)."
            },
            {
                "id": 2,
                "label": "2. Lượng tử hóa mô hình sang 4-bit hoặc 8-bit (QLoRA)?",
                "explanation": "Nén trọng số từ 16-bit float xuống 4-bit giúp giảm 60-70% dung lượng VRAM mà vẫn giữ nguyên độ chính xác tương đương.",
                "example": "💾 Thư viện: Dùng BitsAndBytesConfig(load_in_4bit=True) khi tải model."
            },
            {
                "id": 3,
                "label": "3. Giải phóng bộ nhớ đệm bằng torch.cuda.empty_cache()?",
                "explanation": "Xóa các tensor trung gian không còn sử dụng trong bộ nhớ GPU để nhường chỗ cho các phép tính tiếp theo.",
                "example": "🧹 Code: del tensor; import torch; torch.cuda.empty_cache()."
            }
        ]
    },

    # --- DAY 01 & 02: DATA, CVAT, OBJECT DETECTION, ML/DL ---
    "object detection": {
        "keyword": "Object Detection",
        "direct_answer": "Object Detection (Nhận diện vật thể) là bài toán thị giác máy tính kết hợp giữa Phân loại (vật thể là gì) và Xác định vị trí (vật thể nằm ở đâu qua tọa độ hộp bao Bounding Box x, y, w, h).",
        "extra_example": "📌 Ví dụ: Phát hiện xe ô tô và người đi bộ trên camera giao thông kèm khung chữ nhật bao quanh từng đối tượng.",
        "socratic_question": "Khi tìm hiểu về Object Detection, bạn đang kẹt ở khái niệm nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Phân biệt Classification, Object Detection và Segmentation?",
                "explanation": "Classification chỉ đoán nhãn cả ảnh; Detection đóng khung từng vật thể; Segmentation tô màu chính xác từng điểm ảnh (pixel).",
                "example": "🖼️ So sánh: Phân loại: 'ảnh có mèo' -> Detection: 'mèo ở ô chữ nhật A' -> Segmentation: 'viền mép lông mèo'."
            },
            {
                "id": 2,
                "label": "2. Cấu trúc tọa độ Bounding Box (YOLO vs COCO)?",
                "explanation": "YOLO dùng tọa độ tâm chuẩn hóa (center_x, center_y, w, h) từ 0-1; trong khi COCO/Pascal VOC dùng pixel góc (x_min, y_min, w, h).",
                "example": "📐 Format: YOLO: [0.5, 0.4, 0.2, 0.3] vs Pascal VOC: [120, 80, 240, 190]."
            },
            {
                "id": 3,
                "label": "3. Độ đo đánh giá mAP (Mean Average Precision) và ngưỡng IoU?",
                "explanation": "IoU đo mức độ đè lấn giữa hộp dự đoán và hộp nhãn thật; mAP là diện tích dưới đường cong Precision-Recall trung bình trên các lớp.",
                "example": "🎯 Tiêu chuẩn: mAP@0.5 yêu cầu độ trùng khớp IoU từ 50% trở lên mới tính là đoán đúng."
            }
        ]
    },
    "cvat": {
        "keyword": "CVAT",
        "direct_answer": "CVAT (Computer Vision Annotation Tool) là phần mềm mã nguồn mở chuẩn công nghiệp chuyên dùng để gán nhãn dữ liệu hình ảnh và video cho các mô hình AI/ML.",
        "extra_example": "📌 Ví dụ: Vẽ bounding box quanh các biển báo giao thông hoặc gắn nhãn hành động trong video tự lái.",
        "socratic_question": "Bạn muốn làm rõ quy trình nào khi thực hành trên CVAT?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cách tạo Annotation Task và thiết lập nhãn (labels)?",
                "explanation": "Tải tập ảnh lên CVAT, định nghĩa danh sách lớp cần gán nhãn (Car, Pedestrian, Cyclist) kèm màu sắc nhận diện.",
                "example": "🏷️ Thiết lập: Tạo task 'Traffic-Sign-Batch-01' với 4 label và gán phân quyền cho thành viên."
            },
            {
                "id": 2,
                "label": "2. Xuất dữ liệu theo định dạng YOLO hay COCO?",
                "explanation": "Tùy thuộc framework huấn luyện: chọn YOLO 1.1 nếu train Ultralytics YOLO; chọn COCO JSON nếu train Faster R-CNN.",
                "example": "💾 Xuất file: Export dataset -> YOLO 1.1 -> Tải về thư mục labels chứa các file .txt."
            },
            {
                "id": 3,
                "label": "3. Kiểm soát chất lượng (QA) và độ đồng thuận giữa nhãn thủ?",
                "explanation": "Sử dụng tính năng Review/Quality trong CVAT để kiểm tra tỷ lệ trùng khớp (Consensus) giữa hai người cùng gán nhãn một ảnh.",
                "example": "🔍 Đánh giá: Người giám sát duyệt các nhãn nghi ngờ trước khi đưa vào tập Train chính thức."
            }
        ]
    },
    "self-attention": {
        "keyword": "Self-attention",
        "direct_answer": "Self-Attention (Cơ chế tự chú ý) là trái tim của kiến trúc Transformer, cho phép mô hình tính toán mối quan hệ liên kết và trọng số ngữ cảnh giữa tất cả các từ trong câu đồng thời.",
        "extra_example": "📌 Ví dụ: Trong câu 'Con chó qua đường vì nó mệt', Self-Attention giúp từ 'nó' liên kết mạnh nhất với 'con chó' thay vì 'con đường'.",
        "socratic_question": "Khi tìm hiểu Self-Attention, bạn muốn tháo gỡ điểm nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Ma trận Query (Q), Key (K), Value (V) được tính ra sao?",
                "explanation": "Từ vector nhúng từ ban đầu, nhân với 3 ma trận trọng số W_q, W_k, W_v để tạo thành 3 vai trò: Hỏi (Q), Khóa tìm kiếm (K) và Giá trị (V).",
                "example": "🔑 Phép tính: Attention(Q, K, V) = softmax(Q * K.T / sqrt(d_k)) * V."
            },
            {
                "id": 2,
                "label": "2. Tại sao cần chia cho căn bậc hai của d_k (Scaled Dot-Product)?",
                "explanation": "Khi số chiều d_k lớn, tích vô hướng Q*K có giá trị cực lớn, đẩy hàm Softmax vào vùng bão hòa gradient (vanishing gradient).",
                "example": "⚖️ Ổn định: Phép chia giúp phương sai của tích vô hướng luôn ổn định ở mức 1."
            },
            {
                "id": 3,
                "label": "3. Khác biệt giữa Self-Attention và Multi-Head Attention?",
                "explanation": "Multi-Head Attention chia Q, K, V thành nhiều không gian biểu diễn con (thường là 8 hoặc 12 đầu) để học các góc nhìn ngữ nghĩa khác nhau.",
                "example": "🧠 Đa góc nhìn: Đầu 1 học cấu trúc ngữ pháp, đầu 2 học quan hệ chủ ngữ - tân ngữ."
            }
        ]
    },
    "annotation guideline": {
        "keyword": "Annotation Guideline",
        "direct_answer": "Annotation Guideline (Tài liệu hướng dẫn gán nhãn) là bộ quy chuẩn chi tiết quy định cách thức gán nhãn, phân định các trường hợp biên mập mờ để đảm bảo dữ liệu huấn luyện đạt độ nhất quán cao.",
        "extra_example": "📌 Ví dụ: Quy định rõ: Người ngồi trên xe máy tính là nhãn 'Cyclist/Motorcyclist' chứ không được gán nhãn 'Pedestrian'.",
        "socratic_question": "Bạn muốn làm rõ khía cạnh nào của Annotation Guideline?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cách định nghĩa trường hợp biên (vật thể bị che khuất một phần)?",
                "explanation": "Guideline cần quy định rõ tỷ lệ che khuất (ví dụ: vật thể bị che > 80% thì không gán nhãn hoặc đánh cờ 'difficult').",
                "example": "📐 Quy định: Chỉ đóng khung hộp bao khi nhìn thấy rõ ít nhất 20% thân xe."
            },
            {
                "id": 2,
                "label": "2. Đo chỉ số đồng thuận gán nhãn (Inter-Annotator Agreement)?",
                "explanation": "Sử dụng chỉ số Cohen's Kappa hoặc Fleiss' Kappa để đo lường mức độ đồng thuận giữa các nhãn thủ độc lập trên cùng tập mẫu.",
                "example": "📊 Tiêu chuẩn: Kappa > 0.8 biểu thị bộ guideline rõ ràng và dữ liệu có độ tin cậy cao."
            },
            {
                "id": 3,
                "label": "3. Quy trình cập nhật guideline khi phát hiện phân bố dữ liệu mới?",
                "explanation": "Khi gặp các ca khó chưa có trong quy chuẩn, nhãn thủ báo cáo lên QA Lead để bổ sung ví dụ minh họa vào guideline phiên bản mới.",
                "example": "🔄 Vòng lặp: Guideline v1.0 -> Họp tháo gỡ edge case -> Cập nhật Guideline v1.1."
            }
        ]
    },
    "3,6": {
        "keyword": "3,6",
        "direct_answer": "Giá trị '3,6' là một đại lượng số trong tài liệu bài học, thường xuất hiện trong bảng phân tích độ đo hiệu năng (ví dụ: tỷ lệ lỗi, độ trễ xử lý) hoặc giá trị tham số cấu hình.",
        "extra_example": "📌 Ví dụ: Metric mAP@0.5 đạt 3,6 điểm tăng thêm sau khi tối ưu hóa dữ liệu gán nhãn.",
        "socratic_question": "Bạn đang băn khoăn về ý nghĩa của con số '3,6' trong bối cảnh nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Đây là độ đo mất mát (Loss) hay thời gian trễ xử lý (Latency)?",
                "explanation": "Cần đối chiếu hàng và cột trong bảng dữ liệu bài giảng để xác định đơn vị tính (phần trăm %, giây, hay giá trị hàm mất mát).",
                "example": "📊 Xem lại: Kiểm tra tiêu đề bảng tại mục đánh giá mô hình của slide."
            },
            {
                "id": 2,
                "label": "2. Giá trị này nằm trong bảng so sánh mô hình hay cấu hình tham số?",
                "explanation": "Nếu nằm trong cột hyperparameter, '3,6' có thể là trọng số mất mát hoặc tỷ lệ chia tập dữ liệu huấn luyện.",
                "example": "⚙️ Tham số: Tỷ lệ co dãn anchor box hoặc trọng số regularization."
            },
            {
                "id": 3,
                "label": "3. Tác động của chỉ số này tới ngưỡng chấp nhận của hệ thống thực tế?",
                "explanation": "Đánh giá xem con số này có đạt yêu cầu kỹ thuật (Quality Bar) đề ra trong kịch bản triển khai hay không.",
                "example": "🎯 Quyết định: Xác định xem mô hình có đủ điều kiện đưa lên môi trường thử nghiệm."
            }
        ]
    },
    "đoán token": {
        "keyword": "Cỗ máy đoán token (LLM)",
        "direct_answer": "Về bản chất toán học, LLM là cỗ máy tự hồi quy (Autoregressive Token Predictor) liên tục tính phân phối xác suất để đoán token tiếp theo có khả năng xuất hiện cao nhất dựa trên ngữ cảnh trước đó.",
        "extra_example": "📌 Ví dụ: Với câu 'Hà Nội là thủ đô của...', model tính xác suất cao nhất cho token ' Việt' (98%) rồi tới ' Nam'.",
        "socratic_question": "Khi tìm hiểu về cơ chế đoán token của LLM, bạn muốn làm rõ điều gì?",
        "chips": [
            {
                "id": 1,
                "label": "1. Quá trình Tokenization (BPE/WordPiece) chia từ ngữ ra sao?",
                "explanation": "Token không phải là từ hay chữ cái đơn thuần; các từ phổ biến là 1 token, từ hiếm hoặc tiếng Việt có thể bị tách thành 2-3 sub-word tokens.",
                "example": "🧩 Minh họa: Từ 'Transformer' là 1 token, nhưng từ phức tạp có thể bị tách thành 'Trans' + 'former'."
            },
            {
                "id": 2,
                "label": "2. Cơ chế lấy mẫu (Sampling, Top-p, Top-k, Temperature)?",
                "explanation": "Model không luôn chọn token xác suất số 1 (Greedy Search) mà lấy mẫu ngẫu nhiên có trọng số để văn bản sinh ra tự nhiên hơn.",
                "example": "🎲 Kỹ thuật: Top-k = 50 chỉ lấy mẫu trong 50 token có điểm cao nhất."
            },
            {
                "id": 3,
                "label": "3. Ảo giác (Hallucination) bắt nguồn từ bản chất đoán xác suất?",
                "explanation": "Vì chỉ tối ưu hóa sự trôi chảy của từ ngữ dựa trên xác suất thống kê, model có thể ghép các từ nghe rất thuyết phục nhưng sai sự thật.",
                "example": "⚠️ Bản chất: LLM không có nhận thức chân lý, nó chỉ ghép từ theo quy luật phân phối."
            }
        ]
    },
    "lidar": {
        "keyword": "LiDAR",
        "direct_answer": "LiDAR (Light Detection and Ranging) là cảm biến quang học sử dụng tia laser xung để đo khoảng cách và tạo đám mây điểm 3D (Point Cloud) độ chính xác cao cho môi trường xung quanh xe tự lái.",
        "extra_example": "📌 Ví dụ: Phát xung laser 100.000 lần mỗi giây để tái tạo bản đồ không gian 3D xung quanh xe trong bán kính 100m.",
        "socratic_question": "Bạn muốn làm rõ khía cạnh kỹ thuật nào của cảm biến LiDAR?",
        "chips": [
            {
                "id": 1,
                "label": "1. Khác biệt giữa dữ liệu LiDAR (Point Cloud 3D) và Camera 2D?",
                "explanation": "Camera cung cấp màu sắc và chi tiết bề mặt phong phú nhưng kém về độ sâu; LiDAR cung cấp tọa độ khoảng cách 3D chính xác từng milimet.",
                "example": "📡 So sánh: Camera chụp ảnh 2D RGB vs LiDAR quét chùm tia trả về tọa độ (X, Y, Z, Intensity)."
            },
            {
                "id": 2,
                "label": "2. Cách gán nhãn hộp bao 3D (3D Bounding Box) trên dữ liệu LiDAR?",
                "explanation": "Gán nhãn 3D đòi hỏi xác định 7 tham số: tọa độ tâm (x, y, z), kích thước (w, l, h) và góc xoay hướng đầu xe (yaw angle).",
                "example": "📦 Format 3D: Cần phần mềm chuyên dụng như CVAT 3D hoặc LabelCloud để xoay các góc nhìn."
            },
            {
                "id": 3,
                "label": "3. Kỹ thuật kết hợp cảm biến (Sensor Fusion) giữa Camera và LiDAR?",
                "explanation": "Chiếu đám mây điểm LiDAR lên mặt phẳng ảnh Camera (Calibration) để mô hình tận dụng đồng thời cả độ sâu 3D và màu sắc.",
                "example": "🚗 Ứng dụng: Xe tự lái nhận diện người đi bộ vào ban đêm nhờ laser LiDAR dù camera bị tối."
            }
        ]
    },
    "ai, ml, dl": {
        "keyword": "AI, ML, DL và Data Lifecycle",
        "direct_answer": "Data Lifecycle (Vòng đời dữ liệu) là quy trình toàn diện từ Thu thập -> Làm sạch -> Gán nhãn -> Huấn luyện -> Đánh giá -> Triển khai và Giám sát trong các dự án AI/ML/DL.",
        "extra_example": "📌 Ví dụ: 80% thời gian của dự án AI dành cho việc chuẩn bị, làm sạch và gán nhãn dữ liệu chất lượng cao.",
        "socratic_question": "Bạn đang vướng ở giai đoạn nào trong vòng đời dữ liệu AI?",
        "chips": [
            {
                "id": 1,
                "label": "1. Giai đoạn nào tốn nhiều chi phí và nhân lực nhất?",
                "explanation": "Khâu thu thập và gán nhãn dữ liệu (Data Labeling) chiếm phần lớn chi phí và quyết định trực tiếp trần chất lượng của mô hình (Garbage In, Garbage Out).",
                "example": "💡 Nguyên tắc: Dữ liệu chất lượng cao với model đơn giản luôn thắng model khủng với dữ liệu rác."
            },
            {
                "id": 2,
                "label": "2. Phân biệt phạm vi bao hàm giữa AI, ML và Deep Learning?",
                "explanation": "AI là khái niệm bao trùm rộng nhất; Machine Learning là tập con học từ dữ liệu; Deep Learning là tập con dùng mạng nơ-ron sâu nhiều tầng.",
                "example": "⭕ Biểu đồ Venn: LLM ⊂ Deep Learning ⊂ Machine Learning ⊂ Artificial Intelligence."
            },
            {
                "id": 3,
                "label": "3. Xử lý hiện tượng trôi dạt dữ liệu (Data Drift / Concept Drift)?",
                "explanation": "Sau khi triển khai, phân bố dữ liệu thực tế thay đổi so với dữ liệu huấn luyện đòi hỏi phải liên tục thu thập mẫu mới và re-train định kỳ.",
                "example": "🔄 Giám sát: Model nhận diện khẩu trang mùa dịch bị giảm độ chính xác khi hết dịch."
            }
        ]
    },
    "lịch sử ai": {
        "keyword": "Lịch sử AI",
        "direct_answer": "Lịch sử AI phát triển qua nhiều thăng trầm: từ Hội nghị Dartmouth 1956, các Mùa đông AI (AI Winters), sự bùng nổ của Học sâu (Deep Learning 2012) cho đến kỷ nguyên Mô hình ngôn ngữ lớn (LLM 2020-nay).",
        "extra_example": "📌 Ví dụ: Năm 2012 mạng AlexNet giành chiến thắng áp đảo tại ImageNet mở ra kỷ nguyên bùng nổ của Deep Learning dựa trên GPU.",
        "socratic_question": "Khi tìm hiểu lịch sử AI, bạn muốn làm rõ giai đoạn bước ngoặt nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Nguyên nhân dẫn đến các 'Mùa đông AI' (AI Winters) trong quá khứ?",
                "explanation": "Kỳ vọng bị thổi phồng quá mức so với năng lực tính toán và lượng dữ liệu thực tế tại thời điểm đó, dẫn đến việc cắt giảm tài trợ.",
                "example": "❄️ Bài học: Thập niên 1970 và 1980 khi hệ chuyên gia không đáp ứng được bài toán thực tế phức tạp."
            },
            {
                "id": 2,
                "label": "2. Bước ngoặt AlexNet 2012 và GPU computing làm thay đổi ngành ra sao?",
                "explanation": "Sự kết hợp giữa tập dữ liệu khổng lồ ImageNet, kiến trúc mạng tích chập sâu (CNN) và sức mạnh tính toán song song của card đồ họa GPU.",
                "example": "🚀 Đột phá: Giảm tỷ lệ lỗi nhận diện ảnh từ 26% xuống 16% chỉ trong 1 năm."
            },
            {
                "id": 3,
                "label": "3. Sự chuyển dịch từ mô hình chuyên biệt sang Foundation Models (LLM)?",
                "explanation": "Thay vì huấn luyện riêng từng mô hình cho từng tác vụ nhỏ, một mô hình nền tảng khổng lồ có thể giải quyết hàng trăm tác vụ khác nhau.",
                "example": "🌐 Xu hướng: GPT-4 có thể vừa dịch thuật, viết code, tóm tắt và suy luận logic đa bước."
            }
        ]
    },
    "viết đủ luật": {
        "keyword": "Giới hạn của hệ thống dựa trên luật (Rule-based)",
        "direct_answer": "Nhận định chỉ ra giới hạn cốt lõi của AI dựa trên luật (Rule-based): thế giới thực quá phức tạp và đa dạng, con người không thể viết tay đủ các câu lệnh if/else để bao quát mọi trường hợp biên.",
        "extra_example": "📌 Ví dụ: Để nhận ra chữ viết tay số '8', không thể viết đủ tập luật hình học vì mỗi người uốn nét theo một góc nghiêng khác nhau.",
        "socratic_question": "Bạn muốn làm rõ sự chuyển dịch từ Rule-based sang Machine Learning ở điểm nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Tại sao Machine Learning vượt trội hơn hẳn hệ thống viết luật tay?",
                "explanation": "ML đảo ngược quy trình: thay vì người lập trình đưa ra Quy luật + Dữ liệu -> Đáp án; ML nhận Dữ liệu + Đáp án -> Tự học ra Quy luật.",
                "example": "🔄 Đổi chiều tư duy: Để máy tính tự tìm ra trọng số tối ưu từ hàng triệu bức ảnh mẫu."
            },
            {
                "id": 2,
                "label": "2. Khái niệm Biểu diễn học (Representation Learning) trong Deep Learning?",
                "explanation": "Mô hình tự động học các đặc trưng từ mức thấp (cạnh, góc) đến mức cao (bánh xe, mắt, mũi) mà không cần con người trích xuất tay.",
                "example": "🔍 Tự động hóa: Không cần kỹ sư ngồi đo đạc tỷ lệ khoảng cách giữa hai mắt thủ công."
            },
            {
                "id": 3,
                "label": "3. Khi nào trong thực tế vẫn nên kết hợp Rule-based với ML/LLM?",
                "explanation": "Dùng Rule-based làm lớp Guardrails bảo mật và kiểm tra điều kiện cứng (Hard constraints) để đảm bảo an toàn tuyệt đối.",
                "example": "🛡️ Kết hợp: LLM tạo câu trả lời sáng tạo, nhưng Regex Rule chặn lộ mã số thẻ ngân hàng."
            }
        ]
    },
    "machine learning": {
        "keyword": "Machine Learning",
        "direct_answer": "Machine Learning (Học máy) là phân ngành của AI cho phép máy tính tự học các quy luật và mẫu hình từ dữ liệu thay vì phải lập trình tường minh từng dòng lệnh xử lý.",
        "extra_example": "📌 Ví dụ: Huấn luyện thuật toán phân loại email spam dựa trên 100.000 email mẫu trong quá khứ.",
        "socratic_question": "Khi tìm hiểu về Machine Learning, bạn muốn tháo gỡ điểm nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Ba nhánh chính: Supervised, Unsupervised và Reinforcement Learning?",
                "explanation": "Có giám sát (dữ liệu có nhãn), Không giám sát (tự tìm cụm/cấu trúc dữ liệu) và Học tăng cường (học qua thưởng/phạt từ môi trường).",
                "example": "🌳 Phân loại: Dự đoán giá nhà (Supervised) vs Phân khúc khách hàng (Unsupervised) vs Chơi cờ AlphaGo (RL)."
            },
            {
                "id": 2,
                "label": "2. Quy trình chia tập Train, Validation và Test set?",
                "explanation": "Train set để học trọng số, Validation set để tinh chỉnh siêu tham số và chống Overfitting, Test set để đánh giá khách quan lần cuối.",
                "example": "📊 Tỷ lệ thông dụng: 70% Train - 15% Validation - 15% Test."
            },
            {
                "id": 3,
                "label": "3. Hiện tượng Overfitting và cách phòng ngừa?",
                "explanation": "Mô hình học vẹt quá mức dữ liệu huấn luyện dẫn đến điểm cao trên tập Train nhưng đoán sai khi gặp dữ liệu thực tế mới.",
                "example": "⚠️ Giải pháp: Bổ sung thêm dữ liệu, giảm độ phức tạp mô hình hoặc dùng Regularization (L1/L2, Dropout)."
            }
        ]
    },
    "transformer explainer": {
        "keyword": "Transformer Explainer",
        "direct_answer": "Transformer Explainer là công cụ trực quan hóa tương tác giúp người học quan sát trực tiếp luồng dữ liệu, attention weights và biểu diễn vector bên trong mô hình Transformer.",
        "extra_example": "📌 Ví dụ: Di chuột qua từ 'bank' để thấy attention hướng về 'river' hay 'money' nhằm giải nghĩa từ theo ngữ cảnh.",
        "socratic_question": "Khi khám phá công cụ Transformer Explainer, bạn muốn hiểu sâu thành phần nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Cách đọc Attention Heatmap giữa các cặp token?",
                "explanation": "Màu càng đậm biểu thị trọng số chú ý giữa hai token càng cao; cho biết model đang căn cứ vào từ nào để sinh từ tiếp theo.",
                "example": "🔥 Biểu đồ nhiệt: Cột dọc là Query, hàng ngang là Key; ô giao nhau sáng màu thể hiện liên kết mạnh."
            },
            {
                "id": 2,
                "label": "2. Ý nghĩa của Residual Connection và Layer Normalization?",
                "explanation": "Đường tắt Residual giúp luồng gradient truyền trực tiếp qua hàng chục tầng mạng sâu mà không bị suy hao (triệt tiêu gradient).",
                "example": "⚡ Công thức: Output = LayerNorm(x + Sublayer(x))."
            },
            {
                "id": 3,
                "label": "3. Vai trò của Positional Encoding trong việc giữ trật tự từ?",
                "explanation": "Vì cơ chế Attention xử lý tất cả các từ song song đồng thời nên cần cộng thêm vector mã hóa vị trí để model biết từ nào đứng trước, từ nào đứng sau.",
                "example": "📍 Khác biệt: Giúp model phân biệt giữa 'chó cắn người' và 'người cắn chó'."
            }
        ]
    },
    "xe tự lái": {
        "keyword": "Xe tự lái nhận diện người đi bộ",
        "direct_answer": "Mô hình nhận diện người đi bộ trên xe tự lái học được hình dáng con người thông qua hàng triệu bức ảnh được gắn nhãn bounding box từ camera và cảm biến LiDAR trong quá trình thu thập dữ liệu.",
        "extra_example": "📌 Ví dụ: Huấn luyện mạng nơ-ron nhận diện cả người lớn, trẻ em, người đi xe lăn ở các góc nghiêng và điều kiện ánh sáng khác nhau.",
        "socratic_question": "Bạn muốn làm rõ bài toán nhận diện người đi bộ ở khía cạnh nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Dữ liệu huấn luyện được thu thập và gán nhãn ra sao?",
                "explanation": "Các đội xe chạy hàng triệu km ghi hình, sau đó các chuyên viên gán nhãn vẽ khung hộp bao quanh từng người trong từng khung hình video.",
                "example": "📹 Dữ liệu khổng lồ: Tập dữ liệu Waymo Open Dataset hoặc nuScenes gồm hàng terabyte ảnh đường phố."
            },
            {
                "id": 2,
                "label": "2. Xử lý các góc khuất, ban đêm và điều kiện thời tiết xấu?",
                "explanation": "Dùng kỹ thuật Sensor Fusion kết hợp Camera hồng ngoại, Radar xuyên sương mù và LiDAR đo độ sâu 3D.",
                "example": "🌧️ An toàn: Dù trời mưa camera bị mờ thì cảm biến Radar vẫn phát hiện khoảng cách vật cản phía trước."
            },
            {
                "id": 3,
                "label": "3. Hậu quả của lỗi False Negative (bỏ sót người đi bộ)?",
                "explanation": "Trong xe tự lái, False Negative (có người nhưng tưởng không có) có cái giá sai sót (cost of error) cực cao vì đe dọa trực tiếp tính mạng con người.",
                "example": "⚠️ Tiêu chuẩn an toàn: Hệ thống phanh khẩn cấp tự động (AEB) luôn ưu tiên độ bao phủ Recall gần tuyệt đối."
            }
        ]
    },
    "llm ⊂ dl ⊂ ml ⊂ ai": {
        "keyword": "Quan hệ phân cấp AI - ML - DL - LLM",
        "direct_answer": "Biểu đồ tập hợp con thể hiện quan hệ bao hàm: AI là vòng tròn lớn nhất (Trí tuệ nhân tạo tổng quát) ⊃ ML (Học máy) ⊃ DL (Học sâu với mạng nơ-ron nhiều tầng) ⊃ LLM (Mô hình ngôn ngữ lớn).",
        "extra_example": "📌 Ví dụ: Mọi LLM đều là Deep Learning, nhưng không phải mô hình AI nào cũng là LLM (ví dụ thuật toán cây quyết định Decision Tree thuộc ML nhưng không thuộc DL).",
        "socratic_question": "Bạn muốn làm rõ ranh giới kỹ thuật nào trong biểu đồ phân cấp này?",
        "chips": [
            {
                "id": 1,
                "label": "1. Sự khác biệt then chốt giữa Deep Learning truyền thống và LLM?",
                "explanation": "DL truyền thống thường giải bài toán chuyên biệt (nhận diện khuôn mặt, phân loại ảnh); LLM là mô hình nền tảng tổng quát đa tác vụ xử lý ngôn ngữ.",
                "example": "🔍 So sánh: ResNet (DL chuyên ảnh) vs GPT-4 (LLM đa năng đọc hiểu, viết lách, lập luận)."
            },
            {
                "id": 2,
                "label": "2. Tại sao gọi chung chung là 'AI' có thể gây nhầm lẫn khi thiết kế hệ thống?",
                "explanation": "Mỗi tầng công nghệ có chi phí tính toán, độ trễ và rủi ro ảo giác hoàn toàn khác nhau; dùng LLM cho tác vụ phân loại nhị phân đơn giản là lãng phí tài nguyên.",
                "example": "⚖️ Kiến trúc: Phân loại email chỉ cần ML truyền thống (TF-IDF + SVM) chạy 2ms, không cần gọi LLM tốn 2000ms."
            },
            {
                "id": 3,
                "label": "3. Phạm vi ứng dụng tối ưu của từng tầng công nghệ?",
                "explanation": "Chọn đúng công cụ: Thuật toán Rule/ML cho dữ liệu dạng bảng số liệu; Deep Learning cho xử lý ảnh/âm thanh; LLM cho giao tiếp ngôn ngữ tự nhiên.",
                "example": "🎯 Lựa chọn: Bảng dữ liệu Excel dùng XGBoost; nhận diện khuôn mặt dùng CNN; chatbot tư vấn dùng LLM."
            }
        ]
    },
    "có giám sát": {
        "keyword": "Supervised Learning (Học có giám sát)",
        "direct_answer": "Supervised Learning (Học có giám sát) là phương pháp huấn luyện mô hình dựa trên cặp dữ liệu có sẵn đáp án chuẩn (Features X, Labels Y). Mô hình học cách ánh xạ từ đầu vào sang đầu ra chuẩn xác.",
        "extra_example": "📌 Ví dụ: Cung cấp 10.000 ảnh chụp X-quang phổi kèm nhãn của bác sĩ 'Viêm phổi' hoặc 'Bình thường' để mô hình học cách chẩn đoán.",
        "socratic_question": "Bạn muốn tìm hiểu sâu hơn khía cạnh nào của Học có giám sát?",
        "chips": [
            {
                "id": 1,
                "label": "1. Chi phí và thách thức lớn nhất của việc gán nhãn dữ liệu?",
                "explanation": "Cần nhân lực chuyên gia gán nhãn thủ công từng mẫu dữ liệu; tốn kém thời gian và dễ xảy ra sai lệch chủ quan giữa các nhãn thủ.",
                "example": "💰 Thách thức: Gán nhãn dữ liệu y tế đòi hỏi bác sĩ chuyên khoa đọc từng phim chụp với chi phí rất cao."
            },
            {
                "id": 2,
                "label": "2. Phân biệt giữa bài toán Phân loại (Classification) và Hồi quy (Regression)?",
                "explanation": "Phân loại dự đoán nhãn rời rạc (chó/mèo, đậu/rớt); Hồi quy dự đoán giá trị số liên tục (giá nhà, nhiệt độ ngày mai).",
                "example": "📈 Phân định: Dự đoán 'khách hàng có rời bỏ không' (Phân loại) vs 'doanh thu quý tới' (Hồi quy)."
            },
            {
                "id": 3,
                "label": "3. Bộ chỉ số đánh giá: Accuracy, Precision, Recall và F1-Score?",
                "explanation": "Với dữ liệu mất cân bằng (ví dụ bệnh hiếm 1%), Accuracy không có ý nghĩa; cần dùng Precision (độ chuẩn xác) và Recall (độ bao phủ).",
                "example": "🎯 Đánh giá: Bài toán phát hiện gian lận thẻ tín dụng luôn tối ưu hóa chỉ số Recall để không bỏ lọt tội phạm."
            }
        ]
    },
    "không giám sát": {
        "keyword": "Unsupervised Learning (Học không giám sát)",
        "direct_answer": "Unsupervised Learning (Học không giám sát) huấn luyện mô hình trên dữ liệu không có nhãn (unlabeled data) nhằm tự động tìm kiếm các cấu trúc ẩn, phân cụm dữ liệu (Clustering) hoặc giảm số chiều (Dimensionality Reduction).",
        "extra_example": "📌 Ví dụ: Phân cụm 1 triệu khách hàng siêu thị thành 5 nhóm có hành vi mua sắm tương đồng mà không cần ai dán nhãn trước.",
        "socratic_question": "Khi tìm hiểu về Học không giám sát, bạn muốn làm rõ điều gì?",
        "chips": [
            {
                "id": 1,
                "label": "1. Các thuật toán phổ biến: K-Means, DBSCAN và PCA?",
                "explanation": "K-Means chia dữ liệu thành K cụm theo khoảng cách tâm; DBSCAN gom cụm theo mật độ; PCA nén dữ liệu nhiều chiều xuống 2D/3D trực quan.",
                "example": "📊 Trực quan hóa: Dùng PCA nén 50 thuộc tính người dùng xuống biểu đồ 2D để xem cụm phân bố."
            },
            {
                "id": 2,
                "label": "2. Khi nào nên dùng học không giám sát thay vì học có giám sát?",
                "explanation": "Khi dữ liệu hoàn toàn chưa có nhãn và chi phí gán nhãn quá đắt đỏ, hoặc khi muốn khám phá các mẫu hình bất thường mới lạ.",
                "example": "💡 Ứng dụng: Phát hiện tấn công mạng mới lạ chưa từng có trong lịch sử (Anomaly Detection)."
            },
            {
                "id": 3,
                "label": "3. Đánh giá chất lượng phân cụm bằng chỉ số Silhouette Score?",
                "explanation": "Chỉ số từ -1 đến 1 đo khoảng cách giữa các điểm trong cùng cụm so với khoảng cách tới các cụm lân cận khác.",
                "example": "📐 Chỉ số: Silhouette càng gần 1 chứng tỏ các cụm tách biệt rõ ràng và dữ liệu được nhóm hợp lý."
            }
        ]
    },
    "bounding box": {
        "keyword": "Bounding Box (Hộp bao)",
        "direct_answer": "Bounding Box (Hộp bao) là hình chữ nhật bao quanh vật thể trong bài toán Object Detection, được xác định bởi tọa độ 4 điểm hoặc tọa độ tâm và kích thước (x, y, w, h).",
        "extra_example": "📌 Ví dụ: [x_center=0.45, y_center=0.60, width=0.20, height=0.35] biểu diễn hộp bao người đi bộ trong ảnh 1920x1080.",
        "socratic_question": "Bạn muốn làm rõ khía cạnh kỹ thuật nào của Bounding Box?",
        "chips": [
            {
                "id": 1,
                "label": "1. Phân biệt tọa độ chuẩn hóa YOLO và tọa độ pixel COCO?",
                "explanation": "YOLO chia tọa độ cho chiều rộng và cao của ảnh để giá trị luôn nằm trong khoảng [0, 1]; COCO lưu giá trị pixel tuyệt đối.",
                "example": "📏 Chuẩn hóa: Giúp mô hình huấn luyện độc lập với kích thước phân giải của ảnh gốc."
            },
            {
                "id": 2,
                "label": "2. Xử lý vật thể bị che khuất một phần (Occlusion)?",
                "explanation": "Hộp bao phải bao trọn toàn bộ vật thể bao gồm cả phần bị che khuất theo suy đoán hình học của mắt người.",
                "example": "📦 Nguyên tắc: Nếu xe hơi bị cột đèn che ngang, vẽ 1 hộp bao trùm cả xe thay vì cắt đôi thành 2 hộp."
            },
            {
                "id": 3,
                "label": "3. Thuật toán Non-Maximum Suppression (NMS) loại bỏ hộp trùng lặp?",
                "explanation": "Mô hình sinh ra hàng chục hộp bao xung quanh cùng một vật thể; NMS giữ lại hộp có độ tự tin cao nhất và xóa các hộp có IoU trùng lấn cao.",
                "example": "✂️ Lọc nhiễu: 5 hộp bao quanh 1 con mèo -> NMS gộp lại thành đúng 1 hộp chuẩn xác nhất."
            }
        ]
    },
    "không có": {
        "keyword": "Đoạn bôi đen ngắn ('không có')",
        "direct_answer": "Đoạn bạn bôi đen quá ngắn ('không có') và thiếu ngữ cảnh câu hoàn chỉnh. AI Tutor cần thêm bối cảnh để tháo gỡ chính xác điểm vướng của bạn.",
        "extra_example": "📌 Lời khuyên: Hãy bôi đen trọn vẹn cả câu hoặc cụm từ chuyên môn trong bài giảng để nhận hỗ trợ tốt nhất.",
        "socratic_question": "Bạn đang gặp khó khăn ở khía cạnh nào của nội dung này?",
        "chips": [
            {
                "id": 1,
                "label": "1. Khái niệm lý thuyết trong câu chứa từ này?",
                "explanation": "Bạn đang băn khoăn về thuật ngữ hoặc định nghĩa xuất hiện quanh đoạn này trong slide.",
                "example": "📖 Gợi ý: Bôi đen cả câu chứa từ 'không có' để mình giải thích trọn vẹn."
            },
            {
                "id": 2,
                "label": "2. Logic câu hỏi trắc nghiệm hoặc bài tập Lab?",
                "explanation": "Bạn đang đối chiếu đáp án đúng/sai của một câu hỏi tự lượng giá trong bài học.",
                "example": "❓ Đối chiếu: Xem lại đề bài tại mục kiểm tra kiến thức cuối bài."
            },
            {
                "id": 3,
                "label": "3. Vị trí và ý nghĩa của mục này trong giáo trình?",
                "explanation": "Bạn muốn biết nội dung này nằm ở bài giảng nào và liên hệ với các buổi học khác ra sao.",
                "example": "🧭 Định hướng: Xem mục lục bài học ở thanh menu bên trái."
            }
        ]
    },
    "đáp": {
        "keyword": "Đoạn bôi đen ngắn ('đáp')",
        "direct_answer": "Đoạn bôi đen chỉ gồm một từ rời rạc ('đáp'). Hãy bôi đen cả câu hoặc cụm từ chứa từ này để trợ giảng hiểu rõ bạn đang thắc mắc điều gì.",
        "extra_example": "📌 Lời khuyên: Bôi đen trọn vẹn cụm 'Đáp án trắc nghiệm' hoặc 'Phương án đáp ứng' để nhận phân tích chi tiết.",
        "socratic_question": "Bạn muốn trợ giảng hỗ trợ tháo gỡ nội dung nào?",
        "chips": [
            {
                "id": 1,
                "label": "1. Giải thích đáp án và căn cứ lý thuyết của câu hỏi?",
                "explanation": "Làm rõ tại sao một phương án lại được chọn là đáp án chính xác dựa trên giáo trình bài học.",
                "example": "💡 Căn cứ: Trích dẫn slide bài giảng tương ứng làm bằng chứng."
            },
            {
                "id": 2,
                "label": "2. Phân tích các bẫy thường gặp trong câu hỏi trắc nghiệm?",
                "explanation": "Chỉ ra những nhầm lẫn phổ biến giữa các đáp án gây nhiễu để bạn tránh mất điểm.",
                "example": "⚠️ Phân biệt: Các từ khóa nhạy cảm như 'luôn luôn', 'không bao giờ'."
            },
            {
                "id": 3,
                "label": "3. Cách tra cứu nhanh tài liệu để tự kiểm chứng đáp án?",
                "explanation": "Hướng dẫn phương pháp tìm kiếm từ khóa trong slide để tự tìm ra câu trả lời thuyết phục.",
                "example": "🔍 Kỹ năng: Nhấn Ctrl+F trên slide để tìm định nghĩa gốc."
            }
        ]
    }
}

# Aliases mở rộng để tăng độ phủ của RAG-lite
MOCK_KNOWLEDGE["ml"] = MOCK_KNOWLEDGE["machine learning"]
MOCK_KNOWLEDGE["supervised learning"] = MOCK_KNOWLEDGE["có giám sát"]
MOCK_KNOWLEDGE["unsupervised learning"] = MOCK_KNOWLEDGE["không giám sát"]
MOCK_KNOWLEDGE["transformer"] = MOCK_KNOWLEDGE["self-attention"]

# =============================================================================
# 2. LOGGING & TRACE RECORDING (Rubric R5 & HAX G2)
# =============================================================================
def append_trace_log(entry):
    """Lưu trữ vết thực thi vào file docs/trace_waterfall.json."""
    logs = []
    if os.path.exists(TRACE_LOG_PATH):
        try:
            with open(TRACE_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    logs.insert(0, entry)
    if len(logs) > 100:
        logs = logs[:100]
        
    try:
        with open(TRACE_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Không thể ghi trace_waterfall.json: {e}")

# =============================================================================
# 3. GEMINI 1.5 FLASH PROMPT & CALLER
# =============================================================================
def call_gemini_api(snippet, context_title, api_key):
    """Gọi trực tiếp Google Gemini 1.5 Flash API qua urllib chuẩn."""
    start_time = time.perf_counter()
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    system_instruction = (
        "Bạn là Trợ giảng Sư phạm VLearn cho khóa học AI khoá K4 (Day 03: Chatbot vs ReAct Agent).\n"
        "Khi học viên bôi đen một đoạn văn bản hoặc mã code, TUYỆT ĐỐI KHÔNG xả lý thuyết một chiều.\n"
        "Nhiệm vụ của bạn là Socratic Scaffolding:\n"
        "1. Đặt 1 câu hỏi gợi mở ngắn gọn (<= 2 câu) bắt đúng bản chất vấn đề.\n"
        "2. Đưa ra chính xác 3 chip lựa chọn (options) đại diện cho 3 điểm nghẽn nhận thức phổ biến nhất. "
        "Mỗi chip có label ngắn gọn (<= 15 từ), explanation súc tích và ví dụ trực quan.\n"
        "3. Nếu học viên hỏi về logistics (điểm danh, wifi, phòng học) hoặc đòi viết code giải lab hộ: Đặt is_out_of_scope = true.\n\n"
        "Trả về DUY NHẤT định dạng JSON chuẩn không kèm markdown thừa:\n"
        "{\n"
        '  "socratic_question": "Câu hỏi gợi mở...",\n'
        '  "chips": [\n'
        '    {"id": 1, "label": "Tên điểm nghẽn 1...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."},\n'
        '    {"id": 2, "label": "Tên điểm nghẽn 2...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."},\n'
        '    {"id": 3, "label": "Tên điểm nghẽn 3...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."}\n'
        "  ],\n"
        '  "is_out_of_scope": false\n'
        "}"
    )

    prompt_user = f"Bối cảnh bài học: {context_title}\nĐoạn văn bản/mã code học viên đang bôi đen: \"{snippet}\"\nHãy sinh câu hỏi Socratic và 3 chip tháo gỡ điểm nghẽn nhận thức."

    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": prompt_user}]}],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=12) as res:
        res_data = json.loads(res.read().decode("utf-8"))

    latency_ms = round((time.perf_counter() - start_time) * 1000)
    raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(raw_text)
    tokens_used = res_data.get("usageMetadata", {}).get("totalTokenCount", 210)

    formatted_chips = []
    for idx, c in enumerate(parsed.get("chips", [])):
        label = c.get("label", f"Lựa chọn {idx + 1}")
        words = label.split()
        if len(words) > 15:
            label = " ".join(words[:14]) + "..."
        formatted_chips.append({
            "id": c.get("id", idx + 1),
            "label": label,
            "explanation": c.get("explanation", "Giải thích đang được cập nhật."),
            "example": c.get("example", "💡 Xem ví dụ trong bài giảng Day 03.")
        })

    trace_entry = {
        "turn_id": int(time.time() * 1000),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": "Socratic Probing Generation (Gemini Live API)",
        "model": "gemini-1.5-flash",
        "selected_text": snippet[:45],
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
        "layer_used": "Live-AI",
        "status": "PASS"
    }
    append_trace_log(trace_entry)

    return {
        "matchedKeyword": snippet,
        "directAnswer": f"Đoạn \"{snippet}\" là một khái niệm quan trọng trong bài học. Dưới đây là các hướng tháo gỡ điểm nghẽn.",
        "socraticQuestion": parsed.get("socratic_question", f"Bạn muốn làm rõ khía cạnh nào của \"{snippet}\"?"),
        "chips": formatted_chips,
        "isOutOfScope": parsed.get("is_out_of_scope", False),
        "isLiveAI": True,
        "layerUsed": "Live-AI",
        "latencyMs": latency_ms,
        "tokensUsed": tokens_used
    }

def call_openrouter_api(snippet, context_title, api_key, model="liquid/lfm-2.5-2.6b:free"):
    """Gọi OpenRouter API hỗ trợ key sk-or-v1-... với fallback tự động sang model free."""
    start_time = time.perf_counter()
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    system_instruction = (
        "Bạn là Trợ giảng Sư phạm VLearn cho khóa học AI khoá K4 (Day 03: Chatbot vs ReAct Agent).\n"
        "Khi học viên bôi đen một đoạn văn bản hoặc mã code, TUYỆT ĐỐI KHÔNG xả lý thuyết một chiều.\n"
        "Nhiệm vụ của bạn là Socratic Scaffolding:\n"
        "1. Đặt 1 câu hỏi gợi mở ngắn gọn (<= 2 câu) bắt đúng bản chất vấn đề.\n"
        "2. Đưa ra chính xác 3 chip lựa chọn (options) đại diện cho 3 điểm nghẽn nhận thức phổ biến nhất. "
        "Mỗi chip có label ngắn gọn (<= 15 từ), explanation súc tích và ví dụ trực quan.\n"
        "3. Nếu học viên hỏi về logistics (điểm danh, wifi, phòng học) hoặc đòi viết code giải lab hộ: Đặt is_out_of_scope = true.\n\n"
        "Trả về DUY NHẤT định dạng JSON chuẩn không kèm markdown thừa:\n"
        "{\n"
        '  "socratic_question": "Câu hỏi gợi mở...",\n'
        '  "chips": [\n'
        '    {"id": 1, "label": "Tên điểm nghẽn 1...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."},\n'
        '    {"id": 2, "label": "Tên điểm nghẽn 2...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."},\n'
        '    {"id": 3, "label": "Tên điểm nghẽn 3...", "explanation": "Giải thích ngắn...", "example": "Ví dụ..."}\n'
        "  ],\n"
        '  "is_out_of_scope": false\n'
        "}"
    )

    prompt_user = f"Bối cảnh bài học: {context_title}\nĐoạn văn bản/mã code học viên đang bôi đen: \"{snippet}\"\nHãy sinh câu hỏi Socratic và 3 chip tháo gỡ điểm nghẽn nhận thức."

    models_to_try = [
        model,
        "liquid/lfm-2.5-2.6b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemini-2.5-flash"
    ]
    unique_models = []
    for m in models_to_try:
        if m and m not in unique_models:
            unique_models.append(m)

    res_data = None
    last_err = None
    used_model = unique_models[0]

    for m in unique_models:
        try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt_user}
                ],
                "temperature": 0.2
            }
            if ":free" not in m:
                payload["response_format"] = {"type": "json_object"}

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://vlearn.ai20k.edu.vn",
                    "X-Title": "VLearn Socratic Tutor"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=12) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                used_model = m
                break
        except Exception as e:
            last_err = e
            continue

    if not res_data:
        raise last_err or RuntimeError("All OpenRouter models failed")

    latency_ms = round((time.perf_counter() - start_time) * 1000)
    raw_text = res_data["choices"][0]["message"]["content"]
    
    clean_text = raw_text.strip()
    if clean_text.startswith("```"):
        clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)

    try:
        parsed = json.loads(clean_text)
    except Exception:
        m = re.search(r"\{.*\}", clean_text, re.DOTALL)
        if m:
            parsed = json.loads(m.group(0))
        else:
            raise

    tokens_used = res_data.get("usage", {}).get("total_tokens", 220)

    formatted_chips = []
    for idx, c in enumerate(parsed.get("chips", [])):
        label = c.get("label", f"Lựa chọn {idx + 1}")
        words = label.split()
        if len(words) > 15:
            label = " ".join(words[:14]) + "..."
        formatted_chips.append({
            "id": c.get("id", idx + 1),
            "label": label,
            "explanation": c.get("explanation", "Giải thích đang được cập nhật."),
            "example": c.get("example", "💡 Xem ví dụ trong bài giảng Day 03.")
        })

    trace_entry = {
        "turn_id": int(time.time() * 1000),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": f"Socratic Probing Generation (OpenRouter: {used_model})",
        "model": used_model,
        "selected_text": snippet[:45],
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
        "layer_used": "Live-AI",
        "status": "PASS"
    }
    append_trace_log(trace_entry)

    return {
        "matchedKeyword": snippet,
        "directAnswer": f"Đoạn \"{snippet}\" là một khái niệm quan trọng trong bài học. Dưới đây là các hướng tháo gỡ điểm nghẽn.",
        "socraticQuestion": parsed.get("socratic_question", f"Bạn muốn làm rõ khía cạnh nào của \"{snippet}\"?"),
        "chips": formatted_chips,
        "isOutOfScope": parsed.get("is_out_of_scope", False),
        "isLiveAI": True,
        "layerUsed": "Live-AI",
        "latencyMs": latency_ms,
        "tokensUsed": tokens_used
    }

# =============================================================================
# 4. INTENT GUARDRAILS & SMART ROUTER
# =============================================================================
def check_intent_guardrails(snippet):
    """Kiểm tra các kịch bản biên & rào chắn thẩm quyền (Layer 0)."""
    text = (snippet or "").strip()
    norm = text.lower()

    # 1. Rào chắn URL ngoài (GS-02)
    if re.match(r"^(https?://|www\.)", text, re.IGNORECASE) or norm in ["http", "https"]:
        return {
            "matchedKeyword": text,
            "isOutOfScope": True,
            "rejectionReason": "Bạn đang bôi đen một đường dẫn liên kết (URL).",
            "explanation": "Có vẻ như bạn đã bôi nhầm vào một đường link web thay vì thuật ngữ chuyên môn. Hãy bôi đen cụm từ khóa bạn chưa hiểu trong bài giảng (ví dụ: 'ReAct Agent' hoặc 'Tool Schema') để mình hỗ trợ gỡ rối nhé!",
            "citation": "Mẹo bôi đen từ khóa trọng tâm (HAX G1)"
        }

    # 2. Rào chắn Logistics (Điểm danh, phòng học, wifi)
    if any(k in norm for k in ["điểm danh", "quét mã", "wifi", "phòng học", "mã qr"]):
        return {
            "matchedKeyword": text,
            "isOutOfScope": True,
            "rejectionReason": "Vấn đề điểm danh là quy trình vận hành (Logistics), không thuộc nội dung bài học chuyên môn (Lớp chỗ khó ③).",
            "explanation": "Chào bạn! Việc quét mã QR điểm danh bằng Microsoft Form là hệ thống độc lập, không đồng bộ lịch sử về app MyVinUni. Bạn hãy chủ động chụp lại ảnh màn hình xác nhận sau khi nộp form, và nhắn ngay cho Lab Coach trực phòng E403 để được hỗ trợ đối soát nhé!",
            "citation": "Quy chế điểm danh K4 & Kênh hỗ trợ Lab Coach phòng E403"
        }

    # 3. Rào chắn gian lận học thuật (Đòi code giải lab hộ)
    if any(k in norm for k in ["giải hộ", "làm hộ bài lab", "cho xin full code"]):
        return {
            "matchedKeyword": text,
            "isOutOfScope": True,
            "rejectionReason": "Yêu cầu giải hộ toàn bộ bài tập vi phạm nguyên tắc Sư phạm & Liêm chính học thuật (HAX G1).",
            "explanation": "AI Tutor được thiết kế để gợi mở từng bước (Socratic Scaffolding) giúp bạn tự xây dựng tư duy lập trình, không được phép đưa code giải hoàn chỉnh. Hãy bôi đen dòng code hoặc lỗi cụ thể bạn đang vướng để cùng tháo gỡ nhé!",
            "citation": "Chính sách Học thuật AI20k (Socratic Assistance)"
        }

    # 4. Rào chắn Prompt Injection
    if any(k in norm for k in ["làm thơ", "ignore previous instructions", "bỏ qua hướng dẫn", "bạn là ai"]):
        return {
            "matchedKeyword": text,
            "isOutOfScope": True,
            "rejectionReason": "Phát hiện yêu cầu nằm ngoài phạm vi học tập chuyên môn.",
            "explanation": "Mình là Trợ giảng Sư phạm VLearn chuyên trách nội dung bài Lab K4. Mình chỉ hỗ trợ các câu hỏi liên quan đến kiến thức và mã nguồn bài học!",
            "citation": "Chính sách Giới hạn Trợ giảng (HAX G1)"
        }

    return None

def classify_input_type(snippet):
    """Phân loại dạng thức dữ liệu của đoạn bôi đen để định hình chiến lược phản hồi."""
    text = (snippet or "").strip()
    if not text:
        return "EMPTY"
    
    code_indicators = ["def ", "()", "->", "import ", "from ", "class ", "return ", "print(", "{", "}", "while ", "if "]
    if any(ind in text for ind in code_indicators) or ("\n" in text and ("=" in text or ":" in text)):
        return "CODE_SNIPPET"
        
    if re.match(r"^[\d\s,.\-%/]+$", text):
        return "NUMBER_METRIC"
        
    words = text.split()
    if len(words) > 12 or text.endswith("?"):
        return "LONG_TEXT"
        
    return "CONCEPT"

def score_match(query_norm, kb_key):
    """
    Tính điểm tương đồng giữa đoạn bôi đen và khóa trong Knowledge Base.
    Trả về điểm từ 0.0 đến 1.0.
    """
    if kb_key in query_norm or query_norm in kb_key:
        return 1.0
        
    q_tokens = set(re.findall(r"\w+", query_norm))
    kb_tokens = set(re.findall(r"\w+", kb_key))
    
    if not q_tokens or not kb_tokens:
        return 0.0
        
    overlap = len(q_tokens & kb_tokens)
    if overlap == 0:
        return 0.0
        
    coverage = overlap / len(kb_tokens)
    precision = overlap / len(q_tokens)
    f1 = 2 * (coverage * precision) / (coverage + precision)
    return round(f1, 2)

def query_mock_kb(snippet):
    """
    Tìm kiếm tri thức tối ưu trong RAG-lite Mock KB (Layer 1).
    Trả về (best_entry, confidence_score, best_key)
    """
    norm = (snippet or "").lower().strip()
    best_entry = None
    best_score = 0.0
    best_key = ""
    
    for key, val in MOCK_KNOWLEDGE.items():
        score = score_match(norm, key)
        if score > best_score:
            best_score = score
            best_entry = val
            best_key = key
            
    return best_entry, best_score, best_key

def resolve_socratic_probe(snippet, context_title="", api_key=None, mode="mock"):
    """
    Điều phối thông minh 3-Layer Agent Router:
    Layer 0: Guardrails (URL, Logistics, Prompt Injection)
    Layer 1: RAG-lite Mock KB (0ms, 0 tokens, fuzzy match)
    Layer 2: Live AI Model (OpenRouter/Gemini API) khi cần hoặc khi chọn Live
    """
    # --- Layer 0: Intent Guardrails ---
    guard = check_intent_guardrails(snippet)
    if guard:
        return guard

    active_key = api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
    
    # --- Layer 1: RAG-lite Mock KB Query ---
    best_entry, confidence, matched_key = query_mock_kb(snippet)

    # Nếu người dùng chọn Live AI và có API key -> Gọi Live AI (Layer 2)
    if mode == "gemini" and active_key:
        try:
            if active_key.startswith("sk-or-"):
                model = os.environ.get("GEMINI_MODEL", "google/gemini-2.5-flash")
                return call_openrouter_api(snippet, context_title, active_key, model=model)
            else:
                return call_gemini_api(snippet, context_title, active_key)
        except Exception as err:
            print(f"[WARN] Live AI API gặp lỗi ({err}), tự động chuyển về RAG-lite Mock KB.")

    # --- Khi ở chế độ Mock hoặc khi Live AI fallback ---
    if best_entry and confidence >= 0.4:
        trace_entry = {
            "turn_id": int(time.time() * 1000),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "step": f"RAG Knowledge Retrieval (Key: {best_entry['keyword']} · Score: {confidence})",
            "model": "vlearn-rag-lite-kb",
            "selected_text": snippet[:45],
            "latency_ms": 12,
            "tokens_used": 0,
            "layer_used": "RAG-hit",
            "rag_confidence": confidence,
            "status": "PASS"
        }
        append_trace_log(trace_entry)
        return {
            "matchedKeyword": best_entry["keyword"],
            "directAnswer": best_entry["direct_answer"],
            "socraticQuestion": best_entry["socratic_question"],
            "chips": best_entry["chips"],
            "isOutOfScope": False,
            "isLiveAI": False,
            "layerUsed": "RAG-hit",
            "ragConfidence": confidence,
            "latencyMs": 12,
            "tokensUsed": 0
        }

    # Fallback động thông minh theo dạng thức input
    input_type = classify_input_type(snippet)
    trunc = snippet[:32] + "..." if len(snippet) > 35 else snippet
    
    if input_type == "CODE_SNIPPET":
        socratic_q = f"Bạn đang kiểm tra đoạn mã code '{trunc}'. Điểm nghẽn cú pháp hoặc logic nào bạn muốn tháo gỡ?"
        chips = [
            {"id": 1, "label": "1. Cú pháp và tham số đầu vào của hàm?", "explanation": "Xem xét kiểu dữ liệu của các arguments truyền vào và giá trị mặc định.", "example": "💻 Code check: Kiểm tra type hints và dictionary parameters."},
            {"id": 2, "label": "2. Khối try/except xử lý ngoại lệ runtime?", "explanation": "Bọc đoạn mã để bắt kịp thời các lỗi kết nối hoặc parse JSON.", "example": "🔄 Bẫy lỗi: try: ... except Exception as err: ..."},
            {"id": 3, "label": "3. Vết thực thi trong docs/trace_waterfall.json?", "explanation": "Đối chiếu thời gian thực thi của hàm với nhật ký trace của hệ thống.", "example": "🔍 Trace log: Kiểm tra latency_ms của lời gọi này."}
        ]
    elif input_type == "NUMBER_METRIC":
        socratic_q = f"Bạn đang xem chỉ số số liệu '{trunc}'. Bạn muốn đối soát khía cạnh nào của metric này?"
        chips = [
            {"id": 1, "label": "1. Đơn vị đo và ý nghĩa trong bài Lab?", "explanation": "Xác định đây là thời gian trễ (ms), số token, hay điểm mAP phần trăm.", "example": "📊 Xem tiêu đề cột của bảng số liệu tương ứng."},
            {"id": 2, "label": "2. Tiêu chuẩn nghiệm thu của bài tập?", "explanation": "Đối chiếu với ngưỡng cam kết Quality Bar trong Rubric.", "example": "🎯 Mục tiêu: Kiểm tra xem metric có đạt ngưỡng yêu cầu không."},
            {"id": 3, "label": "3. Cách tối ưu hóa chỉ số này trong code?", "explanation": "Các giải pháp kỹ thuật giúp cải thiện chỉ số này trong vòng lặp tiếp theo.", "example": "⚡ Tối ưu: Giảm batch size hoặc áp dụng caching."}
        ]
    else:
        socratic_q = f"Bạn đang muốn làm rõ khía cạnh nào của đoạn: '{trunc}'?"
        chips = [
            {"id": 1, "label": "1. Nguyên lý hoạt động và bản chất lý thuyết?", "explanation": f"Về mặt lý thuyết, '{trunc}' định hình cách LLM tương tác với môi trường.", "example": "📖 Xem chi tiết trong Slide bài giảng Day 03."},
            {"id": 2, "label": "2. Cách triển khai thực tế trên mã nguồn bài Lab?", "explanation": f"Khi lập trình trong bài Lab, nội dung '{trunc}' nằm trong file src/react_agent.py.", "example": "💻 Kiểm tra cú pháp tại file Starter Repo của lớp."},
            {"id": 3, "label": "3. Các lỗi runtime thường gặp và cách kiểm tra?", "explanation": "Các sự cố thường xoay quanh việc sai lệch schema JSON hoặc timeout API.", "example": "🔍 Đối soát vết lỗi tại file docs/trace_waterfall.json."}
        ]

    trace_entry = {
        "turn_id": int(time.time() * 1000),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": f"Dynamic Classifier Fallback: {trunc} ({input_type})",
        "model": "rule-based-classifier",
        "selected_text": snippet[:45],
        "latency_ms": 10,
        "tokens_used": 0,
        "layer_used": "Dynamic-Fallback",
        "status": "PASS"
    }
    append_trace_log(trace_entry)

    return {
        "matchedKeyword": trunc,
        "directAnswer": f"Đoạn \"{trunc}\" là một thành phần trọng tâm trong bài giảng Day 03, phục vụ việc hoàn thiện Agent.",
        "socraticQuestion": socratic_q,
        "chips": chips,
        "isOutOfScope": False,
        "isLiveAI": False,
        "layerUsed": "Dynamic-Fallback",
        "latencyMs": 10,
        "tokensUsed": 0
    }

# =============================================================================
# 5. MULTI-TURN SOCRATIC FOLLOW-UP (Layer 3 — Vòng 2 Đào Sâu)
# =============================================================================
def resolve_socratic_followup(snippet, selected_chip, mode="mock", api_key=None):
    """Xử lý vòng 2 Socratic khi học viên bấm 'Vẫn chưa rõ ->'."""
    start_time = time.perf_counter()
    chip_label = selected_chip.get("label", "")
    chip_expl = selected_chip.get("explanation", "")
    active_key = api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

    # Thử gọi Live AI nếu bật chế độ Live
    if mode == "gemini" and active_key:
        try:
            endpoint = "https://openrouter.ai/api/v1/chat/completions" if active_key.startswith("sk-or-") else f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={active_key}"
            prompt_sys = (
                "Bạn là Trợ giảng Sư phạm VLearn K4. Học viên đã xem giải thích ban đầu nhưng vẫn chưa hiểu rõ.\n"
                "Nhiệm vụ của bạn là giải thích VÒNG 2 ĐÀO SÂU (Deep Socratic Round):\n"
                "1. Giải thích sâu hơn bản chất cơ chế hoạt động (không lặp lại câu cũ).\n"
                "2. Đưa ra 1 phép ẩn dụ đời thường (Everyday Analogy) cực kỳ trực quan, ai đọc cũng hiểu ngay.\n"
                "3. Nêu 1 bước kiểm chứng thực tế trong code (Action Step).\n"
                "Trả về duy nhất định dạng JSON:\n"
                "{\n"
                '  "deeper_explanation": "Giải thích sâu hơn...",\n'
                '  "everyday_analogy": "Phép ẩn dụ đời thường...",\n'
                '  "action_step": "Bước kiểm chứng cụ thể..."\n'
                "}"
            )
            prompt_usr = f"Khái niệm: '{snippet}'\nĐiểm nghẽn học viên đã chọn: '{chip_label}'\nGiải thích trước đó: '{chip_expl}'\nHọc viên vẫn chưa rõ. Hãy đào sâu tầng 2!"

            if active_key.startswith("sk-or-"):
                payload = {
                    "model": "liquid/lfm-2.5-2.6b:free",
                    "messages": [
                        {"role": "system", "content": prompt_sys},
                        {"role": "user", "content": prompt_usr}
                    ],
                    "temperature": 0.2
                }
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {active_key}"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as res:
                    raw = json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"]
            else:
                payload = {
                    "system_instruction": {"parts": [{"text": prompt_sys}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt_usr}]}],
                    "generationConfig": {"temperature": 0.2, "response_mime_type": "application/json"}
                }
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as res:
                    raw = json.loads(res.read().decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"]

            clean_text = raw.strip()
            if clean_text.startswith("```"):
                clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
                clean_text = re.sub(r"\s*```$", "", clean_text)
            parsed = json.loads(clean_text)

            latency_ms = round((time.perf_counter() - start_time) * 1000)
            trace_entry = {
                "turn_id": int(time.time() * 1000),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "step": f"Multi-Turn Socratic Follow-up (Round 2 Live AI: {chip_label[:30]})",
                "model": "multi-turn-live-ai",
                "selected_text": snippet[:45],
                "latency_ms": latency_ms,
                "tokens_used": 180,
                "layer_used": "MultiTurn-Live",
                "status": "PASS"
            }
            append_trace_log(trace_entry)

            return {
                "deeperExplanation": parsed.get("deeper_explanation", "Bản chất là việc phân tách các pha nhận thức riêng biệt."),
                "everydayAnalogy": parsed.get("everyday_analogy", "Giống như người đầu bếp nếm canh: thử một muỗng -> nhận xét vị -> mới quyết định nêm thêm muối."),
                "actionStep": parsed.get("action_step", "Mở file src/react_agent.py và đặt lệnh print(turn) ngay đầu vòng lặp."),
                "isLiveAI": True,
                "badge": "🤖 Live AI (Vòng 2)"
            }
        except Exception as e:
            print(f"[WARN] Live Follow-up lỗi ({e}), chuyển sang RAG Follow-up.")

    # Multi-turn Curated Knowledge Fallback (Miễn phí, 0ms, 100% ổn định)
    latency_ms = 8
    trace_entry = {
        "turn_id": int(time.time() * 1000),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": f"Multi-Turn Socratic Follow-up (Round 2 RAG KB: {chip_label[:30]})",
        "model": "multi-turn-curated-kb",
        "selected_text": snippet[:45],
        "latency_ms": latency_ms,
        "tokens_used": 0,
        "layer_used": "MultiTurn-RAG",
        "status": "PASS"
    }
    append_trace_log(trace_entry)

    return {
        "deeperExplanation": f"Để hiểu sâu hơn về '{chip_label}': Khi máy tính hoặc LLM xử lý, nó không thể vừa nói vừa suy nghĩ cùng lúc trong một bước toán học duy nhất. Việc tách thành 2 pha riêng biệt giúp đóng băng trạng thái và cho phép hệ thống kiểm tra logic trung gian trước khi quyết định bước tiếp theo.",
        "everydayAnalogy": "Tưởng tượng bạn làm bài thi toán hình: Không ai nhảy bổ vào kết luận ngay. Bạn viết giả thiết ra nháp (Thought) -> Kẻ thêm đường phụ bằng thước kẻ (Action) -> Nhìn hình mới thấy hai tam giác bằng nhau (Observation) -> Lúc đó mới đặt bút viết lời giải chính thức!",
        "actionStep": "Hãy thử mở terminal và gõ lệnh chạy đơn lẻ: python -c 'import src.react_agent; print(dir(src.react_agent))' để nhìn tận mắt các hàm thành phần.",
        "isLiveAI": False,
        "badge": "⚡ VLearn RAG (Vòng 2)"
    }

# =============================================================================
# 6. HTTP REQUEST HANDLER (API & STATIC ASSETS)
# =============================================================================
class VLearnBackendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json({
                "status": "online",
                "service": "VLearn Socratic Tutor Backend",
                "version": "3.5.0",
                "track": "Track A (VLearn Tutor) — Đề A1",
                "architecture": "3-Layer Agent Router (Guardrail -> RAG-lite KB -> Live AI)",
                "kb_concepts_count": len(MOCK_KNOWLEDGE),
                "features": ["Socratic Probing", "Multi-turn Follow-up", "Trace Waterfall Logging"]
            })
        elif self.path == "/api/traces":
            logs = []
            if os.path.exists(TRACE_LOG_PATH):
                try:
                    with open(TRACE_LOG_PATH, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            self._send_json(logs)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/socratic-probe":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body) if body else {}

                snippet = payload.get("snippet", "")
                context_title = payload.get("contextTitle", "DAY 03: Chatbot vs ReAct Agent")
                api_key = payload.get("apiKey", "")
                mode = payload.get("mode", "mock")

                result = resolve_socratic_probe(snippet, context_title, api_key, mode)
                self._send_json({"success": True, "data": result})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)

        elif self.path == "/api/socratic-followup":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body) if body else {}

                snippet = payload.get("snippet", "")
                selected_chip = payload.get("selectedChip", {})
                mode = payload.get("mode", "mock")
                api_key = payload.get("apiKey", "")

                result = resolve_socratic_followup(snippet, selected_chip, mode, api_key)
                self._send_json({"success": True, "data": result})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)

        elif self.path == "/api/resolve-chip":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body) if body else {}

                chip = payload.get("chip", {})
                self._send_json({
                    "success": True,
                    "resolution": {
                        "header": "🎯 Giải thích đúng trọng tâm",
                        "explanation": chip.get("explanation", "Nội dung giải thích chi tiết."),
                        "example": chip.get("example", "💡 Ví dụ minh họa.")
                    }
                })
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)

        else:
            self.send_error(404, "Endpoint not found")

# =============================================================================
# 7. KHỞI CHẠY SERVER
# =============================================================================
def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, VLearnBackendHandler)
    print(f"=================================================================")
    print(f"🚀 VLEARN SOCRATIC TUTOR — BACKEND SERVER RUNNING (v3.5)")
    print(f"=================================================================")
    print(f"🌐 Local URL:      http://localhost:{PORT}")
    print(f"🔌 Socratic API:   POST http://localhost:{PORT}/api/socratic-probe")
    print(f"🔄 Follow-up API:  POST http://localhost:{PORT}/api/socratic-followup")
    print(f"📄 Trace Log:      GET  http://localhost:{PORT}/api/traces")
    print(f"🩺 Health:         GET  http://localhost:{PORT}/api/health")
    print(f"📚 RAG KB Size:    {len(MOCK_KNOWLEDGE)} concepts indexed")
    print(f"=================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dừng server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
