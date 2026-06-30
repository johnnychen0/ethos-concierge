"""
app.py — Streamlit chat UI for the Welcome-Back Concierge, styled in Ethos branding.

Same agent brain as agent.py (imported & reused) — wrapped in a browser chat.
Brand tokens pulled from ethos.com: cypress #05594F, mint #59F8B1, cream #FAF9F5, ink #272727.
Run it:  python3 -m streamlit run app.py
"""
import os
import json
import streamlit as st

# On Streamlit Cloud the API key lives in st.secrets; locally it lives in .env.
# Promote it into the environment BEFORE importing agent (agent builds the Anthropic
# client at import time and reads ANTHROPIC_API_KEY from the environment).
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

import agent  # reuses agent.SYSTEM, agent.TOOLS, agent.DISPATCH, agent.client, etc.

# Ethos's actual wordmark (fill=currentColor so we can tint it cypress green)
ETHOS_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 83 16">'
    '<path d="M11.6369 0.200348V3.32171H3.07416V6.44307H10.5316V9.53622H3.07416V12.6852H11.6369V15.7784H0V0.200348H11.6369Z" fill="currentColor"></path>'
    '<path d="M46.3605 9.53622V6.44307V3.32171V0.200348H43.2863V6.44307H36.3666V3.32171V0.200348H33.2924V15.7784H36.3666V12.6852V9.53622H43.2863V15.7784H46.3605V12.6852V9.53622Z" fill="currentColor"></path>'
    '<path d="M23.9934 15.7784H20.9181V3.32171H15.9298V0.200348H28.9805V3.32171H23.9922V6.44307V15.7784" fill="currentColor"></path>'
    '<path d="M82.5756 2.73281L80.2159 4.63257C80.2159 4.63257 79.106 2.86291 76.3565 2.86291C73.607 2.86291 73.7768 4.58248 73.7768 4.58248C73.7768 4.58248 73.6968 5.40226 74.6266 5.79257C75.5563 6.18231 77.5343 6.49778 78.4963 6.7626C79.2746 6.97675 80.4611 7.26978 81.3857 7.98362C82.3845 8.75504 82.8848 9.57597 82.8848 11.1522C82.8848 12.942 81.9257 13.9218 81.9257 13.9218C81.9257 13.9218 80.4156 16 76.8366 16C73.2576 16 71.4373 14.3714 71.4373 14.3714C71.4373 14.3714 70.4275 13.6317 69.7476 12.6415L72.3129 10.8114C72.3129 10.8114 73.4786 13.0773 76.8228 13.0773C80.1669 13.0773 79.559 11.0284 79.559 11.0284C79.559 11.0284 79.3823 10.2576 78.2344 9.9352C77.1388 9.62778 76.836 9.63411 74.2742 8.99395C71.0694 8.19375 70.477 5.90598 70.4811 4.75922C70.4845 3.73104 70.781 2.39143 72.3751 1.14392C73.9703 -0.104167 76.5488 0.00348611 76.5488 0.00348611C76.5488 0.00348611 80.0368 -0.210668 82.5756 2.73281Z" fill="currentColor"></path>'
    '<path d="M55.203 11.2063C53.028 9.03135 51.6959 5.03092 54.1506 0.801941L53.0033 1.94928C49.8399 5.11267 49.8399 10.242 53.0033 13.4054C56.1673 16.5694 61.296 16.5694 64.46 13.4054L65.6073 12.2581C61.5798 14.5994 57.5719 13.5752 55.203 11.2063Z" fill="currentColor"></path>'
    '<path d="M64.5872 1.82205C62.4261 -0.339649 58.9213 -0.339649 56.7591 1.82205C56.4465 2.13464 55.7959 2.86634 55.5737 3.22672C57.7072 1.91128 60.5379 2.17264 62.387 4.02231C64.2286 5.86393 64.4957 8.6773 63.1993 10.8079L63.5245 10.5609C63.8826 10.3007 64.3299 9.90869 64.5878 9.65078C66.7495 7.48909 66.7495 3.98489 64.5878 1.82262L64.5872 1.82205Z" fill="currentColor"></path>'
    '</svg>'
)

