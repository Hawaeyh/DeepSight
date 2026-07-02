import Card from "../ui/Card";
import ProgressBar from "../ui/ProgressBar";

export default function SystemStatusCard() {

    return (

        <Card title="System Status">

            <div className="space-y-6">

                <div>

                    <div className="flex justify-between mb-2">

                        <span>

                            CPU

                        </span>

                        <span>

                            34%

                        </span>

                    </div>

                    <ProgressBar value={34} />

                </div>

                <div>

                    <div className="flex justify-between mb-2">

                        <span>

                            GPU

                        </span>

                        <span>

                            71%

                        </span>

                    </div>

                    <ProgressBar value={71} />

                </div>

                <div>

                    <div className="flex justify-between mb-2">

                        <span>

                            Memory

                        </span>

                        <span>

                            48%

                        </span>

                    </div>

                    <ProgressBar value={48} />

                </div>

            </div>

        </Card>

    );

}