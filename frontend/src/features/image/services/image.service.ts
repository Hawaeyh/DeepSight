import api from "../../../services/api";

export async function analyzeImage(file: File) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(

        "/analysis/image",

        formData,

        {

            headers: {

                "Content-Type": "multipart/form-data",

            },

        }

    );

    return response.data;

}

export async function downloadReport(

    analysisId: number,

) {

    const response = await api.get(

        `/report/${analysisId}`,

        {

            responseType: "blob",

        }

    );

    return response.data;

}