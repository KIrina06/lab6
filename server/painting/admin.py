from django.contrib import admin

from .models import *

admin.site.register(Requests)
admin.site.register(Expertises)
admin.site.register(ReqExps)
admin.site.register(CustomUser)