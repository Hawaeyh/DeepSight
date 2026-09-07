class AIService:
    @staticmethod
    def analyze_image(image_path: str, model_key: str = "efficientnet"):
        from app.ai.inference.image_inference import predict

        return predict(image_path, model_key)

    @staticmethod
    def analyze_video_frame(image_path: str, model_key: str = "efficientnet"):
        from app.ai.inference.image_inference import predict_faces

        return predict_faces(image_path, model_key)
