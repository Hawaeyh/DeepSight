import type { ImageMetadata, ImageOrientation } from "../types/metadata";

/**
 * Convert bytes to readable size.
 */
export function formatFileSize(bytes: number): string {

    if (bytes < 1024) {

        return `${bytes} B`;

    }

    if (bytes < 1024 * 1024) {

        return `${(bytes / 1024).toFixed(2)} KB`;

    }

    if (bytes < 1024 * 1024 * 1024) {

        return `${(bytes / 1024 / 1024).toFixed(2)} MB`;

    }

    return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;

}

/**
 * Greatest Common Divisor
 */
function gcd(a: number, b: number): number {

    return b === 0 ? a : gcd(b, a % b);

}

/**
 * Calculate aspect ratio.
 */
export function calculateAspectRatio(

    width: number,

    height: number,

): string {

    const divisor = gcd(width, height);

    return `${width / divisor}:${height / divisor}`;

}

/**
 * Detect image orientation.
 */
export function getOrientation(

    width: number,

    height: number,

): ImageOrientation {

    if (width > height) {

        return "Landscape";

    }

    if (height > width) {

        return "Portrait";

    }

    return "Square";

}

/**
 * Read metadata from image.
 */
export async function getImageMetadata(

    file: File,

): Promise<ImageMetadata> {

    return new Promise((resolve, reject) => {

        const image = new Image();

        const url = URL.createObjectURL(file);

        image.onload = () => {

            const extension =

                file.name.split(".").pop()?.toUpperCase() ?? "";

            const width = image.width;

            const height = image.height;

            resolve({

                filename: file.name,

                extension,

                mimeType: file.type,

                fileSize: file.size,

                formattedFileSize:

                    formatFileSize(file.size),

                width,

                height,

                resolution:

                    `${width} × ${height}`,

                aspectRatio:

                    calculateAspectRatio(

                        width,

                        height,

                    ),

                orientation:

                    getOrientation(

                        width,

                        height,

                    ),

                uploadTime:

                    new Date().toLocaleString(),

            });

            URL.revokeObjectURL(url);

        };

        image.onerror = () => {

            URL.revokeObjectURL(url);

            reject(

                new Error(

                    "Unable to load image."

                )

            );

        };

        image.src = url;

    });

}