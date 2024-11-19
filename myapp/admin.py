from django.contrib import admin
from .models import Sequence, Metadata, CHalf

admin.site.register(Sequence)
admin.site.register(Metadata)
admin.site.register(CHalf)
