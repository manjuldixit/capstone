# 🚀 Equipment Financing AI Banking Agent - Setup & Run Guide

**For Complete Beginners** - Step-by-step instructions to get the AI Banking Support Agent running on your computer.

---

## 📋 What You Need Before Starting

### 1. Windows Computer
- You need a Windows computer (Windows 10 or 11)
- At least 4GB RAM (8GB recommended)
- 2GB free disk space

### 2. Internet Connection
- Stable internet connection (for downloading files and API calls)
- No firewall blocking Python or web traffic

### 3. Basic Computer Skills
- Know how to open Command Prompt or PowerShell
- Know how to copy/paste text
- Know how to open web browsers

---

## 🛠️ Step 1: Install Python

### Check if Python is Already Installed
1. Press `Windows + R` keys
2. Type `cmd` and press Enter
3. In the black window, type: `python --version`
4. Press Enter

**If you see a version like "Python 3.10.x" or higher:**
- Great! Python is already installed. Skip to Step 2.

**If you see an error or "Python is not recognized":**
- You need to install Python. Follow these steps:

### Install Python (if needed)
1. Open your web browser
2. Go to: https://www.python.org/downloads/
3. Click the big yellow button: "Download Python 3.11.x" (latest version)
4. Wait for download to finish
5. Double-click the downloaded file (looks like `python-3.11.x-amd64.exe`)
6. **Important:** Check the box "Add Python to PATH" at the bottom
7. Click "Install Now"
8. Wait for installation to complete (5-10 minutes)
9. Close the installer

### Verify Python Installation
1. Open Command Prompt again (`Windows + R`, type `cmd`)
2. Type: `python --version`
3. Press Enter
4. You should see: `Python 3.11.x` or similar

---

## 📁 Step 2: Download the Project

### Option A: Download ZIP (Easiest)
1. Open your web browser
2. Go to the project location (ask your instructor for the link)
3. Click the green "Code" button
4. Click "Download ZIP"
5. Save the ZIP file to your Downloads folder
6. Right-click the ZIP file and select "Extract All..."
7. Extract to: `C:\Users\YourName\Desktop\ai-banking-agent`
8. Remember this folder location!

### Option B: Clone with Git (Advanced)
If you have Git installed:
1. Open Command Prompt
2. Type: `cd Desktop`
3. Type: `git clone [repository URL] ai-banking-agent`

---

## ⚙️ Step 3: Set Up the Project

### Navigate to Project Folder
1. Open Command Prompt (`Windows + R`, type `cmd`)
2. Type: `cd C:\Users\YourName\Desktop\ai-banking-agent\capstone\ai-banking-advisory-agent`
3. Press Enter
4. Type: `dir` to see the files (you should see folders like `backend/`, `frontend/`, etc.)

### Install Required Software
1. In the Command Prompt (still in the project folder), type:
   ```
   pip install -r requirements.txt
   ```
2. Press Enter
3. Wait for installation (this may take 5-10 minutes)
4. You should see "Successfully installed" messages

**If you get an error:**
- Try: `python -m pip install -r requirements.txt`
- Or ask for help if it still fails

---

## 🔑 Step 4: Set Up API Keys (Optional but Recommended)

The agent works with mock data by default, but for better responses, you can add real AI keys.

### Get API Keys (Optional)
1. **OpenAI Key** (free trial available):
   - Go to: https://platform.openai.com/
   - Sign up for an account
   - Go to API Keys section
   - Create a new key
   - Copy the key (starts with `sk-`)

2. **Anthropic Key** (alternative):
   - Go to: https://console.anthropic.com/
   - Sign up and get API key

