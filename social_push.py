import datetime
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from db_classes import *
import twitter
import bitly_api

Session = sa.orm.sessionmaker()
db_engine = sa.create_engine('postgresql+psycopg2://social_push:h3lpUte1l@localhost:5432/social_push?application_name=social_push')
db_connection = db_engine.connect()
Session.configure(bind=db_engine)
db_sqla = Session()

sites = db_sqla.query(db_site).filter(db_site.active == True)

for site in sites:
	client = Client(site.url, site.user, site.password)
	
	updates = client.call(posts.GetPosts({
		'number': 100,
		'offset': 0,
		'orderby': 'post-modified', 
		'order': 'DESC',
		'post_type': 'post',
		'post_status': 'publish'
	}))

	now = datetime.datetime.now()
	
	for update in updates:
		
		exists = db_sqla.query(db_post).filter(db_post.site_id == site.id,db_post.site_post_id == update.id).count()
		if not exists:
			db_sqla.add(db_post(site_id=site.id, site_post_id=update.id, modified_date=update.date_modified, publish_date=update.date, post_status=update.post_status, slug=update.slug, title=update.title, link=update.link, app_create=now, app_update=now))
		else:
			db_sqla.query(db_post).filter(db_post.site_id == site.id, db_post.site_post_id == update.id).\
				update({db_post.modified_date: update.date_modified, db_post.publish_date: update.date, db_post.post_status: update.post_status, db_post.slug: update.slug, db_post.title: update.title, db_post.link: update.link, db_post.app_update: now})

db_sqla.commit()

access_token = 'd856875d28988706cd42b0347588a91273c70df7'
bitly = bitly_api.Connection(access_token=access_token)

for site in sites:
	accounts = db_sqla.query(db_account).filter(db_account.site_id == site.id, is_active == 1)
	if accounts:
		for account in accounts:
			now = datetime.datetime.now()
			then = now - datetime.timedelta(0, 60 * (account.frequency - 2))
			if then > account.last:
				network = db_sqla.query(db_network).filter(db_network.id == account.network_id).one()
				if network and network.name == 'Twitter':
					twt = twitter.Api(consumer_key = network.auth->>'key', consumer_secret = network.auth->>'secret', access_token_key = account.auth->>'key', access_token_secret = account.auth->>'secret')
					post = db_sqla.query(db_post).filter(db_post.site_id == site.id, db_post.tw_id == None, db_post.publish_date <= now ).order_by(db_post.publish_date.asc()).first()
					short = bitly.shorten(post.link)
					text = post.title + ' ' + short['url']
					status = twt.PostUpdate(text)
					post.tw_id = status.id_str
					account.last = now
	
db_sqla.commit()