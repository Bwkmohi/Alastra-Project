from django.shortcuts import render,redirect,get_object_or_404
from .models import CategoryBlog,BlogPost,BlogContents,AuthorModel
from django.contrib import messages
from accaunts.check_auth import check_user_authentication
from facelogin.views import check_secure_and_enter_password
from django.db.models import Q
from django.db.models import Sum


def list_blogs(request):
    blogs=BlogPost.objects.filter(active=True)

    return render(
        request,
        'blog/list_blogs.html',
        {
            'blog':blogs,
            'count':blogs.count(),
            'categorys':CategoryBlog.objects.all()
        }
    )


def filter_blogs(request,category_id):
    category = get_object_or_404(CategoryBlog,id = category_id)
    blogs=BlogPost.objects.filter(active=True,category=category)

    return render(
        request,
        'blog/list_blogs.html',
        {
            'blog':blogs,
            'count':blogs.count(),
            'categorys':CategoryBlog.objects.all()
        }
    )


def get_author(request):
    user_authentication = check_user_authentication(request)
    # national_ID_authentication=check_nation_cart(request)

    if not user_authentication:return None
    
    # if not national_ID_authentication:return None
    # national_ID_authentication=national_ID_authentication,
    try:
        return AuthorModel.objects.get(
            user_authentication = user_authentication,
        )
    except AuthorModel.DoesNotExist:
        return None
      

from django.utils.text import slugify
def blog_add(request):
    author = get_author(request)
    if not author:
        return redirect('acc:pro')

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        title = data.get('title')
        time_read = data.get('time_read') or 0
        image = files.get('image')
        short_des = data.get('short_des')
        category_id = data.get('category_id')
        status = data.get('status') #انتشار یا عدم انتشار

        blog = BlogPost.objects.create(
            title=title,
            author=author,
            time_red=time_read,
            image=image,
            short_des=short_des,
        )
        print(status)
        if category_id:
            try:
                blog.category = CategoryBlog.objects.get(id=category_id)
                blog.save()
            except CategoryBlog.DoesNotExist:
                pass

        if status == 'False':
            blog.active = False
            blog.save()
        elif status == 'True':
            blog.active = True
            blog.save()

        content_titles = data.getlist('content_titles[]')
        content_bodies = data.getlist('content_bodies[]')
        content_images = files.getlist('content_images[]') 

        for i in range(len(content_titles)):
            BlogContents.objects.create(
                post=blog,
                title=content_titles[i],
                content=content_bodies[i],
                image=content_images[i] if i < len(content_images) else None
            )

        if status == 'False':
            messages.success(
                request, 
                'بلاگ با موفقیت ذخیره شد. '
            )
        else:
            messages.success(
                request, 
                'بلاگ با موفقیت انتشار شد!'
            )
        return redirect('blog:author_dashbord')  
 
    return render(
        request, 
        'blog/blog_add.html',
        {
            'categorys': CategoryBlog.objects.all()
        }
    )

 
def blog_edit(request, blog_id):
    author = get_author(request)

    if not author:
        return redirect('acc:pro')

    blog = get_object_or_404(BlogPost, id=blog_id, author=author)
    contents = BlogContents.objects.filter(post=blog)

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        blog.title = data.get('title')
        blog.time_red = data.get('time_read') or 0
        blog.short_des = data.get('short_des')

        if files.get('image'):
            blog.image = files.get('image')

        category_id = data.get('category_id')
        if category_id:
            try:
                blog.category = CategoryBlog.objects.get(id=category_id)
            except CategoryBlog.DoesNotExist:
                blog.category = None

        blog.save()

        # -------- ویرایش BlogContents --------

        existing_ids = data.getlist('content_ids[]')  
        content_titles = data.getlist('content_titles[]')
        content_bodies = data.getlist('content_bodies[]')
        content_images = files.getlist('content_images[]')

        # پاک کردن محتواهایی که حذف شدن (اختیاری ولی حرفه‌ای‌تره)
        deleted_ids = set([str(obj.id) for obj in contents]) - set(existing_ids)
        BlogContents.objects.filter(id__in=deleted_ids).delete()

        # ذخیره محتواها (ویرایش + افزودن جدید)
        for i in range(len(content_titles)):
            content_id = existing_ids[i] if i < len(existing_ids) else None
            title = content_titles[i]
            body = content_bodies[i]
            image = content_images[i] if i < len(content_images) else None

            if content_id:  # محتوای قبلی - ویرایش
                try:
                    content_obj = BlogContents.objects.get(id=content_id, post=blog)
                    content_obj.title = title
                    content_obj.content = body
                    if image:
                        content_obj.image = image
                    content_obj.save()
                except BlogContents.DoesNotExist:
                    pass
            else:  # محتوای جدید
                BlogContents.objects.create(
                    post=blog,
                    title=title,
                    content=body,
                    image=image
                )

        messages.success(
            request, 
            'بلاگ با موفقیت ویرایش شد.'
        )
        return redirect('blog:author_dashbord')

    return render(
        request,
        'blog/blog_edit.html', 
        {
            'blog': blog,
            'contents': contents,
            'categorys': CategoryBlog.objects.all()
        }
    )


