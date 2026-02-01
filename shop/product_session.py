from .models import Products


def viewsProduct(request, id):
    session = request.session.get('view_prod', {})

    if str(id) not in session:
        product = Products.objects.get(id=id)
        product.views += 1
        product.save()
        session[str(id)] = {'id': id}
        request.session['view_prod'] = session
        request.session.modified = True  
        return 'session.values()'
    else:
        return None
    


def LikedProduct(request, id):
    if str(id) not in request.session.get('liked_product', {}):
        return True
    else:
        return False