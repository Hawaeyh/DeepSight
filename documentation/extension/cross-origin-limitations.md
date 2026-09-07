# Cross-origin limitations

Some DRM, encrypted-media, browser-internal, or cross-origin videos taint the capture canvas. The extension cannot bypass that browser security boundary and shows a clear fallback message. Test on an ordinary visible HTML video; restricted pages and Chrome Web Store pages cannot run content scripts.
