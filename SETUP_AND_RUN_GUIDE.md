# NBFC Agentic AI - Complete Setup & Run Guide

## 📋 Prerequisites

Before running the system, ensure you have:
- **Python 3.14** installed
- **Node.js 18+** installed
- **Ollama** installed with `llama3.1:8b` model
- **Git Bash or PowerShell** terminal

## 🚀 Step-by-Step Startup Instructions

### **Step 0: Verify Project Structure**
```bash
cd "d:\Ey techathon\nbfc-agentic-ai"
ls -la  # Verify src/, package.json, etc. exist
```

---

## 🔧 Backend Services (Start in Separate Terminals)

### **Terminal 1: Start Ollama LLM Server** ⚡
```bash
ollama serve
```
**Expected Output:**
```
time=2026-06-22T18:28:16.014+05:30 level=INFO source=routes.go:1810 msg="Listening on 127.0.0.1:11434 (version 0.20.7)"
```
**Port:** 11434

---

### **Terminal 2: Start External Dummy APIs** 🌐
```bash
cd "d:\Ey techathon\nbfc-agentic-ai\src"
$env:PYTHONPATH="d:\Ey techathon\nbfc-agentic-ai\src"
python -m uvicorn apis.external.external_dummy_apis:app --port 8002 --host 127.0.0.1
```
**Expected Output:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```
**Port:** 8002  
**Endpoints:** `/pan/verify`, `/bank/statements`, `/credit/scores`, `/crm/verify`, `/esign/sign`, `/disbursement/process`

---

### **Terminal 3: Start Offer Mart API** 💰
```bash
cd "d:\Ey techathon\nbfc-agentic-ai\src"
$env:PYTHONPATH="d:\Ey techathon\nbfc-agentic-ai\src"
python -m uvicorn apis.offer_mart.offer_mart_api:app --port 8001 --host 127.0.0.1
```
**Expected Output:**
```
LOADED OFFERS: [{'offer_id': 'OFF001', 'customer_id': 'C001', ...}, ...]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```
**Port:** 8001  
**Endpoints:** `/offers/{customer_id}`, `/all-offers`

---

### **Terminal 4: Start Master Agent API** 🤖
```bash
cd "d:\Ey techathon\nbfc-agentic-ai\src"
$env:PYTHONPATH="d:\Ey techathon\nbfc-agentic-ai\src"
python -m uvicorn apis.master_agent_api:app --port 8000 --host 127.0.0.1
```
**Expected Output:**
```
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
**Port:** 8000  
**Endpoints:** `/chat`, `/workflow`  
**Note:** Python 3.14 warning is non-blocking

---

### **Terminal 5: Start API Gateway** 🚪
```bash
cd "d:\Ey techathon\nbfc-agentic-ai\src"
$env:PYTHONPATH="d:\Ey techathon\nbfc-agentic-ai\src"
python -m uvicorn apis.gateway_api:app --port 9000 --host 127.0.0.1
```
**Expected Output:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```
**Port:** 9000  
**Endpoints:** `/chat`, `/upload`, `/health`

---

### **Terminal 6: Start Frontend (Next.js)** 🎨
```bash
cd "d:\Ey techathon\nbfc-agentic-ai"
npm run dev
```
**Expected Output:**
```
▲ Next.js 16.1.1 (Turbopack)
- Local:         http://localhost:3000
- Environments: .env.local
✓ Ready in 5.1s
```
**Port:** 3000  
**URL:** http://localhost:3000

---

## 📊 Verify All Services Are Running

### Quick Health Check (Python Script)
```python
import requests

print("Checking all services...")
services = {
    "Ollama": "http://127.0.0.1:11434/api/generate",
    "External APIs": "http://127.0.0.1:8002/openapi.json",
    "Offer Mart": "http://127.0.0.1:8001/openapi.json",
    "Master Agent": "http://127.0.0.1:8000/openapi.json",
    "Gateway": "http://127.0.0.1:9000/health",
    "Frontend": "http://127.0.0.1:3000"
}

