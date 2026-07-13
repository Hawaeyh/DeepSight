import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

declare global {
    interface Window {
        google?: {
            accounts: {
                id: {
                    initialize(options: { client_id: string; callback(response: { credential: string }): void }): void;
                    renderButton(element: HTMLElement, options: Record<string, unknown>): void;
                };
            };
        };
    }
}

export default function GoogleSignInButton() {
    const container = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    const { googleLogin } = useAuth();
    const [error, setError] = useState<string | null>(null);
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

    useEffect(() => {
        if (!clientId || !container.current) return;
        const render = () => {
            if (!window.google || !container.current) return;
            window.google.accounts.id.initialize({
                client_id: clientId,
                callback: async response => {
                    try {
                        await googleLogin(response.credential);
                        navigate("/dashboard");
                    }
                    catch (requestError: any) {
                        setError(requestError?.response?.data?.detail ?? "Google sign-in failed.");
                    }
                },
            });
            window.google.accounts.id.renderButton(container.current, {
                theme: "filled_black",
                size: "large",
                width: 360,
                text: "continue_with",
            });
        };
        const existing = document.querySelector<HTMLScriptElement>('script[src="https://accounts.google.com/gsi/client"]');
        if (existing) render();
        else {
            const script = document.createElement("script");
            script.src = "https://accounts.google.com/gsi/client";
            script.async = true;
            script.onload = render;
            document.head.appendChild(script);
        }
    }, [clientId, googleLogin, navigate]);

    if (!clientId) {
        return <button type="button" disabled title="Configure VITE_GOOGLE_CLIENT_ID to enable Google sign-in" className="w-full rounded-lg border border-slate-700 p-3 text-slate-500">Continue with Google (configuration required)</button>;
    }
    return <><div ref={container} className="flex min-h-11 justify-center" />{error && <p className="mt-2 text-sm text-red-400">{error}</p>}</>;
}
