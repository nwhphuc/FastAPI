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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎯 Khai báo dữ liệu đầu vào – ĐÃ BỎ user_agent
class UserActivity(BaseModel):
    username: str
    activity: str

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
    log_message = f"[{now}] User: {data.username} | IP: {ip} | Activity: {data.activity}"
    logging.info(log_message)

    # Ghi log vào file CSV
    log_file_path = "data/log_access.csv"
    os.makedirs("data", exist_ok=True)

    new_log = {
        "time": now,
        "username": data.username,
        "ip": ip,
        "activity": data.activity
    }

    df_new = pd.DataFrame([new_log])
    if os.path.exists(log_file_path):
        df_old = pd.read_csv(log_file_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    # 📌 Chuyển cột thời gian thành datetime để lọc
    df_all["time"] = pd.to_datetime(df_all["time"], errors='coerce')
    df_all = df_all.dropna(subset=["time"])  # ✅ Bỏ dòng không convert được
    
    # 🔁 Giữ lại log trong 60 ngày gần nhất
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=60)
    df_all = df_all[df_all["time"] >= cutoff_date]

    # 💾 Ghi lại file sau khi lọc
    df_all.to_csv(log_file_path, index=False)


    return {"status": "ok", "message": "Log added successfully"}

# API xem log gần nhất
@app.get("/view_log")
def view_log():
    log_file_path = "data/log_access.csv"
    try:
        if os.path.exists(log_file_path):
            df = pd.read_csv(log_file_path)
            return df.tail(50).to_dict(orient="records")
        else:
            return {"log": [], "note": "Log chưa tồn tại"}
    except Exception as e:
        return {"error": str(e)}

from fastapi.responses import JSONResponse

# API ping để uptime - hỗ trợ GET + HEAD, ẩn khỏi docs
@app.get("/ping", include_in_schema=False)
@app.head("/ping", include_in_schema=False)
async def ping():
    return JSONResponse(content={"status": "ok"})


