import { Button } from "@/components/ui/Button";
import { APP_NAME } from "@/app/constants";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-8">
      <h1 className="text-5xl font-bold text-cyan-400">
        {APP_NAME}
      </h1>

      <Button>
        Frontend Initialized
      </Button>
    </div>
  );
}