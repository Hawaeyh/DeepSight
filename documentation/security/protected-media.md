# Protected media

The unauthenticated `/media` static mount has been removed. Original images/videos, image thumbnails, reports, and video frames are returned only after identity and ownership verification.

Stored paths are resolved server-side and must remain inside the configured upload, frame, or report root. Requests cannot supply filenames or filesystem paths. Missing files, paths outside the root, and cross-owner access return a safe 404. Responses use private/no-store caching and `nosniff`; absolute paths are excluded from analysis API schemas.

The frontend downloads protected content through the authenticated Axios client with credentials. Blob URLs are created locally and revoked on component cleanup. Bearer tokens are never placed in query strings.

Deletion verifies ownership before deleting the database record and only removes physical files that pass the same containment check.
