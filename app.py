"""
app.py — Ethos Welcome-Back Concierge demo.

Two views, routed by ?view= query param:
  • home  — recreation of Ethos's product-recommendation screen, extended with a
            choose-your-own-adventure: "Do it myself" vs "Speak to a concierge".
  • chat  — the AI concierge (agent.py brain), professional chat UI.
  • diy   — stub for the standard self-serve flow (out of scope for the demo).

Run:  python3 -m streamlit run app.py
"""
import os
import json
import streamlit as st

# On Streamlit Cloud the API key lives in st.secrets; locally it lives in .env.
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

import agent  # reuses agent.SYSTEM, agent.TOOLS, agent.run_tool, agent.client

st.set_page_config(page_title="Ethos — Welcome-Back Concierge",
                   page_icon="ethos_mark.png", layout="centered")

# ── Brand assets ────────────────────────────────────────────────────────────
ETHOS_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 83 16" style="height:22px;color:#05594F">'
    '<path d="M11.6369 0.200348V3.32171H3.07416V6.44307H10.5316V9.53622H3.07416V12.6852H11.6369V15.7784H0V0.200348H11.6369Z" fill="currentColor"></path>'
    '<path d="M46.3605 9.53622V6.44307V3.32171V0.200348H43.2863V6.44307H36.3666V3.32171V0.200348H33.2924V15.7784H36.3666V12.6852V9.53622H43.2863V15.7784H46.3605V12.6852V9.53622Z" fill="currentColor"></path>'
    '<path d="M23.9934 15.7784H20.9181V3.32171H15.9298V0.200348H28.9805V3.32171H23.9922V6.44307V15.7784" fill="currentColor"></path>'
    '<path d="M82.5756 2.73281L80.2159 4.63257C80.2159 4.63257 79.106 2.86291 76.3565 2.86291C73.607 2.86291 73.7768 4.58248 73.7768 4.58248C73.7768 4.58248 73.6968 5.40226 74.6266 5.79257C75.5563 6.18231 77.5343 6.49778 78.4963 6.7626C79.2746 6.97675 80.4611 7.26978 81.3857 7.98362C82.3845 8.75504 82.8848 9.57597 82.8848 11.1522C82.8848 12.942 81.9257 13.9218 81.9257 13.9218C81.9257 13.9218 80.4156 16 76.8366 16C73.2576 16 71.4373 14.3714 71.4373 14.3714C71.4373 14.3714 70.4275 13.6317 69.7476 12.6415L72.3129 10.8114C72.3129 10.8114 73.4786 13.0773 76.8228 13.0773C80.1669 13.0773 79.559 11.0284 79.559 11.0284C79.559 11.0284 79.3823 10.2576 78.2344 9.9352C77.1388 9.62778 76.836 9.63411 74.2742 8.99395C71.0694 8.19375 70.477 5.90598 70.4811 4.75922C70.4845 3.73104 70.781 2.39143 72.3751 1.14392C73.9703 -0.104167 76.5488 0.00348611 76.5488 0.00348611C76.5488 0.00348611 80.0368 -0.210668 82.5756 2.73281Z" fill="currentColor"></path>'
    '<path d="M55.203 11.2063C53.028 9.03135 51.6959 5.03092 54.1506 0.801941L53.0033 1.94928C49.8399 5.11267 49.8399 10.242 53.0033 13.4054C56.1673 16.5694 61.296 16.5694 64.46 13.4054L65.6073 12.2581C61.5798 14.5994 57.5719 13.5752 55.203 11.2063Z" fill="currentColor"></path>'
    '<path d="M64.5872 1.82205C62.4261 -0.339649 58.9213 -0.339649 56.7591 1.82205C56.4465 2.13464 55.7959 2.86634 55.5737 3.22672C57.7072 1.91128 60.5379 2.17264 62.387 4.02231C64.2286 5.86393 64.4957 8.6773 63.1993 10.8079L63.5245 10.5609C63.8826 10.3007 64.3299 9.90869 64.5878 9.65078C66.7495 7.48909 66.7495 3.98489 64.5878 1.82262L64.5872 1.82205Z" fill="currentColor"></path>'
    '</svg>'
)

