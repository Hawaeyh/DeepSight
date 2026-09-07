# Firebase account linking

DeepSight resolves an existing account by Firebase UID. A verified Firebase token whose email matches an unlinked local account receives `ACCOUNT_LINK_CONFLICT`; it is not automatically merged. This prevents possession of a different identity credential from silently taking over an existing password account. An interactive reauthentication/linking flow remains required for that case.
