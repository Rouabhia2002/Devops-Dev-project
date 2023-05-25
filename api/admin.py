from django.contrib import admin
from .models import client
from django.http import HttpResponseRedirect



@admin.register(client)
class ClientAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        # Redirect to the create_instance URL
        return HttpResponseRedirect('/create_instance/')