import SectionTitle from "../ui/SectionTitle";

export default function DashboardHeader() {

    return (

        <div className="flex items-center justify-between">

            <SectionTitle

                title="Dashboard"

                subtitle="AI-powered Deepfake Detection Platform"

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