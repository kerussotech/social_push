import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class db_site(Base):
	__tablename__ = 'site'
	__table_args__ = {'schema': 'psh'}
	id = sa.Column(sa.Integer, primary_key = True)
	active = sa.Column(sa.Boolean)
	url = sa.Column(sa.String)
	user = sa.Column(sa.String)
	password = sa.Column(sa.String)

class db_post(Base):
	__tablename__ = 'post'
	__table_args__ = {'schema': 'psh'}
	
	app_id = sa.Column(sa.Integer, primary_key = True)
	site_id = sa.Column(sa.Integer)
	site_post_id = sa.Column(sa.Integer)
	modified_date = sa.Column(sa.Date)
	publish_date = sa.Column(sa.Date)
	post_status = sa.Column(sa.String)
	slug = sa.Column(sa.String)
	title = sa.Column(sa.String)
	link = sa.Column(sa.String)
	terms = sa.Column(sa.String)
	sticky = sa.Column(sa.String)
	app_create = sa.Column(sa.Date)
	app_update = sa.Column(sa.Date)
	