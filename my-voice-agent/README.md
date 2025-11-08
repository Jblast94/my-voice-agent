---
title: My Voice Agent
emoji: 🏢
colorFrom: green
colorTo: pink
sdk: docker
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: mit
---
# 🤖 Personal AI Assistant

A sophisticated voice-enabled conversational AI agent that learns about you over time and helps with various tasks.

## ✨ Features

- 💬 **Natural Conversation** - Engage in fluid, context-aware conversations
- 🧠 **Automatic Learning** - Learns your interests, preferences, and communication style
- 🎤 **Voice I/O** - Speak and hear responses (Whisper + ChatTTS)
- 🗄️ **Persistent Memory** - All conversations stored in Supabase
- 🔧 **Tool Integration** - Web search, code execution, workflow automation
- 📊 **Memory Dashboard** - See what the AI has learned about you
- 🔄 **Streaming Responses** - Real-time text generation
- 🎯 **Single User** - Private, secure, just for you

## 🏗️ Architecture

```
User Input (Voice/Text)
    ↓
Gradio Interface (app.py)
    ↓
LLM Handler (OpenRouter/Anthropic/HF)
    ↓
Character Learner (extracts traits)
    ↓
Memory Manager (Supabase)
    ↓
Tool Executor (if needed)
    ↓
Response Generation (streaming)
    ↓
Audio Handler (ChatTTS)
    ↓
Save to Database
```

## 📋 Prerequisites

### Required
- **Hugging Face Account** - For hosting the Space
- **Supabase Project** - For database storage
- **OpenRouter API Key** - For LLM access (free models available!)

### Optional (for Voice)
- **OpenAI API Key** OR **HuggingFace Token** - For Whisper (speech-to-text)
- **ChatTTS RunPod Endpoint** - For text-to-speech

### Optional (for Tools)
- **Tavily API Key** - For web search
- **N8N Webhook URL** - For workflow automation

## 🚀 Deployment Guide

### Step 1: Set Up Supabase (10 minutes)

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to **SQL Editor**
4. Copy the contents of `supabase_schema.sql` and paste into the editor
5. Click **Run** to create all tables
6. Go to **Settings** → **API** and copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **service_role key** (NOT the anon key!)

### Step 2: Get API Keys (10 minutes)

#### Required Keys:

