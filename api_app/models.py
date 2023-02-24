from django.db import models 
import datetime


class Producto(models.Model):
    productoName = models.CharField(max_length=50)
    productoDescription = models.CharField(blank=True, max_length=200)
    productoPrice = models.DecimalField(max_digits=10, decimal_places=2)
    productoImage = models.ImageField(null=True, blank=True, upload_to='images/')
    amount = models.IntegerField(default=1)
    def __str__ (self):
        return self.productoName

class Person(models.Model):
    nombre = models.CharField('Nombre', max_length = 100)
    apellido = models.CharField('Apellido', max_length = 200)
    foto = models.ImageField(null=True, blank=True, upload_to='fotos/')
    class Meta:
        abstract = True

class Client(Person):
    email = models.EmailField(blank=True)
    phone = models.CharField(blank=True, null=True, max_length=20)

    def __str__(self):
        return f'{self.nombre}{self.apellido}'

# class Venta(models.Model) :
#     client = models.ForeignKey(Client,on_delete=models.CASCADE, verbose_name='Cliente ok', null=False)
#     fecha = models.DateTimeField(default=datetime.datetime.now)
#     description = models.TextField(blank = True)

#     def __str__ (self):
#          return f'{self.id}'


# class VentaProducto(models.Model):
#     venta = models.ForeignKey(Venta, on_delete=models.CASCADE, verbose_name='Nro Venta', null=False)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name='Producto', null=False)
#     cantidad = models.PositiveIntegerField(default=0)
#     preciounit = models.FloatField()
#     modified = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     state = models.BooleanField(default = True)
#     def __str__(self):
#         return f'{self.venta} to {self.producto}'

#     class Meta:
#         indexes = [
#                 models.Index(fields=['venta', 'producto',]),
#             ]


class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    products = models.ManyToManyField("Producto", through="DetailSale")
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def total_sale(self):
        detail_sale = self.detailsale_set.all()
        total = sum([detail.total_price() for detail in detail_sale])
        self.total = total
        self.save()

    def __str__ (self):
          return f'{self.products}, {self.total}'



class DetailSale(models.Model):
    product = models.ForeignKey("Producto", on_delete=models.CASCADE)
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    price_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.amount * self.price_unit

    class Meta:
        indexes = [
                models.Index(fields=['product']),
            ]

    def __str__ (self):
          return f'{self.amount} de {self.product}, por {self.total_price()} '