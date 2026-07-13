import Card from "../../../components/ui/Card";

import {
    Calendar,
    Compass,
    Crop,
    FileImage,
    FileType,
    HardDrive,
    Monitor,
    ScanFace,
    Users,
} from "lucide-react";

import type { ImageMetadata } from "../types/metadata";
import type { ImageDetectionResponse } from "../types/image";

interface Props {

    metadata: ImageMetadata | null;

    result: ImageDetectionResponse | null;

    loading?: boolean;

}

interface InfoRowProps {

    icon: React.ReactNode;

    label: string;

    value: string;

}

function InfoRow({

    icon,

    label,

    value,

}: InfoRowProps) {

    return (

        <div className="flex justify-between items-center py-3 border-b border-slate-700 last:border-0">

            <div className="flex items-center gap-2 text-slate-400">

                {icon}

                <span>{label}</span>

            </div>

            <span className="font-medium text-white">

                {value}

            </span>

        </div>

    );

}

export default function MetadataCard({

    metadata,

    result,

    loading,

}: Props) {

    if (loading) {

        return (

            <Card
                title="Image Metadata"
                subtitle="Reading image information"
            >

                <div className="py-16 text-center text-slate-500">

                    Loading metadata...

                </div>

            </Card>

        );

    }

    if (!metadata) {

        return (

            <Card
                title="Image Metadata"
                subtitle="Image properties"
            >

                <div className="py-16 text-center text-slate-500">

                    Upload an image to view metadata.

                </div>

            </Card>

        );

    }

    return (

        <Card
            title="Image Metadata"
            subtitle="File properties"
        >

            <div className="space-y-1">

                <InfoRow
                    icon={<FileImage size={18}/>}
                    label="Filename"
                    value={metadata.filename}
                />

                <InfoRow
                    icon={<FileType size={18}/>}
                    label="Extension"
                    value={metadata.extension}
                />

                <InfoRow
                    icon={<HardDrive size={18}/>}
                    label="File Size"
                    value={metadata.formattedFileSize}
                />

                <InfoRow
                    icon={<Monitor size={18}/>}
                    label="Resolution"
                    value={metadata.resolution}
                />

                <InfoRow
                    icon={<Crop size={18}/>}
                    label="Aspect Ratio"
                    value={metadata.aspectRatio}
                />

                <InfoRow
                    icon={<Compass size={18}/>}
                    label="Orientation"
                    value={metadata.orientation}
                />

                <InfoRow
                    icon={<FileType size={18}/>}
                    label="MIME Type"
                    value={metadata.mimeType}
                />

                {

                    result &&

                    <>

                        <InfoRow
                            icon={<ScanFace size={18}/>}
                            label="Face Detected"
                            value={
                                result.face_detected
                                    ? "Yes"
                                    : "No"
                            }
                        />

                        <InfoRow
                            icon={<Users size={18}/>}
                            label="Face Count"
                            value={
                                result.face_count.toString()
                            }
                        />

                    </>

                }

                <InfoRow
                    icon={<Calendar size={18}/>}
                    label="Upload Time"
                    value={metadata.uploadTime}
                />

            </div>

        </Card>

    );

}