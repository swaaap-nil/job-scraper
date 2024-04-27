import os
from datetime import datetime, date, time
from typing import List, Union

from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
import pytz
from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters, OnSiteOrRemoteFilters, TimeFilters, TypeFilters

engine = create_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(bind=engine)
db_session = Session()

Base = declarative_base()

class BaseMixin(object):
    # a base class for logic we want to extend into other models
    indian_tz = pytz.timezone('Asia/Kolkata')
    id =                Column(Integer, primary_key=True)
    created_at =        Column(DateTime, default=datetime.now(tz= indian_tz), nullable=False)
    updated_at =        Column(DateTime, default=datetime.now(tz= indian_tz), onupdate=datetime.now(tz= indian_tz), nullable=False)

    def to_dict(self):
        # Convert all the attributes in this instance of a model
        # into a python dict. Useful for JSON serialization.
        cols = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for k, v in cols.items():
            if isinstance(v, datetime):
                cols[k] = v.isoformat()
            elif isinstance(v, date):
                cols[k] = v.strftime("%Y-%m-%d")
            elif isinstance(v, time):
                cols[k] = v.strftime("%H:%M:%S")
        return cols

    def save(self):
        db_session.add(self)
        db_session.commit()
        return self


class BaseJobPosting(Base, BaseMixin):
    __tablename__ = 'job'
    title = Column(String)
    company = Column(String)
    company_link = Column(String)
    date = Column(String)
    link = Column(String)
    insights = Column(String)
    description = Column(Text)
    description_length = Column(Integer)
    industry = Column(String)
    
    __mapper_args__ = {
        # "polymorphic_on": "type",
        "polymorphic_identity": "job",
        "with_polymorphic" : "*"
    }

class LinkedInPosting(BaseJobPosting):

    __tablename__ = 'linkedin'
    on_site_or_remote= Column(String)
    experience = Column(String)
    type = Column(String)
    time = Column(String)
    query = Column(String)
    job_id = Column(Integer, ForeignKey('job.id'))

    __mapper_args__ = {
        "polymorphic_identity": "linkedin",
    }
