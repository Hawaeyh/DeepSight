# Webcam analysis

The browser samples at most one frame per second, prevents overlapping requests, and uses a seven-result rolling window with a 65% consensus requirement. Hidden tabs are not sampled. Frames use the protected image endpoint and are stored in the signed-in user's history; stop ends camera tracks immediately.
