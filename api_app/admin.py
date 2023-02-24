from django.contrib import admin
# Register your models here.
from .models import Producto, Client, Sale, DetailSale

admin.site.register(Producto)
admin.site.register(Client)
admin.site.register(Sale)
admin.site.register(DetailSale)