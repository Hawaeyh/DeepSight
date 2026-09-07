# Authentication identity

DeepSight currently trusts its server-signed local JWT. Password login is verified against the local password hash; Google Identity Services credentials are verified server-side and exchanged for the same local JWT. Firebase Admin ID-token verification is not yet implemented and is not claimed.

`get_current_user`, `get_optional_current_user`, and `require_admin` are the route-level identity dependencies. They resolve the current database user from the signed token, reject missing/invalid tokens with 401, reject inactive users with 403, and read current roles from the database rather than trusting role or plan claims from React.

The trusted user contains the database ID, nullable Firebase UID, normalized email, database role, active state, email-verification state, and authentication source. New tokens contain a stable database user ID and email but no authoritative role.

Future Firebase adoption must verify Firebase ID tokens through the Admin SDK, link the verified UID to `users.firebase_uid`, preserve local-account migration, and keep authorization roles in PostgreSQL.