st.set_page_config(page_title="Ethos — Welcome-Back Concierge", page_icon="ethos_mark.png")

# ── Ethos branding (fonts, colors, chat bubbles) ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap');

.stApp { background:#FAF9F5; }
html, body, [data-testid="stChatMessage"], .stMarkdown, p, li, span { font-family:'Inter', -apple-system, sans-serif; color:#272727; }
h1,h2,h3 { font-family:'Fraunces', Georgia, serif !important; color:#05594F; }

/* hide default Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer { visibility:hidden; }
.block-container { padding-top:2.2rem; max-width:780px; }

/* header */
.ethos-header svg { height:26px; color:#05594F; }
.ethos-sub { color:#5b6b66; font-size:0.92rem; margin:6px 0 14px; }

/* chat bubbles */
[data-testid="stChatMessage"] {
  border-radius:14px; padding:12px 16px; margin-bottom:6px;
  border:1px solid #ECEAE2; background:#FFFFFF; box-shadow:0 1px 2px rgba(0,0,0,.03);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background:#05594F; border-color:#05594F; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * { color:#FFFFFF !important; }

/* avatars */
[data-testid="stChatMessageAvatarAssistant"] { background:transparent !important; }
[data-testid="stChatMessageAvatarAssistant"] img { border-radius:50%; }
[data-testid="stChatMessageAvatarUser"] { background:#59F8B1 !important; color:#05594F !important; }

/* chat input + accents */
[data-testid="stChatInput"] { border-radius:12px; border-color:#D9D6CC; }
[data-baseweb="textarea"]:focus-within { border-color:#05594F !important; }
section[data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid #ECEAE2; }
section[data-testid="stSidebar"] h2 { color:#05594F; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="ethos-header">{ETHOS_LOGO}</div>', unsafe_allow_html=True)
st.markdown('<div class="ethos-sub">Welcome-Back Concierge &nbsp;·&nbsp; returning-visitor demo (Sarah) &nbsp;·&nbsp; mocked data, not a real Ethos product</div>', unsafe_allow_html=True)

# ── State ───────────────────────────────────────────────────────────────────
if "api_messages" not in st.session_state:
    st.session_state.api_messages = [
        {"role": "user",
         "content": "[The user just returned to the Ethos website. Begin the conversation.]"}
    ]
    st.session_state.display = []
    st.session_state.tool_log = []

# ── Run the model, executing tools until it returns a text reply ────────────
def get_reply():
    while True:
        resp = agent.client.messages.create(
            model=agent.MODEL, max_tokens=1024,
            system=agent.SYSTEM, tools=agent.TOOLS,
            messages=st.session_state.api_messages,
        )
        st.session_state.api_messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "tool_use":
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    out = agent.run_tool(block.name, block.input)
                    st.session_state.tool_log.append(f"{block.name} → {out}")
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": json.dumps(out)})
            st.session_state.api_messages.append({"role": "user", "content": results})
            continue
        return "\n".join(b.text for b in resp.content if b.type == "text").strip()

# ── First load: agent's opening greeting ────────────────────────────────────
if not st.session_state.display:
    with st.spinner("…"):
        st.session_state.display.append({"role": "assistant", "content": get_reply()})

# ── Render conversation ─────────────────────────────────────────────────────
AVATARS = {"assistant": "ethos_mark.png", "user": None}

def render_md(text):
    # Escape $ so Streamlit doesn't read "$500 ... $56" as a LaTeX math block.
    st.markdown(text.replace("$", "\\$"))

for m in st.session_state.display:
    with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
        render_md(m["content"])

# ── Handle new user message ─────────────────────────────────────────────────
if prompt := st.chat_input("Type your message…"):
    st.session_state.display.append({"role": "user", "content": prompt})
    st.session_state.api_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARS["user"]):
        render_md(prompt)
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("…"):
            reply = get_reply()
        render_md(reply)
    st.session_state.display.append({"role": "assistant", "content": reply})

# ── Sidebar: tool calls (educational) ───────────────────────────────────────
with st.sidebar:
    st.subheader("Behind the scenes")
    st.caption("Tools the agent called this session:")
    for entry in st.session_state.tool_log:
        st.code(entry, language=None)