for name, url in services.items():
    try:
        resp = requests.get(url, timeout=2)
        print(f"✓ {name}: {resp.status_code}")
    except:
        print(f"✗ {name}: NOT RESPONDING")
```

---

## 💬 Chatbot Testing Guide

### **Access the Chatbot**
1. Open browser: http://localhost:3000
2. Click "Login" → Use Google OAuth
3. Use test email: `saispandana.chalasani05@gmail.com`
4. Navigate to `/chatbot` page

---

### **Test Scenario 1: Approved Loan Application** ✅

**Customer:** C001 (Credit Score: 750, Salary: ₹75,000)

**What to Ask the Chatbot:**
```
"Hello, I want to apply for a personal loan of 150000 rupees"
```

**Expected Conversation Flow:**

1. **Chatbot Response (Offer):**
   > "Based on the offers found, it appears that you are pre-approved for a loan of ₹1,50,000 with an APR of 13.5% and a tenure of 36 months. Would you like to proceed with the pre-approved offer?"

2. **Ask:**
   ```
   "Yes, I would like to proceed with the pre-approved offer"
   ```

3. **Chatbot Response (KYC Verification):**
   > "Great! Let's proceed with the KYC verification. Please provide your PAN (Permanent Account Number)"

4. **Ask:**
   ```
   "My PAN is AAAPA5055K"
   ```

5. **Chatbot Response (Income Verification):**
   > "KYC verified! Now let's verify your income. Please share your latest salary slip or bank statement"

6. **Ask:**
   ```
   "I am uploading my salary slip now"
   ```

7. **Chatbot Response (Compliance Check):**
   > "Income verified! Let's check compliance requirements."

8. **Chatbot Response (Underwriting):**
   > "Compliance passed! Your application is approved for underwriting."

9. **Chatbot Response (Pricing):**
   > "Based on your profile, your interest rate is 13.5% APR with 36 months tenure."

10. **Chatbot Response (Document):**
    > "Your sanction letter has been generated."

11. **Ask:**
    ```
    "I agree to sign the documents"
    ```

12. **Chatbot Response (eSign):**
    > "Documents signed successfully! Signature ID: SIG-abc12345"

13. **Chatbot Response (Disbursement):**
    > "Your loan of ₹1,50,000 has been disbursed to your account. Bank Reference: NBFC-1234-5678. Expected credit: 2 business days."

---

### **Test Scenario 2: Rejection Case** ❌

**Customer:** C004 (Credit Score: 620 - Below 700, Blacklisted)

**What to Ask the Chatbot:**
```
"I would like to apply for a personal loan of 200000"
```

**Expected Response:**
> "I'm sorry, but based on our review of your profile, your credit score of 620 is below our minimum requirement of 700. Additionally, we're unable to proceed with your application at this time. Please try again after improving your credit score."

---

### **Test Scenario 3: Amount Exceeds Pre-Approved Offer** 🎯

**Customer:** C001 (Pre-approved: ₹150,000)

**What to Ask the Chatbot:**
```
"I want a loan for 300000 rupees"
```

**Expected Response:**
> "Your requested amount of ₹3,00,000 exceeds your pre-approved limit of ₹1,50,000. Would you like to proceed with the pre-approved amount, or would you like me to process your request for a higher amount (which may require additional verification)?"

---

### **Test Scenario 4: File Upload** 📄

During the workflow when prompted for salary slip:

1. **Chatbot asks:**
   > "Please upload your salary slip or bank statement"

2. **You can test via API:**
   ```bash
   curl -X POST "http://127.0.0.1:9000/upload" \
     -F "customer_id=C001" \
     -F "file=@/path/to/salary_slip.pdf"
   ```

3. **Expected Response:**
   ```json
   {
     "status": "success",
     "filename": "salary_slip.pdf",
     "filepath": "src/apis/uploads/C001/salary_slip.pdf",
     "message": "Document uploaded successfully"
   }
   ```

---

## 🔍 Monitoring & Debugging

### **View Master Agent Processing**
Watch Terminal 4 output to see:
- Agent tool calls
- LLM inference responses
- Customer profile details

### **View Ollama LLM Responses**
Watch Terminal 1 output to see:
- Model loading
- Token generation
- Response timing

### **Check Shared Memory**
Access stored conversation context:
```python
from utils.memory import get_shared_memory

