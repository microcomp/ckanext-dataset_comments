import urllib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from ckan.common import _, c
import ckan.plugins.toolkit as toolkit

import comments_db
import logging
import ckan.logic
import __builtin__


class CommentsController(base.BaseController):
	pass
	def DeleteComment(self):
		'''TODO'''
		pass
	def NewComment(self):
		'''TODO'''
		pass
	def ListComments(self):
		'''TODO'''
		pass
