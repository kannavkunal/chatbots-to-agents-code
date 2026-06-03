# From Chatbots to Agents — Code Examples

Code examples from the **From Chatbots to Agents** series on building production AI agents.

📖 **Read the series:**
- [Substack: AI Beyond the Demo](https://aibeyondthedemo.substack.com/)
- [Medium: Kunal Kannav](https://medium.com/@kannavkunal)

## What's This?

This repo contains runnable code from the series. Each part has its own folder with working examples you can run locally.

## Quick Start

### Prerequisites

- Python 3.8+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

```bash
# Clone the repo
git clone https://github.com/kannavkunal/chatbots-to-agents-code.git
cd chatbots-to-agents-code

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY='your-key-here'
```

### Run Your First Agent (Part 5)

```bash
cd part5-build-first-agent
python agent.py
```

You should see the agent solve a math problem using its calculator tool:

```
[step 0] calculator({'expression': '2345 * 678'}) -> 1589910
[step 1] calculator({'expression': '24 * 60 * 60'}) -> 86400
[step 2] calculator({'expression': '1589910 - 86400'}) -> 1503510
The answer is 1,503,510.
```

## Series Overview

- **Part 1:** Beyond Chatbots — what makes an agent different
- **Part 2:** The Reasoning Loop — think, act, observe
- **Part 3:** Tools & MCP — giving your agent hands
- **Part 4:** Memory — why RAG isn't enough
- **Part 5:** Build Your First Agent — 50 lines, no framework ← **start here**
- **Part 6:** Evals — how to know it works
- **Part 7:** Guardrails — stopping bad actions
- **Part 8:** Observability — debugging agents
- **Part 9:** Multi-Agent Systems — when to use them
- **Part 10:** The Agentic Stack — where this is heading

## What's in Each Folder

```
part5-build-first-agent/    # 50-line agent with calculator tool
├── agent.py                # The main agent (start here!)
├── agent_explained.py      # Same code with detailed comments
└── README.md               # Part-specific instructions

part6-evals/                # Coming soon
part7-guardrails/           # Coming soon
...
```

## Common Issues

**"No module named 'anthropic'"**
```bash
pip install anthropic
```

**"API key not set"**
```bash
export ANTHROPIC_API_KEY='your-key-here'
# Or on Windows:
set ANTHROPIC_API_KEY=your-key-here
```

**"Tool returned error"**
- Check the calculator syntax (Python expressions only)
- Make sure you're using quotes correctly

## Contributing

Found a bug? Have a suggestion? Open an issue or PR!

## License

MIT — use this code however you want.

## Author

**Kunal Kannav**  
📬 [AI Beyond the Demo](https://aibeyondthedemo.substack.com/) — weekly newsletter on production AI engineering
