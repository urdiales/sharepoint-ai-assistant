# SharePoint AI Assistant - Enhanced Version

A robust, production-ready SharePoint AI Assistant with comprehensive error handling, validation, and enterprise-grade features.

## 🚀 Features

### Core Functionality

- **AI-Powered Chat Interface**: Natural language queries about SharePoint content
- **Document Search & Preview**: Search and preview PDF, DOCX, and XLSX files
- **SharePoint Integration**: Seamless connection to SharePoint Online
- **File Management**: Download and analyze SharePoint documents

### Enhanced Features

- **Comprehensive Error Handling**: Robust error management with custom exceptions
- **Input Validation & Security**: XSS protection and input sanitization
- **Structured Logging**: Detailed logging with multiple levels and performance tracking
- **Configuration Management**: Environment-based configuration with validation
- **Modular Architecture**: Clean separation of concerns with proper abstractions
- **Unit Testing**: Comprehensive test suite with pytest
- **Docker Support**: Multi-stage Docker builds for production deployment

## 📁 Project Structure

```
sharepoint-ai-assistant/
├── src/                          # Main application source code
│   ├── core/                     # Core functionality and configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py         # Application constants
│   │   ├── exceptions.py        # Custom exception classes
│   │   └── logging_config.py    # Logging configuration
│   ├── clients/                  # External service clients
│   │   ├── __init__.py
│   │   └── sharepoint_client.py # Enhanced SharePoint client
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   └── llm_service.py       # LLM service with error handling
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── validation.py        # Input validation and security
│   │   └── file_utils.py        # File processing utilities
│   └── ui/                       # User interface
│       ├── __init__.py
│       └── main.py              # Enhanced Streamlit UI
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   │   └── test_validation.py   # Validation tests
│   └── integration/              # Integration tests
├── requirements/                 # Dependency management
│   ├── base.txt                 # Base requirements
│   └── dev.txt                  # Development requirements
├── logs/                         # Application logs
├── data/                         # Data directory
├── main.py                       # Application entry point
├── Dockerfile                    # Enhanced Docker configuration
├── docker-compose.yml           # Docker Compose setup
└── README.md                     # This file
```

## 🛠️ Quick Start - Python Environment Setup

### Prerequisites

- **Python 3.11** (required)
- Git
- Ollama (for local LLM support)
- Docker (optional, for containerized deployment)

### ⚡ Simple Manual Setup (5 Steps)

```bash
# 1. Clone and navigate to the project
git clone https://github.com/urdiales/sharepoint-ai-assistant.git
cd sharepoint-ai-assistant

# 2. Create Python 3.11 virtual environment
python3.11 -m venv venv

# 3. Activate environment and install dependencies
# Windows:
venv\Scripts\activate && pip install -r requirements/dev.txt
# macOS/Linux:
source venv/bin/activate && pip install -r requirements/dev.txt

# 4. Set up configuration
cp .env.example .env
# Edit .env with your SharePoint credentials

# 5. Run the application
streamlit run main.py
```

### 🚀 Super Quick Setup (Automated)

For the easiest setup experience, use our interactive setup script:

```bash
# Clone the repository
git clone https://github.com/urdiales/sharepoint-ai-assistant.git
cd sharepoint-ai-assistant

# Run the setup script
python setup.py
```

The script will:

- ✅ Check your Python version
- 🔍 Detect available environment managers (Conda, UV, venv)
- 📋 Guide you through setup options
- ⚙️ Create your environment automatically
- 📄 Copy configuration files

### 🛠️ Manual Setup Options

#### 🎯 Option A: Anaconda/Miniconda (Recommended for Beginners)

**Step 1: Install Anaconda/Miniconda**

