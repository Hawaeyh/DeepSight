from app.ai.inference.video_inference import (
    predict_video,
)


class VideoService:

    @staticmethod
    def analyze(

        video_path: str,

    ):

        return predict_video(

            video_path

        )