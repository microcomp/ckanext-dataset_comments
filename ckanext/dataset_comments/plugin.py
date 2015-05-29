
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import json
import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

        map.connect('del_app_comment', '/apps/comments/delete', action='DeleteAppComment', controller='ckanext.dataset_comments.comments:CommentsController')
        map.connect('new_app_comment', '/apps/{app_id}/comments/new', action='NewAppComment', controller='ckanext.dataset_comments.comments:CommentsController')
        map.connect('report_app_comment', '/comments/report', action='ReportComment', controller='ckanext.dataset_comments.comments:CommentsController')

        map.connect('admin_delete', '/comments/delete', action='AdminDeleteComment', controller='ckanext.dataset_comments.comments:CommentsController')
        map.connect('admin_restore', '/comments/restore', action='AdminRestoreComment', controller='ckanext.dataset_comments.comments:CommentsController')

        map.connect('moderator_v', '/admin/comments', action='AdminList', controller='ckanext.dataset_comments.comments:CommentsController')
        map.connect('moderator_page', '/admin', action='AdminPage', controller='ckanext.dataset_comments.comments:CommentsController')

        map.connect('comment_new_api', '/custom_api/comment/new', action='NewCommentApi', controller='ckanext.dataset_comments.comments:CommentsController')
        map.connect('comment_del_api', '/custom_api/comment/del', action='DelCommentApi', controller='ckanext.dataset_comments.comments:CommentsController')
        
        return map
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
    def get_helpers(self):
        return {'list': comments.ListComments,
                'username': comments.GetUsername,
                'list_children': comments.ListChildren,
                'editor': comments.Editor,
                'is_app': comments.IsApp,
                'is_dataset': comments.IsDataset,
                'app_n': comments.AppName,
                'dataset_n': comments.DatasetName,
                'resource_n': comments.resource_name,
                'resource_url_helper': comments.resource_url_helper,
                'admin_or_moderator': comments.admin_or_moderator, 
                'comment_admin': comments.comment_admin,
                'tag_admin': comments.tag_admin,
                'report_admin': comments.report_admin,
                'storage_admin': comments.storage_admin,
                'sla_management' : comments.auth_sla_management,
                'md5_create': comments.md5_create }
                
