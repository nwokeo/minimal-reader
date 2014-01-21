from django.contrib import admin
from reader.models import Feed

admin.site.register(Feed)

#use fieldsets?

#to order fields:

#class FeedAdmin(admin.ModelAdmin):
#    fields = ['add_date', 'title']

#admin.site.register(Feed, FeedAdmin)
