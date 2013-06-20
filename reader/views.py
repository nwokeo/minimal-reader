from django.http import HttpResponse, HttpResponseRedirect, HttpRequest 
from reader.models import Feed, Article, Rating, Label
from django.template import Context, loader
from reader.forms import ArticleForm
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.db.models import Max, Min
from random import randrange

#monkeypatch to allow video embeds. thx http://www.rumproarious.com/

#show starred.
def index(request):
    articles = Article.objects.filter(read_later__exact='True').order_by('-update_date', '-add_date')    
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)
    #feed__label__label=cat   
    feeds_labels =  Label.objects.all()
    disp_feeds=''
    #order by most recent
    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'disp_feeds':disp_feeds,},
        context_instance = RequestContext(request),
    )

def magic(request):
    #feed_list=[]
    vars=request.GET
    amount=int(vars.get('amt',20))
    sortby=vars.get('sort','desc')
    cat=vars.get('cat','uncategorized')
    f=vars.get('f','all')
    if sortby=='rand': #random
	articles = sortrandom(amount, sortby, cat)
    elif sortby=='desc': #descending
        articles = Article.objects.filter(unread__exact='True', feed__label__label=cat).order_by('-update_date', 'add_date')[:amount]
    elif sortby=='asc': #ascending
        articles = Article.objects.filter(unread__exact='True', feed__label__label=cat).order_by('update_date', 'add_date')[:amount]
    else:  #default
        pass    
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)
    if f=='all':
        feeds_labels =  Label.objects.all()
        disp_feeds=''
    elif f=='unread':
        disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('unread_count')#[:10]
        feeds_labels=''
    elif f=='new':
	disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('-add_date')#[:10]
	feeds_labels=''

    #return HttpResponse(vars['s'])
    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'disp_feeds':disp_feeds,},
        context_instance = RequestContext(request),
    )

def sortrandom(amount, sortby, cat):
    feed_list=[]
    high=Article.objects.filter(unread__exact='True', feed__label__label=cat).aggregate(Max('id'))['id__max']
    low=Article.objects.filter(unread__exact='True', feed__label__label=cat).aggregate(Min('id'))['id__min']
    for x in range(amount):
        feed_list.append(randrange(low, high))
    return Article.objects.filter(id__in=feed_list, unread__exact='True') #feed__label__label=cat
    #random by category disabled for now

#show specific feed
def detail(request, feed_id_pk):
    feed = Feed.objects.filter(id=feed_id_pk)[0]
    articles = Article.objects.filter(feed_id=feed_id_pk, unread=True).order_by('-update_date', 'add_date')[:20]
    #unread_count= Article.objects.filter(feed_id=feed_id_pk, unread=True).count()
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later', 'id'))
    formset = ArticleFormSet(queryset=articles)
    #feeds_labels = Label.objects.filter(feeds__unread_count__gt=0)   
    feeds_labels = Label.objects.all()
    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'feed':feed,},
        context_instance = RequestContext(request),
    )

#updates POST, no data returned
def update(request, feed_id_pk=''):
    l=[]
    for item in request.POST.items():
        if '-id' in item[0]:
            l.append(item[1])
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    form = ArticleFormSet(request.POST, queryset=Article.objects.filter(id__in=l, unread=True))
    form.save()
    return redirect(request.META['HTTP_REFERER'])

def allread(request,feed_id_pk):
    Article.objects.filter(feed_id=feed_id_pk).update(unread=0)
    return redirect(request.META['HTTP_REFERER'])
