from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from reader.models import Feed, Article, Label
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.db import IntegrityError
from random import randrange
#from reader.forms import ArticleForm, LabelForm
#from django.core.urlresolvers import reverse
#from django.db.models import Max, Min


#monkeypatch to allow video embeds. thx http://www.rumproarious.com/
#show starred.
def index(request):
    vars = request.GET
    p = int(vars.get('p', 1))
    p *= 20
    articles = Article.objects.filter(read_later__exact='True').order_by('-update_date', '-add_date')[p-20:p]
    ArticleFormSet = modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)
    #feed__label__label=cat
    feeds_labels = Label.objects.all()
    disp_feeds = ''
    #order by most recent
    return render_to_response(
        'reader/magic.html',
        {'formset': formset, 'feeds_labels': feeds_labels, 'articles': articles, 'disp_feeds': disp_feeds, },
        context_instance=RequestContext(request),
    )


#configurable display
def magic(request):
    vars = request.GET
    p = int(vars.get('p', 20))
    p *= 20

    if vars.get('cat'):
        cat_filter = vars.get('cat')
    else:
        cat_filter = False

    sortby = vars.get('sort', 'desc')

    if cat_filter:
        if sortby == 'rand': #random
            articles = sortrandom(20, cat_filter) #hard-code to 20 for now. was get.amount
        elif sortby == 'desc': #descending
            articles = Article.objects.filter(unread__exact='True', feed__label__label__exact=cat_filter).order_by('-update_date', '-add_date')[p-20:p]
        elif sortby == 'asc': #ascending
            articles = Article.objects.filter(unread__exact='True', feed__label__label__exact=cat_filter).order_by('update_date', 'add_date')[p-20:p]
        else:  #default
            pass
    else:
        if sortby == 'rand': #random
            articles = sortrandom(20, cat_filter) #hard-code to 20 for now. was get.amount
        elif sortby == 'desc': #descending
            articles = Article.objects.filter(unread__exact='True').order_by('-update_date', '-add_date')[p-20:p]
        elif sortby == 'asc': #ascending
            articles = Article.objects.filter(unread__exact='True').order_by('update_date', 'add_date')[p-20:p]
        else:  #default
            pass

    #feed filter works. implement later? if implemented, remove feeds_labels,disp_feeds statement below
    '''
    f=vars.get('f','all')
    if f=='all':
        feeds_labels =  Label.objects.all()
        disp_feeds=''
    elif f=='unread':
        disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('unread_count')#[:10]
        feeds_labels=''
    elif f=='new':
        disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('-add_date')#[:10]
        # feeds_labels=''
    '''
    feeds_labels = Label.objects.all()
    disp_feeds = ''

    ArticleFormSet = modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)

    return render_to_response(
        'reader/magic.html',
        {'formset': formset, 'feeds_labels': feeds_labels, 'articles': articles, 'disp_feeds': disp_feeds, }, #'last_update':last_update(),
        context_instance=RequestContext(request),
    )


def sortrandom(amount, cat_filter):
    #random by feed
    if cat_filter:
        return Article.objects.filter(unread__exact='True', feed__label__label__exact=cat_filter).order_by('?')[:amount]
    else:
        #no feed filter. no need to scan whole table.
        rands = []
        for x in range(amount):
            rands.append(randrange(Article.objects.count()))
        return Article.objects.filter(unread__exact='True', id__in=rands)


#show specific feed
def detail(request, feed_id_pk):
    vars=request.GET
    p=int(vars.get('p',1))
    p=p*20
    feed = Feed.objects.filter(id=feed_id_pk)[0]
    articles = Article.objects.filter(feed_id=feed_id_pk, unread=True).order_by('-update_date', 'add_date')[p-20:p]
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later', 'id'))
    formset = ArticleFormSet(queryset=articles)
    feeds_labels = Label.objects.all()

    #later: clean up via args
    #args={}
    #args['formset']=ArticleFormSet(queryset=articles)
    #args['feeds_labels']=Label.objects.all()
    #return  render_to_response('reader/magic.html',args,context_instance = RequestContext(request),)

    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'feed':feed,},
        context_instance = RequestContext(request),
    )

#updates POST, no data returned
def update(request):
    l=[]
    for item in request.POST.items():
        if '-id' in item[0]:
            l.append(item[1])
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    form = ArticleFormSet(request.POST, queryset=Article.objects.filter(id__in=l))#, unread=True))
    form.save()
    return redirect(request.META['HTTP_REFERER'])

def search(request):
    vars=request.GET
    p=int(vars.get('p',1))
    q=vars.get('q')
    p=p*20
    #TODO:  use get instead to have multiple pages of results
    #uses boolean mysql full-text search: https://dev.mysql.com/doc/refman/5.0/en/fulltext-boolean.html
    articles = Article.objects.raw('SELECT id,link,update_date,add_date,title,content,unread,read_later FROM reader_article WHERE MATCH (title,content) AGAINST ('+ \
                                   "'"+q+"' IN BOOLEAN MODE)"+'order by add_date desc')[p-20:20]

    #return  HttpResponse(request.POST.items()[1][1])
    #return  HttpResponse('SELECT * FROM reader_article WHERE MATCH (title,content) AGAINST ('+"'"+request.POST.items()[1][1]+"')")
    #return HttpResponse(articles[0][1])

    return  render_to_response(
        'reader/search.html',
        {'articles':articles,},
        context_instance = RequestContext(request),
    )

#mark all as read helper
def allread(request,feed_id_pk):
    Article.objects.filter(feed_id=feed_id_pk).update(unread=0)
    return redirect(request.META['HTTP_REFERER'])


def labels(request):
    feeds=Feed.objects.all()
    return  render_to_response(
        'reader/labels.html',
        {'feeds':feeds,},
        context_instance = RequestContext(request),
    )

#move to stats page
'''
def last_update():
    return Article.objects.all().aggregate(Max('add_date'))
'''