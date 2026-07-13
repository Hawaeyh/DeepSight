import type {

    Analysis,

} from "./analysis";

export interface VideoAnalysis extends Analysis {

    frames_analyzed: number;

    fake_frames: number;

    real_frames: number;

    video_duration: number;

}