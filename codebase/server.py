#!/usr/bin/env python3
"""
=============================================================================
VLearn Socratic Tutor — Backend Server (Track A1)
Nhóm: Chungtoidongtinh · Phòng: E403 · Lớp: 3A
Đội trưởng: Trần Chí Vĩ (2A202602968)
-----------------------------------------------------------------------------
Kiến trúc:
1. RESTful API Server (Python Standard Library - Zero Dependency)
2. Socratic Scaffolding Engine (Google Gemini 1.5 Flash + Hybrid Mock Fallback)
3. Intent Guardrail Router (HAX G1: Chặn Logistics, URL, Prompt Injection)
4. Trace Waterfall Logger (Rubric R5: Ghi vết latency, tokens, steps)
5. Static Asset File Server (Phục vụ giao diện VLearn Reader & Chat Panel)
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
# 1. KNOWLEDGE BASE & MOCK FALLBACK (Day 03 Curriculum)
# =============================================================================
MOCK_KNOWLEDGE = {
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
    }
}

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

    # Ràng buộc Brevity: Cắt tỉa nhãn chip tự động nếu vượt quá 15 từ
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
        "latencyMs": latency_ms,
        "tokensUsed": tokens_used
    }

def call_openrouter_api(snippet, context_title, api_key, model="google/gemini-2.5-flash"):
    """Gọi OpenRouter API hỗ trợ key sk-or-v1-..."""
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

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=12) as res:
        res_data = json.loads(res.read().decode("utf-8"))

    latency_ms = round((time.perf_counter() - start_time) * 1000)
    raw_text = res_data["choices"][0]["message"]["content"]
    
    try:
        parsed = json.loads(raw_text)
    except Exception:
        clean_text = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE)
        parsed = json.loads(clean_text)

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
        "step": f"Socratic Probing Generation (OpenRouter: {model})",
        "model": model,
        "selected_text": snippet[:45],
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
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
        "latencyMs": latency_ms,
        "tokensUsed": tokens_used
    }

# =============================================================================
# 4. INTENT GUARDRAILS & ROUTER (HAX G1 & Taxonomy 4 Lớp)
# =============================================================================
def check_intent_guardrails(snippet):
    """Kiểm tra các kịch bản biên & rào chắn thẩm quyền."""
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

    return None

def resolve_socratic_probe(snippet, context_title="", api_key=None, mode="mock"):
    """Điều phối quyết định gợi mở giữa Live AI và Mock Fallback."""
    # Bước 1: Kiểm tra Guardrail
    guard = check_intent_guardrails(snippet)
    if guard:
        return guard

    # Lấy key từ payload hoặc từ .env
    active_key = api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

    # Bước 2: Thử gọi Live AI nếu có key và chọn chế độ Live
    if mode == "gemini" and active_key:
        try:
            if active_key.startswith("sk-or-"):
                model = os.environ.get("GEMINI_MODEL", "google/gemini-2.5-flash")
                return call_openrouter_api(snippet, context_title, active_key, model=model)
            else:
                return call_gemini_api(snippet, context_title, active_key)
        except Exception as err:
            print(f"[WARN] Live AI API gặp lỗi ({err}), tự động chuyển về Mock Fallback.")

    # Bước 3: Mock Fallback thông minh
    norm = snippet.lower()
    for key, val in MOCK_KNOWLEDGE.items():
        if key in norm:
            trace_entry = {
                "turn_id": int(time.time() * 1000),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "step": f"Socratic Probing Generation (Mock Mode: {val['keyword']})",
                "model": "rule-based-mock",
                "selected_text": snippet[:45],
                "latency_ms": 15,
                "tokens_used": 0,
                "status": "PASS"
            }
            append_trace_log(trace_entry)
            return {
                "matchedKeyword": val["keyword"],
                "directAnswer": val["direct_answer"],
                "socraticQuestion": val["socratic_question"],
                "chips": val["chips"],
                "isOutOfScope": False,
                "isLiveAI": False,
                "latencyMs": 15,
                "tokensUsed": 0
            }

    # Fallback cho từ khóa bất kỳ
    trunc = snippet[:32] + "..." if len(snippet) > 35 else snippet
    trace_entry = {
        "turn_id": int(time.time() * 1000),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": f"Socratic Probing Generation (Generic Fallback: {trunc})",
        "model": "rule-based-fallback",
        "selected_text": snippet[:45],
        "latency_ms": 10,
        "tokens_used": 0,
        "status": "PASS"
    }
    append_trace_log(trace_entry)

    return {
        "matchedKeyword": trunc,
        "directAnswer": f"Đoạn \"{trunc}\" là một thành phần trọng tâm trong bài giảng Day 03, phục vụ việc hoàn thiện Agent.",
        "socraticQuestion": f"Bạn đang muốn làm rõ khía cạnh nào của đoạn: \"{trunc}\"?",
        "chips": [
            {"id": 1, "label": "1. Nguyên lý hoạt động và bản chất lý thuyết?", "explanation": f"Về mặt lý thuyết, \"{trunc}\" định hình cách LLM tương tác với môi trường.", "example": "📖 Xem chi tiết trong Slide bài giảng Day 03."},
            {"id": 2, "label": "2. Cách triển khai thực tế trên mã nguồn bài Lab?", "explanation": f"Khi lập trình trong bài Lab, nội dung \"{trunc}\" nằm trong file src/react_agent.py.", "example": "💻 Kiểm tra cú pháp tại file Starter Repo của lớp."},
            {"id": 3, "label": "3. Các lỗi runtime thường gặp và cách kiểm tra?", "explanation": "Các sự cố thường xoay quanh việc sai lệch schema JSON hoặc timeout API.", "example": "🔍 Đối soát vết lỗi tại file docs/trace_waterfall.json."}
        ],
        "isOutOfScope": False,
        "isLiveAI": False,
        "latencyMs": 10,
        "tokensUsed": 0
    }

# =============================================================================
# 5. HTTP REQUEST HANDLER (API & STATIC ASSETS)
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
                "version": "3.0.0",
                "track": "Track A (VLearn Tutor) — Đề A1",
                "model_support": ["gemini-1.5-flash", "offline-mock-fallback"]
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
            # Phục vụ file tĩnh (HTML, CSS, JS)
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
# 6. KHỞI CHẠY SERVER
# =============================================================================
def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, VLearnBackendHandler)
    print(f"=================================================================")
    print(f"🚀 VLEARN SOCRATIC TUTOR — BACKEND SERVER RUNNING")
    print(f"=================================================================")
    print(f"🌐 Local URL:  http://localhost:{PORT}")
    print(f"🔌 API Route:  POST http://localhost:{PORT}/api/socratic-probe")
    print(f"📄 Trace Log:  GET  http://localhost:{PORT}/api/traces")
    print(f"🩺 Health:     GET  http://localhost:{PORT}/api/health")
    print(f"=================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
