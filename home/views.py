from django.shortcuts import render
from projects.models import Category , Project
from django.db.models import Avg


def homepage(request):
    all_categories = Category.objects.all()
    
    # Fetch the latest 5 projects
    latest_projects = Project.objects.order_by('-created_at')[:5]
    featured_projects = Project.objects.order_by('-created_at')[:5]


    # Fetch the top 3 highest-rated projects
    highest_rated_projects = Project.objects.annotate(
        average_rating=Avg('ratings__rating')
    ).order_by('-average_rating')[:3]
    context = {
        'all_categories': all_categories,
        'latest_projects': latest_projects,
        'highest_rated_projects': highest_rated_projects,
         'featured_projects': featured_projects,

    }



    return render(request, 'home/homepage.html', context)
