
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import json
import os
import logging

import ckan.logic
import ckan.model as model
from ckan.common import _, c
import comments

class DatasetCommentsPlugin(plugins.SingletonPlugin):
    controller = 'ckanext.dataset_comments.comments:CommentsController'
    
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    def before_map(self, map):
    	map.connect('del_comment', '/dataset/comments/delete', action='DeleteComment', controller='ckanext.dataset_comments.comments:CommentsController')
    	map.connect('new_comment', '/dataset/{id}/comments/new', action='NewComment', controller='ckanext.dataset_comments.comments:CommentsController')
        return map
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
    def get_helpers(self):
        return {'list': comments.ListComments,
                'username': comments.GetUsername }