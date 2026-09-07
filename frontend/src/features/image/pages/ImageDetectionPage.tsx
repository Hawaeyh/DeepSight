import { useNavigate } from "react-router-dom";

import UploadCard from "../components/UploadCard";
import ImagePreview from "../components/ImagePreview";
import PredictionResultCard from "../components/PredictionResultCard";
import DetectionPipeline from "../components/DetectionPipeline";
import DetectionStatistics from "../components/DetectionStatistics";
import RecentAnalysisCard from "../components/RecentAnalysisCard";
import ActionBar from "../components/ActionBar";
import MetadataCard from "../components/MetadataCard";
import AIInformationCard from "../components/AIInformationCard";
import RecommendationCard from "../components/RecommendationCard";
import ModelCard from "../components/ModelCard";
import ProbabilityCard from "../components/ProbabilityCard";
import ModelSelector from "../components/ModelSelector";
import FeedbackPanel from "../components/FeedbackPanel";
import AnalysisProgress from "../components/AnalysisProgress";

import EmptyState from "../../../components/ui/EmptyState";

import { useDashboard } from "../../../hooks/useDashboard";
import { useImageDetection } from "../hooks/useImageDetection";

export default function ImageDetectionPage() {

    const navigate = useNavigate();

    const { overview } = useDashboard();

    const {

        selectedFile,
        preview,
        metadata,
        models,
        selectedModel,
        result,
        recent,
        loading,
        error,
        stage,
        progress,
        progressMessage,

        selectImage,
        setSelectedModel,
        detectImage,
        handleDownloadReport,
        reset,

    } = useImageDetection();

    return (

        <div className="space-y-8">

            {/* ======================================== */}
            {/* Header */}
            {/* ======================================== */}

            <div>

                <h1 className="text-3xl font-bold">

                    Image Detection

                </h1>

                <p className="mt-2 text-slate-400">

                    Upload an image to detect authentic, manipulated, or deepfake facial content using the DeepSight AI Engine.

                </p>

            </div>

            {/* ======================================== */}
            {/* Error */}
            {/* ======================================== */}

            {error && (

                <EmptyState

                    title="Detection Error"

                    description={error}

                />

            )}

            {/* ======================================== */}
            {/* Upload */}
            {/* ======================================== */}

            <UploadCard

                selectedFile={selectedFile}

                loading={loading}

                onSelect={selectImage}

            />

            <ModelSelector
                models={models}
                selected={selectedModel}
                disabled={loading}
                onChange={setSelectedModel}
            />

            {(selectedFile || stage === "failed" || stage === "completed") && <AnalysisProgress stage={stage} progress={progress} message={progressMessage} />}

            {/* ======================================== */}
            {/* Hero Result */}
            {/* ======================================== */}

            {result && (

                <PredictionResultCard

                    result={result}

                />

            )}

            {result && <div id="analysis-feedback"><FeedbackPanel result={result} /></div>}

            {/* ======================================== */}
            {/* Preview + Pipeline */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <ImagePreview

                    image={preview}

                    filename={selectedFile?.name}

                />

                <DetectionPipeline

                    loading={loading}

                    finished={!!result}

                />

            </div>

            {/* ======================================== */}
            {/* Metadata + AI Info */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

            <MetadataCard
                metadata={metadata}
                result={result}
                loading={loading && !metadata}
            />

                <AIInformationCard

                    result={result}

                />

            </div>

            {/* ======================================== */}
            {/* Probability + Recommendation */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <ProbabilityCard

                    result={result}

                />

                <RecommendationCard

                    result={result}

                />

            </div>

            {/* ======================================== */}
            {/* Model + Statistics */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <ModelCard

                    result={result}

                />

                <DetectionStatistics

                    today={overview?.todayDetection ?? 0}

                    week={overview?.weekDetection ?? 0}

                    confidence={overview?.averageConfidence ?? 0}

                    device={overview?.device ?? "CPU"}

                />

            </div>

            {/* ======================================== */}
            {/* Recent Analysis */}
            {/* ======================================== */}

            <RecentAnalysisCard

                data={recent}

            />

            {/* ======================================== */}
            {/* Bottom Action Bar */}
            {/* ======================================== */}

            <ActionBar

                loading={loading}

                disabled={!selectedFile}

                canDownload={!!result}
                completed={stage === "completed"}

                onAnalyze={detectImage}

                onDownload={handleDownloadReport}

                onReset={reset}

                onHistory={() => navigate("/history")}
                onFeedback={() => document.getElementById("analysis-feedback")?.scrollIntoView({ behavior: "smooth" })}

            />

        </div>

    );

}
