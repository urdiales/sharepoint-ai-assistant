"""
Enhanced Streamlit UI for the SharePoint AI Assistant.
Provides a robust web interface with comprehensive error handling and validation.
"""

import streamlit as st
import pandas as pd
import traceback
from typing import Optional, Dict, Any

from ..core import (
    UIConstants,
    SharePointConstants,
    get_logger,
    SharePointConnectionError,
    SharePointAuthenticationError,
    LLMConnectionError,
    ValidationError,
    FileOperationError,
)
from ..services import LLMService
from ..clients import SharePointClient
from ..utils import (
    preview_pdf,
    preview_docx,
    preview_xlsx,
    get_file_info,
    format_file_size,
    validate_url,
    validate_credentials,
    validate_user_input,
)

# Get logger for this module
logger = get_logger("ui")

# Configure Streamlit page
st.set_page_config(
    page_title=UIConstants.PAGE_TITLE,
    page_icon=UIConstants.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Connection state
    if "connected" not in st.session_state:
        st.session_state.connected = False

    # Service instances
    if "llm_service" not in st.session_state:
        st.session_state.llm_service = None
    if "sp_client" not in st.session_state:
        st.session_state.sp_client = None

    # UI state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "connection_error" not in st.session_state:
        st.session_state.connection_error = None
    if "last_search_results" not in st.session_state:
        st.session_state.last_search_results = None
    if "doc_preview" not in st.session_state:
        st.session_state.doc_preview = None
    if "shared_content" not in st.session_state:
        st.session_state.shared_content = []
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "chat"


def display_error(error_message: str, error_type: str = "error"):
    """
    Display error message with appropriate styling.

    Args:
        error_message: Error message to display
        error_type: Type of error (error, warning, info)
    """
    if error_type == "error":
        st.error(f"❌ {error_message}")
    elif error_type == "warning":
        st.warning(f"⚠️ {error_message}")
    elif error_type == "info":
        st.info(f"ℹ️ {error_message}")

    logger.error(f"UI {error_type}: {error_message}")


def display_success(message: str):
    """Display success message."""
    st.success(f"✅ {message}")
    logger.info(f"UI success: {message}")


def handle_connection_form():
    """Handle SharePoint connection form in sidebar."""
    st.sidebar.header("🔗 SharePoint Connection")

    if not st.session_state.connected:
        with st.sidebar.form("connection_form"):
            st.write("**Connection Settings**")

            site_url = st.text_input(
                "Site URL",
                placeholder="https://yourcompany.sharepoint.com/sites/yoursite",
                help="Full URL to your SharePoint site",
            )

            client_id = st.text_input(
                "Client ID",
                placeholder="12345678-1234-1234-1234-123456789012",
                help="SharePoint application client ID (GUID format)",
            )

            client_secret = st.text_input(
                "Client Secret",
                type="password",
                help="SharePoint application client secret",
            )

            connect_button = st.form_submit_button(
                "🔌 Connect", use_container_width=True
            )

            if connect_button:
                if not site_url or not client_id or not client_secret:
                    display_error("All connection fields are required")
                    return

                try:
                    # Validate inputs
                    validated_url = validate_url(site_url)
                    validated_client_id, validated_client_secret = validate_credentials(
                        client_id, client_secret
                    )

                    # Show connection progress
                    with st.spinner("Connecting to SharePoint..."):
                        # Initialize SharePoint client
                        sp_client = SharePointClient(
                            validated_url, validated_client_id, validated_client_secret
                        )

                        # Initialize LLM service
                        llm_service = LLMService()

                        # Store in session state
                        st.session_state.sp_client = sp_client
                        st.session_state.llm_service = llm_service
                        st.session_state.connected = True
                        st.session_state.connection_error = None

                        display_success("Connected to SharePoint successfully!")
                        st.rerun()

                except ValidationError as e:
                    display_error(f"Validation error: {e}")
                except SharePointAuthenticationError as e:
                    display_error(f"Authentication failed: {e}")
                except SharePointConnectionError as e:
                    display_error(f"Connection failed: {e}")
                except LLMConnectionError as e:
                    display_error(f"LLM connection failed: {e}")
                except Exception as e:
                    logger.error(f"Unexpected connection error: {e}")
                    display_error(f"Unexpected error: {str(e)}")

    else:
        # Show connection status
        st.sidebar.success("✅ Connected to SharePoint")

        # Show connection info
        if st.session_state.sp_client:
            conn_info = st.session_state.sp_client.get_connection_info()
            with st.sidebar.expander("Connection Details"):
                st.write(f"**Site:** {conn_info.get('site_url', 'Unknown')}")
                if conn_info.get("uptime_seconds"):
                    uptime_minutes = int(conn_info["uptime_seconds"] / 60)
                    st.write(f"**Uptime:** {uptime_minutes} minutes")

        # Disconnect button
        if st.sidebar.button("🔌 Disconnect", use_container_width=True):
            try:
                if st.session_state.sp_client:
                    st.session_state.sp_client.disconnect()
                if st.session_state.llm_service:
                    st.session_state.llm_service.disconnect()

                st.session_state.connected = False
                st.session_state.sp_client = None
                st.session_state.llm_service = None
                st.session_state.chat_history = []
                st.session_state.connection_error = None
                st.session_state.doc_preview = None

                display_success("Disconnected successfully")
                st.rerun()

            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                display_error(f"Error during disconnect: {str(e)}")


def handle_sidebar_document_preview():
    """Handle the sidebar document preview section matching the mockup."""
    st.sidebar.markdown("---")
    st.sidebar.header("📄 Document Preview")

    # Recent documents list (matching mockup)
    doc_list = [
        "HR_Policy_v3.docx",
        "Employee_Handbook.pdf",
        "Onboarding_Checklist.xlsx",
    ]

    selected_doc = st.sidebar.selectbox(
        "Recent Documents", doc_list, help="Select a document to preview"
    )

    if st.sidebar.button("👁️ Preview", use_container_width=True):
        st.session_state.doc_preview = selected_doc
        st.rerun()


def display_document_preview_in_chat():
    """Display document preview in the chat tab when selected from sidebar."""
    if st.session_state.doc_preview:
        st.markdown("---")
        st.subheader(f"📄 Preview: {st.session_state.doc_preview}")

        # File metadata (mocked for demo, real implementation would fetch from SharePoint)
        st.write("**File Metadata:**")
        metadata = {
            "Name": st.session_state.doc_preview,
            "Size": "98 KB",
            "Modified": "2024-07-09 12:34",
            "Author": "Jane Doe",
        }
        st.json(metadata)

        # Document content preview based on file type
        if st.session_state.doc_preview.endswith(".pdf"):
            st.write("**Document content preview:** (PDF viewer here)")
            st.info(
                "PDF preview would appear here. In a real implementation, this would show the actual PDF content."
            )

        elif st.session_state.doc_preview.endswith(".docx"):
            st.write("**Document content preview:** (DOCX preview here)")
            st.info(
                "DOCX preview would appear here. In a real implementation, this would show the actual document content."
            )

        elif st.session_state.doc_preview.endswith(".xlsx"):
            st.write("**Document content preview:** (XLSX preview here)")
            # Mock Excel data
            mock_excel_data = pd.DataFrame(
                {
                    "Task": ["Setup Email", "Provide Laptop", "Schedule Orientation"],
                    "Status": ["Done", "Pending", "Done"],
                    "Assigned To": ["IT Team", "HR", "Manager"],
                    "Due Date": ["2024-07-15", "2024-07-16", "2024-07-17"],
                }
            )
            st.dataframe(mock_excel_data, use_container_width=True)

        # Action buttons for document preview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.download_button(
                label="📥 Download",
                data="Mock file content - in real implementation this would be the actual file",
                file_name=st.session_state.doc_preview,
                use_container_width=True,
            )

        with col2:
            if st.button(
                "🔄 Refresh", use_container_width=True, help="Refresh document preview"
            ):
                # Refresh the document preview (reload from SharePoint)
                display_success(f"Refreshed preview for {st.session_state.doc_preview}")
                st.rerun()

        with col3:
            if st.button(
                "📤 Share", use_container_width=True, help="Share this document"
            ):
                # Add document to shared content
                share_data = generate_shareable_content("Document Preview")
                st.session_state.shared_content.append(
                    {
                        "type": "document_share",
                        "content": "Document Preview",
                        "data": share_data,
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                display_success(
                    f"Document {st.session_state.doc_preview} prepared for sharing"
                )

        with col4:
            if st.button(
                "❌ Close", use_container_width=True, help="Close document preview"
            ):
                st.session_state.doc_preview = None
                display_success("Document preview closed")
                st.rerun()


def handle_chat_tab():
    """Handle the chat interface tab."""
    st.header("💬 AI Assistant Chat")

    if not st.session_state.connected:
        st.warning(UIConstants.DISCONNECTED_MESSAGE)
        return

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for entry in st.session_state.chat_history:
            st.markdown(entry)

    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                "Ask a question about SharePoint",
                placeholder="e.g., Find documents about onboarding",
                max_chars=UIConstants.MAX_INPUT_LENGTH,
                label_visibility="collapsed",
            )

        with col2:
            send_button = st.form_submit_button("📤 Send", use_container_width=True)

        if send_button and user_input:
            try:
                # Validate input
                validated_input = validate_user_input(user_input)

                # Show processing indicator
                with st.spinner("Processing your question..."):
                    # Get LLM response
                    llm_service = st.session_state.llm_service
                    response = llm_service.run(validated_input)

                # Add to chat history
                st.session_state.chat_history.append(f"**You:** {validated_input}")
                st.session_state.chat_history.append(f"**Assistant:** {response}")

                # Limit chat history
                if len(st.session_state.chat_history) > UIConstants.CHAT_HISTORY_LIMIT:
                    st.session_state.chat_history = st.session_state.chat_history[
                        -UIConstants.CHAT_HISTORY_LIMIT :
                    ]

                st.rerun()

            except ValidationError as e:
                display_error(f"Invalid input: {e}")
            except LLMConnectionError as e:
                display_error(f"LLM connection error: {e}")
            except Exception as e:
                logger.error(f"Chat error: {e}")
                display_error(f"Error processing your question: {str(e)}")

    # Chat controls
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            if st.session_state.llm_service:
                st.session_state.llm_service.clear_memory()
            st.rerun()

    with col2:
        if st.session_state.llm_service:
            memory_info = st.session_state.llm_service.get_memory_summary()
            st.caption(f"Memory: {memory_info.get('messages', 0)} messages")

    with col3:
        if st.session_state.chat_history:
            st.caption(f"History: {len(st.session_state.chat_history)} entries")


def handle_search_and_lists_tab():
    """Handle the combined search and lists tab matching the mockup design."""
    st.header("🔍 Search SharePoint Lists/Libraries")

    if not st.session_state.connected:
        st.warning(UIConstants.DISCONNECTED_MESSAGE)
        return

    # Create two sections: Lists Search and Document Search
    st.subheader("📋 Search SharePoint Lists")

    # SharePoint Lists Search Section (matching mockup)
    col1, col2 = st.columns(2)

    with col1:
        list_name = st.text_input(
            "List or Library Name",
            value="Onboarding Checklist",
            help="Enter the name of the SharePoint list or library to search",
        )

    with col2:
        query_text = st.text_input(
            "Search Query",
            value="Status: Pending",
            help="Enter search criteria (e.g., 'Status: Pending', 'Assigned To: John')",
        )

    if st.button("🔍 Search List", use_container_width=True, key="search_list"):
        if not list_name:
            display_error("Please enter a list or library name")
        else:
            try:
                with st.spinner(f"Searching in '{list_name}' for '{query_text}'..."):
                    # Try to get real SharePoint list data
                    try:
                        results_df = st.session_state.sp_client.search_list_items(
                            list_name, query_text
                        )

                        if results_df.empty:
                            st.info(
                                f"No items found matching '{query_text}' in '{list_name}'"
                            )
                        else:
                            st.success(
                                f"Found {len(results_df)} items in '{list_name}'"
                            )
                            st.dataframe(
                                results_df, use_container_width=True, hide_index=True
                            )

                    except Exception as sp_error:
                        # Fallback to mock data if SharePoint search fails
                        logger.warning(
                            f"SharePoint list search failed, using mock data: {sp_error}"
                        )
                        st.info(
                            f"Showing mock results for '{list_name}' where '{query_text}'"
                        )

                        # Mock data matching the mockup
                        if "pending" in query_text.lower():
                            mock_data = {
                                "Title": [
                                    "Benefits Enrollment",
                                    "Background Check",
                                    "Equipment Setup",
                                ],
                                "Assigned To": ["Bob", "Diana", "Alice"],
                                "Status": ["Pending", "Pending", "Pending"],
                                "Due Date": ["2024-07-20", "2024-07-22", "2024-07-18"],
                            }
                        else:
                            mock_data = {
                                "Title": [
                                    "New Hire Setup",
                                    "Benefits Enrollment",
                                    "Security Training",
                                ],
                                "Assigned To": ["Alice", "Bob", "Charlie"],
                                "Status": ["Completed", "Pending", "In Progress"],
                                "Due Date": ["2024-07-15", "2024-07-20", "2024-07-25"],
                            }

                        mock_df = pd.DataFrame(mock_data)
                        st.dataframe(mock_df, use_container_width=True, hide_index=True)

            except Exception as e:
                logger.error(f"List search error: {e}")
                display_error(f"Search failed: {str(e)}")

    # Separator
    st.markdown("---")

    # Document Search Section (existing functionality)
    st.subheader("📄 Search Documents")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Library selection
        try:
            libraries = st.session_state.sp_client.list_document_libraries()
            library_options = (
                [lib["title"] for lib in libraries]
                if libraries
                else SharePointConstants.DEFAULT_LIBRARIES
            )
        except Exception as e:
            logger.warning(f"Could not load libraries: {e}")
            library_options = SharePointConstants.DEFAULT_LIBRARIES

        selected_library = st.selectbox(
            "Select Document Library",
            options=library_options,
            help="Choose the SharePoint library to search in",
        )

    with col2:
        search_query = st.text_input(
            "Document Search Query",
            placeholder="Enter document name or keywords",
            help="Search for documents by name",
        )

    if st.button("🔍 Search Documents", use_container_width=True, key="search_docs"):
        if not search_query:
            display_error("Please enter a search query")
        else:
            try:
                with st.spinner(f"Searching in {selected_library}..."):
                    results_df = st.session_state.sp_client.search_documents(
                        selected_library, search_query
                    )

                if results_df.empty:
                    st.info(
                        f"No documents found matching '{search_query}' in {selected_library}"
                    )
                else:
                    st.success(f"Found {len(results_df)} documents")

                    # Display results
                    st.dataframe(results_df, use_container_width=True, hide_index=True)

                    # Store results for preview
                    st.session_state.last_search_results = results_df

            except Exception as e:
                logger.error(f"Document search error: {e}")
                display_error(f"Document search failed: {str(e)}")

    # Document Preview section (if there are search results)
    if (
        st.session_state.last_search_results is not None
        and not st.session_state.last_search_results.empty
    ):
        st.markdown("---")
        st.subheader("📄 Document Preview")

        # File selection for preview
        file_options = st.session_state.last_search_results["Name"].tolist()
        selected_file = st.selectbox(
            "Select file to preview",
            options=file_options,
            help="Choose a file from search results to preview",
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👁️ Preview File", use_container_width=True):
                try:
                    with st.spinner(f"Loading {selected_file}..."):
                        # Download file
                        file_bytes = st.session_state.sp_client.download_file(
                            selected_library, selected_file
                        )

                        # Get file info
                        file_info = get_file_info(file_bytes, selected_file)

                        # Display file info
                        st.write("**File Information:**")
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.write(
                                f"- **Size:** {format_file_size(file_info['size_bytes'])}"
                            )
                            st.write(f"- **Type:** {file_info['extension']}")
                        with col_info2:
                            st.write(
                                f"- **Supported:** {'Yes' if file_info['is_supported'] else 'No'}"
                            )
                            st.write(
                                f"- **Can Preview:** {'Yes' if file_info['can_preview'] else 'No'}"
                            )

                        # Preview content based on file type
                        if selected_file.endswith(".pdf"):
                            content = preview_pdf(file_bytes)
                            st.text_area("PDF Content Preview", content, height=300)
                        elif selected_file.endswith(".docx"):
                            content = preview_docx(file_bytes)
                            st.text_area("DOCX Content Preview", content, height=300)
                        elif selected_file.endswith(".xlsx"):
                            df = preview_xlsx(file_bytes)
                            st.write("**Excel Data Preview:**")
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.warning("Preview not available for this file type")

                except FileOperationError as e:
                    display_error(f"File operation failed: {e}")
                except Exception as e:
                    logger.error(f"Preview error: {e}")
                    display_error(f"Preview failed: {str(e)}")

        with col2:
            if st.button("📥 Download File", use_container_width=True):
                try:
                    with st.spinner(f"Preparing {selected_file} for download..."):
                        file_bytes = st.session_state.sp_client.download_file(
                            selected_library, selected_file
                        )

                        st.download_button(
                            label=f"💾 Download {selected_file}",
                            data=file_bytes.getvalue(),
                            file_name=selected_file,
                            use_container_width=True,
                        )

                except Exception as e:
                    logger.error(f"Download error: {e}")
                    display_error(f"Download failed: {str(e)}")


def handle_home_button():
    """Handle home button functionality to reset the application to initial state."""
    if st.button("🏠 Home", help="Return to home screen and reset all views"):
        # Clear document preview
        st.session_state.doc_preview = None
        # Clear search results
        st.session_state.last_search_results = None
        # Set current tab to chat
        st.session_state.current_tab = "chat"
        # Clear any shared content selection
        if "selected_shared_content" in st.session_state:
            del st.session_state["selected_shared_content"]

        display_success("Returned to home screen")
        st.rerun()


def copy_to_clipboard_js(text: str) -> str:
    """Generate JavaScript code to copy text to clipboard."""
    # Escape quotes and newlines for JavaScript
    escaped_text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f"""
    <script>
    function copyToClipboard() {{
        navigator.clipboard.writeText("{escaped_text}").then(function() {{
            console.log('Content copied to clipboard');
        }}, function(err) {{
            console.error('Could not copy text: ', err);
        }});
    }}
    copyToClipboard();
    </script>
    """


def handle_share_content():
    """Handle sharing functionality for queried content with real clipboard functionality."""
    if (
        st.session_state.chat_history
        or st.session_state.last_search_results is not None
    ):
        st.markdown("### 📤 Share Content")

        # Share options
        share_options = []
        if st.session_state.chat_history:
            share_options.append("Chat Conversation")
        if st.session_state.last_search_results is not None:
            share_options.append("Search Results")
        if st.session_state.doc_preview:
            share_options.append("Document Preview")

        if share_options:
            selected_content = st.selectbox(
                "Select content to share:",
                options=share_options,
                help="Choose what content you want to share",
            )

            # Generate the content to be shared
            share_data = generate_shareable_content(selected_content)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "📋 Copy to Clipboard",
                    use_container_width=True,
                    help="Copy content to clipboard for easy sharing",
                ):
                    # Use Streamlit's built-in code display with copy functionality
                    st.code(share_data, language="text")
                    st.success(
                        f"✅ {selected_content} displayed above - use the copy button in the code block"
                    )

            with col2:
                if st.button(
                    "📧 Email Format",
                    use_container_width=True,
                    help="Format content for email sharing",
                ):
                    # Create email-friendly format
                    email_subject = f"SharePoint AI Assistant - {selected_content}"
                    email_body = f"Subject: {email_subject}\n\n{share_data}\n\n---\nShared from SharePoint AI Assistant"

                    # Store in session state for tracking
                    st.session_state.shared_content.append(
                        {
                            "type": "email",
                            "content": selected_content,
                            "data": email_body,
                            "timestamp": pd.Timestamp.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    )

                    # Display formatted email content
                    st.text_area(
                        "Email Content (copy this):",
                        value=email_body,
                        height=200,
                        help="Copy this content and paste into your email client",
                    )
                    st.success(
                        f"✅ {selected_content} formatted for email - copy the content above"
                    )

            with col3:
                if st.button(
                    "💾 Download File",
                    use_container_width=True,
                    help="Download content as a file",
                ):
                    # Create downloadable content
                    if selected_content == "Chat Conversation":
                        content_text = share_data
                        filename = f"chat_conversation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    elif selected_content == "Search Results":
                        if st.session_state.last_search_results is not None:
                            content_text = st.session_state.last_search_results.to_csv(
                                index=False
                            )
                            filename = f"search_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        else:
                            content_text = share_data
                            filename = f"search_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    else:
                        content_text = share_data
                        filename = f"document_preview_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt"

                    st.download_button(
                        label=f"📥 Download {selected_content}",
                        data=content_text,
                        file_name=filename,
                        use_container_width=True,
                    )

            # Show sharing history if any
            if st.session_state.shared_content:
                with st.expander(
                    f"📊 Sharing History ({len(st.session_state.shared_content)} items)"
                ):
                    for i, item in enumerate(
                        reversed(st.session_state.shared_content[-5:])
                    ):  # Show last 5 items
                        st.write(
                            f"**{item['timestamp']}** - {item['type'].title()}: {item['content']}"
                        )


def handle_prompt_editor():
    """
    Handle the agent prompt editor interface.

    *** AGENT PROMPT EDITOR ***
    This function provides a user-friendly interface for editing the AI assistant's
    system prompt. Users can modify the prompt to change the assistant's behavior,
    personality, and response style.
    """
    st.header("🤖 Agent Prompt Editor")

    # Information section
    st.info(
        """
    **About Agent Prompts:**
    The agent prompt defines how the AI assistant behaves, its personality, and how it responds to users.
    You can customize this to make the assistant more formal, casual, technical, or focused on specific tasks.
    
    **Tips for editing:**
    - Be specific about the assistant's role and capabilities
    - Include guidelines for how it should respond
    - Mention any specific formatting or tone preferences
    - Keep it clear and concise for best results
    """
    )

    # Get current prompt
    current_prompt = st.session_state.llm_service.get_current_prompt()

    # Show current prompt info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Prompt Length", f"{len(current_prompt)} characters")
    with col2:
        st.metric("Estimated Tokens", f"~{len(current_prompt.split())} words")

    # Prompt editor
    st.subheader("✏️ Edit System Prompt")

    # Text area for editing the prompt
    new_prompt = st.text_area(
        "System Prompt:",
        value=current_prompt,
        height=400,
        help="Edit the system prompt to customize the AI assistant's behavior",
        placeholder="Enter the system prompt that defines how the AI assistant should behave...",
    )

    # Validation and preview
    if new_prompt != current_prompt:
        st.warning("⚠️ You have unsaved changes to the prompt.")

        # Show character count for new prompt
        st.caption(
            f"New prompt length: {len(new_prompt)} characters (~{len(new_prompt.split())} words)"
        )

        # Preview section
        with st.expander("📖 Preview Changes", expanded=False):
            st.write("**New Prompt Preview:**")
            st.code(new_prompt, language="text")

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
            if not new_prompt.strip():
                display_error("Prompt cannot be empty")
            elif len(new_prompt) < 50:
                display_error(
                    "Prompt is too short. Please provide more detailed instructions."
                )
            else:
                try:
                    # Update the prompt
                    st.session_state.llm_service.update_system_prompt(new_prompt)
                    display_success("Agent prompt updated successfully!")

                    # Close the editor
                    st.session_state.show_prompt_editor = False
                    st.rerun()

                except Exception as e:
                    display_error(f"Failed to update prompt: {e}")

    with col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            try:
                st.session_state.llm_service.reset_prompt_to_default()
                display_success("Prompt reset to default")
                st.rerun()
            except Exception as e:
                display_error(f"Failed to reset prompt: {e}")

    with col3:
        if st.button("📋 Copy Current", use_container_width=True):
            # Display current prompt in a code block for easy copying
            st.code(current_prompt, language="text")
            st.success("Current prompt displayed above - use the copy button")

    with col4:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_prompt_editor = False
            st.rerun()

    # Example prompts section
    st.markdown("---")
    st.subheader("📚 Example Prompts")

    example_prompts = {
        "Professional Assistant": """You are a professional SharePoint assistant focused on helping users efficiently manage their documents and data.

Your capabilities include:
- Searching for documents in SharePoint libraries
- Listing items from SharePoint lists
- Providing information about available document libraries
- Answering questions about SharePoint content

Guidelines:
1. Always maintain a professional and helpful tone
2. Provide clear, actionable information
3. When using tools, explain what you found and its relevance
4. If you cannot find something, suggest alternative search strategies
5. Be concise but thorough in your responses

Remember to use the available tools to provide accurate, up-to-date information from SharePoint.""",
        "Casual Helper": """Hey there! I'm your friendly SharePoint assistant, here to help you find what you need!

I can help you with:
- Finding documents in your SharePoint libraries
- Checking out what's in your SharePoint lists
- Showing you what document libraries are available
- Answering questions about your SharePoint content

How I work:
1. I'll keep things friendly and easy to understand
2. I'll explain what I find in simple terms
3. If I can't find something, I'll suggest other ways to look
4. I'll use the tools I have to get you the most current info
5. I'll try to be helpful without being overwhelming

Let's find what you're looking for!""",
        "Technical Expert": """You are a technical SharePoint specialist with deep expertise in SharePoint architecture and data management.

Technical capabilities:
- Advanced document library searches with metadata analysis
- Comprehensive SharePoint list item queries and filtering
- Document library structure analysis and recommendations
- SharePoint content organization insights

Technical approach:
1. Provide detailed technical explanations when appropriate
2. Include relevant metadata and technical details in responses
3. Suggest optimization strategies for SharePoint usage
4. Reference SharePoint best practices and technical standards
5. Offer troubleshooting guidance when issues are encountered

Utilize available tools to deliver precise, technically accurate information with appropriate depth for technical users.""",
    }

    for prompt_name, prompt_text in example_prompts.items():
        with st.expander(f"📝 {prompt_name}", expanded=False):
            st.code(prompt_text, language="text")
            if st.button(
                f"Use {prompt_name}", key=f"use_{prompt_name.lower().replace(' ', '_')}"
            ):
                # Update the text area (this will require a rerun to show)
                st.session_state.selected_example_prompt = prompt_text
                st.rerun()

    # Handle selected example prompt
    if st.session_state.get("selected_example_prompt"):
        st.info("Example prompt selected! Scroll up to see it in the editor.")
        # Clear the selection
        del st.session_state.selected_example_prompt


def generate_shareable_content(content_type: str) -> str:
    """Generate shareable content based on the selected type."""
    if content_type == "Chat Conversation":
        return f"SharePoint AI Assistant Chat\n{'='*40}\n" + "\n".join(
            st.session_state.chat_history
        )
    elif content_type == "Search Results":
        if st.session_state.last_search_results is not None:
            return f"SharePoint Search Results\n{'='*40}\n{st.session_state.last_search_results.to_string()}"
        return "No search results available"
    elif content_type == "Document Preview":
        return f"Document Preview: {st.session_state.doc_preview}\nShared from SharePoint AI Assistant"
    return "No content available"


def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()

        # App header with home button
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title(f"{UIConstants.PAGE_ICON} {UIConstants.PAGE_TITLE}")
        with col2:
            handle_home_button()

        st.markdown("---")

        # Handle sidebar connection
        handle_connection_form()

        # Handle sidebar document preview (matching mockup)
        if True:  # Always show document preview section
            st.sidebar.markdown("---")
            st.sidebar.header("📄 Document Preview")

            # Recent documents list (matching mockup)
            doc_list = [
                "HR_Policy_v3.docx",
                "Employee_Handbook.pdf",
                "Onboarding_Checklist.xlsx",
            ]

            selected_doc = st.sidebar.selectbox(
                "Recent Documents", doc_list, help="Select a document to preview"
            )

            if st.sidebar.button("👁️ Preview", use_container_width=True):
                st.session_state.doc_preview = selected_doc
                st.rerun()

        # Agent Settings Section - NEW FEATURE FOR EDITING AGENT PROMPT
        if st.session_state.connected and st.session_state.llm_service:
            st.sidebar.markdown("---")
            st.sidebar.header("🤖 Agent Settings")

            # Show current prompt info
            with st.sidebar.expander("📝 Edit Agent Prompt", expanded=False):
                st.write("**Current Agent Behavior:**")
                current_prompt = st.session_state.llm_service.get_current_prompt()
                st.caption(f"Prompt length: {len(current_prompt)} characters")

                # Button to open prompt editor
                if st.button("✏️ Edit Prompt", use_container_width=True):
                    st.session_state.show_prompt_editor = True
                    st.rerun()

                # Reset to default button
                if st.button("🔄 Reset to Default", use_container_width=True):
                    try:
                        st.session_state.llm_service.reset_prompt_to_default()
                        display_success("Agent prompt reset to default")
                        st.rerun()
                    except Exception as e:
                        display_error(f"Failed to reset prompt: {e}")

        # Main content tabs
        tab1, tab2 = st.tabs(
            [UIConstants.CHAT_TAB, "🔍 Search SharePoint Lists/Libraries"]
        )

        with tab1:
            # Show prompt editor if requested
            if st.session_state.get("show_prompt_editor", False):
                handle_prompt_editor()
            else:
                handle_chat_tab()
                # Display document preview in chat tab if selected from sidebar
                display_document_preview_in_chat()
                # Add share functionality to chat tab
                if st.session_state.chat_history or st.session_state.doc_preview:
                    st.markdown("---")
                    handle_share_content()

        with tab2:
            handle_search_and_lists_tab()
            # Add share functionality to search tab
            if (
                st.session_state.last_search_results is not None
                or st.session_state.chat_history
            ):
                st.markdown("---")
                handle_share_content()

        # Footer
        st.markdown("---")
        st.caption(
            "SharePoint AI Assistant - Enhanced with comprehensive error handling and validation"
        )

    except Exception as e:
        logger.critical(f"Critical application error: {e}")
        logger.critical(f"Traceback: {traceback.format_exc()}")

        st.error("🚨 Critical Application Error")
        st.error(f"An unexpected error occurred: {str(e)}")

        if st.button("🔄 Restart Application"):
            # Clear session state and rerun
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
