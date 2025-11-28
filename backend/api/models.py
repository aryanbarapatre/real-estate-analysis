from django.db import models

# Create your models here.
# For this project, we'll work directly with Excel data, so models are optional
# If you want to store data in database in the future, you can create models here

# Example model structure (commented out - not used in current implementation):
# class RealEstateData(models.Model):
#     year = models.IntegerField()
#     area = models.CharField(max_length=100)
#     price = models.FloatField()
#     demand = models.FloatField()
#     size = models.FloatField()
#     
#     class Meta:
#         db_table = 'real_estate_data'
#         unique_together = ['year', 'area']
#     
#     def __str__(self):
#         return f"{self.area} - {self.year}"

