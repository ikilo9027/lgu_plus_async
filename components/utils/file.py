import os
from datetime import datetime
from pytz import timezone
from dateutil import relativedelta
import time
import shutil
import json
from celery.result import AsyncResult
from components.worker.celery_app import app

def createDirectory(directory: str):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")


# def deleteFile(directory: str):
#     try:
#         if os.path.exists(directory):
#             os.remove(directory)
#     except OSError:
#         print("Error: Failed to delete the file.")


def deletefolder(directory: str):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    except OSError:
        print("Error: Failed to delete the file.")


def expiration_date(file_path: str):
    for folder in os.listdir(file_path):
        now_date = datetime.now(timezone('Asia/Seoul')).strftime("%c")
        create_date = time.ctime(os.path.getmtime(f"{file_path}/{folder}"))
        week_later = (datetime.strptime(create_date, "%c") +
                      relativedelta.relativedelta(days=7)).strftime("%c")
        if week_later <= now_date:
            deletefolder(f"{file_path}/{folder}")

def expiration_progress():
    progress_list_path = '/app/progress'
    for folder in os.listdir(progress_list_path):
        t = AsyncResult(id=folder, app=app)
        if(t.state == "SUCCESS"):
            try:
                if os.path.exists(f"{progress_list_path}/{folder}"):
                    shutil.rmtree(f"{progress_list_path}/{folder}")
            except OSError:
                print("Error: Failed to delete the file.")