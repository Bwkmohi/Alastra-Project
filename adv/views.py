from django.shortcuts import render,get_object_or_404,redirect
from .models import Project,ProjectFiles,Conactions,DemoVideos,DemoPhotoGraphs,PowerFullSeo,OgPowerFullSeo


def indexPage(request):
    return render(
        request,
        'adv/index.html',
        {
            'Project':Project.objects.all(),
            'alastra':Project.objects.first(),
            'ProjectFiles':ProjectFiles.objects.all(),
            'Conactions':Conactions.objects.all(),
            'DemoVideos':DemoVideos.objects.all(),
            'DemoPhotoGraphs':DemoPhotoGraphs.objects.all(),
            'power_full_seo':PowerFullSeo.objects.all(),
            'OgPowerFullSeo':OgPowerFullSeo.objects.all(),

        }
    )


def project_detail(request,id,slug):
    project = get_object_or_404(Project,id = id)

    return redirect(project.url_domain if project.url_domain else 'index')
