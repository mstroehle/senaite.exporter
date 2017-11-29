# -*- coding: utf-8 -*-
#
# Copyright 2017-2017 SENAITE

import json

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from bika.lims.interfaces import ITopLeftListingHook


class ListsExporter(object):
    """
    Creates a view with the available list exporters. It gives values to the
    form elements that will be sued by the exporter.
    """
    implements(ITopLeftListingHook)
    template = ViewPageTemplateFile("templates/lists_exporters.pt")

    def __init__(self, listing_table):
        self.request = None
        self.pagesize = None
        self.listing_table = listing_table
        self.bika_listing = listing_table.bika_listing
        self.context = listing_table.context

    def __call__(self, request):
        self.request = request
        self.pagesize = self.bika_listing.pagesize

        return self.template()

    def get_pagesize(self):
        """
        Retrieves the current page size used to display the list.

        :return: json string with page size
        """
        return json.dumps(self.pagesize)

    def get_view_name(self):
        """
        Returns the vew name registered in ZCML
        :return: The browser view name registered in ZCML
        """
        return self.bika_listing.__name__
