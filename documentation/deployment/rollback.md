# Rollback

Prefer application rollback while leaving forward-compatible schema intact. Before a schema downgrade, back up PostgreSQL and storage, inspect the migration downgrade, stop workers, and test against a restored copy. Migration `0005_integrations` removes integration records when downgraded and therefore requires explicit data-loss review.
