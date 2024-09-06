from datetime import datetime

from django.shortcuts import render, redirect

from authentication.models import Register
from projects.forms import ProjectForm, ProjectImageForm
from projects.models import Project, Category, ProjectImage, Tag, Donation, Comment


# Create your views here.
def all_projects_view(request):
    """
    get all projects record from models
    """
    search_query = request.GET.get('search', '')

    # Filter the projects based on the search query
    if search_query:
        # Filter projects by title or details, you can add other fields as well
        all_projects = Project.objects.filter(
            title__icontains=search_query
        ) | Project.objects.filter(
            details__icontains=search_query
        )
    else:
        # If no search query, return all projects
        all_projects = Project.objects.all()
    # all_projects = Project.objects.all()
    categories = Category.objects.all()
    return render(request, 'projects/all_projects.html', {'all_projects': all_projects, 'all_categories': categories})


def category_projects(request, category_id):
    filter_category = Category.objects.filter(id=category_id).first()
    all_projects = Project.objects.filter(category=filter_category)
    categories = Category.objects.all()
    return render(request, 'projects/all_projects.html', {'all_projects': all_projects, 'all_categories': categories})


def project_details_view(request, project_id):
    project = Project.objects.get(id=project_id)
    project_images = ProjectImage.objects.filter(project_id=project.id)
    tags = project.tags.all()
    print(project.tags)
    counter = []
    counter_index = 1
    for image in project_images:
        counter.append(f'{counter_index}')
        counter_index += 1
    counter.pop()
    if 'user_id' in request.session:
        user = Register.objects.filter(id=request.session['user_id']).first()
    else:
        user = Register()


    return render(request, 'projects/project_details.html', {
        'project': project,
        'project_images': project_images,
        'counter': counter,
        'tags': tags,
        'user': user,
        'rating': project.average_rating() * 20,
        'rating_range': range(5, 0, -1),
        'comments': project.comments.all(),
        'all_categories': Category.objects.all()
    })

def donate(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
    else:
        user = Register.objects.get(id=request.session['user_id'])
        if request.method == "POST":
            if request.POST['donate']:
                donation = Donation.objects.create(
                    donated_at=datetime.now(),
                    project_id=project_id,
                    user_id=user.id,
                    amount=request.POST['donate'],
                )
                return redirect('project_details', project_id)
        return redirect("project_details.html", project_id)


def add_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, files=request.FILES)
        images_form = ProjectImageForm(request.POST, files=request.FILES)
        print(form.data)

        if form.is_valid():
            print(form.cleaned_data)
            project = form.save(commit=False)
            project.created_by = Register.objects.get(id=request.session["user_id"])
            project.pictures = form.cleaned_data['pictures']

            project.save()
            tag_ids = request.POST.getlist('tags')  # Assuming 'tags' is the name of the select field in the form
            tags = Tag.objects.filter(id__in=tag_ids)
            project.tags.set(tags)
            images = request.FILES.getlist('images')
            for image in images:
                ProjectImage.objects.create(project=project, image=image)

            return redirect('/')
    else:
        form = ProjectForm()
        images_form = ProjectImageForm()

    return render(request, 'projects/add_project.html', {'form': form, 'image_form': images_form})


def make_project_comment(request, project_id):
    if 'user_id' not in request.session:
        return redirect('login')
    else:
        user = Register.objects.get(id=request.session['user_id'])
        project = Project.objects.filter(id=project_id).first()
        Comment.objects.create(
            project=project,
            user=user,
            content=request.POST['content']
        )
        return redirect('project_details', project_id)


