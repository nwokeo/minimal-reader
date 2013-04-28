#!/usr/bin/python
import MySQLdb
import feedparser
import sys
from dateutil import parser
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('reader.cfg')

#monkeypatch to allow video embeds. thx http://www.rumproarious.com/
feedparser._HTMLSanitizer.acceptable_elements = feedparser._HTMLSanitizer.acceptable_elements + ['object', 'embed','iframe']
#import bs4

db=MySQLdb.connect(host="localhost",user=config.get('Database', 'username'),passwd=config.get('Database', 'password'),db="micro_rss", charset='utf8')

cur = db.cursor() 

####enough of a use case to only look at recent articles? speed?
#cur.execute("SELECT * FROM reader_feed")
#last_update=cur.fetchall()

cur.execute('SELECT * FROM reader_feed_base')

for row in cur.fetchall() :
    print 'reading ' + row[1], row[2]
    fp = feedparser.parse(row[2])
    #print fp['entries'][0].keys()
    for entry in fp['entries']:
	#print entry['title'].decode('utf-8')
	#print entry['title']
	#print entry['title'].encode('utf-8')

	try:
	    cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)', 
		(row[0], entry['link'], parser.parse(entry['updated']),  entry['title'], entry['summary']))
        except MySQLdb.IntegrityError as e:
            print 'Article Already Exists', e
        except KeyError as e:
	    e=y=str(e).replace("'","")
	    try:
	        if e=='link':
		    for entry in fp['entries']:
		        cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
		        (row[0], '', parser.parse(entry['updated']),  entry['title'], entry["summary"]))
		elif e=='updated':
		    print 'attempted update fix'
		    for entry in fp['entries']:
		        cur.execute('insert into reader_article (feed_id, link, title, content) VALUES (%s, %s, %s, %s)',
		        (row[0], entry['link'], entry['title'], entry["summary"]))
		elif e=='summary':
		    print 'attempted summary fix'
		    for entry in fp['entries']:
			cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
		        (row[0], entry['link'], parser.parse(entry['updated']),  entry['title'], ''))
		elif e=='title':
		    for entry in fp['entries']:
		        cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
		        (row[0], entry['link'], parser.parse(entry['updated']), entry['link'] , entry["summary"]))
		else:
		    print '!!Key Error!!: ', e, entry
	    except:
		print "Unexpected error:", sys.exc_info()[0]
            #print 'Error, written to DB:', e, entry
	#need to add this to each error section? use functions
        except ValueError as e:
	    print 'Value Error', e, entry
 	except:
	    print "Unexpected error:", sys.exc_info()[0]
	
        cur.execute('commit')
