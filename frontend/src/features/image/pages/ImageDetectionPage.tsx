import { useNavigate } from "react-router-dom";

import UploadCard from "../components/UploadCard";
import ImagePreview from "../components/ImagePreview";
import PredictionResultCard from "../components/PredictionResultCard";
import DetectionPipeline from "../components/DetectionPipeline";
import DetectionStatistics from "../components/DetectionStatistics";
import RecentAnalysisCard from "../components/RecentAnalysisCard";
import ActionBar from "../components/ActionBar";

import EmptyState from "../../../components/ui/EmptyState";
import Spinner from "../../../components/ui/Spinner";

import { useDashboard } from "../../../hooks/useDashboard";
import { useImageDetection } from "../hooks/useImageDetection";

export default function ImageDetectionPage() {

    const navigate = useNavigate();

    const {

        overview,

    } = useDashboard();

    const {

        selectedFile,

        preview,

        result,

        recent,

        loading,

        error,

        selectImage,

        detectImage,

        handleDownloadReport,

        reset,

    } = useImageDetection();

    if (!overview) {

        return (

            <div className="flex justify-center items-center h-[70vh]">

                <Spinner />

            </div>

        );

    }

    return (

        <div className="space-y-8">

            {/* ======================================== */}
            {/* Page Header */}
            {/* ======================================== */}

            <div>

                <h1 className="text-3xl font-bold">

                    Image Detection

                </h1>

                <p className="text-slate-400 mt-2">

                    Upload an image to detect whether it is Real or AI Generated.

                </p>

            </div>

            {/* ======================================== */}
            {/* Error */}
            {/* ======================================== */}

            {

                error && (

                    <EmptyState

                        title="Detection Error"

                        description={error}

                    />

                )

            }

            {/* ======================================== */}
            {/* Upload + AI Result */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <UploadCard

                    selectedFile={selectedFile}

                    loading={loading}

                    onSelect={selectImage}

                />

                <PredictionResultCard

                    result={result}

                />

            </div>

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
            {/* Recent + Statistics */}
            {/* ======================================== */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <RecentAnalysisCard

                    data={recent}

                />

                <DetectionStatistics

                    today={overview.todayDetection ?? 0}

                    week={overview.weekDetection ?? 0}

                    confidence={overview.averageConfidence}

                    device={overview.device ?? "CPU"}

                />

            </div>

            {/* ======================================== */}
            {/* Bottom Actions */}
            {/* ======================================== */}

            <ActionBar

                loading={loading}

                disabled={!selectedFile}

                canDownload={!!result}

                onAnalyze={detectImage}

                onDownload={handleDownloadReport}

                onReset={reset}

                onHistory={() => navigate("/history")}

            />

        </div>

    );

}