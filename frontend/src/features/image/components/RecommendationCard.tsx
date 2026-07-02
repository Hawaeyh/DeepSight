import Card from "../../../components/ui/Card";

import type {

    ImageDetectionResponse,

} from "../types/image";

interface Props {

    result: ImageDetectionResponse | null;

}

export default function RecommendationCard({

    result,

}: Props) {

    if (!result) {

        return (

            <Card title="Recommendation">

                <p className="text-slate-500">

                    No recommendation available.

                </p>

            </Card>

        );

    }

    const fake =

        result.prediction.label === "Fake";

    return (

        <Card title="Recommendation">

            {

                fake ? (

                    <ul className="space-y-3">

                        <li>

                            ⚠ This image is likely manipulated.

                        </li>

                        <li>

                            Verify the source before sharing.

                        </li>

                        <li>

                            Perform manual verification if required.

                        </li>

                    </ul>

                ) : (

                    <ul className="space-y-3">

                        <li>

                            ✅ Image appears authentic.

                        </li>

                        <li>

                            No manipulation detected.

                        </li>

                        <li>

                            Safe for further verification.

                        </li>

                    </ul>

                )

            }

        </Card>

    );

}