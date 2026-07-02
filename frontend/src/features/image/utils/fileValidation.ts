const MAX_FILE_SIZE = 20 * 1024 * 1024;

const ALLOWED_TYPES = [

    "image/png",

    "image/jpeg",

    "image/jpg",

    "image/webp",

];

export function validateImage(

    file: File,

): string | null {

    if (!file) {

        return "Please select an image.";

    }

    if (

        !ALLOWED_TYPES.includes(

            file.type,

        )

    ) {

        return "Only PNG, JPG, JPEG and WEBP images are allowed.";

    }

    if (

        file.size > MAX_FILE_SIZE

    ) {

        return "Maximum file size is 20 MB.";

    }

    return null;

}