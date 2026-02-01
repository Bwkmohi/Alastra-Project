
  
class Cart_Session:
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get('cart')
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}
        self.cart =cart


    def add(self,id):
        if id not in self.cart:
            self.cart[id] = {'id':id}
        else:
            message = True
        self.session.modified = True

    def clear(self):
        self.session.pop('cart', None)
        self.session.modified = True