def save_chat_view_id_in_session(request, id):

    session = request.session.get('suppoerterchat',{})
    request.session.pop('suppoerterchat',{})
    session.pop('suppoerterchat',{})

    if not session:

        session[str(id)]= {'id': id}
        request.session['suppoerterchat'] = session
        request.session.modified = True  

        return session
    
    else:
        return session