memory = get_shared_memory()
history = memory.get_conversation_history('C001')
print(history)
```

---

## ⚙️ Backend API Endpoints

### **Gateway (9000)**
- `GET /health` - Health check
- `POST /chat` - Chat endpoint (email-based)
  ```json
  {
    "email": "user@example.com",
    "message": "loan request message"
  }
  ```
- `POST /upload` - File upload
- `GET /documents/{customer_id}` - Get stored documents

### **Master Agent (8000)**
- `POST /chat` - Direct chat (customer_id-based)
  ```json
  {
    "customer_id": "C001",
    "message": "loan request message"
  }
  ```
- `GET /health` - Health check

### **Offer Mart (8001)**
- `GET /offers/{customer_id}` - Get offers for specific customer
- `GET /all-offers` - Get all offers

### **External APIs (8002)**
- `POST /pan/verify` - PAN verification
- `POST /bank/statements` - Bank statement retrieval
- `POST /credit/scores` - Credit score lookup
- `POST /crm/verify` - CRM verification
- `POST /esign/sign` - Digital signing
- `POST /disbursement/process` - Disbursement processing

---

## 🧪 Sample API Calls (via Terminal)

### **Test Direct Master Agent**
```bash
# For PowerShell:
$payload = @{
    customer_id = 'C001'
    message = 'I want a loan for 150000'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/chat' `
  -Method POST `
  -Body $payload `
  -ContentType 'application/json' `
  -UseBasicParsing
```

### **Test Gateway with Email**
```bash
# For PowerShell:
$payload = @{
    email = 'saispandana.chalasani05@gmail.com'
    message = 'I need a personal loan'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:9000/chat' `
  -Method POST `
  -Body $payload `
  -ContentType 'application/json' `
  -UseBasicParsing
```

---

## 🚨 Troubleshooting

### **Issue: Port Already in Use**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

### **Issue: ModuleNotFoundError**
```bash
# Make sure PYTHONPATH is set correctly
$env:PYTHONPATH="d:\Ey techathon\nbfc-agentic-ai\src"

# Run from src directory
cd "d:\Ey techathon\nbfc-agentic-ai\src"
```

### **Issue: Ollama Model Not Found**
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify model exists
ollama list
```

### **Issue: Frontend Won't Load**
```bash
# Clear cache and reinstall dependencies
cd "d:\Ey techathon\nbfc-agentic-ai"
rm -r node_modules .next
npm install
npm run dev
```

---

## ✅ Complete System Checklist

Before testing, verify:
- [ ] All 6 terminals have services running (no errors)
- [ ] Ollama is listening on 11434
- [ ] External APIs running on 8002 (shows loaded offers)
- [ ] Offer Mart running on 8001
- [ ] Master Agent running on 8000 (Python 3.14 warning is OK)
- [ ] Gateway running on 9000
- [ ] Frontend running on 3000
- [ ] Frontend loads without errors in browser
- [ ] Google OAuth is configured

---

## 📝 Test Summary

| Test Case | Customer | Expected Result |
|-----------|----------|-----------------|
| Approved Loan | C001 (score 750) | Loan approved, full workflow |
| Rejection | C004 (score 620) | Rejected at credit check |
| High Amount | C001 | Exceeds pre-approved, ask for verification |
| Low Amount | Any | Quick approval if eligible |

---

**You're ready to go! 🚀**
