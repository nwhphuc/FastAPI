from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime
import logging
import os
import pandas as pd

app = FastAPI()

# CORS cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả domain, có thể giới hạn sau
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khai báo dữ liệu đầu vào
class UserActivity(BaseModel):
    username: str
    activity: str
    user_agent: str

# API root
@app.get("/")
def read_root():
    return {"message": "RMA Log API is running"}

# API ghi log truy cập
@app.post("/log_user_activity")
async def log_user_activity(data: UserActivity, request: Request):
    ip = request.client.host
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ghi log ra console
    log_message = f"[{now}] User: {data.username} | IP: {ip} | Activity: {data.activity} | User-Agent: {data.user_agent}"
    logging.info(log_message)

    # Ghi log vào file CSV
    log_file_path = "data/log_access.csv"
    os.makedirs("data", exist_ok=True)

    new_log = {
        "time": now,
        "username": data.username,
        "ip": ip,
        "activity": data.activity,
        "user_agent": data.user_agent,
    }

    df_new = pd.DataFrame([new_log])
    if os.path.exists(log_file_path):
        df_old = pd.read_csv(log_file_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(log_file_path, index=False)

    return {"status": "ok", "message": "Log added successfully"}
