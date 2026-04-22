# Oral English Test — README V2（实现规格版 / V1闭环）

目标：构建一个适合儿童使用的本地英语口语练习工具（单轮对话），实现 **“点一下录音 → 说一句 → 发给后端 → 看到文字 → 听到英文回复”** 的闭环。

> 约束：V1 **不做多轮上下文**、不做账号系统、不做复杂 UI、不做纠错（纠错属于 V2+）。

---

## 1. V1 完成定义（Definition of Done）

前端：
- 页面只有最小交互：
  - 按钮：开始录音 / 结束录音
  - 按钮：发送
  - 展示：ASR 识别文本、LLM 回复文本
  - 播放：后端返回的音频（可点击播放）

后端：
- 提供 `POST /chat` 接口，接收一段录音文件（multipart/form-data）。
- 同步返回 JSON：
  - `transcript`：识别文本（英文）
  - `response`：LLM 回复文本（简单英语、鼓励继续说）
  - `audio_url`：静态资源 URL，指向可播放的英文 TTS 音频

---

## 2. 总体架构与数据流

```text
[Browser]
  ↓ 录音（MediaRecorder, webm/opus）
[FastAPI Backend]
  ↓ 转码（统一到 16kHz mono WAV）
[faster-whisper]
  ↓ transcript
[Ollama + Qwen 7B]
  ↓ response text
[TTS]
  ↓ response audio（建议 mp3）
[/static/audio/<id>.mp3]
  ↓ audio_url
[Browser 播放]
```

---

## 3. 技术选型（V1 固定）

### 3.1 LLM
- Ollama（本地运行）
- 模型：`qwen` 7B（优先 instruct 版本，例如 `qwen2.5:7b-instruct`，以实际 Ollama 可用模型为准）

接入方式（V1 推荐）：
- **后端使用 Ollama HTTP API** 调用本地服务（默认 `http://127.0.0.1:11434`）。
  - 原因：更容易做超时/重试/并发控制，也避免每次用 CLI 拉起子进程与解析输出。
- **CLI 仅用于手动验证**（例如 Day 1 验证模型可用：`ollama run ...`），不建议作为后端运行时调用方式。

LLM 输出约束（强建议写死在 prompt/参数中）：
- 面向 10 岁儿童：简单词汇、短句
- 鼓励继续对话：每次结尾用一个简单问题引导
- 限制输出长度：建议最多 ~100 tokens（或等效长度限制）
- 温度：建议 0.3–0.7

推荐 System Prompt（V1）：

```text
You are a friendly English teacher talking to a 10-year-old child.
Use simple words and short sentences.
Be encouraging.
Always ask one short follow-up question to keep the conversation going.
Reply in English only.
```

### 3.2 ASR（语音识别）
- `faster-whisper`（Python 库方式接入）
- 模型：首选 `small.en`
  - 目标：低延迟、英文口语场景足够好
- 计算类型：推荐 `int8`（CPU 场景更合适）
- 语言：固定英文（`en`）

升级路径（V1 不默认启用）：
- 如果 `small.en` 误识别明显，再改 `medium.en`（更慢）

### 3.3 TTS（语音合成）
- V1 选择：**Piper**（轻量、易部署）

V1 音频输出格式建议：
- 对前端播放最友好：`mp3`
- 如果 TTS 只方便输出 wav，则后端统一转为 mp3。

---

## 4. 音频 I/O 规格（强制统一，减少踩坑）

### 4.1 前端上传格式（推荐）
- 录音：`MediaRecorder`
- 上传文件 MIME：`audio/webm;codecs=opus`
- 表单字段名：`file`

说明：
- webm/opus 体积小、上传快，是浏览器录音的默认友好格式。
- 不要求前端输出 wav；由后端做转码与标准化。

### 4.2 后端 ASR 前的统一转码
后端收到上传文件后，应统一转码为：
- 容器：WAV
- 编码：PCM s16le
- 采样率：16kHz
- 声道：mono

> 这样可以屏蔽不同浏览器录音差异，提升 ASR 稳定性。

### 4.3 后端返回音频格式（推荐）
- 返回音频文件：`mp3`
- `audio_url`：指向 `/static/audio/<uuid>.mp3`

说明：
- mp3 在 Safari/Chrome/Edge 兼容性更稳。

---

## 5. 后端 API 规格

### 5.1 `POST /chat`
请求：
- `Content-Type: multipart/form-data`
- 字段：
  - `file`: 录音文件（webm/opus 或其他浏览器可录制格式）

响应（成功）：

```json
{
  "transcript": "...",
  "response": "...",
  "audio_url": "/static/audio/<id>.mp3"
}
```

错误响应（建议统一结构，V1 最小化即可）：

```json
{
  "error": {
    "code": "ASR_FAILED | LLM_FAILED | TTS_FAILED | INVALID_AUDIO | TIMEOUT",
    "message": "human readable message"
  }
}
```

### 5.2 静态资源
- 后端需要暴露静态目录：
  - `/static/audio/` 用于存放生成的 TTS 文件

### 5.3 超时与限制（建议写入实现）
- 单次上传大小限制：建议 10–20MB
- 总处理超时：建议 60–120 秒（根据机器表现调整）
- V1 不做队列：请求同步处理，超时报错即可

### 5.4 文件清理策略（V1 简化）
- V1 允许“临时不清理”，但建议至少留一个 TODO：
  - 定期删除超过 N 小时的 `/static/audio/` 文件

---

## 6. 前端行为规格（V1）

- 用户点击“开始录音”：调用 `getUserMedia({ audio: true })`，启动 `MediaRecorder`。
- 用户点击“结束录音”：停止 recorder，生成一个音频 Blob。
- 用户点击“发送”：
  - 构造 `FormData`，字段名为 `file`，上传到 `POST /chat`。
- 收到后端 JSON：
  - 页面展示：`transcript`（用户说的话）
  - 页面展示：`response`（AI 回复）
  - 提供可播放控件：`audio_url`

> V1 不做自动播放也可以（更可控），但要能“点击播放”。

---

## 7. 运行与依赖（建议补齐到实际项目）

本节只定义需要具备的能力，不绑定具体脚本（待实现时补充）：

- Ollama 已安装并可运行，且能 `ollama run <qwen-7b-model>`。
- 后端需要能访问 Ollama HTTP 服务（默认 `http://127.0.0.1:11434`）。
- Python 环境可安装：FastAPI、faster-whisper 及其依赖。
- 系统具备音频转码能力（推荐 ffmpeg）。
- 选择并安装一种 TTS（Piper 或 Coqui）。

---

## 8. 验收用例（V1）

1. 打开页面 → 点击开始录音 → 说一句英文 → 结束录音 → 点击发送。
2. 10–120 秒内（视模型与机器而定）返回：
   - transcript 为英文句子（即使有错也可）
   - response 为简单英语，且末尾有一个短问题
   - audio_url 可访问且能播放出英文语音

---

## 9. 明确不做（防止范围膨胀）

V1 不做：
- 多轮上下文记忆
- 用户系统 / 登录
- 纠错与语法解释（可在 V2+ 做）
- 复杂 UI（卡片、动画、多页面等）
- 训练/微调模型
