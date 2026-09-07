# Database integrity audit

The read-only audit checks required tables, row counts, orphan feedback, case-insensitive duplicate user and entitlement emails, entitlements without matching users, invalid roles/plans/statuses, and missing required analysis values. It reports counts, not personal rows.

```powershell
.\scripts\audit-database.ps1
```

The 2026-07-28 legacy SQLite audit found 5 users, 803 analyses, 4 feedback rows, 5 entitlements, and 824 usage rows. It found zero orphan feedback, duplicate emails, orphan entitlements, invalid enumerated values, or missing required analysis values. The legacy database had no foreign keys; therefore migration `0002` adds only the feedback-to-analysis relationship supported by current data. Other semantic relationships (including ownership) are deliberately deferred.
