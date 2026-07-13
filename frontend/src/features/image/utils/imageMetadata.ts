import type { ImageMetadata } from "../types/metadata";

function formatFileSize(bytes: number): string {

    if (bytes < 1024) {

        return `${bytes} B`;

    }

    if (bytes < 1024 * 1024) {

        return `${(bytes / 1024).toFixed(2)} KB`;

    }

    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;

}

function gcd(a: number, b: number): number {

    return b === 0

        ? a

        : gcd(b, a % b);

}

function getAspectRatio(
    width: number,
    height: number,
): string {

    const divisor = gcd(width, height);

    return `${width / divisor}:${height / divisor}`;

}

function getOrientation(
    width: number,
    height: number,
): "Landscape" | "Portrait" | "Square" {

    if (width > height) {

        return "Landscape";

    }

    if (height > width) {

        return "Portrait";

    }

    return "Square";

}

export async function getImageMetadata(
    file: File,
): Promise<ImageMetadata> {

    return new Promise((resolve, reject) => {

        const image = new Image();

        const objectUrl = URL.createObjectURL(file);

        image.onload = () => {

            const extension =
                file.name.split(".").pop()?.toUpperCase() ?? "";

            resolve({

                filename: file.name,

                extension,

                mimeType: file.type,

                fileSize: file.size,

                formattedFileSize: formatFileSize(file.size),

                width: image.width,

                height: image.height,

                resolution: `${image.width} × ${image.height}`,

                aspectRatio: getAspectRatio(
                    image.width,
                    image.height,
                ),

                orientation: getOrientation(
                    image.width,
                    image.height,
                ),

                uploadTime:
                    new Date().toLocaleString(),

            });

            URL.revokeObjectURL(objectUrl);

        };

        image.onerror = () => {

            URL.revokeObjectURL(objectUrl);

            reject(

                new Error(
                    "Unable to read image metadata.",
                ),

            );

        };

        image.src = objectUrl;

    });

}