# Image validation

`POST /api/v1/analysis/image` accepts JPEG, PNG, and WebP only. The MIME type, extension, decoded Pillow format, dimensions, and bounded byte length must agree. Defaults are 10 MB, 128x128 minimum, and 8192x8192 maximum. Files receive generated storage names under an owner-scoped directory; failed validation or inference removes the staged file.
