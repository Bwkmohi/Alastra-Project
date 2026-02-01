
class SearchHistory:
    def __init__(self,request):
        self.session = request.session
        search = self.session.get('search_h')
        if 'search_h' not in request.session:
            search = self.session['search_h'] = {}
        self.search =search

    def add(self,text):
        if text not in self.search:
            self.search[text] = {'text':text}
            self.session.modified = True
            return ''
        else:
            self.session.modified = True
            return ''

    def search_history(self):
        return self.search.values()
