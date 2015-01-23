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
def get_comments(context, data_dict):
    
    if comments_db.dataset_comments_table is None:
        comments_db.init_db(context['model'])
    res = comments_db.DatasetComments.get(**data_dict)
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
class CommentsController(base.BaseController):


    def NewComment(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        c.post_data = logic.clean_dict(df.unflatten(logic.tuplize_dict(logic.parse_params(base.request.params))))
        id = unicode(uuid.uuid4()) 
        date = time.strftime("%Y/%m/%d %H:%m:%S")  
        text = c.post_data['comment_text']
        dataset_id = c.post_data['dataset_id']

        g.comment_errors = []

        if c.userobj.id == '' or c.userobj.id == None:
            base.redirect_to(controller='user', action='login')
        text = " ".join(text.split())

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
    def DeleteComment(self):
    	context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': base.request.params.get('id', '')}
        
        mod_comments(context, data_dict)
        dataset_id = get_comments(context, data_dict)[0].dataset_id
        return h.redirect_to(controller='package', action='read', id=dataset_id)


def ListComments(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'dataset_id':  id, 'parent': ''}
    comments = get_comments(context, data_dict)
    
    c.hasprivileg = 'True'

    
    '''
    context2 = {'user' : c.user}
    try:
        logic.check_access('app_create', context2)
    except logic.NotAuthorized:
   		c.hasprivileg = 'False'
	'''
    comments = sorted(comments, key=lambda comments: comments.date)
    comments2 = []
    for i in comments:
        if i.pub == 'public':
            comments2.append(i)

    if c.hasprivileg:
        return comments
    else:
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
    return comments
'''
TODO:
-reply
-list replied comments
-privilegs to edit/show hidden comments
-hide all 2nd lvl comments if the parent is hidden

'''
