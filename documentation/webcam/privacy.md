# Webcam privacy

Webcam access is explicit. Frames are sampled at most once per second, unchanged, blurry, and no-face frames are skipped, and every uploaded frame is deleted after inference. DeepSight stores only one final owned session summary. Stopping or leaving the page closes camera tracks and finalises or cancels the session.
