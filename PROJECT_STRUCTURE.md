# SharePoint AI Assistant - Project Structure

## 📁 Clean Project Organization

The duplicate `sharepoint-ai-assistant/` folder has been removed to avoid confusion. The project now follows a clean, professional structure:

```
sharepoint-ai-assistant/
├── 📁 src/                       # Main application source code
│   ├── 📁 core/                  # Core functionality and configuration
│   │   ├── config.py            # ⚙️ Configuration management
│   │   ├── constants.py         # 🔧 Application constants (EDIT HERE)
│   │   ├── exceptions.py        # ❌ Custom exception classes
│   │   └── logging_config.py    # 📝 Logging configuration
│   ├── 📁 clients/               # External service clients
│   │   └── sharepoint_client.py # 🔗 Enhanced SharePoint client
│   ├── 📁 services/              # Business logic services
│   │   └── llm_service.py       # 🤖 LLM service (EDIT AGENT PROMPT HERE)
│   ├── 📁 utils/                 # Utility functions
│   │   ├── validation.py        # 🛡️ Input validation and security
│   │   └── file_utils.py        # 📄 File processing utilities
│   └── 📁 ui/                    # User interface
│       └── main.py              # 🖥️ Enhanced Streamlit UI
├── 📁 tests/                     # Test suite
├── 📁 requirements/              # Dependency management
├── 📁 logs/                      # Application logs
├── 📁 data/                      # Data directory
├── main.py                       # 🚀 Application entry point
├── Dockerfile                    # 🐳 Docker configuration
├── docker-compose.yml           # 🐳 Docker Compose setup
└── README.md                     # 📖 Documentation
```

## 🎯 Key Locations for Customization

### 1. **Agent Prompt Editing**

- **File**: `src/services/llm_service.py`
- **Look for**: `*** EDIT AGENT PROMPT HERE ***`
- **UI Method**: Use the Agent Settings in the sidebar when connected

### 2. **Application Constants**

- **File**: `src/core/constants.py`
- **Look for**: `*** CONFIGURATION CONSTANTS ***`
- **Contains**: All configurable values and magic numbers

### 3. **Main UI**

- **File**: `src/ui/main.py`
- **Contains**: All UI components and the new Agent Prompt Editor

## 🚀 Quick Start

1. **Run the application**:

   ```bash
   streamlit run main.py
   ```

2. **Edit Agent Prompt via UI**:

   - Connect to SharePoint
   - Look for "🤖 Agent Settings" in sidebar
   - Click "✏️ Edit Prompt"

3. **Edit Agent Prompt via Code**:
   - Open `src/services/llm_service.py`
   - Find the `*** EDIT AGENT PROMPT HERE ***` section
   - Modify the `default_prompt` variable

## ✅ What Was Cleaned Up

- ❌ Removed duplicate `sharepoint-ai-assistant/` folder
- ❌ Removed old app/ structure
- ❌ Removed duplicate README.md
- ❌ Removed duplicate docker-compose.yml
- ✅ Kept enhanced `src/` structure
- ✅ Kept comprehensive documentation
- ✅ Kept all new features (Agent Prompt Editor, Enhanced Sharing, etc.)

## 🔧 No Breaking Changes

The main entry point (`main.py`) automatically uses the enhanced UI from `src/ui/main.py`, so all functionality remains intact while providing a cleaner, more professional structure.
