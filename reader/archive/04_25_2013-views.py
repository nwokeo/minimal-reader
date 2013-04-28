from django.http import HttpResponse, HttpResponseRedirect 
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

#show starred. later: random, all feeds
def index(request):
    #articles = Article.objects.filter(read_later__exact='True')
    #ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'), extra=0)
    articles = Article.objects.filter(read_later__exact='True')#.order_by('-update_date', '-add_date')    
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)   
    feeds_labels =  Label.objects.all()
    return  render_to_response(
        'reader/index.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,},
        context_instance = RequestContext(request),
    )

#pass parameter for how many to show
def magic(request, amount):
    feed_list=[]
    high=Article.objects.filter(unread__exact='True').aggregate(Max('id'))['id__max']
    low=Article.objects.filter(unread__exact='True').aggregate(Min('id'))['id__min']
    for x in range(int(amount)):
        feed_list.append(randrange(low, high))
    articles = Article.objects.filter(id__in=feed_list, unread__exact='True').order_by('-update_date', '-add_date')    
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=articles)
    feeds_labels =  Label.objects.all()
    #return HttpResponse(articles)
    return  render_to_response(
        'reader/magic.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,},
        context_instance = RequestContext(request),
    )

#show specific feed
def detail(request, feed_id_pk):
    feed = Feed.objects.filter(id=feed_id_pk)[0]
    articles = Article.objects.filter(feed_id=feed_id_pk, unread=True).order_by('-update_date', '-add_date')
    #unread_count= Article.objects.filter(feed_id=feed_id_pk, unread=True).count()
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    formset = ArticleFormSet(queryset=Article.objects.filter(feed_id=feed_id_pk, unread=True))
    #feeds_labels = Label.objects.filter(feeds__unread_count__gt=0)   
    feeds_labels = Label.objects.all()
    return  render_to_response(
        'reader/detail.html',
        {'formset':formset, 'feeds_labels':feeds_labels, 'articles':articles,'feed':feed,},
        context_instance = RequestContext(request),
    )

#updates POST, no data returned
def update(request, feed_id_pk):
    #articles = Article.objects.filter(feed_id=feed_id_pk, unread=True)
    ArticleFormSet=modelformset_factory(Article, fields=('unread', 'read_later'))
    #formset = ArticleFormSet(queryset=Article.objects.filter(feed_id=feed_id_pk))
    form = ArticleFormSet(request.POST, queryset=Article.objects.filter(feed_id=feed_id_pk, unread=True))
    #article = Article.objects.get(id=article_id_pk)
    #form = ArticleForm(request.POST, instance=article)
    form.save()
    #return HttpResponseRedirect(reverse('detail', args=(feed_id_pk)))
    return redirect('/reader/'+feed_id_pk)



def testing(request, article_id_pk):
    article = Article.objects.get(id=article_id_pk)
    form = ArticleForm(request.POST, instance=article)
    if form.is_valid():
         result = "valid"
         form.save()
    else:
         result = "not valid"
    
    return  render_to_response(
        'reader/t.html',
        {'form':form, 'result':result, 'article':article},
        context_instance = RequestContext(request),
    )

    #article_id = int(request.POST['article_id'])
    #event = get_object_or_404(Article, id=article_id)
    #test get
    #article = Article.objects.get(id=165)
    #form = ArticleForm(request.POST, instance = article)
    # 
    # if form.is_valid():
    ##     result = "valid"
    #     a = form.save()
    #     article.unread = form.cleaned_data['unread']
    #     article.read_later = form.cleaned_data['read_later']
    # else:
    #     result = "not valid"
    #
    #return  render_to_response(
    #    'reader/t.html',
    #    {'form':form, 'result':result, 'article':article},
    #    context_instance = RequestContext(request),
    #)

    #labels = Label.objects.all()
    #template = loader.get_template('reader/t.html')
    #context = Context({
    #    'labels': labels,
    #})
    #return  HttpResponse(template.render(context))
