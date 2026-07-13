from app.ai.inference.image_inference import predict


class AIService:

    @staticmethod
    def analyze_image(
        image_path: str,
        model_key: str = "efficientnet",
    ):

        return predict(image_path, model_key)
