class VideoService:
    @staticmethod
    def analyze(video_path: str):
        from app.ai.inference.video_inference import predict_video

        return predict_video(video_path)
