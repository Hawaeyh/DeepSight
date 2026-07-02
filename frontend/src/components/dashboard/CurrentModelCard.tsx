import Card from "../ui/Card";

interface Props {

    model: string;

    version: string;

}

export default function CurrentModelCard({

    model,

    version,

}: Props) {

    return (

        <Card title="Current Model">

            <div className="space-y-4">

                <div>

                    <p className="text-slate-400">

                        Model

                    </p>

                    <h2 className="text-2xl font-bold">

                        {model}

                    </h2>

                </div>

                <div>

                    <p className="text-slate-400">

                        Version

                    </p>

                    <h2>

                        {version}

                    </h2>

                </div>

            </div>

        </Card>

    );

}