- Download from [anaconda.com](https://www.anaconda.com/download) or [miniconda](https://docs.conda.io/en/latest/miniconda.html)

**Step 2: Create and activate environment**

```bash
# Clone the repository
git clone https://github.com/urdiales/sharepoint-ai-assistant.git
cd sharepoint-ai-assistant

# Create environment with Python 3.11
conda create -n sharepoint-ai python=3.11 -y
conda activate sharepoint-ai

# Install dependencies
pip install -r requirements/dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run main.py
```

#### ⚡ Option B: UV (Fast & Modern)

**Step 1: Install UV**

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Set up project**

```bash
# Clone the repository
git clone https://github.com/urdiales/sharepoint-ai-assistant.git
cd sharepoint-ai-assistant

# Create virtual environment with Python 3.11
uv venv --python 3.11

# Activate environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies (lightning fast!)
uv pip install -r requirements/dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run main.py
```

#### 🐍 Option C: Traditional Python venv

**Step 1: Verify Python 3.11**

```bash
python3.11 --version  # Should show Python 3.11.x
# If not available, install Python 3.11 from python.org
```

**Step 2: Set up project**

```bash
# Clone the repository
git clone https://github.com/urdiales/sharepoint-ai-assistant.git
cd sharepoint-ai-assistant

# Create virtual environment
python3.11 -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements/dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run main.py
```

### 🔍 Quick Verification

After setup, verify everything works:

```bash
# Check Python version
python --version  # Should show Python 3.11.x

# Test import of key dependencies
python -c "import streamlit, pandas, langchain; print('✅ All dependencies installed successfully!')"

# Check if Streamlit runs
streamlit hello  # Should open Streamlit demo in browser
```

### 🚨 Troubleshooting

**Common Issues:**

1. **Python 3.11 not found**

   - Install from [python.org](https://www.python.org/downloads/)
   - On Ubuntu: `sudo apt install python3.11 python3.11-venv`
   - On macOS with Homebrew: `brew install python@3.11`

2. **Permission errors on Windows**

   - Run terminal as Administrator
   - Or use: `python -m pip install --user -r requirements/dev.txt`

3. **Conda environment conflicts**

   - Remove existing environment: `conda env remove -n sharepoint-ai`
   - Create fresh environment

4. **UV installation issues**
   - Check [UV documentation](https://docs.astral.sh/uv/) for platform-specific instructions
   - Alternative: Use pip in virtual environment

### Docker Deployment

1. **Build the Docker image**

   ```bash
   docker build -t sharepoint-ai-assistant .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# SharePoint Configuration
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/yoursite
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret

# LLM Configuration
LLM_MODEL=llama2
LLM_HOST=http://localhost:11434
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Security Configuration
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=60
```

### SharePoint App Registration

1. **Register an app in Azure AD**

   - Go to Azure Portal > App registrations
   - Create a new registration
   - Note the Application (client) ID

2. **Configure API permissions**

   - Add SharePoint permissions:
     - `Sites.Read.All`
     - `Sites.ReadWrite.All` (if write access needed)

3. **Create client secret**
   - Go to Certificates & secrets
   - Create a new client secret
   - Copy the secret value

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/unit/test_validation.py -v
```

## 📊 Logging and Monitoring

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that allow application to continue
- **CRITICAL**: Serious errors that may abort the program

### Log Locations

- **Console**: Real-time logging output
- **File**: `logs/app.log` (configurable)
- **Structured**: JSON format for log aggregation

### Performance Monitoring

The application includes built-in performance monitoring:

- Function execution times
- Memory usage tracking
- API response times
- Error rate monitoring

## 🔒 Security Features

### Input Validation

- XSS protection with HTML sanitization
- SQL injection prevention
- File type validation
- Size limit enforcement

### Authentication

- Secure credential handling
- Environment-based configuration
- No hardcoded secrets

### Rate Limiting

- Configurable request limits
- Protection against abuse
- Graceful degradation

## 🚀 Deployment

### Production Checklist

- [ ] Environment variables configured
- [ ] SharePoint app registered and permissions granted
- [ ] Ollama service running (for local LLM)
- [ ] Log directory writable
- [ ] Health checks configured
- [ ] Monitoring set up

### Docker Production Deployment

```bash
# Build production image
docker build -t sharepoint-ai-assistant:latest .

# Run with production settings
docker run -d \
  --name sharepoint-ai-assistant \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  sharepoint-ai-assistant:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sharepoint-ai-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sharepoint-ai-assistant
  template:
    metadata:
      labels:
        app: sharepoint-ai-assistant
    spec:
      containers:
        - name: app
          image: sharepoint-ai-assistant:latest
          ports:
            - containerPort: 8501
          env:
            - name: SHAREPOINT_SITE_URL
              valueFrom:
                secretKeyRef:
                  name: sharepoint-secrets
                  key: site-url
          # Add other environment variables
```

## 🔧 Troubleshooting

### Common Issues

1. **SharePoint Connection Failed**

   - Verify client ID and secret
   - Check app permissions in Azure AD
   - Ensure site URL is correct

2. **LLM Service Unavailable**

   - Verify Ollama is running
   - Check model is downloaded
   - Verify host URL and port

3. **File Preview Errors**
   - Check file size limits
   - Verify file type is supported
   - Ensure sufficient memory

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
streamlit run main.py
```

### Health Checks

The application provides health check endpoints:

- **Streamlit Health**: `http://localhost:8501/_stcore/health`
- **Application Status**: Check logs for service status

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

### Code Standards

- **Python**: Follow PEP 8
- **Type Hints**: Use type annotations
- **Documentation**: Docstrings for all functions
- **Testing**: Unit tests for new features
- **Logging**: Appropriate log levels

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation

- [SharePoint API Documentation](https://docs.microsoft.com/en-us/sharepoint/dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)

### Issues

Report issues on [GitHub Issues](https://github.com/urdiales/sharepoint-ai-assistant/issues)

### Community

- [Discussions](https://github.com/urdiales/sharepoint-ai-assistant/discussions)
- [Wiki](https://github.com/urdiales/sharepoint-ai-assistant/wiki)

## 🎯 Roadmap

### Version 2.0 (Planned)

- [ ] Multi-tenant support
- [ ] Advanced search with filters
- [ ] Document summarization
- [ ] Workflow automation
- [ ] Mobile-responsive UI
- [ ] API endpoints
- [ ] Advanced analytics
- [ ] Integration with Teams

### Version 1.1 (In Progress)

- [x] Enhanced error handling
- [x] Comprehensive logging
- [x] Input validation
- [x] Unit testing framework
- [x] Docker optimization
- [ ] Performance improvements
- [ ] Additional file formats
- [ ] Caching layer

---

**Built with ❤️ for the SharePoint community**
