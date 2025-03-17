from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from mlops_decorators.core.feature_api import Client
from typing import Any, Dict
import os
import json
import uvicorn
import logging
import time
import uuid
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from src.handler import RequestHandler

configs = TemplateConfigs()


predict_config = configs.get("prediction_aws_config")

model_config = predict_config.model_config.toDict()
feature_store_config = predict_config.toDict().get("feature_store")

# Define FastAPI app
app = FastAPI(
    title=f"{configs.get('project_config').experiment_name} ModelServer", 
    version="1.0.0", 
    docs_url="/docs", 
    default_response_class=ORJSONResponse)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.on_event("startup")
async def initialize_global_resources():
    """Initialize global resources."""
    logging.info("Initializing global resources...")
    from mlops_decorators.core.feature_api import Client
    from src.model import Model

    RequestHandler.logging = logging

    if feature_store_config is not None:
        RequestHandler.feature_store_client = Client.initialize(
            store_api = feature_store_config["store_api"], 
            config = feature_store_config["config"]
        )

    RequestHandler.model = Model(
        name=configs.get("project_config").experiment_name,
        artifacts=model_config["artifacts"],
        feature_store_client=RequestHandler.feature_store_client,
        **model_config.get("extra_init_params", {}),
    )
    RequestHandler.model.load_model()
    logging.info("Global resources initialized successfully.")


@app.get("/live", status_code=200)
def live_check():
    """Check if the application is live."""
    return {
        "status": "live", 
        "model_name": RequestHandler.model.name
    }

@app.get("/metadata", status_code=200)
def model_metadata():
    """Retrieve model metadata."""
    return {
        "model_name": RequestHandler.model.name,
        "description": "Model",
    }

@app.post("/predict")
async def predict(request: Request):
    """Predict route that uses preprocess, predict, and postprocess methods."""
    process_start = time.time()

    body = await request.body()

    if isinstance(body, bytes):
        body = json.loads(body.decode("utf-8"))
    headers = dict(request.headers.items())

    output = await RequestHandler.predict(body)

    tt = time.time() - process_start
    logging.info(f"Total processing time: {tt:0.4f} Request: {body} \n Response: {output}")

    if not isinstance(output, dict):
        return Response(content=output, headers={})
    
    return output


if __name__ == "__main__":
    # Run the application using uvicorn for scalability and performance
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind the server to (default: 8080)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    parser.add_argument("--log_level", type=str, default="debug", choices=["critical", "error", "warning", "info", "debug", "trace"],
                        help="Logging level (default: debug)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    parser.add_argument("--limit_concurrency", type=int, default=1, help="Maximum number of concurrent connections (default: 1)")
    parser.add_argument("--limit_max_requests", type=int, default=1, help="Maximum number of requests before restarting a worker (default: 1)")

    # Parse the arguments
    args = parser.parse_args()

    uvicorn.run(app, 
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        debug=args.debug,
        workers=args.workers,
        limit_concurrency=args.limit_concurrency,
        limit_max_requests=args.limit_max_requests,)
