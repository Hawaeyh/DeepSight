# Video validation

MP4, MOV, and WebM uploads are bounded before storage and checked for declared MIME, extension, container signature, OpenCV decode, dimensions, FPS, frame count, duration, and configured limits. Invalid uploads are removed. Rotation and variable-frame-rate interpretation remain codec/backend dependent and require representative manual fixtures.
