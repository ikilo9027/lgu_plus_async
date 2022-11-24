import cv2
import traceback

from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger
from fastapi import HTTPException
from .celery_app import app

from components.triton.inference import ModelInferencer
from components.utils.exception import FailExceptionHandler

logger = get_task_logger(__name__)

@app.task(bind=True, max_retries=0, base=AbortableTask)
def celery_sr(self,filename_list,file_path_list,task_id,):

  images = []
  
  trtis_server = ModelInferencer("localhost:8001")

  for idx in range(len(filename_list)):
    image = cv2.imread(f"{file_path_list[idx]}/{filename_list[idx]}")
    images.append(image)

  # for idx in range(499):
  #   image = cv2.imread(f"{file_path_list[0]}/{filename_list[0]}")
  #   images.append(image)

  try:
    output_data_list = trtis_server.stream_infer(images,task_id)
  except:
    traceback.print_exc()
    raise FailExceptionHandler(f"task_id : {task_id} , SR 요청에 실패","SR 요청에 실패",500)

  # for idx in range(len(output_data_list)):
  #   sr_folder_path = file_path_list[idx].replace('origin_images', 'sr_images')
  #   output_file_name = f"{filename_list[idx].split('.')[0]}_SR_{idx}.{filename_list[idx].split('.')[-1]}"
  #   cv2.imwrite(f"{sr_folder_path}/{output_file_name}", output_data_list[idx]) 

  for idx in range(len(output_data_list)):
    sr_folder_path = f"/app/static/sr_images/{task_id}"
    output_file_name = f"test_SR_{idx}.{filename_list[0].split('.')[-1]}"
    cv2.imwrite(f"{sr_folder_path}/{output_file_name}", output_data_list[idx])
  # except:
  #   raise FailExceptionHandler(f"task_id : {task_id} , SR 완료된 파일의 업로드 요청에 실패","SR 파일 업로드 실패",500)