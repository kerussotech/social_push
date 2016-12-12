import datetime
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from db_classes import *
import twitter
import bitly_api
import calendar
from datetime import datetime, timedelta

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

	now = datetime.now()
		
	for update in updates:
		
		utc_dt1 = update.date
		timestamp1 = calendar.timegm(utc_dt1.timetuple())
		local_dt1 = datetime.fromtimestamp(timestamp1)
		
		utc_dt2 = update.date_modified
		timestamp2 = calendar.timegm(utc_dt2.timetuple())
		local_dt2 = datetime.fromtimestamp(timestamp2)
		
		exists = db_sqla.query(db_post).filter(db_post.site_id == site.id,db_post.site_post_id == update.id).count()
		if not exists:
			db_sqla.add(db_post(site_id=site.id, site_post_id=update.id, modified_date=local_dt2, publish_date=local_dt1, post_status=update.post_status, slug=update.slug, title=update.title, link=update.link, app_create=now, app_update=now))
		else:
			db_sqla.query(db_post).filter(db_post.site_id == site.id, db_post.site_post_id == update.id).\
				update({db_post.modified_date: local_dt2, db_post.publish_date: local_dt1, db_post.post_status: update.post_status, db_post.slug: update.slug, db_post.title: update.title, db_post.link: update.link, db_post.app_update: now})

db_sqla.commit()

access_token = 'd856875d28988706cd42b0347588a91273c70df7'
bitly = bitly_api.Connection(access_token=access_token)

for site in sites:
	accounts = db_sqla.query(db_account).filter(db_account.site_id == site.id, db_account.is_active == 1)
	if accounts:
		for account in accounts:
			now = datetime.now()
			then = now - timedelta(0, 60 * (account.frequency - 2))
			if (account.last and then > account.last) or account.last == None:
				network = db_sqla.query(db_network).filter(db_network.id == account.network_id).one()
				if network and network.name == 'Twitter':
					twt = twitter.Api(consumer_key = network.auth['key'], consumer_secret = network.auth['secret'], access_token_key = account.auth['key'], access_token_secret = account.auth['secret'])
					next_post = db_sqla.query(db_post).filter(db_post.site_id == site.id, db_post.tw_id == None, db_post.publish_date <= now ).order_by(db_post.publish_date.asc()).first()
					short = bitly.shorten(next_post.link)
					text = next_post.title + ' ' + short['url']
					status = twt.PostUpdate(text)
					next_post.tw_id = status.id_str
					account.last = now
	
db_sqla.commit()