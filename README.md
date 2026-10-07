# MLAI Chatbot VannaAI

Chatbot hỏi đáp dữ liệu bằng ngôn ngữ tự nhiên (Text-to-SQL) trên PostgreSQL, xây dựng với [Vanna 2.0](https://github.com/vanna-ai/vanna). Hỗ trợ nhiều nhà cung cấp LLM: Gemini, OpenRouter, OpenAI (hoặc endpoint tương thích OpenAI).

## Yêu cầu

- Python 3.10+
- PostgreSQL có thể truy cập từ máy chạy ứng dụng
- API key của nhà cung cấp LLM bạn chọn

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## Cấu hình

Cấu hình qua biến môi trường. Cách nhanh nhất là sửa file [run_app.sh](run_app.sh).

### LLM

| Biến | Mô tả | Mặc định |
|---|---|---|
| `LLM_PROVIDER` | `gemini`, `openrouter` hoặc `openai` | `gemini` |
| `LLM_MODEL` | Tên model | Tuỳ provider (xem bảng dưới) |
| `LLM_KEY` | API key | — |
| `LLM_BASE_URL` | (Tuỳ chọn) Ghi đè base URL cho endpoint tương thích OpenAI | — |

Model mặc định khi không đặt `LLM_MODEL`:

| Provider | Model mặc định |
|---|---|
| `gemini` | `gemini-2.5-flash` |
| `openrouter` | `google/gemini-2.5-flash` |
| `openai` | `gpt-4o-mini` |

Ví dụ:

```bash
# Gemini
export LLM_PROVIDER="gemini"
export LLM_MODEL="gemini-2.5-flash"
export LLM_KEY="<google-api-key>"

# OpenRouter (tên model dạng "<hãng>/<model>")
export LLM_PROVIDER="openrouter"
export LLM_MODEL="anthropic/claude-sonnet-4.5"
export LLM_KEY="sk-or-..."

# OpenAI
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"
export LLM_KEY="sk-..."

# Endpoint tương thích OpenAI khác (vLLM, Ollama, ...)
export LLM_PROVIDER="openai"
export LLM_BASE_URL="http://localhost:11434/v1"
export LLM_MODEL="<ten-model>"
export LLM_KEY="<bat-ky-neu-khong-can>"
```

Danh sách model OpenRouter: https://openrouter.ai/models

### Database

| Biến | Mô tả | Mặc định |
|---|---|---|
| `DB_USER` | Tên người dùng | — |
| `DB_PASSWORD` | Mật khẩu | — |
| `DB_DOMAIN` | Host | `localhost` |
| `DB_PORT` | Port | `5432` |
| `DB_NAME` | Tên database | `postgres` |

> Nên dùng tài khoản DB **chỉ đọc** vì chatbot sinh và chạy SQL tự động.

## Chạy ứng dụng

```bash
bash run_app.sh
```

Hoặc tự export các biến môi trường rồi chạy `python app.py`. Truy cập giao diện tại http://localhost:8000.

## Sử dụng

1. Mở http://localhost:8000 và đặt câu hỏi bằng ngôn ngữ tự nhiên, ví dụ: *"Doanh thu theo tháng năm nay là bao nhiêu?"*.
2. Chatbot sinh SQL, chạy trên database và trả về bảng kết quả hoặc biểu đồ.
3. Câu hỏi và SQL đúng được lưu vào bộ nhớ (ChromaDB, thư mục `./chroma_db`) để cải thiện các lần sau.

### Phân quyền

Người dùng được xác định qua cookie `vanna_email` (mặc định `guest@example.com`).

| Nhóm | Điều kiện | Quyền |
|---|---|---|
| `admin` | email là `admin@example.com` | Chạy SQL, vẽ biểu đồ, tìm và lưu bộ nhớ, **lưu cặp câu hỏi–SQL đúng** |
| `user` | các email còn lại | Chạy SQL, vẽ biểu đồ, tìm và lưu ghi chú bộ nhớ |

> Cách xác thực này chỉ phục vụ demo (tin cookie phía client). Hãy thay `SimpleUserResolver` trong [app.py](app.py) trước khi triển khai thật.

## Xử lý sự cố

- **`ModuleNotFoundError`** cho một integration: kiểm tra đã cài đủ extra trong [requirement.txt](requirement.txt).
- **`Unsupported LLM_PROVIDER`**: `LLM_PROVIDER` chỉ nhận `gemini`, `openrouter`, `openai`.
- **Lỗi 401/403 từ LLM**: kiểm tra `LLM_KEY` khớp với provider đã chọn.
- **Không kết nối được DB**: kiểm tra `DB_*` và firewall/`pg_hba.conf`.