def blog_delete(request, blog_id):
    author = get_author(request)

    if not author:
        return redirect('acc:pro')

    blog = get_object_or_404(BlogPost, id=blog_id, author=author)
    blog.delete()

    messages.success(
        request, 
        'بلاگ با موفقیت حذف شد.'
    )
    return redirect('blog:author_dashbord')  
 
 
def blog_detail(request,id):

    blog = get_object_or_404(BlogPost,id = id)
    blog.views += 1
    blog.save()

    return render(
        request,
        'blog/blog_detail.html',
        {
            'category':CategoryBlog.objects.all()[:14],
            'article':blog,
            'popular_articles':BlogPost.objects.filter(active=True).order_by('-views')[:5],
            'contents':BlogContents.objects.filter(
                post=get_object_or_404(BlogPost,id=id)
            )
        }
    )
  

def blog_search(request):
    query = request.GET.get('q')
    results = []

    if query: 
        results = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(short_des__icontains=query) |
            Q(blogcontents__title__icontains=query) |
            Q(blogcontents__content__icontains=query)
        ).distinct()

    return render(
        request, 
        'blog/list_blogs.html', 
        {
            'results': results, 
            'query': query
        }
    )


def filter(request):
    author = get_author(request)

    if not author:
        return redirect('acc:pro')
    
    posts = BlogPost.objects.filter(author = author)

    query = request.GET.get('filter')
    if query:
        if query == 'draft':
            filtered_posts = posts.filter(
                active = False
            )

        elif query == 'published':
            filtered_posts = posts.filter(
                active = True
            )

        elif query == 'all':
            filtered_posts = posts.all()


        return render(
            request,
            'blog/dashbord.html',
            {
                'author':author,
                'blogs':filtered_posts.distinct()
            }
         )
    

def author_dashbord(request):
    author = get_author(request)
    if not author:
        return redirect('index')
    
    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    
    posts_count = BlogPost.objects.filter(author__id = author.pk).count()
    draft_posts_count = BlogPost.objects.filter(author__id = author.pk,active = False).count()
    published_posts_count = BlogPost.objects.filter(author__id = author.pk,active = True).count()
    total_views = BlogPost.objects.filter(author=author).aggregate(total=Sum('views'))['total']

    return render(
        request,
        'blog/dashbord.html',
        {
            'author':get_author(request),
            'blogs':BlogPost.objects.filter(author__id = author.pk),
            'latest_posts':BlogPost.objects.filter(author__id = author.pk).order_by('-created')[:4],
            'posts_count':posts_count,
            'total_views':total_views,
            'published_posts_count':published_posts_count,
            'top_blog_posts':BlogPost.objects.filter(author=author,active=True).order_by('-views')[:5],
            'numbers':[1,2,3,4,5],
            'draft_posts_count':draft_posts_count

        }
    )
    

def author_edit(request):
    author = get_author(request)
    if not author:
        return redirect('acc:pro')
    
    if request.method == 'POST':
        profile = request.FILES.get('profile')

        if profile:
            author.profile = profile

        author.full_name = request.POST.get('full_name')
        author.biographi = request.POST.get('bio')
        author.save()

        messages.success(
            request,
            'ویرایش اطلاعات موفقیت امیز'
        )
        return redirect('blog:author_dashbord')
     

def become_author(request):

    user_authentication = check_user_authentication(request)
    author = get_author(request)
    # national_ID_authentication=check_nation_cart(request)

    if not user_authentication:return redirect('acc:authentication')

    # if not national_ID_authentication:return redirect('acc:authentication_with_nation_cart_image')
    
    if author:return redirect('blog:author_dashbord')
    
    if request.method == 'POST':
        AuthorModel.objects.create(
            full_name = request.POST.get('name'),
            user_authentication = user_authentication,
            # national_ID_authentication = national_ID_authentication,
            profile = request.FILES.get('profile'),
            biographi = request.POST.get('biographi')
        )
        messages.success(
            request,
            'اطلاعات شما ثبت شد! اماده همکاری با سایت ما'
        )
        return redirect('blog:author_dashbord')
    else:
        return render(
            request,
            'blog/become_author.html'
        )