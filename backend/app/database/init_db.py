from app.database.database import Base, engine

from app.models.analysis import Analysis

Base.metadata.create_all(bind=engine)