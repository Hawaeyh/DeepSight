from app.database.migrations import current_revision


def test_current_revision_is_head(migrated_database):
    _, engine = migrated_database
    assert current_revision(engine) == "0006_external_identity_billing"
