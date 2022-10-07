from django.db import models
from django.core.exceptions import ValidationError

FILE = "FILE"
FOLDER = "FOLDER"
ITEM_TYPE = [(FILE, "FILE"), (FOLDER, "FOLDER")]

def calc_size(item):
    children = Item.objects.filter(parent = item)
    size = 0
    if children.exists():
        size = children.aggregate(sum_size = models.Sum('size'))['sum_size']
    item.size = size
    item.save()

class Item(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, null = False)
    size = models.IntegerField(null = True, blank = True, default=0)
    type = models.CharField(max_length = 255, choices=ITEM_TYPE, editable=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                                    related_name='children', null = True, 
                                    blank = True)
    url = models.SlugField(max_length=255, null=True, blank = True)
    date = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name_plural = "Storage"
    
    def __str__(self) -> str:
        return f"{self.type}:{self.id}"
        
    def save(self, *args, **kwargs):
        if self.size is None:
            self.size = 0
        super(Item, self).save(*args, **kwargs)
        if self.parent:
            self.parent.date = self.date
            calc_size(self.parent)

    def delete(self, *args, **kwargs):
        parent = self.parent
        super(Item, self).delete(*args, **kwargs)
        if parent:
            calc_size(parent)
