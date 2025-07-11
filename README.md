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
