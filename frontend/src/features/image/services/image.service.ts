import api, { ensureGuestSession } from "../../../services/api";
import type { ImageDetectionResponse } from "../types/image";
import type { ModelCatalogResponse, ModelKey } from "../../../types/model";

export async function analyzeImage(
    file: File,
    model: ModelKey,
): Promise<ImageDetectionResponse> {

    await ensureGuestSession();

    const formData = new FormData();

    formData.append("file", file);

    formData.append("model", model);

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

        `/reports/${analysisId}`,

        {

            responseType: "blob",

        }

    );

    return response.data;

}

export async function getDetectionModels(): Promise<ModelCatalogResponse> {
    const response = await api.get<ModelCatalogResponse>("/models");
    return response.data;
}
