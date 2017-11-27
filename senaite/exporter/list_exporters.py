# -*- coding: utf-8 -*-
#
# Copyright 2017-2017 SENAITE

import json

import plone
from senaite.exporter.utils import build_header
from senaite.exporter.utils import build_line
from senaite.exporter.utils import get_strings

from bika.lims.browser import BrowserView


class ListExporter(BrowserView):
    """
    Exports the current list (all the possible items to list or only the
    visible ones) to different formats, such as CSV or XML.
    """
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.view_instance = None
        self.items_list = None

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)

        submitted = self.request.form.get('export-list-submission', None)
        if not submitted:
            return None

        export_format = self.request.form.get('exporter-selection', None)
        if not export_format:
            return None

        view_class_id = json.loads(
            self.request.form.get('view-class-id', None),
            object_hook=get_strings)

        # Getting view module
        list_view_class = self.get_view_object(view_class_id)
        # Getting view instance
        self.view_instance = list_view_class(self.context, self.request)
        # Getting all items as list of lists
        self.items_list = self.export_to_list()
        import pdb;pdb.set_trace()

    def get_view_object(self, class_view_id):
        """
        Gets current class view dynamically.

        :param class_view_id: class view module name.
        :return: object class not instantiated
        """
        module_id, class_id = class_view_id.rsplit('.', 1)
        mod = __import__(module_id, fromlist=['class_id'])
        return getattr(mod, class_id)

    def export_to_list(self):
        """
        Export listed items to a python list of lists where the first list
        is the header and the later lists are each line.

        :return: A list of lists as the list of items
        """
        # Basic info that will be needed
        lines = []
        columns_map = self.view_instance.columns
        review_states = self.view_instance.review_states
        form_id = self.view_instance.form_id
        review_state = self.request.get(form_id + '_review_state', 'default')

        # Getting columns for review_state
        columns_order = []
        for dic in review_states:
            if dic.get('id', None) == review_state:
                columns_order = dic.get('columns', [])
                break
        visible_columns = self.view_instance.get_toggle_cols()

        # Getting items
        items = self.get_items()

        # building the list of lists
        for item in items:
            lines.append(build_line(item, columns_order, visible_columns))
        header = build_header(columns_map, columns_order, visible_columns)
        return [header] + lines

    def get_items(self):
        """
        This function uses a instance of the current view object to get the
        same listed items.

        :return: A list of lists with all the listed values.
        """
        # Filter bar data
        cookie_filter_bar = self.request.get('bika_listing_filter_bar', '')
        if cookie_filter_bar is not None and cookie_filter_bar != '':
            cookie_filter_bar = json.loads(cookie_filter_bar)

        cookie_data = {}
        for k, v in cookie_filter_bar:
            cookie_data[k] = v

        # Setting filters and processes before getting final items
        self.view_instance.save_filter_bar_values(cookie_data)
        self.view_instance.printwfenabled = \
            self.context.bika_setup.getPrintingWorkflowEnabled()
        self.view_instance._process_request()

        # Getting all items
        return self.view_instance.folderitems()