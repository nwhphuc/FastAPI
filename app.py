from fastapi import FastAPI, Request
import datetime
import logging
import os
import pandas as pd

# Khởi tạo FastAPI
app = FastAPI()

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Đường dẫn file log
LOG_FILE = "data/log_access.csv"

# Định nghĩa endpoint ghi log người dùng
@app.post("/log_user_activity")
async def log_user_activity(request: Request):
    try:
        data = await request.json()
        username = data.get("username", "Unknown")
        activity = data.get("activity", "No activity")
        ip = request.client.host
        user_agent = data.get("userAgent", "Unknown")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ghi ra log console
        log_message = f"[{now}] User: {username} | IP: {ip} | Activity: {activity} | User-Agent: {user_agent}"
        logging.info(log_message)

        # Ghi vào file CSV
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(LOG_FILE):
            df = pd.DataFrame(columns=["time", "username", "ip", "activity", "user_agent"])
            df.to_csv(LOG_FILE, index=False)

        df = pd.read_csv(LOG_FILE)
        new_row = {
            "time": now,
            "username": username,
            "ip": ip,
            "activity": activity,
            "user_agent": user_agent
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)

        return {"status": "ok", "message": "Log added successfully"}
    except Exception as e:
        logging.error(f"Error logging activity: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"message": "RMA Log API is running"}
