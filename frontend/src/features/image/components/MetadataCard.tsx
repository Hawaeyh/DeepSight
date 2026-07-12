import Card from "../../../components/ui/Card";
import type { ImageMetadata } from "../types/metadata";

interface Props {
    metadata: ImageMetadata | null;
    loading?: boolean;
}

interface MetadataItemProps {
    label: string;
    value: string;
}

function MetadataItem({
    label,
    value,
}: MetadataItemProps) {
    return (
        <div className="flex items-center justify-between py-3 border-b border-slate-700 last:border-b-0">
            <span className="text-sm text-slate-400">
                {label}
            </span>

            <span className="text-sm font-medium text-white text-right break-all">
                {value}
            </span>
        </div>
    );
}

export default function MetadataCard({
    metadata,
    loading = false,
}: Props) {

    if (loading) {
        return (
            <Card title="Image Metadata">
                <div className="animate-pulse space-y-4">

                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>
                    <div className="h-5 bg-slate-700 rounded"></div>

                </div>
            </Card>
        );
    }

    if (!metadata) {
        return (
            <Card title="Image Metadata">

                <div className="flex flex-col items-center justify-center py-12">

                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-14 h-14 text-slate-600 mb-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16
                            16m-2-2l1.586-1.586a2 2 0 012.828
                            0L20 14m-6-10h.01M6
                            20h12a2 2 0 002-2V6a2 2
                            0 00-2-2H6a2 2 0
                            00-2 2v12a2 2 0
                            002 2z"
                        />
                    </svg>

                    <p className="text-slate-400 font-medium">
                        No Image Selected
                    </p>

                    <p className="text-sm text-slate-500 mt-2 text-center">
                        Upload an image to display its metadata.
                    </p>

                </div>

            </Card>
        );
    }

    return (

        <Card
            title="Image Metadata"
            subtitle="Basic information about the uploaded image."
        >

            <div className="space-y-1">

                <MetadataItem
                    label="Filename"
                    value={metadata.filename}
                />

                <MetadataItem
                    label="Extension"
                    value={metadata.extension}
                />

                <MetadataItem
                    label="MIME Type"
                    value={metadata.mimeType}
                />

                <MetadataItem
                    label="File Size"
                    value={metadata.formattedFileSize}
                />

                <MetadataItem
                    label="Resolution"
                    value={metadata.resolution}
                />

                <MetadataItem
                    label="Width"
                    value={`${metadata.width}px`}
                />

                <MetadataItem
                    label="Height"
                    value={`${metadata.height}px`}
                />

                <MetadataItem
                    label="Aspect Ratio"
                    value={metadata.aspectRatio}
                />

                <MetadataItem
                    label="Orientation"
                    value={metadata.orientation}
                />

                <MetadataItem
                    label="Upload Time"
                    value={metadata.uploadTime}
                />

            </div>

        </Card>

    );

}