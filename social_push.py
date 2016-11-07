import datetime
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from db_classes import *

Session = sa.orm.sessionmaker()
db_engine = sa.create_engine('postgresql+psycopg2://social_push:xxxxxxxx@localhost:5432/social_push?application_name=social_push')
db_connection = db_engine.connect()
Session.configure(bind=db_engine)
db_sqla = Session()

site = db_sqla.query(db_site).filter(db_site.active == True,db_site.id == 1).one()

client = Client(site.url, site.user, site.password)

updates = client.call(posts.GetPosts({
		'number': 10,
		'offset': 0,
		'orderby': 'post-modified', 
		'order': 'DESC',
		'post_type': 'post',
		'post_status': 'publish'
	}))

now = datetime.datetime.now()
#adjust timezone of server
	
for update in updates:

	# Query db for post
	# if not exist insert it
	# if exists, check timestamps
	# if different modified date, update it

	db_sqla.add(db_post(site_id=site.id, site_post_id=update.id, modified_date=update.date_modified, publish_date=update.date, post_status=update.post_status, slug=update.slug, title=update.title, link=update.link, app_create=now, app_update=now))

db_sqla.commit()