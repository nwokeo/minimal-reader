import opml
import MySQLdb

import feedparser

####todo####
#1. rmove labels from my sql, re-run feed block to remove dups
#2. complete else logic: uncategorized feeds. 

feedparser._HTMLSanitizer.acceptable_elements = feedparser._HTMLSanitizer.acceptable_elements + ['object', 'embed','iframe']
#import bs4

db=MySQLdb.connect(host="localhost",user=config.get('Database', 'username'),passwd=config.get('Database', 'password'),db="micro_rss", charset='utf8')
cur = db.cursor()

opml_file = '/home/ch1r0n/django_dev/micro_rss/subscriptions.xml'
o=opml.parse(opml_file)

print 'reading ' + o.title + ' ...'

#create list of existing labels
cur.execute('SELECT * FROM reader_label')
labels = []
for item in cur.fetchall():
        labels.append(item[1])
#add labels
for item in o:
    if len(item) > 0:
        if item.title in labels:
            print 'LABEL EXISTS', item.title
        else:
            cur.execute('insert into reader_label (label) VALUES (%s)', item.title)
            print 'added ',item.title
            labels.append(item.title)
        cur.execute('commit')

#add feeds
for item in o:
    #somewhere better to update this?
    #create list of feed URLs whose labels exist
    existing_label = []
    cur.execute('SELECT * FROM reader_label_feeds lf join reader_feed_base f on f.id=lf.feed_id')
    for x in cur.fetchall():
        existing_label.append(x[5])
    #create list of feed URLs that exist
    existing_feed = []
    cur.execute('SELECT link FROM reader_feed_base')
    for y in cur.fetchall():
        existing_feed.append(y[0])

    if len(item) > 0:
  	print item.title
	for feed in item: #link is unique, so dont need to enforce.
	    print '\t ADDING', feed.title, '(label: ', item.title, ')'
	    try:
            	cur.execute('insert into reader_feed_base (title, link, description, homepage, type) VALUES (%s, %s, %s, %s, %s)',
                    (feed.title, feed.xmlUrl,feed.text, feed.htmlUrl, feed.type))
            	cur.execute('commit')
	    	print '\t added to feeds'
	    except MySQLdb.IntegrityError, e:
		print 'FEED EXISTS in reader_feed_base-', feed.title, e
            #associate label
	    try:
	        cur.execute('insert into reader_label_feeds (label_id, feed_id) select l.id, f.id from reader_label l, reader_feed_base f where f.link="' + feed.xmlUrl + '" and l.label="' + item.title + '"')
                cur.execute('commit')
	        print '\t associated with label'
            except MySQLdb.IntegrityError, e:
                print 'Reader/Label Relationship EXISTS-', feed.title, item.title, e
    else:
        #uncat - add to db, associate label
	if item.xmlUrl in existing_feed:
	    print 'Uncategorized Feed EXISTS- ', item.title, item.xmlUrl
        else:
            print 'ADDED- ',item.title
 	    #add uncat feeds
	    cur.execute('insert into reader_feed_base (title, link, description, homepage, type) VALUES (%s, %s, %s, %s, %s)', 
		(item.title, item.xmlUrl,item.text, item.htmlUrl, item.type))
	    cur.execute('commit')
	    #associate label
            cur.execute('insert into reader_label_feeds (label_id, feed_id) select l.id, f.id from reader_label l, reader_feed_base f where f.link="' + item.xmlUrl + '" and l.label="uncategorized"')
            cur.execute('commit')

#update articles