def icon(paths, size=40):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{size}" height="{size}" '
            f'fill="none" stroke="#05594F" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{paths}</svg>')

I_COUPLE = icon('<circle cx="18" cy="16" r="6"/><path d="M6 40c0-7 5-11 12-11s12 4 12 11"/>'
                '<circle cx="33" cy="18" r="5"/><path d="M29 40c.6-5.5 4-8.5 9-8.5 4 0 7 2 8.5 5.5"/>'
                '<path d="M39 4.8c1.2-1.4 3.4-1.4 4.6 0 1.1 1.3.9 3.2-.4 4.4L39 12l-4.2-2.8c-1.3-1.2-1.5-3.1-.4-4.4 1.2-1.4 3.4-1.4 4.6 0z"/>', 44)
I_WALLET = icon('<rect x="7" y="13" width="34" height="24" rx="4"/><path d="M7 21h34"/><circle cx="33" cy="29" r="2"/>')
I_HOUSE  = icon('<path d="M8 22 24 9l16 13"/><path d="M12 20v18h24V20"/><rect x="20" y="28" width="8" height="10"/>')
I_SHIELD = icon('<path d="M24 6l14 5v10c0 9-6 15-14 18-8-3-14-9-14-18V11z"/><path d="M17 23l5 5 9-10"/>')

# ── Global styles ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap');

