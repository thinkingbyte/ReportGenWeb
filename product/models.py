from django.db import models

# Create your models here.
class Product(models.Model):
    # 产品类型
    type_name = models.CharField(max_length=15)
    # 产品特性
    product_character = models.CharField(max_length=200)
    # 产品引言
    product_preface = models.TextField()
    # 产品结束语
    product_closing = models.TextField()
