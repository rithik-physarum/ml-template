import os
import os.path as op
import uvicorn
import logging
import json

from fastapi import Request, FastAPI

from online_prediction import app_config
from online_prediction.predict_handler import PredictHandler


app = FastAPI()

pred_handler = PredictHandler(app_config.model_path, app_config.model_name)
pred_handler.load_model()


@app.post("/predict")
async def predict(request: Request):
    """
    Prediction endpoint on FastAPI.

    This function will get the JSON from the request,
    run the prediction on the model object,
    and tidy up the prediction to meet JSON output format.

    Parameters
    ----------
    request : Request
        The request object containing the payload JSON.

    Returns
    -------
    dict
        The JSON outcome with predictions.

    """

    body = await request.json()
    instances = body.get("instances")
    outputs = []

    for req in instances:
        prediction = pred_handler.predict(req)
        outputs.append(prediction)

    return json.loads(json.dumps(dict(predictions=outputs)))


@app.get("/health")
def health():
    """
    Ping endpoint for health check or debug on FastAPI.

    Returns
    -------
    dict
        The status of the service.

    """
    return json.loads(json.dumps({"status": 200}))


if __name__ == "__main__":
    uvicorn.run(app, port=8080, debug=True)
