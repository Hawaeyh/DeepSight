from app.ai.inference.image_inference import predict


class AIService:

    @staticmethod
    def analyze_image(image_path: str):

        return predict(image_path)