.stApp { background:#FAF9F5; }
html, body, .stMarkdown, p, li, span, div { font-family:'Inter',-apple-system,sans-serif; }
#MainMenu, header[data-testid="stHeader"], footer { visibility:hidden; height:0; }
.block-container { padding-top:1.6rem; padding-bottom:2.5rem; max-width:800px; }

/* ── shared top bar ── */
.eh-top { display:flex; justify-content:space-between; align-items:center; padding-bottom:14px;
          border-bottom:1px solid #EEEBE2; margin-bottom:22px; }
.eh-help { font-size:.72rem; letter-spacing:.09em; font-weight:600; color:#272727; }
.eh-help span { color:#5b6b66; }

/* ── landing ── */
.eh-back, .eh-back:visited, .eh-back:hover { color:#272727 !important; font-weight:500;
  font-size:.95rem; text-decoration:none !important; }
.eh-h1 { font-family:'Fraunces',Georgia,serif; font-weight:500; font-size:2.35rem; line-height:1.15;
         color:#1E2A28; margin:.4rem 0 1rem; }
.eh-sub { color:#3F4A47; font-size:1.02rem; line-height:1.65; max-width:58ch; }
.eh-label { font-size:.72rem; letter-spacing:.13em; font-weight:700; color:#272727;
            text-transform:uppercase; margin:1.7rem 0 .6rem; }
.eh-protect { background:#EDF7F1; border-radius:12px; padding:26px; text-align:center; }
.eh-protect div { margin-top:6px; font-size:.92rem; color:#1E2A28; font-weight:500; }

.eh-choice { display:flex; gap:16px; margin:1.5rem 0 .4rem; flex-wrap:wrap; }
.eh-card { flex:1 1 270px; background:#FFFFFF; border:1px solid #E7E4DB; border-radius:14px;
           padding:22px; display:flex; flex-direction:column; gap:8px;
           box-shadow:0 1px 3px rgba(0,0,0,.04); }
.eh-card h3 { margin:0; font-size:1.06rem; font-weight:700; color:#1E2A28; }
.eh-card p { margin:0; font-size:.92rem; color:#52605C; line-height:1.55; flex-grow:1; }
.eh-pill { display:inline-block; background:#59F8B1; color:#0B3F36; font-size:.68rem; font-weight:700;
           letter-spacing:.05em; border-radius:99px; padding:3px 10px; margin-bottom:2px; width:fit-content; }
.eh-btn { display:block; text-align:center; padding:14px 18px; border-radius:10px; font-weight:600;
          font-size:.97rem; text-decoration:none !important; margin-top:10px; }
.eh-btn-dark { background:#272727; color:#FFFFFF !important; }
.eh-btn-dark:hover { background:#000; }
.eh-btn-mint { background:#59F8B1; color:#0B3F36 !important; }
.eh-btn-mint:hover { filter:brightness(.94); }
.eh-micro { font-size:.78rem; color:#6B7773; text-align:center; margin-top:8px; }

.eh-payout { margin-top:1.6rem; color:#3F4A47; font-size:1rem; line-height:1.6; }
.eh-benefit { display:flex; gap:16px; align-items:flex-start; margin:18px 0; }
.eh-benefit h4 { margin:0 0 3px; font-size:1rem; font-weight:700; color:#1E2A28; }
.eh-benefit p { margin:0; font-size:.9rem; color:#52605C; line-height:1.55; }
.eh-foot { margin-top:2.4rem; padding-top:1rem; border-top:1px solid #EEEBE2; font-size:.75rem;
           color:#8A948F; text-align:center; }

/* ── chat ── */
.eh-chat-sub { display:flex; align-items:center; gap:8px; color:#5B6B66; font-size:.88rem; margin:2px 0 16px; }
.eh-dot { width:8px; height:8px; border-radius:50%; background:#2BB673; display:inline-block; }
[data-testid="stChatMessage"] { border-radius:16px; padding:14px 18px; margin-bottom:10px;
  border:1px solid #ECEAE2; background:#FFFFFF; box-shadow:0 1px 3px rgba(0,0,0,.04); }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { line-height:1.6; color:#272727; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background:#05594F; border-color:#05594F; flex-direction:row-reverse;
  margin-left:auto; max-width:85%; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * { color:#FFFFFF !important; }
[data-testid="stChatMessageAvatarAssistant"] { background:transparent !important; }
[data-testid="stChatMessageAvatarAssistant"] img { border-radius:50%; }
[data-testid="stChatMessageAvatarUser"] { background:#59F8B1 !important; color:#05594F !important; }
[data-testid="stChatInput"] { border-radius:14px; border:1px solid #D9D6CC; background:#FFFFFF;
  box-shadow:0 2px 8px rgba(0,0,0,.05); }
[data-baseweb="textarea"]:focus-within { border-color:#05594F !important; }
section[data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid #ECEAE2; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color:#05594F; font-family:'Fraunces',serif; }
</style>
""", unsafe_allow_html=True)

TOPBAR = (f'<div class="eh-top"><div>{ETHOS_LOGO}</div>'
          f'<div class="eh-help">NEED HELP? <span>(415) 555-0119</span></div></div>')

view = st.query_params.get("view", "home")

# ════════════════════════════════════════════════════════════════════════════
# VIEW: landing — recommendation screen + choose-your-own-adventure
# ════════════════════════════════════════════════════════════════════════════
if view == "home":
    st.markdown(TOPBAR + f"""
<a class="eh-back" href="./" target="_self">&larr; Back</a>
<div class="eh-h1">Term life insurance sounds like a good&nbsp;fit!</div>
<div class="eh-sub">A Term Life policy helps cover your financial obligations, like debt and
children's tuition, for a set period of time (term) at a fixed monthly price.</div>

<div class="eh-label">Protection for</div>
<div class="eh-protect">{I_COUPLE}<div>Spouse or partner</div></div>

<div class="eh-label">How would you like to continue?</div>
<div class="eh-choice">
  <div class="eh-card">
    <h3>Do it myself</h3>
    <p>Breeze through the online application at your own pace. Most people finish
       in about 10 minutes.</p>
    <a class="eh-btn eh-btn-dark" href="?view=diy" target="_self">Continue my application</a>
  </div>
  <div class="eh-card">
    <span class="eh-pill">NEW</span>
    <h3>Talk it through first</h3>
    <p>Chat with our concierge about fit, price, and coverage — get answers,
       then apply when you're ready. No pressure.</p>
    <a class="eh-btn eh-btn-mint" href="?view=chat" target="_self">Chat with the concierge</a>
  </div>
</div>
<div class="eh-micro">The concierge is an AI assistant &middot; a licensed human is available anytime.</div>

<div class="eh-payout">If you were to die during your policy term length, they would get a
lump-sum payout that can help cover the following things:</div>
<div class="eh-benefit">{I_WALLET}<div><h4>Living expenses</h4>
  <p>Covering everyday costs like groceries and bills helps ensure your family's daily needs are met.</p></div></div>
<div class="eh-benefit">{I_HOUSE}<div><h4>Mortgage coverage</h4>
  <p>Covering large debts like your mortgage ensures your loved ones aren't left with the bill.</p></div></div>
<div class="eh-benefit">{I_SHIELD}<div><h4>Burial costs</h4>
  <p>Funeral costs in the U.S. range from $7,000 to $12,000+.</p></div></div>

<div class="eh-foot">Product demo by Johnny Chen &middot; not affiliated with Ethos &middot; mocked data, not a real product.</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# VIEW: diy — stub for the standard self-serve flow
# ════════════════════════════════════════════════════════════════════════════
elif view == "diy":
    st.markdown(TOPBAR + """
<a class="eh-back" href="?view=home" target="_self">&larr; Back</a>
<div class="eh-h1">Continuing on your own</div>
<div class="eh-sub">From here, Ethos's standard application flow picks up — plan review, final
details, and submission. That existing flow is out of scope for this demo, which focuses on the
new concierge path.</div>
<div class="eh-choice">
  <div class="eh-card">
    <h3>Changed your mind?</h3>
    <p>You can switch to the concierge at any point — it picks up right where the
       application leaves off.</p>
    <a class="eh-btn eh-btn-mint" href="?view=chat" target="_self">Chat with the concierge</a>
  </div>
</div>
<div class="eh-foot">Product demo by Johnny Chen &middot; not affiliated with Ethos &middot; mocked data, not a real product.</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# VIEW: chat — the AI concierge
# ════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(TOPBAR + """
<a class="eh-back" href="?view=home" target="_self">&larr; Back to my recommendation</a>
<div class="eh-chat-sub" style="margin-top:10px">
  <span class="eh-dot"></span> Concierge is online &middot; AI assistant &middot; mocked demo data
</div>
""", unsafe_allow_html=True)

    if "api_messages" not in st.session_state:
        st.session_state.api_messages = [
            {"role": "user",
             "content": "[The user just returned to the Ethos website. Begin the conversation.]"}
        ]
        st.session_state.display = []
        st.session_state.tool_log = []

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

    def render_md(text):
        # Escape $ so Streamlit doesn't read "$500 ... $56" as a LaTeX math block.
        st.markdown(text.replace("$", "\\$"))

    if not st.session_state.display:
        with st.spinner("…"):
            st.session_state.display.append({"role": "assistant", "content": get_reply()})

    AVATARS = {"assistant": "ethos_mark.png", "user": None}
    for m in st.session_state.display:
        with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
            render_md(m["content"])

    if prompt := st.chat_input("Ask about coverage, price, or picking up your application…"):
        st.session_state.display.append({"role": "user", "content": prompt})
        st.session_state.api_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATARS["user"]):
            render_md(prompt)
        with st.chat_message("assistant", avatar=AVATARS["assistant"]):
            with st.spinner("…"):
                reply = get_reply()
            render_md(reply)
        st.session_state.display.append({"role": "assistant", "content": reply})

    with st.sidebar:
        st.subheader("Behind the scenes")
        st.caption("Live tool calls the agent makes:")
        for entry in st.session_state.tool_log:
            st.code(entry, language=None)
        st.divider()
        if st.button("Restart demo"):
            for k in ("api_messages", "display", "tool_log"):
                st.session_state.pop(k, None)
            st.rerun()
