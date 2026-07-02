import { useEffect, useState } from "react";

import type { ImageMetadata } from "../types/metadata";

import { getImageMetadata } from "../utils/imageMetadata";

export function useImageMetadata(file: File | null) {

    const [metadata, setMetadata] =
        useState<ImageMetadata | null>(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);

    useEffect(() => {

        if (!file) {

            setMetadata(null);

            setError(null);

            return;

        }

        let mounted = true;

        async function loadMetadata() {

            try {

                setLoading(true);

                setError(null);

                const result =
                    await getImageMetadata(file);

                if (mounted) {

                    setMetadata(result);

                }

            }

            catch (err) {

                console.error(err);

                if (mounted) {

                    setError(

                        "Unable to read image metadata."

                    );

                }

            }

            finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        }

        loadMetadata();

        return () => {

            mounted = false;

        };

    }, [file]);

    return {

        metadata,

        loading,

        error,

    };

}