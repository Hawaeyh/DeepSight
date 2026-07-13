export interface ImageMetadata {

    filename: string;

    extension: string;

    mimeType: string;

    fileSize: number;

    formattedFileSize: string;

    width: number;

    height: number;

    resolution: string;

    aspectRatio: string;

    orientation: "Landscape" | "Portrait" | "Square";

    uploadTime: string;

}