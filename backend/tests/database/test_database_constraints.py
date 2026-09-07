import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError


def test_indexes_and_unique_email(migrated_database):
    _, engine = migrated_database
    names = {item["name"] for item in inspect(engine).get_indexes("analysis")}
    assert {"ix_analysis_created_at", "ix_analysis_file_type", "ix_analysis_prediction", "ix_analysis_model_name"} <= names
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO users (email, full_name, password) VALUES ('same@example.com','A','hash')"))
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(text("INSERT INTO users (email, full_name, password) VALUES ('same@example.com','B','hash')"))


def test_feedback_foreign_key_and_cascade(migrated_database):
    _, engine = migrated_database
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(text("INSERT INTO analysis_feedback (analysis_id,is_correct,status,created_at) VALUES (999,1,'reviewed',CURRENT_TIMESTAMP)"))
    required = "filename,file_path,file_type,prediction,confidence,risk_level,model_name,model_version,device,processing_time,status"
    values = "'a','a','image','Real',.9,'low','m','1','cpu',.1,'Completed'"
    with engine.begin() as connection:
        analysis_id = connection.execute(text(f"INSERT INTO analysis ({required}) VALUES ({values}) RETURNING id")).scalar_one()
        connection.execute(text("INSERT INTO analysis_feedback (analysis_id,is_correct,status,created_at) VALUES (:id,1,'reviewed',CURRENT_TIMESTAMP)"), {"id": analysis_id})
        connection.execute(text("DELETE FROM analysis WHERE id=:id"), {"id": analysis_id})
        assert connection.execute(text("SELECT count(*) FROM analysis_feedback WHERE analysis_id=:id"), {"id": analysis_id}).scalar_one() == 0


def test_analysis_cannot_have_user_and_guest_owners(migrated_database):
    _, engine = migrated_database
    with engine.begin() as connection:
        user_id = connection.execute(text("INSERT INTO users (email,full_name,password) VALUES ('owner@example.com','Owner','hash') RETURNING id")).scalar_one()
        guest_id = connection.execute(text(
            "INSERT INTO guest_sessions (token_hash,analysis_count,created_at,last_used_at,expires_at) "
            "VALUES ('hash',0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,'2099-01-01') RETURNING id"
        )).scalar_one()
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(text(
            "INSERT INTO analysis (owner_user_id,guest_session_id,filename,file_path,file_type,prediction,confidence,risk_level,model_name,model_version,device,processing_time,status) "
            "VALUES (:user_id,:guest_id,'a','a','Image','Real',90,'Low','m','1','cpu',.1,'Completed')"
        ), {"user_id": user_id, "guest_id": guest_id})
