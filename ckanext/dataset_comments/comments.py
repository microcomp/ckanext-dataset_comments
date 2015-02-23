# coding=utf-8
import urllib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from ckan.common import _, c, g
#import ckan.lib.app_globals.Globals as g
import ckan.plugins.toolkit as toolkit

import time
import uuid
import comments_db
import logging
import ckan.logic
import __builtin__

_check_access = logic.check_access
def IsApp(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'related_id': id}
    related = model.Session.query(model.Related) \
                .filter(model.Related.id == id).first()
    if related != None:
        return True
    return False

def create_dataset_comments_table(context):
    if comments_db.dataset_comments_table is None:
        comments_db.init_db(context['model'])


@ckan.logic.side_effect_free
def new_comment(context, data_dict):
    create_dataset_comments_table(context)
    info = comments_db.DatasetComments()
    info.id = data_dict.get('id')
    info.user_id = data_dict.get('user_id')
    info.date = data_dict.get('date')
    info.dataset_id = data_dict.get('dataset_id')
    info.pub = data_dict.get('pub')
    info.comment_text = data_dict.get('comment_text')
    info.parent = data_dict.get('parent')
    info.save()
    session = context['session']
    session.add(info)
    session.commit()
    return {"status":"success"}

@ckan.logic.side_effect_free
def get_comments(context, data_dict = None):
    
    if comments_db.dataset_comments_table is None:
        comments_db.init_db(context['model'])
    res = comments_db.DatasetComments.get(**data_dict)
    return res
@ckan.logic.side_effect_free
def get_all_comments(context, data_dict = None):
    
    if comments_db.dataset_comments_table is None:
        comments_db.init_db(context['model'])
    res = comments_db.DatasetComments.getAll(**data_dict)
    return res

