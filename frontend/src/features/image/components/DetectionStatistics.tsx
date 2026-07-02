import Card from "../../../components/ui/Card";
import Metric from "../../../components/ui/Metric";

interface Props{

    today:number;

    week:number;

    confidence:number;

    device:string;

}

export default function DetectionStatistics({

    today,

    week,

    confidence,

    device,

}:Props){

    return(

        <Card

            title="Detection Statistics"

            subtitle="Current AI Activity"

        >

            <div className="space-y-4">

                <Metric

                    label="Today's Detection"

                    value={today}

                />

                <Metric

                    label="Week Detection"

                    value={week}

                />

                <Metric

                    label="Average Confidence"

                    value={`${confidence}%`}

                />

                <Metric

                    label="Device"

                    value={device.toUpperCase()}

                />

            </div>

        </Card>

    );

}