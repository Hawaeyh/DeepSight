export type ModelKey = "deepsightnet" | "efficientnet";

export interface DetectionModel {
    key: ModelKey;
    name: string;
    version: string;
    description: string;
    available: boolean;
}

export interface ModelCatalogResponse {
    device: string;
    models: DetectionModel[];
}
