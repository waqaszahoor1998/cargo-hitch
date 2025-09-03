# 🚚 Cargo Hitchhiking Simulation - Client Guide

## 📋 **What This Project Does**

This is a **cargo delivery simulation** that models how Metro buses can be used to deliver packages from Metro Cash & Carry stores. Think of it like Uber for packages, but using public buses!

**IMPORTANT: This simulation includes both real data and estimated data:**

- **Real Data**: Metro Cash & Carry operations (orders, pricing, delivery charges, trucks, buses, routes from Excel file)
- **Real Metro Operations**: 3-4 Shahzore trucks (1000kg payload), 16-20 Metro buses, 3 routes, Islamabad/Rawalpindi coverage
- **Estimated Data**: Traditional delivery comparison (based on industry benchmarks, not real Metro data)

### **Key Features:**
- ✅ **Real Metro Data**: Uses actual Metro Cash & Carry order data and pricing from Excel file
- ✅ **Hitchhiking vs Traditional Comparison**: Compare cargo hitchhiking with traditional delivery methods
- ✅ **Pakistani Rupees**: All prices shown in Rs (not dollars)
- ✅ **Detailed Shipping Info**: Shows which bus, route, and time slot for each delivery
- ✅ **Business Analysis**: Tracks revenue, costs, and success rates
- ✅ **Professional Output**: Clean, easy-to-read results

## 🚀 **How to Run the Project (Simple Steps)**

### **Step 1: Open Terminal/Command Prompt**
- **Windows**: Press `Windows + R`, type `cmd`, press Enter
- **Mac**: Press `Command + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### **Step 2: Navigate to Project Folder**
```bash
cd /path/to/your/cargo/folder
```
*Replace `/path/to/your/cargo/folder` with the actual location of your project*

### **Step 3: Activate Virtual Environment**
```bash
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### **Step 4: Run the Simulation**
```bash
python3 main.py
```

### **Step 5: Choose Your Option**
You'll see a menu with 3 options:
- **Option 1**: Metro Main Simulation (Recommended) ← Choose this!
- **Option 2**: Metro Scenario Comparison (Advanced analysis)
- **Option 3**: Hitchhiking vs Traditional Delivery Comparison

Type `1` and press Enter.

### **Step 6: Watch the Results!**
The simulation will run and show you:
- Metro bus information
- Order matching process
- Detailed delivery information
- Financial summary in Pakistani Rupees

## 📁 **Project Structure Explained**

### **Main Files:**
```
cargo/
├── main.py                    ← START HERE! Main program
├── README.md                  ← This file (instructions)
├── sim/                       ← Simulation engine folder
│   ├── engine.py             ← Core simulation logic
│   ├── entities.py           ← Data models (orders, drivers)
│   ├── events.py             ← Event system
│   ├── kpi.py                ← Performance tracking
│   ├── config.py             ← Settings and constants
│   ├── matcher/              ← Order-driver matching
│   └── policies/             ← Pricing and business rules
└── Documentation files        ← Project requirements
```

### **What Each File Does:**

#### **🚀 main.py (Main Program)**
- **Purpose**: Entry point - this is what you run
- **What it does**: 
  - Shows the menu
  - Runs the Metro simulation
  - Displays results in Pakistani Rupees
  - Shows detailed shipping information

#### **⚙️ sim/engine.py (Simulation Engine)**
- **Purpose**: The "brain" of the simulation
- **What it does**:
  - Creates 300 orders (like Metro Cash & Carry daily orders)
  - Creates 39 drivers (3 per Metro bus)
  - Matches orders to drivers
  - Tracks delivery progress
  - Calculates distances and times

#### **📦 sim/entities.py (Data Models)**
- **Purpose**: Defines what orders and drivers look like
- **What it does**:
  - Order: pickup location, drop location, size, price
  - Driver: vehicle type, capacity, current location
  - Fleet: backup delivery vehicles

#### **⏰ sim/events.py (Event System)**
- **Purpose**: Manages what happens when
- **What it does**:
  - Driver arrives at work
  - Order gets picked up
  - Delivery completed
  - Time ticks (every 15 minutes)

#### **📊 sim/kpi.py (Performance Tracking)**
- **Purpose**: Calculates business metrics
- **What it does**:
  - Success rate (how many orders delivered)
  - Revenue and profit in Pakistani Rupees
  - Delivery times and costs
  - Environmental impact (CO2 emissions)

