"""
agent.py — the agent loop for the Welcome-Back Concierge.

This is the "brain stem": it sends the system prompt + conversation to Claude,
and whenever Claude asks to use a tool, it runs the matching mock function,
hands the result back, and lets Claude continue. That cycle IS the agent.
Run it:  .venv/bin/python agent.py
"""
import os
import json
import anthropic
import mock_tools

# ── 1. Load the API key from .env ──────────────────────────────────────────
def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()
client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY automatically
MODEL = "claude-sonnet-4-6"             # good balance of quality/speed/cost
USER_ID = "sarah_001"

# ── 2. Load the system prompt (strip the python-comment header lines) ──────
def load_system_prompt(path="SYSTEM_PROMPT.md"):
    body = "\n".join(l for l in open(path).read().splitlines()
                     if not l.startswith("# "))
    return body.strip() + f'\n\n[Session] The current user_id is "{USER_ID}".'

SYSTEM = load_system_prompt()

# ── 3. Tool schemas (names MUST match the system prompt) ───────────────────
TOOLS = [
    {"name": "getUserProfile", "description": "Get the user's name, age, state, household details.",
     "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}}}},
    {"name": "getCustomerContext", "description": "Get sentiment, frustration level, and prior conversation topics.",
     "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}}}},
    {"name": "getApplicationStatus", "description": "Get where the user is in the funnel and where they dropped off.",
     "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}}}},
    {"name": "getPlanOptions", "description": "List plan products available in the user's state.",
     "input_schema": {"type": "object", "properties": {"state": {"type": "string"}}, "required": ["state"]}},
    {"name": "getQuote", "description": "Get an illustrative monthly price for a plan.",
     "input_schema": {"type": "object", "properties": {
         "age": {"type": "integer"}, "coverage": {"type": "integer"},
         "term_length": {"type": "integer"}, "plan_type": {"type": "string", "enum": ["term", "whole"]}},
         "required": ["age", "coverage", "term_length", "plan_type"]}},
    {"name": "getPromotions", "description": "Get promotions the user is eligible for.",
     "input_schema": {"type": "object", "properties": {"user_id": {"type": "string"}}}},
    {"name": "submitApplication", "description": "Submit the application. ONLY after the user explicitly says yes.",
     "input_schema": {"type": "object", "properties": {
         "user_id": {"type": "string"}, "plan_type": {"type": "string"},
         "coverage": {"type": "integer"}, "term_length": {"type": "integer"}},
         "required": ["plan_type", "coverage", "term_length"]}},
    {"name": "escalateToHuman", "description": "Hand off to a licensed human with a context summary.",
     "input_schema": {"type": "object", "properties": {"context_package": {"type": "string"}},
                      "required": ["context_package"]}},
]

# ── 4. Map each tool name to its mock function ─────────────────────────────
DISPATCH = {
    "getUserProfile":      lambda a: mock_tools.get_user_profile(a.get("user_id", USER_ID)),
    "getCustomerContext":  lambda a: mock_tools.get_customer_context(a.get("user_id", USER_ID)),
    "getApplicationStatus":lambda a: mock_tools.get_application_status(a.get("user_id", USER_ID)),
    "getPlanOptions":      lambda a: mock_tools.get_plan_options(a["state"]),
    "getQuote":            lambda a: mock_tools.get_quote(a["age"], a["coverage"], a["term_length"], a["plan_type"]),
    "getPromotions":       lambda a: mock_tools.get_promotions(a.get("user_id", USER_ID)),
    "submitApplication":   lambda a: mock_tools.submit_application(a.get("user_id", USER_ID), a["plan_type"], a["coverage"], a["term_length"]),
    "escalateToHuman":     lambda a: mock_tools.escalate_to_human(a["context_package"]),
}

def run_tool(name, args):
    try:
        return DISPATCH[name](args)
    except Exception as e:
        return {"error": str(e)}

# ── 5. The loop ────────────────────────────────────────────────────────────
def main():
    print("\n— Ethos Welcome-Back Concierge (type 'quit' to exit) —")
    messages = [{"role": "user",
                 "content": "[The user just returned to the Ethos website. Begin the conversation.]"}]
    while True:
        # Inner loop: keep going while Claude wants to use tools
        while True:
            resp = client.messages.create(model=MODEL, max_tokens=1024,
                                           system=SYSTEM, tools=TOOLS, messages=messages)
            messages.append({"role": "assistant", "content": resp.content})

            if resp.stop_reason == "tool_use":
                results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        out = run_tool(block.name, block.input)
                        print(f"   · [tool] {block.name} → {out}")
                        results.append({"type": "tool_result", "tool_use_id": block.id,
                                        "content": json.dumps(out)})
                messages.append({"role": "user", "content": results})
                continue
            # No tool needed → print Claude's text and break to ask the user
            for block in resp.content:
                if block.type == "text":
                    print(f"\nConcierge: {block.text.strip()}\n")
            break

        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!"); return
        if user.lower() in ("quit", "exit"):
            print("Goodbye!"); return
        messages.append({"role": "user", "content": user})

if __name__ == "__main__":
    main()
