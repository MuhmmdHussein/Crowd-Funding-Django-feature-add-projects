from django.db import models
from django.contrib.auth.models import User
from authentication.models import Register
from core import settings


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=250)
    details = models.TextField()
    category = models.ForeignKey(
        Category,
        related_name='projects',
        on_delete=models.CASCADE,
    )
    pictures = models.ImageField(upload_to='project_pics/', blank=True, null=True)
    total_target = models.DecimalField(max_digits=10, decimal_places=2)
    tags = models.ManyToManyField(Tag, related_name='projects')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(Register, related_name='created_projects', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_donations(self):
        donations = self.donations.all()
        if donations.exists():
            return donations.aggregate(donation__sum=models.Sum('amount'))['donation__sum']
        return 0

    def get_donation_count(self):
        donations = self.donations.all()
        if donations.exists():
            return donations.aggregate(total_amount=models.Count('amount'))['total_amount']
        return 0

    def get_progress(self):
        return self.get_donations() / self.total_target * 100

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    def __str__(self):
        return self.title


    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    @property
    def similar_projects(self):
        return Project.objects.filter(category=self.category).exclude(id=self.id)[:4]

    def can_cancel(self):
        total_donations = self.donations.aggregate(total=models.Sum('amount'))['total'] or 0
        return total_donations < (0.25 * self.total_target)

    def cancel_project(self):
        if self.can_cancel():
            self.delete()


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='project_pics/')

    def __str__(self):
        return f"Image for {self.project.title}"


class Donation(models.Model):
    user = models.ForeignKey(Register, related_name='donations', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='donations', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} donated {self.amount} to {self.project.title}'


class Comment(models.Model):
    user = models.ForeignKey(Register, related_name='comments', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} commented on {self.project.title}'


class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, related_name='reports', on_delete=models.CASCADE)
    reported_by = models.ForeignKey(Register, related_name='comment_reports', on_delete=models.CASCADE)
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report on {self.comment} by {self.reported_by.username}'


class ProjectReport(models.Model):
    project = models.ForeignKey(Project, related_name='reports', on_delete=models.CASCADE)
    reported_by = models.ForeignKey(Register, related_name='project_reports', on_delete=models.CASCADE)
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report on {self.project.title} by {self.reported_by.username}'


class Rating(models.Model):
    project = models.ForeignKey(Project, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(Register, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} rated {self.project.title} {self.rating}/5'


"""
2 - Projects:
    - The user can create a project fund raise campaign which contains:
    - Title
    - Details
    - Category (from list of categories added previously by admins)
    - Multiple pictures
    - Total target (i.e 250000 EGP)
    - Multiple Tags
    - Set start/end time for the campaign
    - Users can view any project and donate to the total target
    - Users can add comments on the projects
    - Bonus: Comments can have replies
    - Users can report inappropriate projects
    - Users can report inappropriate comments
    - Users can rate the projects
    - Project creator can cancel the project if the donations are less than
    25% of the target
    - Project page should show the overall average rating of the project
    - Project page should show 4 other similar projects based on project

"""