### Create Environment File
1. In the project folder, look for `.env.example` file
2. Make a copy and rename it to `.env`
3. Open `.env` in Notepad
4. Add your keys like this:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=your-anthropic-key-here
   ```
5. Save the file

**Note:** If you don't have API keys, the app will still work with mock responses.

---

## 🚀 Step 5: Run the Application

### Option A: Run Both API and Web Interface (Recommended)

#### Start the API Server (Backend)
1. Open **Command Prompt 1**
2. Navigate to project: `cd C:\Users\YourName\Desktop\ai-banking-agent\capstone\ai-banking-advisory-agent`
3. Type: `python backend\deploy_server.py`
4. Press Enter
5. You should see: "Uvicorn running on http://0.0.0.0:8000"
6. **Keep this window open** - don't close it!

#### Start the Web Interface (Frontend)
1. Open **Command Prompt 2** (new window)
2. Navigate to project: `cd C:\Users\YourName\Desktop\ai-banking-agent\capstone\ai-banking-advisory-agent`
3. Type: `python -m streamlit run frontend/app.py`
4. Press Enter
5. You should see: "Local URL: http://localhost:8501"
6. **Keep this window open** - don't close it!

#### Use the Application
1. Open your web browser
2. Go to: `http://localhost:8501`
3. You should see the AI Banking Agent interface
4. Type questions like:
   - "What equipment financing options do you offer?"
   - "I'm a small business owner, am I eligible?"
   - "What documents do I need for a loan?"

### Option B: Run API Only (For Developers)

#### Start API Server Only
1. Open Command Prompt
2. Navigate to project folder
3. Type: `python backend\deploy_server.py`
4. API will be available at: `http://localhost:8000`

#### Test API with Commands
1. Open another Command Prompt
2. Test health: `curl http://localhost:8000/health`
3. Test query:
   ```
   curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d "{\"query\": \"What financing options do you have?\"}"
   ```

---

## 🧪 Step 6: Test the Application

### Basic Tests
1. **Health Check:**
   - Open browser to: `http://localhost:8000/health`
   - Should show: `{"status": "healthy"}`

2. **Web Interface Test:**
   - Go to: `http://localhost:8501`
   - Type: "Hello, what can you help me with?"
   - Should get a response about equipment financing

3. **API Test:**
   - Use the curl command from Step 5
   - Should get a JSON response with agent reply

### Sample Questions to Try
- "What are your equipment financing rates?"
- "I need financing for manufacturing equipment"
- "Can you help me check my eligibility?"
- "What documents do I need to apply?"
- "Compare your loan options"

---

## 🛠️ Troubleshooting

### "Python is not recognized"
- Reinstall Python and make sure to check "Add to PATH"
- Or use full path: `C:\Python311\python.exe` instead of `python`

### "Module not found" errors
- Run: `pip install -r requirements.txt` again
- Make sure you're in the project folder

### "Port already in use" error
- Close other applications using port 8000 or 8501
- Or change ports in the code (advanced)

### API Key errors
- Check your `.env` file has correct keys
- Or remove the file to use mock mode

### Streamlit won't start
- Try: `python -m streamlit run frontend/app.py --server.port 8502`
- Or check if port 8501 is blocked

### Slow responses
- This is normal for AI processing
- Mock mode is faster than real API calls

### Application crashes
- Check the command prompt windows for error messages
- Make sure you have enough RAM (4GB minimum)

---

## 📞 Getting Help

### If Something Goes Wrong:
1. Check the troubleshooting section above
2. Look at error messages in the command prompt windows
3. Ask your instructor or team member
4. Check the project documentation in `docs/` folder

### Useful Files to Check:
- `docs/PHASE_8_QUICK_START.md` - Deployment guide
- `docs/PHASE_9_EVALUATION.md` - Testing guide
- `backend/deploy_server.py` - API server code
- `frontend/app.py` - Web interface code

---

## 🎉 Success Checklist

- [ ] Python installed and working
- [ ] Project downloaded and extracted
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API server running on port 8000
- [ ] Web interface running on port 8501
- [ ] Can ask questions and get responses
- [ ] Health check works: `http://localhost:8000/health`

**Congratulations!** You now have a working AI Banking Support Agent that can help customers with equipment financing questions.

---

*Last Updated: May 5, 2026*