minimal-reader
==============

django-powered minimal rss feed reader

VERY untested, VERY preliminary.

Inteded to run on internal server - data transfer is somewhat inefficient, so should be LAN connection.

GET variables:

amt (int):
number of articles to return

sort (rand/desc/asc):
order by which to sort returned articles

cat ([defined label]):
return articles with a given label

f (new/unread/all):
order by which feeds are sorted in the nav bar. this will not display label categories

example:
http://[server]:[port]/reader/magic?amt=20&sort=rand&cat=uncategorized&f=new

returns 20 random articles with the "uncategorized" label, shows all feeds in the nav bar, ordered by most recently added
