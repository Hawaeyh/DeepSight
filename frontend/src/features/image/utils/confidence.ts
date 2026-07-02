import type {

    RiskLevel,

} from "../types/image";

/**
 * Convert confidence to risk level.
 */
export function getRiskLevel(

    confidence: number,

    prediction: "Real" | "Fake",

): RiskLevel {

    if (prediction === "Real") {

        if (confidence >= 95) {

            return "Low";

        }

        if (confidence >= 80) {

            return "Medium";

        }

        return "High";

    }

    if (confidence >= 95) {

        return "High";

    }

    if (confidence >= 80) {

        return "Medium";

    }

    return "Low";

}

/**
 * Tailwind colour class.
 */
export function getConfidenceColor(

    confidence: number,

): string {

    if (confidence >= 95) {

        return "text-green-400";

    }

    if (confidence >= 80) {

        return "text-yellow-400";

    }

    return "text-red-400";

}

/**
 * Badge background.
 */
export function getBadgeColor(

    confidence: number,

): string {

    if (confidence >= 95) {

        return "bg-green-500/20 text-green-400";

    }

    if (confidence >= 80) {

        return "bg-yellow-500/20 text-yellow-400";

    }

    return "bg-red-500/20 text-red-400";

}

/**
 * Confidence label.
 */
export function getConfidenceLabel(

    confidence: number,

): string {

    if (confidence >= 99) {

        return "Excellent";

    }

    if (confidence >= 95) {

        return "Very High";

    }

    if (confidence >= 85) {

        return "High";

    }

    if (confidence >= 70) {

        return "Moderate";

    }

    return "Low";

}

/**
 * Recommendation text.
 */
export function getRecommendation(

    prediction: "Real" | "Fake",

    confidence: number,

): string {

    if (prediction === "Real") {

        if (confidence >= 95) {

            return "The uploaded image appears authentic. No significant manipulation artefacts were detected.";

        }

        return "The uploaded image is likely authentic. Manual verification is recommended if the image is critical.";

    }

    if (confidence >= 95) {

        return "Strong evidence of AI manipulation was detected. Avoid using this image without further verification.";

    }

    return "Potential manipulation detected. Additional verification is recommended.";

}