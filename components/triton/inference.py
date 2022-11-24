from functools import partial
import queue
import sys
import json
import cv2
import numpy as np

import tritonclient.grpc as grpcclient
from components.triton.utils import preprocess, postprocess

from components.worker.celery_app import app
from celery.exceptions import Ignore
from celery import states
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore


from fastapi import HTTPException
            
logger = get_task_logger(__name__)
# if __name__ == "__main__":
    
# else:
#     from components.triton.utils import preprocess, postprocess

class UserData:
    def __init__(
        self,
        count_image_data,
        task_id,
        model_name,
        triton_client,
        result_model_name,
    ):
        self.completed_requests = queue.Queue()
        self.count_image_data = count_image_data
        self.task_id = task_id
        self.model_name = model_name
        self.triton_client = triton_client
        self.result_model_name = result_model_name
        self.infer_count = 0

def task_check(task_id):
    t = AsyncResult(id=task_id, app=app)
    return t.state

def completion_callback(user_data, result, error):

    user_data.completed_requests.put((result, error))
    t = AsyncResult(id=user_data.task_id, app=app)
    
    user_data.infer_count += 1
    with open(f"/app/progress/{user_data.task_id}/progress.txt", "w") as f:
        json.dump(
            {
                "progress": "model",
                "SR_folder_path": user_data.result_model_name,
                "done": user_data.infer_count,
                "total":user_data.count_image_data,
                "state": t.state
            },
            f,
        )

def aborted_task_stop(self,task_id, triton_client):
    t = AsyncResult(id=task_id, app=app)
    print('state------------------>',t.state)
    if t.state == "ABORTED":
        self.update_state(state=states.FAILURE)
        triton_client.stop_stream()
    else:
        pass

class ModelInferencer:
    def __init__(self, url: str = "localhost:8001"):
        try:
            self.triton_client = grpcclient.InferenceServerClient(url)
        except Exception as e:
            print("channel creation failed: " + str(e))
            sys.exit()

    def infer(self, input_data: np.array):
        """
        이미지를 각각 넣어야합니다.
        """
        input0_data = preprocess(input_data)

        h, w = input0_data.shape[-2:]

        inputs = []
        outputs = []

        inputs.append(grpcclient.InferInput("input", input0_data.shape, "FP32"))
        inputs[0].set_data_from_numpy(input0_data)

        outputs.append(grpcclient.InferRequestedOutput("output"))

        # Inference
        results = self.triton_client.infer(
            model_name="SR_e", inputs=inputs, outputs=outputs
        )

        # Get the output arrays from the results
        output0_data = results.as_numpy("output")
        output0_data = postprocess(output0_data, h, w)

        return output0_data

    def stream_infer(self, input_data: list,task_id):
        """
        이미지의 리스트를 넣어줍니다.
        """
        result_data = []

        total_count = 0
        model_name = 'SR_e'
        result_model_name = f"/app/static/sr_images/{task_id}"
        
        # for infer_data in input_data:
        #     input0_data = [preprocess(infer_data)]
        #     total_count += len(input0_data)

        user_data = UserData(
            len(input_data),
            task_id,
            model_name,
            self.triton_client,
            result_model_name
        )
        self.triton_client.start_stream(partial(completion_callback, user_data))
        
        remainder = len(input_data) % 30 
        quotient = len(input_data) / 30 if remainder==0 else (len(input_data) / 30)+1

        for i in range(int(quotient)):
            print(quotient)

            aborted_task_stop(self,task_id, self.triton_client)
            number = remainder if remainder != 0 and i == int(quotient)-1 else 30

            for k in range(number):
                data_index = k+(30*i)
                # print("data_index------------",data_index)
                input0_data = preprocess(input_data[data_index])

                inputs = []
                outputs = []

                inputs.append(
                    grpcclient.InferInput("input", input0_data.shape, "FP32")
                )
                inputs[0].set_data_from_numpy(input0_data)

                outputs.append(grpcclient.InferRequestedOutput("output"))

                self.triton_client.async_stream_infer(
                    model_name="SR_e",
                    inputs=inputs,
                    outputs=outputs,
                )

            try:
                for j in range(number):
                    data_index = j+(30*i)

                    h, w, _ = input_data[data_index].shape

                    results, error = user_data.completed_requests.get()

                    if error is not None:
                        print(f"inference failed: {error}")

                    output0_data = results.as_numpy("output")
                    output0_data = postprocess(output0_data, h, w)

                    result_data.append(output0_data)
                
                
            except Exception:
                logger.error(task_id + " SR file upload failed")
                self.update_state(state=states.FAILURE)
                

        
        self.triton_client.stop_stream()
        print("SR SUCCESS!")
        logger.info(task_id + " end ")
        return result_data

if __name__ == "__main__":
    trtis_server = ModelInferencer("localhost:8001")
    # load image
    input0_data = cv2.imread(
        "/workspace/junseo/lgu_plus_sync/static/origin_images/caac6819db9b3e16e78384f3dcc217bc/Lenna6.png"
    )

    data = []

    for i in range(100):
        data.append(input0_data)

    output0_data = trtis_server.stream_infer(data)

    cv2.imwrite(
        "/workspace/junseo/lgu_plus_sync/static/origin_images/caac6819db9b3e16e78384f3dcc217bc/Lenna6_SR.png",
        output0_data[0],
    )

