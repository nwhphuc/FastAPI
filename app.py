from fastapi import FastAPI, Request
import datetime
import logging
import os

# Khởi tạo FastAPI
app = FastAPI()

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Định nghĩa endpoint ghi log người dùng
@app.post("/log_user_activity")
async def log_user_activity(request: Request):
    try:
        data = await request.json()
        username = data.get("username", "Unknown")
        activity = data.get("activity", "No activity")
        ip = request.client.host
        user_agent = data.get("userAgent", "Unknown")

        # Ghi log vào console (hoặc file)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{now}] User: {username} | IP: {ip} | Activity: {activity} | User-Agent: {user_agent}"
        logging.info(log_message)

        return {"status": "ok", "message": "Log added successfully"}
    except Exception as e:
        logging.error(f"Error logging activity: {e}")
        return {"status": "error", "message": str(e)}

