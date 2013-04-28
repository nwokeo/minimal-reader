from django.http import HttpResponse
from reader.models import Feed, Article, Rating, Label
from django.template import Context, loader

import feedparser
#monkeypatch to allow video embeds. thx http://www.rumproarious.com/
feedparser._HTMLSanitizer.acceptable_elements = feedparser._HTMLSanitizer.acceptable_elements + ['object', 'embed','iframe']
#import bs4

def index(request,):
    latest_feed_list = Feed.objects.order_by('-add_date')[:5]
    #output = '<br />'.join([f.title for f in latest_feed_list])
    template = loader.get_template('reader/index.html')
    context = Context({
        'latest_feed_list': latest_feed_list,
    })

    #can also use + to join
    return HttpResponse(template.render(context))

#def detail(request, feed_id):
#    #feed_id = Feed.objects.order_by('-add_date')[:5]
#    current_feed=Feed.objects.get(id=feed_id)    
#    template = loader.get_template('reader/detail.html')
#    context = Context({
#        'current_feed': current_feed,
#    })
#    return HttpResponse(template.render(context))
    #return HttpResponse("You're looking at poll %s." % feed_id)


def detail(request, feed_id):
    current_feed=Feed.objects.get(id=feed_id)
    current_url=current_feed.link
    fp = feedparser.parse(current_url)
    html=[]
    for entry in fp['entries'][0:10]: #only first 10 for testing
        html.append(entry['summary'])
    template = loader.get_template('reader/detail.html')
    context = Context({
        'html': html,
    })
    return HttpResponse(template.render(context))
    #return HttpResponse(feedparser._HTMLSanitizer.acceptable_elements)
