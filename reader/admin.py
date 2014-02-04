from django.contrib import admin
from reader.models import Feed

admin.site.register(Feed)

#class FeedAdmin(admin.ModelAdmin):
#    fields = ['add_date', 'title']
