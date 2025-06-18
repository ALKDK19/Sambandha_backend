from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql import text


@as_declarative()
class Base:
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"))
