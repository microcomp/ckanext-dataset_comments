
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import json
import os
import logging

import ckan.logic
import ckan.model as model
from ckan.common import _, c

class DatasetCommentsPlugin(plugins.SingletonPlugin):
    controller = 'ckanext.dataset_comments.comments:CommentsController'
    
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
    def get_helpers(self):
        return {}