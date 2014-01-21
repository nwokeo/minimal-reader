from django.forms import ModelForm
from reader.models import Article, Feed, Rating, Label
#import reader.models

class FeedForm(ModelForm):
    class Meta:
        model = Feed

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ('unread', 'read_later')


class RatingForm(ModelForm):
    class Meta:
        model = Rating

class LabelForm(ModelForm):
    class Meta:
        model = Label
        fields = ('id',)

