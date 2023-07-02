from django.db import models

from flats.validators import validate_url_has_brackets, validate_url_page


class Category(models.Model): 
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=500)
    price = models.PositiveSmallIntegerField(validators=[validate_url_has_brackets, validate_url_page])
    search = models.BooleanField(default=True)

    @property
    def construct_url(self):
        return self.name.format(self.price) + '&page='
    
    @classmethod
    def search_all(cls):
        breakpoint()
        for url in cls.objects.filter(search=True).values_list(cls.construct_url, flat=True):
            breakpoint()
            
            


class Search(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='category_search')
    time = models.DateTimeField(auto_now_add=True)

    @property
    def found(self):
        return self.category_search.count()


class Flat(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    search = models.ForeignKey(Search, on_delete=models.PROTECT)
    
