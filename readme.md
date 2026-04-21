# 项目目标：构建一个基于本地模型的英语口语练习工具，适合儿童使用
一个语音->文本->LLM->文本response->语音输出的一个对话系统，基于网页和本地模型，目标是让孩子通过说英语来练习口语，LLM会用简单的英语回复，并且鼓励孩子继续对话。
```
[Browser]
  ↓ (录音)
[Backend API]
  ↓
[ASR 模型（语音识别）]
  ↓
[LLM（对话理解）]
  ↓
[TTS（语音合成）]
  ↓
[返回音频]
```
# 一、先明确 V1 的“完成定义”（避免越做越大）

你的 V1 应该只做到：

* 浏览器点击按钮录音
* 后端返回：

  * 识别文本（给你确认）
  * LLM 回复文本
  * 一段语音（英文）
* 单轮对话（不做上下文）

👉 就是一个 **“点一下 → 说一句 → 听回复”** 的闭环

---

# 二、整体任务拆分（按模块）

## 模块 A：本地模型准备（Day 1）

### 任务 A1：LLM

安装并测试：

* Ollama

建议模型：

* `qwen:7b` 或 `mistral:7b`

验证：

```bash
ollama run qwen:7b
```

---

### 任务 A2：语音识别

安装：

* Whisper
  （建议直接用 faster-whisper）

验证：

```bash
whisper test.wav --language en
```

---

### 任务 A3：语音合成

选一个轻量的：

* Coqui TTS 或 Piper

验证：

```bash
tts --text "Hello" --out_path test.wav
```

---

✅ Day 1 目标：
👉 三个模块都能**单独跑通**

---

# 三、后端开发（Day 2–4）

## 模块 B：FastAPI 服务

你已经很熟这个了，这里是核心接口设计：

---

### 任务 B1：基础接口

```http
POST /chat
Content-Type: multipart/form-data

file: 音频文件
```

返回：

```json
{
  "transcript": "...",
  "response": "...",
  "audio_url": "..."
}
```

---

### 任务 B2：串联 pipeline

流程：

```text
音频文件
  ↓
Whisper → transcript
  ↓
LLM → response text
  ↓
TTS → response.wav
```

---

### 任务 B3：LLM prompt设计（很关键）

你这个场景建议固定 prompt：

```text
You are a friendly English teacher talking to a 10-year-old child.
Use simple words and short sentences.
Encourage the child to continue the conversation.
```

👉 这一步对体验影响非常大

---

### 任务 B4：音频文件管理

简单方案：

* 保存到 `/static/audio/xxx.wav`
* 返回 URL

---

✅ Day 2–4 目标：
👉 curl 能打通整个链路

---

# 四、前端（Day 5–6）

## 模块 C：网页录音

不用复杂框架，直接：

* `MediaRecorder`
* 一个按钮

---

### 任务 C1：录音

```js
navigator.mediaDevices.getUserMedia({ audio: true })
```

---

### 任务 C2：上传音频

```js
fetch('/chat', {
  method: 'POST',
  body: formData
})
```

---

### 任务 C3：播放返回语音

```js
new Audio(audio_url).play()
```

---

### 任务 C4：显示文本

* 用户说的话（ASR结果）
* AI回复

---

✅ Day 5–6 目标：
👉 浏览器能完整对话一轮

---

# 五、优化（Day 7+ 可选）

这是“体验增强”，不是必须：

---

## 模块 D：更像英语老师

### D1：控制难度

在 prompt 加：

* “Use A1 level English”
* 或限制句长

---

### D2：纠错功能（很适合孩子）

让 LLM返回：

```json
{
  "correction": "...",
  "response": "..."
}
```

---

### D3：引导式对话

例如：

* 问问题
* 让孩子回答

---

# 六、整体时间表（压缩版）参考用

| 天数    | 内容                |
| ----- | ----------------- |
| Day 1 | 模型安装 + 单独验证       |
| Day 2 | FastAPI + Whisper |
| Day 3 | 接入 LLM            |
| Day 4 | 接入 TTS（跑通闭环）      |
| Day 5 | 前端录音              |
| Day 6 | 前后端打通             |
| Day 7 | 调整 prompt + 体验优化  |


# 模型下载：
pip install huggingface_hub
pip install huggingface_hub hf_transfer

# 可选：启用更快的下载器
export HF_HUB_ENABLE_HF_TRANSFER=1

# 预下载到 Hugging Face 缓存（默认 ~/.cache/huggingface/hub）
# 注：如果你在公司网络/证书环境里遇到 SSL 校验失败，`hf download` 可能会报错。
# 这里使用一个会注入 macOS 系统证书信任链（truststore）的 Python 脚本来下载。
export HF_ENDPOINT=https://hf-mirror.com
hf download Systran/faster-distil-whisper-small.en --format human