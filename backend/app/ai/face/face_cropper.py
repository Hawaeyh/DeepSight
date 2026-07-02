import cv2

from insightface.app import FaceAnalysis

# ---------------------------------------
# Initialize InsightFace
# ---------------------------------------

face_app = FaceAnalysis(
    providers=[
        "CPUExecutionProvider",
    ]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640),
)

print("InsightFace Loaded")


# ---------------------------------------
# Extract Largest Face
# ---------------------------------------

def extract_face(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return None

    faces = face_app.get(img)

    if len(faces) == 0:
        return None

    face = max(
        faces,
        key=lambda x: x.bbox[2] * x.bbox[3],
    )

    x1, y1, x2, y2 = map(
        int,
        face.bbox,
    )

    face_crop = img[y1:y2, x1:x2]

    face_crop = cv2.cvtColor(
        face_crop,
        cv2.COLOR_BGR2RGB,
    )

    return face_crop