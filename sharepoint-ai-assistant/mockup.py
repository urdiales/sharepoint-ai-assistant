import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Local AI SharePoint Assistant", page_icon="🧠", layout="wide"
)

# --- Session State Setup ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "site_url" not in st.session_state:
    st.session_state.site_url = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_secret" not in st.session_state:
    st.session_state.api_secret = ""
if "doc_preview" not in st.session_state:
    st.session_state.doc_preview = None
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "assistant",
            "msg": "Hi! Ask me anything about your SharePoint documents or lists.",
        }
    ]

# --- Sidebar: Connect / Disconnect ---
st.sidebar.header("🔑 Connect to SharePoint")
if not st.session_state.connected:
    site_url = st.sidebar.text_input(
        "SharePoint Site URL",
        value=st.session_state.site_url
        or "https://yourcompany.sharepoint.com/sites/hr",
    )
    api_key = st.sidebar.text_input(
        "API Key", type="default", value=st.session_state.api_key
    )
    api_secret = st.sidebar.text_input(
        "API Secret", type="password", value=st.session_state.api_secret
    )
    connect_btn = st.sidebar.button("Connect")
    if connect_btn:
        st.session_state.connected = True
        st.session_state.site_url = site_url
        st.session_state.api_key = api_key
        st.session_state.api_secret = api_secret
        st.sidebar.success(f"Connected to {site_url}!")
else:
    st.sidebar.markdown(
        f"**Connected to:** [{st.session_state.site_url}]({st.session_state.site_url})"
    )
    if st.sidebar.button("Disconnect"):
        st.session_state.connected = False
        st.session_state.site_url = ""
        st.session_state.api_key = ""
        st.session_state.api_secret = ""
        st.session_state.doc_preview = None
        st.experimental_rerun()

# --- Sidebar: Tool Status ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Tool Status")
st.sidebar.write(
    "SharePoint: "
    + ("🟢 Connected" if st.session_state.connected else "🔴 Not Connected")
)
st.sidebar.write("Ollama (LLM): 🟢 Ready")
st.sidebar.write("Teams: 🔴 Not Connected")

# --- Sidebar: Document Preview Selector (not the preview itself) ---
st.sidebar.markdown("---")
st.sidebar.header("📄 Document Preview")
doc_list = ["HR_Policy_v3.docx", "Employee_Handbook.pdf", "Onboarding_Checklist.xlsx"]
selected_doc = st.sidebar.selectbox("Recent Documents", doc_list)
if st.sidebar.button("Preview"):
    st.session_state.doc_preview = selected_doc

# --- Main Panel ---
st.title("🧠 Local AI SharePoint Assistant")
st.markdown(
    """
    Type a question or command about your SharePoint site below.
    The LLM will automatically search documents, answer in real time, and provide links/previews.

    You can also use the **Search SharePoint Lists/Libraries** tab for a direct table search.
    """
)

tab1, tab2 = st.tabs(["💬 Chat", "🔍 Search SharePoint Lists/Libraries"])

# -------------------------------
# Tab 1: Chat
# -------------------------------
with tab1:
    st.subheader("💬 Chat")
    for entry in st.session_state.history:
        if entry["role"] == "user":
            st.markdown(f"**You:** {entry['msg']}")
        else:
            st.markdown(f"**Assistant:** {entry['msg']}")

    user_input = st.text_input("Your question", "", key="user_input")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.history.append({"role": "user", "msg": user_input})
            # --- MOCKED: Respond to SharePoint query requests with a fake table preview
            if any(
                q in user_input.lower()
                for q in ["show me", "list", "find", "query", "search"]
            ):
                reply = "Here are the latest items from the 'Onboarding Checklist' SharePoint list:"
                st.session_state.history.append({"role": "assistant", "msg": reply})
                # Mocked SharePoint list data
                data = {
                    "Title": [
                        "New Hire Setup",
                        "Benefits Enrollment",
                        "Security Training",
                    ],
                    "Assigned To": ["Alice", "Bob", "Charlie"],
                    "Status": ["Completed", "Pending", "In Progress"],
                }
                df = pd.DataFrame(data)
                st.session_state.history.append(
                    {"role": "assistant", "msg": df.to_markdown(index=False)}
                )
            else:
                # Standard mock reply
                reply = f"Here's a summary of the latest HR Policy: ... [Open HR_Policy_v3.docx]"
                st.session_state.history.append({"role": "assistant", "msg": reply})
            st.experimental_rerun()

    # --- Main Panel: Document Preview if selected ---
    if st.session_state.doc_preview:
        st.markdown("---")
        st.subheader(f"📄 Preview: {st.session_state.doc_preview}")
        st.write("**File Metadata:** (Mocked example)")
        st.json(
            {
                "Name": st.session_state.doc_preview,
                "Size": "98 KB",
                "Modified": "2024-07-09 12:34",
                "Author": "Jane Doe",
            }
        )
        # Show a "fake" document content preview
        if st.session_state.doc_preview.endswith(".pdf"):
            st.write("**Document content preview:** (PDF viewer here)")
            st.info("PDF preview would appear here.")
        elif st.session_state.doc_preview.endswith(".docx"):
            st.write("**Document content preview:** (DOCX preview here)")
            st.info("DOCX preview would appear here.")
        elif st.session_state.doc_preview.endswith(".xlsx"):
            st.write("**Document content preview:** (XLSX preview here)")
            st.dataframe(
                pd.DataFrame(
                    {
                        "Task": [
                            "Setup Email",
                            "Provide Laptop",
                            "Schedule Orientation",
                        ],
                        "Status": ["Done", "Pending", "Done"],
                    }
                )
            )
        st.download_button(
            label="Download File",
            data="Mock file content",
            file_name=st.session_state.doc_preview,
        )

# -------------------------------
# Tab 2: Search SharePoint Lists/Libraries
# -------------------------------
with tab2:
    st.subheader("🔍 Search SharePoint Lists/Libraries")
    # Mock search form
    list_name = st.text_input("List or Library Name", "Onboarding Checklist")
    col1, col2 = st.columns(2)
    with col1:
        query_text = st.text_input("Search Query", "Status: Pending")
    with col2:
        search_btn = st.button("Search", key="search_list")
    if search_btn:
        st.info(f"Showing results for `{list_name}` where `{query_text}`")
        # Mocked table result
        data = {
            "Title": ["Benefits Enrollment", "Background Check"],
            "Assigned To": ["Bob", "Diana"],
            "Status": ["Pending", "Pending"],
        }
        st.dataframe(pd.DataFrame(data))

# --- Bottom Status Bar ---
st.markdown("---")
cols = st.columns(3)
with cols[0]:
    st.write(
        "🔑 **SharePoint**: "
        + ("🟢 Connected" if st.session_state.connected else "🔴 Not Connected")
    )
with cols[1]:
    st.write("🧠 **LLM**: 🟢 Ready")
with cols[2]:
    st.write("💻 **Running locally**")
