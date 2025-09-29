# 📦 Installation Guide for Cargo Hitchhiking Simulation

## 🎯 **What You Need**

### **Required Software:**
- **Python 3.7 or higher** (the programming language)
- **Git** (to download the project) - optional

### **Operating System:**
- ✅ **Windows 10/11**
- ✅ **macOS 10.14 or higher**
- ✅ **Linux (Ubuntu 18.04 or higher)**

## 🚀 **Step-by-Step Installation**

### **Step 1: Install Python**

#### **Windows:**
1. Go to [python.org](https://www.python.org/downloads/)
2. Click "Download Python 3.x.x"
3. Run the installer
4. **IMPORTANT**: Check "Add Python to PATH" during installation
5. Click "Install Now"

#### **macOS:**
1. Open Terminal
2. Run: `brew install python3` (if you have Homebrew)
3. Or download from [python.org](https://www.python.org/downloads/)

#### **Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### **Step 2: Verify Python Installation**

Open Terminal/Command Prompt and run:
```bash
python3 --version
```

You should see something like: `Python 3.9.7`

### **Step 3: Download the Project**

#### **Option A: If you have Git:**
```bash
git clone [project-url]
cd cargo
```

#### **Option B: Download as ZIP:**
1. Download the project ZIP file
2. Extract it to a folder
3. Open Terminal/Command Prompt
4. Navigate to the extracted folder:
   ```bash
   cd /path/to/cargo/folder
   ```

### **Step 4: Create Virtual Environment**

#### **Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### **macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**You should see `(venv)` at the start of your command line.**

### **Step 5: Install Dependencies**

```bash
pip install -r requirements.txt
```

*If requirements.txt doesn't exist, the project should work with basic Python libraries.*

### **Step 6: Run the Simulation**

```bash
python3 main.py
```

## 🔧 **Troubleshooting**

### **"python3 not found"**
- Try: `python main.py` instead of `python3 main.py`
- Make sure Python is installed and added to PATH

### **"venv not found"**
- Make sure you're in the correct project folder
- Check if the `venv` folder exists

### **"Module not found"**
- Make sure virtual environment is activated (you should see `(venv)`)
- Try: `pip install -r requirements.txt`

### **"Permission denied" (macOS/Linux)**
```bash
chmod +x venv/bin/activate
```

### **"pip not found"**
```bash
python -m pip install --upgrade pip
```

## 📋 **Quick Test**

After installation, run this to test everything:

```bash
# Activate virtual environment
source venv/bin/activate  # (macOS/Linux)
# OR
venv\Scripts\activate     # (Windows)

# Run simulation
python3 main.py

# Choose option 1 when prompted
```

## 🎉 **Success!**

If you see the Metro simulation running with results in Pakistani Rupees, everything is working correctly!

## 📞 **Need Help?**

If you encounter issues:

1. **Check Python version**: `python3 --version`
2. **Check if you're in the right folder**: `ls` (macOS/Linux) or `dir` (Windows)
3. **Check if virtual environment is active**: You should see `(venv)` at the start of your command line
4. **Try running with `python` instead of `python3`**

## 📁 **Project Structure**

After installation, your folder should look like this:
```
cargo/
├── main.py              ← Run this file!
├── README.md            ← This guide
├── INSTALLATION_GUIDE.md ← This file
├── sim/                 ← Simulation engine
├── venv/                ← Virtual environment
└── Documentation files
```

---

**Ready to run your Metro cargo delivery simulation!** 🚛✨
