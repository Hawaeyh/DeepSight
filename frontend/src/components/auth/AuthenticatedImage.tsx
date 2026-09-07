import { useEffect, useState } from "react";

import api from "../../services/api";


export function AuthenticatedImage({
    endpoint,
    alt,
    className,
}: {
    endpoint: string;
    alt: string;
    className?: string;
}) {
    const [source, setSource] = useState<string | null>(null);

    useEffect(() => {
        let active = true;
        let objectUrl: string | null = null;
        api.get<Blob>(endpoint, { responseType: "blob" })
            .then(response => {
                objectUrl = URL.createObjectURL(response.data);
                if (active) setSource(objectUrl);
                else URL.revokeObjectURL(objectUrl);
            })
            .catch(() => { if (active) setSource(null); });
        return () => {
            active = false;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [endpoint]);

    if (!source) return <div className={className} aria-label={`${alt} unavailable`} />;
    return <img src={source} alt={alt} className={className} loading="lazy" />;
}
