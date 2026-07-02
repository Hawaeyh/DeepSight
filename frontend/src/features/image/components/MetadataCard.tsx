import Card from "../../../components/ui/Card";

import type {

    ImageDetectionResponse,

} from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function MetadataCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="Image Metadata">

                <p className="text-slate-500">

                    No metadata available.

                </p>

            </Card>

        );

    }

    return (

        <Card title="Image Metadata">

            <div className="space-y-4">

                <div>

                    <p className="text-slate-400">

                        Filename

                    </p>

                    <h2>

                        {result.image.filename}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Resolution

                    </p>

                    <h2>

                        {result.image.width} × {result.image.height}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Face Detected

                    </p>

                    <h2>

                        {result.image.faceDetected ? "Yes" : "No"}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Face Count

                    </p>

                    <h2>

                        {result.image.faceCount}

                    </h2>

                </div>

            </div>

        </Card>

    );

}