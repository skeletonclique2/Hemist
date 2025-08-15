# 🚀 System Startup Commands - Complete Guide

## **After Computer Restart - Run These Commands in Order:**

### **1. Navigate to Project Directory**
```bash
cd /Users/a/Documents/Hemist
```

### **2. Activate Python Environment**
```bash
conda activate hem
# OR if using venv:
# source hem/bin/activate
```

### **3. Start Database Services (Docker)**
```bash
# Set Docker path
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Start PostgreSQL and Redis containers
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Should show:
# hemist-postgres-1   Up (healthy)
# hemist-redis-1      Up (healthy)
```

### **4. Initialize Database (if needed)**
```bash
# Check if tables exist
docker exec -it hemist-postgres-1 psql -U ai_user -d ai_agents -c "\dt"

# If no tables, run initialization
python -c "
import asyncio
from app.database.connection import init_db
asyncio.run(init_db())
"
```

### **5. Start Backend API Server**
```bash
# In Terminal 1
uvicorn app.main:app --reload

# Should show:
# INFO: Uvicorn running on http://127.0.0.1:8000
```

### **6. Start Frontend (Streamlit)**
```bash
# In Terminal 2 (new terminal window)
cd /Users/a/Documents/Hemist
conda activate hem
streamlit run app/frontend/streamlit_app.py

# Should show:
# Local URL: http://localhost:8501
```

### **7. Verify Everything is Working**
```bash
# Test API health
curl http://localhost:8000/health

# Test login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "skeletoncliqs", "password": "Lolxxxno1"}'
```

---

## **Quick One-Command Startup Script**

Create this script for easy startup:

```bash
# Save as start_system.sh
#!/bin/bash
cd /Users/a/Documents/Hemist
conda activate hem
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
docker-compose up -d postgres redis
echo "Waiting for database to be ready..."
sleep 10
echo "Starting backend API..."
uvicorn app.main:app --reload &
echo "Starting frontend..."
streamlit run app/frontend/streamlit_app.py
```

Then run: `chmod +x start_system.sh && ./start_system.sh`

---

## **Login Credentials**
- **Admin:** skeletoncliqs / Lolxxxno1
- **Admin:** admin / adminpassword  
- **User:** user / userpassword
- **Demo:** demo / demo123

---

## **URLs After Startup**
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:8501
- **Database:** localhost:5432 (PostgreSQL)
- **Redis:** localhost:6379

---

## **Troubleshooting**

### **If Docker containers won't start:**
```bash
docker-compose down
docker-compose up -d postgres redis
```

### **If database connection fails:**
```bash
# Restart PostgreSQL
docker-compose restart postgres
# Wait 10 seconds, then test connection
```

### **If API won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill process if needed, then restart API
```

### **If Streamlit won't start:**
```bash
# Check if port 8501 is in use  
lsof -i :8501
# Kill process if needed, then restart Streamlit
