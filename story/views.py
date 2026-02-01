from django.shortcuts import render,get_object_or_404,redirect
from .models import Story
from sellers.models import Shop
from django.contrib import messages
from datetime import timedelta
from collaborator.views import check_collab_and_jobs
from notifications.user_notification import notification_in_add_story
from django.utils import timezone



def add_story(request,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)


    if not request.user.is_authenticated:
        return redirect('acc:pro')
    

    if not check_collab_and_jobs(request, 'story_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    if request.method == 'POST':

        file = request.FILES.get('file')
        expiry_time = timezone.now() + timedelta(hours=24)  # 24 ساعت بعد از الان

        story=Story.objects.create(
            shop = shop,
            file = file,
            expiry_time = expiry_time
        )
        notification_in_add_story(story.pk,shop_id)

        messages.success(
            request,
            'استوری با موفقیت اضافه شد.'
        )
        return redirect('story:list_story',shop_id)
    
 
    
def remove_story(request,story_id,shop_id):
    story = get_object_or_404(Story,id = story_id,shop__id = shop_id)


    if not check_collab_and_jobs(request, 'story_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    story.delete()
    messages.success(
        request,
        'استوری با موفقیت حذف شد!'
    )
    return redirect('story:list_story',shop_id)

 

def list_story(request,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)
    story=Story.objects.filter(
        shop = shop,
        active = True
    )

    if not check_collab_and_jobs(request, 'story_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    status = request.GET.get('status')

    if status:
        if status == 'deactive':
            story=Story.objects.filter(
                shop = shop,
            )

        return render(
            request,
            'story/list_story.html',
            {
                'story':story.filter(active = False).distinct(),
                'count_story':story.filter(active = False).count(),
                'count_story_history':story.count()
            }
        )        


    return render(
        request,
        'story/list_story.html',
        {
            'story':story.filter(active = True),
            'count_story':story.filter(active = False).count(),
            'count_story_history':story.count()
        }
    )        



def default_disactive_history():
    expiry_time = timezone.now() - timedelta(hours=24)
    old_stories = Story.objects.filter(created_at__lt=expiry_time, active=True)
    old_stories.update(active=False)



def defult_remove_storys_after_3_month():
    three_months_ago = timezone.now() - timedelta(days=90)  # تقریباً ۳ ماه
    Story.objects.filter(created_at__lt=three_months_ago).delete()