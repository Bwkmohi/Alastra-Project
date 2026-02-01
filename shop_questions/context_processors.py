from shop.models import Comments
from question_response.models import Question,Response
from sellers.context_processors import default_shop_context


def count_shop_comments(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_comments':Comments.objects.filter(product__shop__id = shop_id).count()
    }
    

def count_shop_questions(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_questions':Question.objects.filter(product__shop__id = shop_id).count()
    }


def count_shop_responses(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_responses':Response.objects.filter(reply_ques__product__shop__id = shop_id).count()
    }