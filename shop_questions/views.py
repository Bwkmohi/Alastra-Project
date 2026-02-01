from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Comments
from django.contrib import messages
from question_response.models import Response,Question
from facelogin.views import check_secure_and_enter_password
from collaborator.views import check_collabrator,check_collab_and_jobs
from sellers.check import check_is_seller
from collaborator.views import create_activity
from notifications.user_notification import your_question_has_been_responsed



def list_questions(request,shop_id):

    filter_questions=request.GET.get('filter')
    search=request.GET.get('search')


    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    

    if check_collab_and_jobs(request,'see_messages',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    if filter_questions:

        if filter_questions == 'answered':
            questions=Question.objects.filter(
                product__shop__id = shop_id,
                responsed = True
            )        

        elif filter_questions == 'unanswered':
            questions=Question.objects.filter(
                product__shop__id = shop_id,
                responsed = False
            )  
            
        return render(
            request,
            'shop_questions/list_questions.html',
            {
                'text':'',
                'question':questions.distinct(),
                'len':questions.count(),
                'shop_id':shop_id,               
            }
    )                  


    if search:
        questions=Question.objects.filter(text__icontains=search)    
        return render(
            request,
            'shop_questions/list_questions.html',
            {
                'text':'',
                'question':questions,
                'len':questions.count(),
                'shop_id':shop_id,               
            }
        )

    
    questions=Question.objects.filter(
        product__shop__id = shop_id,
        responsed = False
    )


    return render(
        request,
        'shop_questions/list_questions.html',
        {
            'text':'',
            'question':questions,
            'len':questions.count(),
            'shop_id':shop_id,
        }
    )



def list_comments(request,shop_id):

    comments=Comments.objects.filter(
        product__shop__id = shop_id,
    )


    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    

    if check_collab_and_jobs(request,'see_messages',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    return render(
        request,
        'shop_questions/list_comments.html',
        {
            'comments':comments,
            'len':comments.count(),
            'shop_id':shop_id,
        }
    )


import bleach
def reponse_to_question(request, shop_id, question_id):
    question = get_object_or_404(Question,id=question_id,product__shop__id=shop_id)

    if not check_collab_and_jobs(request, 'reponse_questions', shop_id):
        messages.warning(request,'شما به این بخش دسترسی ندارید!')
        return redirect('acc:pro')


    if request.method == 'POST':

        response = Response.objects.create(
            response_text=bleach.clean(request.POST.get('response_text')),
            seller=check_is_seller(request),
            reply_ques=question,                                        
        )

        your_question_has_been_responsed(response.reply_ques.pk,response.pk)    
        question.responsed = True
        question.save()

        if check_collabrator(request, shop_id):
            create_activity(request, 'پاسخ به سوال کاربر', response.pk, 'ADD', shop_id)
        
        messages.success(
            request,
            'پاسخ ثبت شد'
        )
        return redirect('s_ques:list_questions', shop_id)



def list_responses(request,shop_id):

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    

    if check_collab_and_jobs(request,'see_messages',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    return render(
        request,
        'shop_questions/list_responses.html',
        {
            'responses':Response.objects.filter(reply_ques__product__shop__id = shop_id).order_by('-time'),
            'shop_id':shop_id,
        }
    )



def remove_response(request,shop_id,response_id):
    response=get_object_or_404(Response,id=response_id,reply_ques__product__shop__id = shop_id)


    if check_collab_and_jobs(request,'reponse_questions',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    
    if not check_collabrator(request,shop_id):pass
    else:create_activity(request,'حذف پاسخ کاربر',response.pk,'REMOVE',shop_id)


    response.delete()
    messages.success(
        request,
        'پاسخ با موفقیت حذف شد!'
    )
    return redirect('s_ques:list_responses',shop_id)



def edit_reseponse(request,shop_id,reseponse_id):
    response=get_object_or_404(Response,id = reseponse_id,seller=check_is_seller(request))  


    if check_collab_and_jobs(request,'reponse_questions',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
 
    if request.method == 'POST':

        response.response_text = bleach.clean(request.POST.get('response_text',''))
        response.save()

        if not check_collabrator(request,shop_id):pass
        else:
            create_activity(request,'ویرایش پاسخ به کاربر',response.pk,'EDIT',shop_id)

        messages.success(
            request,
            'پیام اپدیت شد!'
        )
        return redirect('s_ques:list_responses',shop_id)



def remove_comment(request,shop_id,comment_id):
    
    if check_collab_and_jobs(request,'reponse_questions',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    comment=get_object_or_404(Comments,product__shop__id = shop_id,id =comment_id)


    if not check_collabrator(request,shop_id):pass
    else:
        create_activity(request,'حذف کامنت کاربر',comment.pk,'REMOVE',shop_id)


    comment.delete()
    messages.success(
        request,
        'کامنت یا موفقیت حذف شد!'
    )
    return redirect('s_ques:list_comments',shop_id)