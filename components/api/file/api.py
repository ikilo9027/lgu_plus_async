from pydantic import BaseModel

import json
import os
from xmlrpc.client import boolean
import cv2
from PIL import Image
import logging
import base64

from fastapi import APIRouter, File, HTTPException, UploadFile, Response
from typing import List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from celery import uuid
from celery.contrib.abortable import AbortableAsyncResult
from celery.result import AsyncResult
from components.worker.celery_app import app

from components.utils.file import createDirectory, deletefolder, expiration_date, expiration_progress
from components.utils.exception import FailExceptionHandler, SuccessExceptionHandler
from components.worker.celery_worker import celery_sr


log = logging.getLogger("uvicorn")
router = APIRouter(prefix="/esp/async_api/v2", tags=["SR"])

class TaskId(BaseModel):
    task_id: str

class Progress(BaseModel):
    progress: str
    SR_folder_path: str
    done: int
    total: int
    state: str


@router.post(
    "/file_upload_SR",
    summary="파일 업로드",
    status_code=200,
)
async def file_upload(files: List[UploadFile] = File(...)):

    task_id = uuid()
    # event_key = secrets.token_hex(nbytes=16)

    origin_image_path = f"/app/static/origin_images/{task_id}"
    sr_image_path = f"/app/static/sr_images/{task_id}"
    progress_path = f"/app/progress/{task_id}"

    createDirectory(origin_image_path)
    createDirectory(sr_image_path)
    createDirectory(progress_path)

# 생성된 날짜로부터 7일이 지난 파일은 삭제
    expiration_date('/app/static/origin_images')
    expiration_date('/app/static/sr_images')
    
    with open(f"{progress_path}/progress.txt", "w") as pf:
        json.dump(
            {
                "progress": "upload",
                "SR_folder_path": "str",
                "done": 0,
                "total": 0,
                "state": "null",
            },
            pf,
        )

    filename_list = []
    file_path_list = []
    if len(files) != 0:
        for file in files:
            file_path = os.path.join(origin_image_path, file.filename)

            if file.filename.split('.')[-1].lower().endswith(
                ("png", "jpg")
            ):
                try:
                    contents = await file.read()
                
                    with open(file_path, "wb") as fp:
                        fp.write(contents)
                except:
                    deletefolder(origin_image_path)
                    return FailExceptionHandler(f'{file.filename} 파일 업로드 요청에 실패하였습니다.', '파일 업로드 실패.', 500)
                        
                
                img = cv2.imread(file_path)
                h, w, _ = img.shape
                if w > 1920 or h > 1088 :
                    deletefolder(origin_image_path)
                    return FailExceptionHandler(f"해상도 1920 x 1088 이하인 파일만 업로드 가능합니다. , {file.filename} : {w} x {h}", '해상도 1920 x 1088 이하인 파일만 업로드 가능합니다.', 500)

                filename_list.append(file.filename)
                file_path_list.append(origin_image_path)

            else:
                return FailExceptionHandler(f"현재 업로드된 파일형식({file.filename.split('.')[-1]}), 지원 가능한 확장자(jpg, png).", '파일 형식이 맞지 않습니다.', 500)

        celery_sr.apply_async((filename_list, file_path_list , task_id ,),task_id=task_id,)
        
        expiration_progress()

        response = {
           'task_id': task_id
        }
        return JSONResponse(content=jsonable_encoder(response), status_code=200)
    else:
        return FailExceptionHandler("파일 업로드 & SR 요청 실패.", '파일 업로드 & SR 요청 실패.', 500)


@router.post(
    "/file_download",
    summary="파일 다운로드",
    responses={200: {"description": "Success File Download"}},
)
async def file_download(task_id: TaskId):
    """
    SR 요청을 통해 얻은 task_id 를 이용해 SR binary 다운로드
    """
    download_filelist=[]
    file_path = f"/app/static/sr_images/{task_id.task_id}"
    
    for file in os.listdir(file_path):
        try:
            image = cv2.imread(f"{file_path}/{file}")
            _, buffer = cv2.imencode(os.path.splitext(file)[1], image)
            binary = base64.b64encode(buffer)
        except:
            return FailExceptionHandler('파일 읽기에 실패하였습니다.', '파일 읽기 실패.', 500)
        filelist = {
            "filename": file,
            "file": str(binary)
        }

        download_filelist.append(filelist)
    return download_filelist


@router.post("/progress", summary="SR 진행상황 조회", response_model=Progress)
async def progress(task_id: TaskId):
    """
    모델 요청 후 inference 진행상황 조회\n
    ### state: PENDING(파일만 업로드되고 SR은 대기중인 상태) -> STARTED(SR 진행중) -> SUCCESS(SR 완료), FAILURE(에러)
    """
    progress_path = f"/app/progress/{task_id.task_id}"

    try:
        with open(f"{progress_path}/progress.txt", "r") as f:
            data = json.load(f)
    except Exception:
       
        return FailExceptionHandler(f'task_id : {task_id} , 파일을 찾을 수 없습니다.', '파일을 찾을 수 없습니다.', 500)

    # redis 에서 celery 상태값 조회
    t = AsyncResult(id=task_id.task_id, app=app)

    return Progress(
        progress=data["progress"],
        SR_folder_path=data["SR_folder_path"],
        done=int(data["done"]),
        total=int(data["total"]),
        state=t.state,
    )

@router.post(
    "/task_kill", summary="SR 중단", responses={200: {"description": "Success Task Kill"}}
)
async def task_kill(task_id: TaskId):
    """
    sr 진행중인 task를 강제로 종료.
    """
    task_id = task_id.task_id
    try:
        AbortableAsyncResult(task_id).abort()
        AsyncResult(id=task_id).revoke(terminate=True, signal="SIGKILL")
        # app.control.revoke(task_id,terminate=True, signal='SIGKILL')
        log.info("task kill")
        return Response("success task kill")
        # return SuccessExceptionHandler(f'task_id : {task_id} , success task kill.', 'success task kill.')
    except Exception:
        return FailExceptionHandler(f'task_id : {task_id} , fail task kill.', 'fail task kill.', 500)
