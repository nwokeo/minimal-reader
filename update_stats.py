#!/usr/bin/python
import MySQLdb
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('reader.cfg')

db=MySQLdb.connect(host="localhost",user=config.get('Database', 'username'),passwd=config.get('Database', 'password'),db="micro_rss", charset='utf8')

cur = db.cursor()
cur.execute('SELECT rf.id,rf.title,(select count(0) from reader_article ra where ((ra.unread = 1) and (rf.id = ra.feed_id))) AS unread_count FROM reader_feed rf')

for row in cur.fetchall():
    cur.execute('update reader_feed set unread_count=%s where id=%s',(row[2],row[0]))

'''
TODO:
-define article update interval
-rss/atom validation API?
-locate dead links
-
'''