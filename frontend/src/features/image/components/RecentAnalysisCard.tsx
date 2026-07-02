import Card from "../../../components/ui/Card";
import PredictionBadge from "../../../components/ui/PredictionBadge";

import type {

    RecentDetection,

} from "../../../types/dashboard";

interface Props{

    data:RecentDetection[];

}

export default function RecentAnalysisCard({

    data,

}:Props){

    return(

        <Card

            title="Recent Analysis"

            subtitle="Latest detections"

        >

            <div className="space-y-4">

                {

                    data.length===0?

                    (

                        <p className="text-slate-500">

                            No analysis found.

                        </p>

                    )

                    :

                    data.slice(0,5).map(item=>(

                        <div

                            key={item.id}

                            className="

                            flex

                            justify-between

                            items-center

                            border-b

                            border-slate-800

                            pb-3

                            "

                        >

                            <div>

                                <p

                                    className="font-medium"

                                >

                                    {item.filename}

                                </p>

                                <p

                                    className="text-xs text-slate-500"

                                >

                                    {

                                        new Date(

                                            item.createdAt

                                        ).toLocaleString()

                                    }

                                </p>

                            </div>

                            <div className="text-right">

                                <PredictionBadge

                                    prediction={

                                        item.prediction

                                    }

                                />

                                <p

                                    className="text-sm mt-1"

                                >

                                    {

                                        item.confidence

                                    }%

                                </p>

                            </div>

                        </div>

                    ))

                }

            </div>

        </Card>

    );

}