@ckan.logic.side_effect_free
def mod_comments(context, data_dict):
    create_dataset_comments_table(context)
    info = comments_db.DatasetComments.get(**data_dict)
    
    if info[0].pub == 'private':
    	info[0].pub = 'public'
    else:
    	info[0].pub = 'private'

    info[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"}
@ckan.logic.side_effect_free
def restore_comments(context, data_dict):
    create_dataset_comments_table(context)
    info = comments_db.DatasetComments.get(**data_dict)
    
    
    info[0].pub = 'public'

    info[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"}

@ckan.logic.side_effect_free
def report_comments(context, data_dict):
    create_dataset_comments_table(context)

    info = comments_db.DatasetComments.get(**data_dict)
    
    if info[0].pub == 'public':
        info[0].pub = 'reported'
    

    info[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"}

class CommentsController(base.BaseController):
    def ReportComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}
        try:
            logic.check_access('app_create', context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to report, please login first'))
            
        report_comments(context, data_dict)
        
        dataset_id = get_comments(context, data_dict)[0].dataset_id

        if IsApp(dataset_id):
            return h.redirect_to(controller='ckanext.apps_and_ideas.detail:DetailController', action='detail', id=dataset_id)
        else:
            return h.redirect_to(controller='package', action='read', id=dataset_id)


    def AdminRestoreComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}

        try:
            logic.check_access('app_editall', context)
            restore_comments(context, data_dict)
        except logic.NotAuthorized:
            logging.warning('NotAuthorized')
        
        page = base.request.params.get("page",'')
        type = base.request.params.get("type",'')
        sort = base.request.params.get("sort",'')
        username = base.request.params.get("username",'')
        search = base.request.params.get("search",'')

        return h.redirect_to(controller='ckanext.dataset_comments.comments:CommentsController', action='AdminList',  type=type, sort=sort, username= username, search= search )        
    def AdminDeleteComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}

        try:
            logic.check_access('app_editall', context)
            mod_comments(context, data_dict)
        except logic.NotAuthorized:
            logging.warning('NotAuthorized')
        
        page = base.request.params.get("page",'')
        type = base.request.params.get("type",'')
        sort = base.request.params.get("sort",'')
        username = base.request.params.get("username",'')
        search = base.request.params.get("search",'')

        return h.redirect_to(controller='ckanext.dataset_comments.comments:CommentsController', action='AdminList',  type=type, sort=sort, username= username, search= search )

    def AdminList(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj,
                   'for_view': True}

        try:
            logic.check_access('commets_admin', context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))

        all_comments = AdminCommentList()
        
        c.comments = []
        comment_type = base.request.params.get('type','')
        if comment_type == 'deleted':
            for i in all_comments:
                if i.pub == 'private':
                    c.comments.append(i)
        elif comment_type == 'public':
            for i in all_comments:
                if i.pub == 'public':
                    c.comments.append(i)
        elif comment_type == 'reported':
            for i in all_comments:
                if i.pub == 'reported':
                    c.comments.append(i)
        else:
            c.comments = all_comments

        sort = base.request.params.get('sort','')

        if sort == 'newest':
            c.comments = sorted(c.comments, key=lambda comments: comments.date, reverse=True)
        if sort == 'oldest':
            c.comments = sorted(c.comments, key=lambda comments: comments.date)
        username = base.request.params.get('username','')
        
        if len(username) > 0:
            user_id = model.Session.query(model.User) \
                .filter(model.User.name == username).first()
            if user_id:
                user_id = user_id.id
            cc = [x for x in c.comments if x.user_id == user_id]
            c.comments = cc
        c.search_user = username

        search_text = base.request.params.get('search','')
        
        if len(search_text) > 0:
            cc = [x for x in c.comments if search_text.lower() in x.comment_text.lower()]
            c.comments = cc
        c.search_text = search_text

        c.len = len(c.comments)
        page = base.request.params.get("page",'')
        if page == '':
            page = 1
        try:
            page = int(page)
        except ValueError, e:
            base.abort(400, ('"page" parameter must be an integer'))

        c.comment_page = []
        buffer = []
        for i in range(len(c.comments)):
            buffer.append(c.comments[i])
            if len(buffer) > 9:
                c.comment_page.append(buffer)
                buffer = []
        
        c.comment_page.append(buffer)

        c.comments = c.comment_page[page-1]
        c.page_num = c.len // 10 +1
        c.page = page
        

        c.pages = [x for x in range(c.page-3, c.page+3) if x > 0 and x <= c.page_num]
        

        return base.render("comments/admin.html")

    def NewComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        c.post_data = logic.clean_dict(df.unflatten(logic.tuplize_dict(logic.parse_params(base.request.params))))
        id = unicode(uuid.uuid4()) 
        date = time.strftime("%Y/%m/%d %H:%M:%S")  
        text = c.post_data['comment_text']
        dataset_id = c.post_data['dataset_id']

        g.comment_errors = []
        if c.userobj:
            pass
        else:
            base.redirect_to(controller='user', action='login')

        if c.userobj.id == '' or c.userobj.id == None or c.userobj == None:
            base.redirect_to(controller='user', action='login')
        text = " ".join(text.split(" "))
        text = text.replace('\r\n', '<br />')
        text = text.split('<br />')
        text2 = []
        for i in range(len(text)):
            if text[i] != '' and text[i] != ' ':
                text2.append(text[i])

        text = "<br />".join(text2)
        if len(text) < 5:
            base.redirect_to(controller='package', action='read', id=dataset_id, error='too_short')
        
        parent = base.request.params.get('parent_id','') 

        if parent == "":
            parent = None   

        data_dict = {'id': id, 'user_id':c.userobj.id, 
        			'date': date, 'pub': 'public', 
        			'dataset_id': dataset_id,
        			'comment_text': text, 'parent': parent}
        logging.warning(c.post_data)
        new_comment(context, data_dict)
        model.Session.commit()
        url = "dataset/"+dataset_id
        return h.redirect_to(controller='package', action='read', id=dataset_id)


    def NewAppComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        c.post_data = logic.clean_dict(df.unflatten(logic.tuplize_dict(logic.parse_params(base.request.params))))
        id = unicode(uuid.uuid4()) 
        date = time.strftime("%Y/%m/%d %H:%M:%S")  
        text = c.post_data['comment_text']
        dataset_id = c.post_data['app_id']

        g.comment_errors = []
        if c.userobj:
            pass
        else:
            base.redirect_to(controller='user', action='login')

        if c.userobj.id == '' or c.userobj.id == None or c.userobj == None:
            base.redirect_to(controller='user', action='login')
        
        text = " ".join(text.split(" "))
        text = text.replace('\r\n', '<br />')
        text = text.split('<br />')
        text2 = []
        for i in range(len(text)):
            if text[i] != '' and text[i] != ' ':
                text2.append(text[i])

        text = "<br />".join(text2)

        if len(text) < 5:
            base.redirect_to(controller='ckanext.apps_and_ideas.detail:DetailController', action='detail', id=dataset_id, error='too_short')
        parent = base.request.params.get('parent_id','') 

        if parent == "":
            parent = None   

        data_dict = {'id': id, 'user_id':c.userobj.id, 
                    'date': date, 'pub': 'public', 
                    'dataset_id': dataset_id,
                    'comment_text': text, 'parent': parent}
        
        logging.warning(c.post_data)
        new_comment(context, data_dict)
        model.Session.commit()

        return h.redirect_to(controller='ckanext.apps_and_ideas.detail:DetailController', action='detail', id=dataset_id)

    def DeleteComment(self):
    	context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}

        try:
            logic.check_access('app_editall', context)
            mod_comments(context, data_dict)
        except logic.NotAuthorized:
            logging.warning('NotAuthorized')
        
        dataset_id = get_comments(context, data_dict)[0].dataset_id
        return h.redirect_to(controller='package', action='read', id=dataset_id)

    def DeleteAppComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}

        try:
            logic.check_access('app_editall', context)
            mod_comments(context, data_dict)
        except logic.NotAuthorized:
            logging.warning('NotAuthorized')
        
        dataset_id = get_comments(context, data_dict)[0].dataset_id
        return h.redirect_to(controller='ckanext.apps_and_ideas.detail:DetailController', action='detail', id=dataset_id)



