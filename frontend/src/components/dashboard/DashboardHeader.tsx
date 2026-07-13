import SectionTitle from "../ui/SectionTitle";

export default function DashboardHeader() {

    return (

        <div className="flex items-center justify-between">

            <SectionTitle

                title="Admin Analytics"

                subtitle="System-wide detection activity and model performance"

            />

            <div className="text-right">

                <p className="text-sm text-slate-400">

                    Environment

                </p>

                <p className="font-semibold text-cyan-400">

                    Production

                </p>

            </div>

        </div>

    );

}
