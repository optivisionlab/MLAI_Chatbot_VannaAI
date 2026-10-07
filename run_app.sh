# CẤU HÌNH LLM
# gemini | openrouter | openai
export LLM_PROVIDER="gemini"
# Gemini: gemini-2.5-flash | OpenRouter: google/gemini-2.5-flash, anthropic/claude-sonnet-4.5, ...
export LLM_MODEL="gemini-2.5-flash"
export LLM_KEY="........."
# (tuỳ chọn) ghi đè base URL cho endpoint tương thích OpenAI
# export LLM_BASE_URL=""

# CẤU HÌNH DATABASE
export DB_USER=''
export DB_PASSWORD=''
export DB_DOMAIN='localhost'
export DB_PORT=''
export DB_NAME=''

python app.py