1. **OpenRouter** (FREE models available!)
   - Go to [openrouter.ai](https://openrouter.ai)
   - Sign up and create an API key
   - Free models available: `google/gemini-2.0-flash-exp:free`

2. **Hugging Face Token**
   - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a token with **read** and **write** permissions

#### Optional Keys (for full features):

3. **OpenAI** (for Whisper STT)
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create API key

4. **ChatTTS RunPod** (for TTS)
   - Deploy ChatTTS on RunPod
   - Get endpoint URL and API key

5. **Tavily** (for web search)
   - Go to [tavily.com](https://tavily.com)
   - Get API key

### Step 3: Create Hugging Face Space (5 minutes)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Configure:
   - **Name**: Choose a name (e.g., `my-voice-agent`)
   - **SDK**: Gradio
   - **Visibility**: Public or Private
3. Click **Create Space**

### Step 4: Upload Files

Upload all these files to your Space:
- `app.py`
- `llm_handler.py`
- `memory_manager.py`
- `tool_executor.py`
- `character_learner.py`
- `audio_handler.py`
- `requirements.txt`
- `README.md` (this file)

### Step 5: Configure Secrets

In your Space's **Settings** → **Variables and Secrets**, add:

#### Required:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENROUTER_API_KEY=sk-or-v1-xxxxx
PREFERRED_MODEL=google/gemini-2.0-flash-exp:free
USER_NAME=YourName
```

#### Optional (for voice):
```bash
OPENAI_API_KEY=sk-xxxxx
# OR
HUGGINGFACE_TOKEN=hf_xxxxx

CHATTTS_ENDPOINT=https://api.runpod.ai/v2/xxxxx/
CHATTTS_API_KEY=xxxxx
```

#### Optional (for tools):
```bash
TAVILY_API_KEY=tvly-xxxxx
N8N_WEBHOOK_URL=https://your-n8n.app/webhook/xxxxx
```

#### Optional (custom):
```bash
SYSTEM_PROMPT=You are a helpful assistant...
```

### Step 6: Launch! 🎉

1. Your Space will automatically build and deploy
2. Wait for the build to complete (~2-3 minutes)
3. Click on your Space URL to start using it!

## 💬 Using the Agent

### Text Chat
1. Type your message in the input box
2. Click "Send" or press Enter
3. Watch the streaming response appear

### Voice Chat
1. Click the microphone icon to record
2. Speak your message
3. Click "Send with Voice" for audio response

### Memory Dashboard
- Click "Refresh Stats" to see what the AI has learned
- View your interests, preferences, and conversation count

## 🧠 How Learning Works

The agent automatically learns from every conversation:

### Interests
Detects phrases like:
- "I love..."
- "I'm interested in..."
- "My hobby is..."

### Background
Detects phrases like:
- "I work as a..."
- "I'm a software engineer..."
- "My profession is..."

### Preferences
Detects phrases like:
- "I prefer..."
- "I usually..."
- "I don't like..."

### Communication Style
Analyzes:
- Message length (concise vs. detailed)
- Tone (casual vs. formal)
- Questions vs. statements

All learned information is stored and used to personalize future responses!

## 🔧 Tool Capabilities

### Web Search
Triggered by: "search", "find", "look up", "what is", "who is"
```
You: "What's the latest in AI?"
Agent: [Searches web] → Provides current information
```

### Code Execution
Triggered by: "calculate", "run", "execute code"
```
You: "Calculate fibonacci sequence to 100"
Agent: [Runs Python] → Shows results
```

### N8N Workflows
Triggered by: "add task", "trigger workflow"
```
You: "Add a reminder to my board"
Agent: [Triggers N8N] → Confirms automation
```

## 💰 Cost Breakdown

### Free Tier (Text-Only)
- **Supabase**: FREE (500MB database)
- **OpenRouter**: FREE models available
- **HuggingFace Space**: FREE (CPU tier)
- **Total**: $0/month ✅

### With Voice
- **RunPod**: ~$0.10-0.50/hour (only when running)
- **OpenAI Whisper**: ~$0.006/minute
- **Total**: Pay as you go

### Recommended Starting Point
Start with **free text-only** setup, then add voice features if needed!

## 🔒 Security & Privacy

- All data stored in your personal Supabase project
- Service role key kept secure in Space secrets
- Single-user system - no data sharing
- Full control over your data
- Can export or delete anytime

## 🛠️ Troubleshooting

### "No LLM provider configured"
- Make sure `OPENROUTER_API_KEY` is set in Space secrets
- Check that the key is valid

### "Supabase connection failed"
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
- Make sure you ran the SQL schema in Supabase
- Check that your Supabase project is active

### Voice not working
- For STT: Add either `OPENAI_API_KEY` or `HUGGINGFACE_TOKEN`
- For TTS: Add both `CHATTTS_ENDPOINT` and `CHATTTS_API_KEY`
- Check that your RunPod endpoint is active

### "Model is loading"
- HuggingFace models may need to warm up (30-60 seconds)
- Try again after a moment

### Tools not working
- Web search: Add `TAVILY_API_KEY`
- N8N: Add `N8N_WEBHOOK_URL`
- Check that API keys are valid

## 📊 Database Schema

The agent uses 3 main tables:

### `user_profiles`
- Stores learned traits and preferences
- One record per user

### `conversations`
- Stores all conversation messages
- Timestamped with role (user/assistant)

### `learned_facts`
- Stores specific learned facts
- Categorized with confidence scores

## 🔄 Upgrading

To upgrade your agent:
1. Pull latest files from repository
2. Update files in your Space
3. Space will automatically rebuild
4. Database schema is backward compatible

## 🤝 Contributing

This is a personal AI assistant designed for single-user use. Feel free to:
- Fork and customize for your needs
- Add new tool integrations
- Improve learning algorithms
- Share your improvements!

## 📝 License

MIT License - feel free to use and modify!

## 🎯 Next Steps

Now that your agent is deployed:

1. **Chat and let it learn** - The more you talk, the smarter it gets!
2. **Check memory stats** - See what it's learning about you
3. **Try voice features** - If configured, speak to your agent
4. **Use tools** - Ask it to search, calculate, or automate
5. **Customize** - Adjust the system prompt to match your needs

**Enjoy your personal AI assistant!** 🎉

## 📞 Support

- Check Supabase dashboard for database issues
- Check Space logs for runtime errors
- Verify all API keys are correctly set
- Join HuggingFace Discord for Space support

---

Built with ❤️ using Gradio, Supabase, and OpenRouter
Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference