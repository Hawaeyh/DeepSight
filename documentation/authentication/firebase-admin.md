# Firebase Admin authentication

Firebase Admin is disabled by default. Configure `FIREBASE_ADMIN_ENABLED`, project ID, and either an external credential file or environment-provided service-account fields. `/auth/firebase` verifies signature, issuer, audience, expiry, revocation, UID, and verified email through Firebase Admin before issuing a local JWT. Database roles remain authoritative.
