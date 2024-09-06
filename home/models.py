from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    end_time = models.DateTimeField()
    total_target = models.DecimalField(max_digits=10, decimal_places=2)
    donations = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='projects/', blank=True, null=True) 

    def __str__(self):
        return self.title
