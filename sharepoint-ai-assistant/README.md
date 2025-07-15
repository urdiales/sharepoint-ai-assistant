# 🤖 Local AI SharePoint Assistant

**Talk to your SharePoint site with AI, right on your computer.  
No data leaves your machine—everything runs locally! 🔒**

---

## ✨ What does this app do?

- 💬 Lets you ask questions about your SharePoint site and documents in plain English
- 🧠 Uses a smart AI (runs locally!) to search, read, and answer your questions
- 📊 Shows you documents, lists, and summaries—all in a friendly web interface

---

## 📋 What you need before starting

1. **💻 A computer with Docker Desktop installed**

   - [Download Docker Desktop (Windows/Mac)](https://www.docker.com/products/docker-desktop/)
   - If you're on Linux, you might already have Docker

2. **🔑 Your SharePoint site details:**

   - Site URL (looks like `https://yourcompany.sharepoint.com/sites/YourSiteName`)
   - API Key and Secret (from your admin or SharePoint setup)

3. **⏱️ A little patience!**
   - The app will download the AI model the first time you run it (~5-10 minutes)

---

## 🚀 How to set it up (Step by Step)

# 🤖 Local AI SharePoint Assistant

**Talk to your SharePoint site with AI, right on your computer.  
No data leaves your machine—everything runs locally! 🔒**

---

## ✨ What does this app do?

- 💬 Lets you ask questions about your SharePoint site and documents in plain English
- 🧠 Uses a smart AI (runs locally!) to search, read, and answer your questions
- 📊 Shows you documents, lists, and summaries—all in a friendly web interface

---

## 📋 What you need before starting

1. **💻 Container Runtime (Choose one option):**

   **Option A: Docker Desktop (Recommended)**

   - [Download Docker Desktop (Windows/Mac)](https://www.docker.com/products/docker-desktop/)
   - If you're on Linux, you might already have Docker

   **Option B: If Docker Desktop is not allowed** 🚫

   - **Windows:** Use [Podman Desktop](https://podman-desktop.io/) or [Docker Engine](https://docs.docker.com/engine/install/)
   - **Mac:** Use [Podman](https://podman.io/docs/installation#macos) or [OrbStack](https://orbstack.dev/)
   - **Linux:** Use system Docker (`sudo apt install docker.io` or `sudo yum install docker`)

   **Option C: Manual Installation (Advanced)** 🔧

   - Install Python 3.8+ and Ollama separately (see Alternative Setup section below)

2. **🔑 Your SharePoint site details:**

   - Site URL (looks like `https://yourcompany.sharepoint.com/sites/YourSiteName`)
   - API Key and Secret (from your admin or SharePoint setup)

3. **⏱️ A little patience!**
   - The app will download the AI model the first time you run it (~5-10 minutes)

---

## 🚀 How to set it up (Step by Step)

### 1️⃣ Download the App Files

**If the files are hosted on GitLab:**

1. **📂 Go to the GitLab project page** (ask your admin for the link)
2. **⬇️ Download the project:**
   - Click the **"Download"** button (usually near the top right)
   - Select **"Download zip"** from the dropdown menu
   - Save the zip file to your computer (e.g., Downloads folder)
3. **📁 Extract the files:**
   - Right-click the downloaded zip file
   - Select "Extract All" (Windows) or double-click (Mac)
   - Choose where to extract (e.g., Desktop)
   - You should now have a folder named something like `sharepoint-ai-assistant-main`

**Alternative method using Git (if you have Git installed):**

```
git clone [GitLab-repository-URL]
```

**If you received the files another way:**

- Download the folder with all the files (ask your admin or get the files from your team's link)
- Put the folder anywhere on your computer (for example, on your Desktop)

### 2️⃣ Add Your SharePoint Info

- Find the file called `.env` in the folder  
  If you don't see it, make a new file called `.env` (yes, it starts with a dot!)

- Open `.env` with Notepad (Windows) or TextEdit (Mac)
- Paste this in and fill out your details:

```
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/YourSiteName
SHAREPOINT_CLIENT_ID=your-api-key-here
SHAREPOINT_CLIENT_SECRET=your-secret-here
OLLAMA_HOST=http://ollama:11434
```

- **Save the file**

#### 🔧 Alternative Ollama Configuration Options

Choose the configuration that matches your setup:

**1. 🐳 Using Docker Compose (Default - Most Common)**

```
OLLAMA_HOST=http://ollama:11434
```

**2. 🏠 If Ollama is Already Running on Your Computer**

- You might already have Ollama running locally (not started by Docker Compose).
- In this case, change your `.env` file:
  - **🪟 On Windows or Mac:**
    ```
    OLLAMA_HOST=http://host.docker.internal:11434
    ```
  - **🐧 On Linux:**
    ```
    OLLAMA_HOST=http://127.0.0.1:11434
    ```
    or use your machine's local IP address.

**3. 🌐 If Ollama is Running on Another Server**

- Set the `.env` file to the correct address:
  ```
  OLLAMA_HOST=http://<server-ip>:11434
  ```
  Replace `<server-ip>` with the server's address.

### 3️⃣ Open a Terminal or Command Prompt

**On Windows:**

- Click Start, type "cmd", and hit Enter

**On Mac:**

- Open Spotlight (Cmd+Space), type "Terminal", and hit Enter

Navigate to the folder where you put the app:  
Example (if the folder is on your Desktop and named `sharepoint-ai-assistant`):

```
cd Desktop\sharepoint-ai-assistant
```

### 4️⃣ Start the App

**🐳 Using Docker/Podman (Recommended)**

**⚠️ The first time will take a little longer—just let it finish!**

For Docker:

```
docker compose up -d
```

For Podman:

```
podman-compose up -d
```

or

```
podman compose up -d
```

- This will start the AI and the app
- Wait for about 1-3 minutes on the first run

**🔧 Alternative: Manual Setup (If containers aren't allowed)**

If you can't use containers, see the "Alternative Manual Setup" section below.

### 5️⃣ Open the App in Your Browser

- Open Chrome, Edge, or Safari
- Go to: [http://localhost:8501](http://localhost:8501)

### 6️⃣ Connect to SharePoint

- You'll see the app in your browser
- Enter your SharePoint Site URL, API Key, and Secret (from your `.env` file)
- Click "Connect"
- Now you can start asking questions about your SharePoint site! 🎉

### 7️⃣ Stopping the App

**🐳 For Docker:**

```
docker compose down
```

**🐳 For Podman:**

```
podman-compose down
```

or

```
podman compose down
```

**🔧 For Manual Setup:**

- Press `Ctrl+C` in the terminal where you started the app
- Stop Ollama if you started it separately

---

## 🔧 Alternative Manual Setup (No Containers Required)

**Use this if Docker Desktop/containers are not allowed in your environment**

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed separately

### Steps

#### 1️⃣ Install Ollama

- Download and install Ollama from [ollama.ai](https://ollama.ai/)
- Start Ollama: `ollama serve`
- Download the AI model: `ollama pull llama2` (or your preferred model)

#### 2️⃣ Set up Python Environment

```bash
# Create a virtual environment
python -m venv sharepoint-ai-env

# Activate it
# Windows:
sharepoint-ai-env\Scripts\activate
# Mac/Linux:
source sharepoint-ai-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ Update your .env file

```
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/YourSiteName
SHAREPOINT_CLIENT_ID=your-api-key-here
SHAREPOINT_CLIENT_SECRET=your-secret-here
OLLAMA_HOST=http://localhost:11434
```

#### 4️⃣ Start the Application

```bash
streamlit run app.py
```

#### 5️⃣ Access the App

- Open your browser and go to: [http://localhost:8501](http://localhost:8501)

### 🛑 Stopping Manual Setup

- Press `Ctrl+C` in the terminal where you started the app
- Stop Ollama: `ollama stop` or close the Ollama terminal

---

## ❓ Troubleshooting

- **🔄 If you see "connection refused" or nothing loads:**  
  Wait a bit longer—the AI model may still be downloading

- **📝 If you mess up your `.env` file:**  
  Just edit it and try again!

- **🔧 If you have Ollama connection issues:**  
  Check your `OLLAMA_HOST` setting matches your setup (see configuration options above)

- **🐳 If containers don't work:**  
  Try the "Alternative Manual Setup" section for running without Docker

- **🔒 If your organization blocks Docker Desktop:**  
  Use Podman, OrbStack, or the manual setup method

- **🆘 If you need help:**  
  Ask your admin or IT team

---

## 🔒 Privacy & Security

- This app **does not send your data to the cloud or any outside servers**
- Everything runs locally on your computer
- It's just for you—no one else can see your questions or answers

---

## 📊 Quick Reference

### 🐳 Container Method (Docker/Podman)

| Step | What you do | How                                                  |
| ---- | ----------- | ---------------------------------------------------- |
| 1    | Add details | Edit `.env`                                          |
| 2    | Open folder | `cd ...`                                             |
| 3    | Start app   | `docker compose up -d` or `podman compose up -d`     |
| 4    | Use browser | Go to [http://localhost:8501](http://localhost:8501) |
| 5    | Stop app    | `docker compose down` or `podman compose down`       |

### 🔧 Manual Method (No Containers)

| Step | What you do    | How                                                  |
| ---- | -------------- | ---------------------------------------------------- |
| 1    | Install Ollama | Download from [ollama.ai](https://ollama.ai/)        |
| 2    | Set up Python  | `python -m venv sharepoint-ai-env`                   |
| 3    | Install deps   | `pip install -r requirements.txt`                    |
| 4    | Add details    | Edit `.env`                                          |
| 5    | Start app      | `streamlit run app.py`                               |
| 6    | Use browser    | Go to [http://localhost:8501](http://localhost:8501) |
| 7    | Stop app       | `Ctrl+C`                                             |

---

**That's it! 🎉 Enjoy your own local AI SharePoint Assistant.**

### 1️⃣ Download the App Files

**If the files are hosted on GitLab:**

1. **📂 Go to the GitLab project page** (ask your admin for the link)
2. **⬇️ Download the project:**
   - Click the **"Download"** button (usually near the top right)
   - Select **"Download zip"** from the dropdown menu
   - Save the zip file to your computer (e.g., Downloads folder)
3. **📁 Extract the files:**
   - Right-click the downloaded zip file
   - Select "Extract All" (Windows) or double-click (Mac)
   - Choose where to extract (e.g., Desktop)
   - You should now have a folder named something like `sharepoint-ai-assistant-main`

**Alternative method using Git (if you have Git installed):**

```
git clone [GitLab-repository-URL]
```

**If you received the files another way:**

- Download the folder with all the files (ask your admin or get the files from your team's link)
- Put the folder anywhere on your computer (for example, on your Desktop)

### 2️⃣ Add Your SharePoint Info

- Find the file called `.env` in the folder  
  If you don't see it, make a new file called `.env` (yes, it starts with a dot!)

- Open `.env` with Notepad (Windows) or TextEdit (Mac)
- Paste this in and fill out your details:

```
SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/YourSiteName
SHAREPOINT_CLIENT_ID=your-api-key-here
SHAREPOINT_CLIENT_SECRET=your-secret-here
OLLAMA_HOST=http://ollama:11434
```

- **Save the file**

#### 🔧 Alternative Ollama Configuration Options

Choose the configuration that matches your setup:

**1. 🐳 Using Docker Compose (Default - Most Common)**

```
OLLAMA_HOST=http://ollama:11434
```

**2. 🏠 If Ollama is Already Running on Your Computer**

- You might already have Ollama running locally (not started by Docker Compose).
- In this case, change your `.env` file:
  - **🪟 On Windows or Mac:**
    ```
    OLLAMA_HOST=http://host.docker.internal:11434
    ```
  - **🐧 On Linux:**
    ```
    OLLAMA_HOST=http://127.0.0.1:11434
    ```
    or use your machine's local IP address.

**3. 🌐 If Ollama is Running on Another Server**

- Set the `.env` file to the correct address:
  ```
  OLLAMA_HOST=http://<server-ip>:11434
  ```
  Replace `<server-ip>` with the server's address.

### 3️⃣ Open a Terminal or Command Prompt

**On Windows:**

- Click Start, type "cmd", and hit Enter

**On Mac:**

- Open Spotlight (Cmd+Space), type "Terminal", and hit Enter

Navigate to the folder where you put the app:  
Example (if the folder is on your Desktop and named `sharepoint-ai-assistant`):

```
cd Desktop\sharepoint-ai-assistant
```

### 4️⃣ Start the App with Docker

**⚠️ The first time will take a little longer—just let it finish!**

Type:

```
docker compose up -d
```

- This will start the AI and the app
- Wait for about 1-3 minutes on the first run

### 5️⃣ Open the App in Your Browser

- Open Chrome, Edge, or Safari
- Go to: [http://localhost:8501](http://localhost:8501)

### 6️⃣ Connect to SharePoint

- You'll see the app in your browser
- Enter your SharePoint Site URL, API Key, and Secret (from your `.env` file)
- Click "Connect"
- Now you can start asking questions about your SharePoint site! 🎉

### 7️⃣ Stopping the App

- When you're done, go back to your terminal and type:
  ```
  docker compose down
  ```

---

## ❓ Troubleshooting

- **🔄 If you see "connection refused" or nothing loads:**  
  Wait a bit longer—the AI model may still be downloading

- **📝 If you mess up your `.env` file:**  
  Just edit it and try again!

- **🔧 If you have Ollama connection issues:**  
  Check your `OLLAMA_HOST` setting matches your setup (see configuration options above)

- **🆘 If you need help:**  
  Ask your admin or IT team

---

## 🔒 Privacy & Security

- This app **does not send your data to the cloud or any outside servers**
- Everything runs locally on your computer
- It's just for you—no one else can see your questions or answers

---

## 📊 Quick Reference

| Step | What you do | How                                                  |
| ---- | ----------- | ---------------------------------------------------- |
| 1    | Add details | Edit `.env`                                          |
| 2    | Open folder | `cd ...`                                             |
| 3    | Start app   | `docker compose up -d`                               |
| 4    | Use browser | Go to [http://localhost:8501](http://localhost:8501) |
| 5    | Stop app    | `docker compose down`                                |

---

**That's it! 🎉 Enjoy your own local AI SharePoint Assistant.**