def ListComments(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'dataset_id':  id, 'parent': ''}
    comments = get_comments(context, data_dict)

    

    comments = sorted(comments, key=lambda comments: comments.date)
    comments2 = []
    comments3 = comments[:]
    for i in comments3:
        if i.pub == 'public' or i.pub == 'reported':
            comments2.append(i)
        else:
            try:
                logic.check_access('app_editall', context)
                comments2.append(i)
            except logic.NotAuthorized:
                i.comment_text = _('Komentár obsahoval nevhodný obsah a bol odstránený správcom.'.decode('utf-8')) #_('inappropriate content')
                comments2.append(i)
    return comments2


def GetUsername(user_id):
    username = model.Session.query(model.User) \
                .filter(model.User.id == user_id).first()
    return username.name
def ListChildren(id, comment_id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'dataset_id':  id, 'parent': comment_id}
    comments = get_comments(context, data_dict)
    comments = sorted(comments, key=lambda comments: comments.date)
    comments2 = []
    comments3 = comments[:]
    for i in comments3:
        if i.pub == 'public' or i.pub == 'reported':
            comments2.append(i)
        else:
            try:
                logic.check_access('app_editall', context)
                comments2.append(i)
            except logic.NotAuthorized:
                i.comment_text = _('Komentár obsahoval nevhodný obsah a bol odstránený správcom.'.decode('utf-8')) #_('inappropriate content')
                comments2.append(i)
    return comments2
def Editor():
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    try:
        logic.check_access('app_editall', context)
        return True
    except logic.NotAuthorized:
        return False

def AdminCommentList():
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'dataset_id':  id, 'parent': ''}

    comments = get_all_comments(context, {'id':'*'})
    comments = sorted(comments, key=lambda comments: comments.date)

    return comments


