#!/usr/bin/python
import MySQLdb
import feedparser
import sys
from dateutil import parser
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('reader.cfg')

#monkeypatch to allow video embeds. thx http://www.rumproarious.com/
s=set(['object', 'embed','iframe'])
feedparser._HTMLSanitizer.acceptable_elements = feedparser._HTMLSanitizer.acceptable_elements | s

db=MySQLdb.connect(host="localhost",user=config.get('Database', 'username'),passwd=config.get('Database', 'password'),db="micro_rss", charset='utf8')

cur = db.cursor() 

####enough of a use case to only look at recent articles? speed?
cur.execute('SELECT * FROM reader_feed')

for row in cur.fetchall() :
    print 'Reading ID:' + str(row[0]), '( '+row[2].encode('ascii', 'ignore')+' )'
    fp = feedparser.parse(row[2])
    c=0
    for entry in fp['entries']:
        try:
            cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
                        (row[0], entry['link'], parser.parse(entry['updated']),  entry['title'], entry['content'][0]['value']))
            #use fp['entries'][0]['content'][0]['value'] instead of summary for full text
            #print 'all good'
        except MySQLdb.IntegrityError as e:
            #print 'Article Already Exists', e
	        pass
        except KeyError as e:
            e=y=str(e).replace("'","")
            try:
                if e=='link':
                    #print "No Link Element"
                    cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
                                (row[0], '', parser.parse(entry['updated']),  entry['title'], entry['content'][0]['value']))
                elif e=='updated':
                    #print 'No Updated Element'
                    cur.execute('insert into reader_article (feed_id, link, title, content) VALUES (%s, %s, %s, %s)',
                                (row[0], entry['link'], entry['title'], entry["summary"]))
                elif e=='content': #if content is broken, attempt to insert summary
                    #print 'No Content Element'
                    try:
                        cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
                                    (row[0], entry['link'], parser.parse(entry['updated']), entry['title'], entry['summary']))
                    except KeyError as e2:
                        if str(e2).replace("'","")=='summary':
                            print 'No content or summary entries. Inserting NULL.'
                            cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
                                        (row[0], entry['link'], parser.parse(entry['updated']),  entry['title'], ''))
                elif e=='title':
                    #print "No title element. Inserting link instead"
                    cur.execute('insert into reader_article (feed_id, link, update_date, title, content) VALUES (%s, %s, %s, %s, %s)',
                                (row[0], entry['link'], parser.parse(entry['updated']), entry['link'] , ['content'][0]['value']))
                else:
                    print '!!Key Error!!: ', e, entry
            except MySQLdb.IntegrityError as e:
                #print 'Article Already Exists', e
                pass
            except:
                print "Unexpected error (inside loop):", sys.exc_info()[0]

        #need to add this to each error section? use functions
        except ValueError as e:
            #most value errors seem to be bad date formats. try removing date
            try:
                cur.execute('insert into reader_article (feed_id, link, title, content) VALUES (%s, %s, %s, %s)',
                            (row[0], entry['link'], entry['title'], entry["summary"]))
            except ValueError as e:
                print 'Value Error', e, entry
            except MySQLdb.IntegrityError as e:
                #print 'Article Already Exists', e
                pass

        except:
            print "Unexpected error (outer loop):", sys.exc_info()[0]
        c += 1
        cur.execute('commit')
    print "Read " + str(c) + 'rows.'
