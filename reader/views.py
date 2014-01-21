from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from reader.models import Feed, Article, Rating, Label, Feed_base
from django.template import Context, loader
from reader.forms import ArticleForm, LabelForm
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.db.models import Max, Min
from random import randrange
from django.db import IntegrityError

#monkeypatch to allow video embeds. thx http://www.rumproarious.com/

#show starred.
def index(request):
    vars=request.GET
    p=int(vars.get('p',1))
    p=p*20
    articles = Article.objects.filter(read_later__exact='True').order_by('-update_date', '-add_date')[p-20:p]
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

#configurable display
def magic(request):
    vars=request.GET
    p=int(vars.get('p',20))
    p=p*20

    if vars.get('cat'):
	      cat_filter=vars.get('cat')
    else:
	      cat_filter='.'

    sortby=vars.get('sort','desc')

    if sortby=='rand': #random
	    articles = sortrandom(20, cat_filter) #hard-code to 20 for now. was get.amount
    elif sortby=='desc': #descending
        articles = Article.objects.filter(unread__exact='True', feed__label__label__regex=cat_filter).order_by('-update_date', '-add_date')[p-20:p]
    elif sortby=='asc': #ascending
        articles = Article.objects.filter(unread__exact='True', feed__label__label__regex=cat_filter).order_by('update_date', 'add_date')[p-20:p]
    else:  #default
        pass

    f=vars.get('f','all')
    if f=='all':
        feeds_labels =  Label.objects.all()
        disp_feeds=''
    elif f=='unread':
        disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('unread_count')#[:10]
        feeds_labels=''
    elif f=='new':
	    disp_feeds=Feed.objects.filter(unread_count__gt=0).order_by('-add_date')#[:10]
	    feeds_labels=''

    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)

    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'disp_feeds':disp_feeds,'last_update':last_update(),},
        context_instance = RequestContext(request),
    )

def sortrandom(amount, cat_filter):
    return Article.objects.filter(unread__exact='True', feed__label__label__regex=cat_filter).order_by('?')[:amount]

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

def allread(request,feed_id_pk):
    Article.objects.filter(feed_id=feed_id_pk).update(unread=0)
    return redirect(request.META['HTTP_REFERER'])



def last_update():
    return Article.objects.all().aggregate(Max('add_date'))
