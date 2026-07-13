export interface ManipulationInfo {
    category: "Deepfake" | "Unresolved manipulation";
    technique: string;
    description: string;
    modelClass: string | null;
}

const DEEPFAKE_CLASSES: Record<string, Omit<ManipulationInfo, "category" | "modelClass">> = {
    celebdf: {
        technique: "Face swap / identity replacement",
        description: "Facial identity cues resemble celebrity face-swap examples. Boundaries, skin texture, and identity consistency may have been synthesized.",
    },
    deepfakedetection: {
        technique: "Mixed facial manipulation",
        description: "The image resembles examples containing multiple facial manipulation methods. A single technique cannot be isolated reliably.",
    },
    deepfakes: {
        technique: "Face swap",
        description: "One person's facial identity may have been transferred onto another face while retaining the target pose and scene.",
    },
    face2face: {
        technique: "Facial reenactment",
        description: "Facial expression or motion cues may have been transferred from a source performer while keeping the target identity.",
    },
    faceshifter: {
        technique: "Identity swap",
        description: "Identity features may have been replaced using a high-fidelity face-shifting method designed to preserve pose and lighting.",
    },
    faceswap: {
        technique: "Face swap",
        description: "The face region may have been replaced with another identity and blended into the original image.",
    },
    neuraltextures: {
        technique: "Neural texture synthesis",
        description: "Learned facial textures may have been rendered to alter expressions, mouth movement, or local appearance.",
    },
};

export function getManipulationInfo(deepfakeType: string | null): ManipulationInfo {
    const modelClass = deepfakeType?.toLowerCase() ?? null;
    const known = modelClass ? DEEPFAKE_CLASSES[modelClass] : undefined;
    if (known) {
        return { category: "Deepfake", modelClass, ...known };
    }
    return {
        category: "Unresolved manipulation",
        technique: "Unknown synthetic or manipulated content",
        description: "The binary detector found fake characteristics, but the current multiclass model did not resolve a known deepfake technique. AI-generated content requires a dedicated trained class or reviewer correction.",
        modelClass,
    };
}

export const AI_MANIPULATIONS = [
    "Text-to-image generation",
    "Fully synthetic face",
    "Generative fill / inpainting",
    "Object or background replacement",
    "Style transfer",
    "Other AI generation",
];

export const DEEPFAKE_MANIPULATIONS = [
    "Face swap",
    "Identity swap",
    "Facial reenactment",
    "Lip sync",
    "Neural texture synthesis",
    "Facial attribute editing",
    "Other deepfake manipulation",
];
