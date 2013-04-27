from django.contrib import admin
from reader.models import Feed_base

admin.site.register(Feed_base)

#use fieldsets?

#to order fields:

#class FeedAdmin(admin.ModelAdmin):
#    fields = ['add_date', 'title']

#admin.site.register(Feed, FeedAdmin)
