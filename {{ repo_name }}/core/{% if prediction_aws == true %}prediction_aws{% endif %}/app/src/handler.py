import time

# Initialize global resources at startup
class RequestHandler:
    feature_store_client = None
    model = None
    mode = None
    logging = None

    @classmethod
    async def predict(cls, body: dict):
        start = time.time()
        cls.logging.info(f"Start processing request")
        
        preprocessed_data = await cls.model.preprocess(body)
        cls.logging.info(f"Time for preprocessing: {time.time() - start}")

        # Make prediction
        start = time.time()
        prediction = await cls.model.predict(preprocessed_data)
        cls.logging.info(f"Time for prediction: {time.time() - start}")

        # Postprocess the prediction
        start = time.time()
        final_output = await cls.model.postprocess(prediction)
        cls.logging.info(f"Time for postprocessing: {time.time() - start}")

        return final_output