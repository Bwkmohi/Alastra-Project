class ViewedProducts:
    def __init__(self, request):
        self.session = request.session
        self.session_key = 'viewed_products'
        if self.session_key not in self.session:
            self.session[self.session_key] = []
        self.history = self.session[self.session_key]

    def add(self, id):
        id = str(id)
        if id in self.history:
            self.history.remove(id)  # حذف آیتم تکراری
        self.history.insert(0, id)
        if len(self.history) > 15:
            self.history = self.history[:15]
        self.session[self.session_key] = self.history
        self.session.modified = True

    def get(self):
        return self.history