#### **⚙️ sim/config.py (Settings)**
- **Purpose**: All the numbers and settings
- **What it does**:
  - Islamabad coordinates (33.7294, 73.0931)
  - Metro bus routes
  - Pricing rules
  - Time windows

#### **🔍 sim/matcher/ (Matching System)**
- **Purpose**: Decides which driver gets which order
- **What it does**:
  - Finds best driver for each order
  - Checks if driver can reach pickup in time
  - Considers vehicle capacity
  - Optimizes routes

#### **💰 sim/policies/ (Business Rules)**
- **Purpose**: Pricing and payment calculations
- **What it does**:
  - Calculates delivery charges in Rs
  - Determines driver wages
  - Applies surge pricing
  - Calculates platform profit

## 📊 **Understanding the Results**

### **What You'll See:**

1. **Metro Bus Information:**
   - 16-20 Metro buses (from Excel file)
   - 3 routes covering Islamabad and Rawalpindi areas
   - Real Metro operations data

2. **Metro Cash & Carry Operations:**
   - 280 daily orders (from Excel file)
   - 3-4 Shahzore trucks with 1000kg payload each
   - Less than 1% cancellation rate (0.6% return rate)
   - Delivery charges: Rs 99 (standard), Rs 129 (premium)
   - 4 time slots: 10 AM-1 PM, 1 PM-4 PM, 4 PM-7 PM, 7 PM-10 PM

3. **Simulation Progress:**
   - Shows how many orders are matched vs unmatched
   - Updates every hour (tick)
   - Shows available drivers

4. **Detailed Shipping Information:**
   - Which Metro bus (Metro_Bus_01, Metro_Bus_02, etc.)
   - Which route (Faiz Ahmed Faiz → Blue Area, etc.)
   - Pickup and dropoff coordinates
   - Delivery charge in Rs

5. **Financial Summary:**
   - Total Revenue in Pakistani Rupees
   - Driver Costs
   - Platform Profit
   - Average delivery cost
   - Success rate percentage

### **Example Output:**
```
METRO SIMULATION RESULTS
--------------------------------------------------
Total Orders: 300
Successfully Matched: 49
Success Rate: 16.3%

DETAILED SHIPPING INFORMATION
--------------------------------------------------
   Delivery #1:
      Vehicle: Metro_Bus_11
      Route: Route 1: Faiz Ahmed Faiz - Blue Area
      Time Slot: 10 AM - 1 PM
      Pickup: (33.8214, 72.8606)
      Dropoff: (33.6837, 73.1126)
      Delivery Charge: Rs 130

KPI SUMMARY (Pakistani Rupees)
----------------------------------------
   Total Revenue: Rs 5,712
   Driver Costs: Rs 3,427
   Platform Profit: Rs 2,285
   Average Delivery Cost: Rs 117
```

## 🔧 **Troubleshooting**

### **Common Issues:**

**"python3 not found"**
- Try: `python main.py` instead of `python3 main.py`

**"venv not found"**
- Make sure you're in the correct folder
- Check if `venv` folder exists

**"Module not found"**
- Make sure virtual environment is activated
- You should see `(venv)` at the start of your command line

**"Permission denied"**
- On Mac/Linux, try: `chmod +x venv/bin/activate`

## 📞 **Need Help?**

If you encounter any issues:
1. Make sure you're in the correct folder
2. Make sure virtual environment is activated
3. Try running `python main.py` instead of `python3 main.py`
4. Check that all files are present in the project folder

## 🎯 **What This Simulation Proves**

This simulation demonstrates:
- **Feasibility**: Metro buses can handle cargo delivery
- **Efficiency**: 16.3% success rate with current constraints
- **Profitability**: Platform can make profit in Pakistani Rupees
- **Scalability**: Can handle 300 daily orders
- **Sustainability**: Reduces CO2 emissions compared to dedicated delivery vehicles

The simulation uses **real Metro Cash & Carry data** including trucks, buses, routes, and operations from the Excel file, plus **real geographic data** from Islamabad and Rawalpindi areas to provide accurate, practical results for cargo hitchhiking implementation.

---

**Ready to run? Just follow the steps above and watch your Metro cargo delivery simulation in action!** 🚛✨
