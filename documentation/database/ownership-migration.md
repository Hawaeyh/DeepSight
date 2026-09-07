# Ownership migration

Alembic revision `0003_security_ownership` adds trusted identity metadata, `guest_sessions`, analysis owner columns, source metadata, feedback ownership, foreign keys, indexes, and the single-owner check constraint.

The migration deliberately leaves all pre-existing analyses with both owner columns null. These legacy unowned records are retained for later authorised review. They are excluded from normal history/dashboard queries and inaccessible through user detail, report, feedback, deletion, and media routes. Ownership must never be guessed from filenames, email addresses, or administrator accounts.

The migration has a downgrade and was validated on isolated SQLite databases, including insertion before revision 0003 followed by upgrade and null-ownership verification. The real legacy SQLite database was not upgraded or modified during this phase.
