import Card from "../../../components/ui/Card";

import type {

    ImageDetectionResponse,

} from "../../../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function AIInformationCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="AI Information">

                <p className="text-slate-500">

                    No AI information.

                </p>

            </Card>

        );

    }

    return (

        <Card title="AI Information">

            <div className="space-y-4">

                <div>

                    <p className="text-slate-400">

                        Model

                    </p>

                    <h2>

                        {result.model.name}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Version

                    </p>

                    <h2>

                        {result.model.version}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Device

                    </p>

                    <h2>

                        {result.model.device.toUpperCase()}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Processing Time

                    </p>

                    <h2>

                        {result.processing.time.toFixed(2)} sec

                    </h2>

                </div>

            </div>

        </Card>

    );

}