# LLM Provider Configuration

This directory contains configuration for your LLM (Large Language Model) provider. The agentic workflow template is **provider-agnostic** and works with any AI assistant.

## Quick Setup

1. **Set your API key:**
   ```bash
   # Linux/macOS (add to ~/.bashrc or ~/.zshrc for persistence):
   export LLM_API_KEY="your-api-key-here"

   # Windows (PowerShell — add to $PROFILE for persistence):
   # $env:LLM_API_KEY = "your-api-key-here"
   ```


## Supported Providers

### Anthropic (Claude)
```json
{
  "provider": { "name": "anthropic" },
  "model": { "name": "claude-sonnet-4-20250514" },
  "api": { "key_env_var": "LLM_API_KEY" }
}
```

**CLI Tool:** [Claude Code](https://github.com/anthropics/claude-code)
```bash
npm install -g @anthropic-ai/claude-code

# Linux/macOS:
export LLM_API_KEY="your-key"
# Windows (PowerShell): $env:LLM_API_KEY = "your-key"

claude
```

### OpenAI (GPT)
```json
{
  "provider": { "name": "openai" },
  "model": { "name": "gpt-4o" },
  "api": { "key_env_var": "LLM_API_KEY" }
}
```

**CLI Tools:**
- [Aider](https://aider.chat): `pip install aider-chat && aider`
- [OpenAI CLI](https://github.com/openai/openai-python): `pip install openai`

### Azure OpenAI
```json
{
  "provider": { "name": "azure" },
  "model": { "name": "gpt-4" },
  "api": {
    "key_env_var": "LLM_API_KEY",
    "base_url": "https://your-resource.openai.azure.com"
  }
}
```

### Google (Gemini)
```json
{
  "provider": { "name": "google" },
  "model": { "name": "gemini-1.5-pro" },
  "api": { "key_env_var": "LLM_API_KEY" }
}
```

### Ollama (Local)
```json
{
  "provider": { "name": "ollama" },
  "model": { "name": "llama3" },
  "api": {
    "key_env_var": null,
    "base_url": "http://localhost:11434"
  }
}
```

**Setup:**
```bash
# Install Ollama
# Linux/macOS:
curl -fsSL https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.ai/download

# Pull a model (all platforms):
ollama pull llama3

# Use with Aider (all platforms):
aider --model ollama/llama3
```

### Custom Provider
```json
{
  "provider": { "name": "custom" },
  "model": { "name": "your-model" },
  "api": {
    "key_env_var": "LLM_API_KEY",
    "base_url": "https://your-api-endpoint.com/v1"
  }
}
```

## Compatible AI Coding Tools

The agentic workflow works with various AI coding assistants:

| Tool | Providers | Install |
|------|-----------|---------|
| [Claude Code](https://github.com/anthropics/claude-code) | Anthropic | `npm i -g @anthropic-ai/claude-code` |
| [GitHub Copilot](https://github.com/features/copilot) | GitHub/OpenAI | VS Code extension |
| [Cursor](https://cursor.sh) | OpenAI, Anthropic | Download from website |
| [Windsurf](https://codeium.com/windsurf) | Multiple | Download from website |
| [Continue](https://continue.dev) | Multiple | VS Code extension |
| [Aider](https://aider.chat) | OpenAI, Anthropic, Ollama, Azure | `pip install aider-chat` |
| [Cody](https://sourcegraph.com/cody) | Multiple | VS Code extension |

## Environment Variables

Store API keys as environment variables, never in files:


> **Note:** If you are only using an AI tool (Claude CLI, Cursor, Copilot, etc.), you do **not** need to set any 'extra' provider specific environment variables for using this software. Just follow your tool’s own setup instructions for authentication. The llm api key environment variable below is only required if you want to use this repo's automation/scripts (such as automated PR reviews or direct API calls from scripts).


**Linux/macOS** (add to `~/.bashrc` or `~/.zshrc`):
```bash
export LLM_API_KEY="your-api-key-here"   # Only LLM_API_KEY is required for this template's automation/scripts
```

**Windows (PowerShell)** (add to `$PROFILE` for persistence):
```powershell
$env:LLM_API_KEY = "your-api-key-here"   # Only LLM_API_KEY is required for this template's automation/scripts
```

**Windows (CMD):**
```cmd
set LLM_API_KEY=your-api-key-here   # Only LLM_API_KEY is required for this repo's automation/scripts
```

## Security

**Never commit API keys!** The following are gitignored:
- `.env` files
- `*_key`, `*_token`, `*_secret` files
- `.api_key`, `.llm_key`

## Using the Workflow

Once configured, interact with the AI assistant:

1. **Start your AI tool** (e.g., `claude`, `aider`, `cursor`)
2. **Describe your task** - the agent system will activate
3. **The AI will:**
   - Adopt the appropriate agent role
   - Follow the multi-agent workflow
   - Create PRs for review

## Adapting Agent Prompts

The agent definitions in `ai-assistants/agents/` work with any LLM. If your tool uses different prompt formats:

1. Copy the agent files to your tool's format
2. Maintain the same role definitions and responsibilities
3. Keep the workflow and handoff patterns

## Troubleshooting

**API Key not found:**
```bash
# Linux/macOS — verify your key is set:
echo $LLM_API_KEY
source ~/.bashrc   # Reload profile if recently added

# Windows (PowerShell):
# echo $env:LLM_API_KEY
# . $PROFILE   # Reload profile if recently added
```

**Model not available:**
- Check your API subscription tier
- Verify model name spelling
- Some models require waitlist access

**Rate limits:**
- Add delays between requests
- Use a smaller model for drafts
- Check provider rate limit documentation
