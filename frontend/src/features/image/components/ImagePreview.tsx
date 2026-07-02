import { useEffect, useState } from "react";

import Card from "../../../components/ui/Card";

import {
    ImageIcon,
    FileImage,
    HardDrive,
    Maximize,
} from "lucide-react";

interface Props {

    image: string | null;

    filename?: string;

}

export default function ImagePreview({

    image,

    filename,

}: Props) {

    const [

        resolution,

        setResolution,

    ] = useState("");

    useEffect(() => {

        if (!image) {

            setResolution("");

            return;

        }

        const img = new Image();

        img.onload = () => {

            setResolution(

                `${img.width} × ${img.height}`

            );

        };

        img.src = image;

    }, [image]);

    if (!image) {

        return (

            <Card

                title="Image Preview"

                subtitle="Preview uploaded image"

            >

                <div className="h-96 flex flex-col items-center justify-center text-slate-500">

                    <ImageIcon

                        size={80}

                        className="mb-5"

                    />

                    <p>No image selected.</p>

                </div>

            </Card>

        );

    }

    return (

        <Card

            title="Image Preview"

            subtitle="Uploaded Image"

        >

            <div className="space-y-6">

                <div className="overflow-hidden rounded-xl border border-slate-700">

                    <img

                        src={image}

                        alt="Preview"

                        className="

                            w-full

                            h-96

                            object-contain

                            bg-slate-950

                            hover:scale-105

                            transition-transform

                            duration-300

                        "

                    />

                </div>

                <div className="grid grid-cols-2 gap-4">

                    <InfoItem

                        icon={<FileImage size={18} />}

                        label="Filename"

                        value={

                            filename ?? "-"

                        }

                    />

                    <InfoItem

                        icon={<Maximize size={18} />}

                        label="Resolution"

                        value={

                            resolution || "-"

                        }

                    />

                    <InfoItem

                        icon={<HardDrive size={18} />}

                        label="Status"

                        value="Ready"

                    />

                    <InfoItem

                        icon={<ImageIcon size={18} />}

                        label="Preview"

                        value="Available"

                    />

                </div>

            </div>

        </Card>

    );

}

interface InfoItemProps {

    icon: React.ReactNode;

    label: string;

    value: string;

}

function InfoItem({

    icon,

    label,

    value,

}: InfoItemProps) {

    return (

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">

            <div className="flex items-center gap-2 text-slate-400 mb-2">

                {icon}

                <span className="text-sm">

                    {label}

                </span>

            </div>

            <p className="font-semibold break-all">

                {value}

            </p>

        </div>

    );

}