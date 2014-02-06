from django.db import models
from django.forms import ModelForm
import datetime
from django.utils import timezone

#class Label(models.Model):
#    label = models.CharField(max_length=25)
    #feeds = models.ManyToManyField(Feed)
#    def __unicode__(self):
#        return self.label
#    class Meta:
#        ordering = ('label',)

class Feed(models.Model):
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    add_date = models.DateTimeField()
    description=models.CharField(max_length=255)
    homepage=models.CharField(max_length=255)
    type =models.CharField(max_length=10,blank=True)
    favico_url=models.CharField(max_length=100,blank=True)
    favico=models.CharField(max_length=10,blank=True)
    unread_count=models.IntegerField(blank=True)
    #labels = models.ManyToManyField(Label)

    def __unicode__(self):
        return self.title

    def was_added_recently(self):
        return self.add_date >= timezone.now() - datetime.timedelta(days=1)

    class Meta:
        ordering = ('title',)

class Article(models.Model):
    feed = models.ForeignKey(Feed)
    link = models.TextField()
    update_date = models.DateTimeField()
    add_date = models.DateTimeField()
    title = models.TextField()
    content = models.TextField()
    unread = models.BooleanField()
    read_later = models.BooleanField()    

    def __unicode__(self):
        return self.title

    def was_published_recently(self):
        return self.update_date >= timezone.now() - datetime.timedelta(days=1)

class Rating(models.Model):
    article = models.ForeignKey(Article) #need to enforce unique=true?
    rating = models.CharField(max_length=1)

    def __unicode__(self):
        return (self.rating)


class Label(models.Model):
    label = models.CharField(max_length=25)
    feeds = models.ManyToManyField(Feed)

    def __unicode__(self):
        return self.label

    class Meta:
        ordering = ('label',)
