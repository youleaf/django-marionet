# -*- coding: utf-8 -*-
#

# django imports
from django.contrib.flatpages.models import FlatPage
from django.db import IntegrityError
from django.template import RequestContext
from django.test import TestCase

# reviews imports
from portlets.models import PortletAssignment
from portlets.models import PortletBlocking
from portlets.models import PortletRegistration
from portlets.models import Slot
import portlets.utils

from urllib import quote, unquote
from BeautifulSoup import BeautifulSoup

from marionet import log
from marionet.models import Marionet, PortletFilter
from marionet.models import WebClient
from marionet.tests.utils import RequestFactory
from test.settings import TEST_LOG_LEVEL
log.setlevel(TEST_LOG_LEVEL)

#import inspect
#import libxml2
#from copy import copy


class MarionetTestCase(TestCase):

    def setUp(self):
        self.junit_base = 'http://localhost:3000'
        self.junit_url = self.junit_base + '/caterpillar/test_bench/junit'
        #self.session_secret='xxx'

    #'''

    def test_create(self):
        """ Database object creation
        """
        portlet = Marionet.objects.create(
            url = self.junit_url,
            title = 'test portlet'
            )
        self.assert_(portlet)
        _portlet = Marionet.objects.get(id=portlet.id)
        self.assert_(_portlet)
        self.assertEqual(_portlet,portlet)
        self.assertEqual(_portlet.url, self.junit_url)
        self.assertEqual(_portlet.title, 'test portlet')
        self.assertEqual(_portlet.session.get('base'), self.junit_base)

    def test_render(self):
        """ Basic GET
        """
        url = self.junit_url + '/index'
        portlet = Marionet.objects.create(url=url,title='junit index')
        self.assert_(portlet)
        self.assertEqual(portlet.id,1)
        self.assertEqual(portlet.namespace(),'__portlet_1__')

        path = '/page/1'
        request = RequestFactory().get(path)
        ctx = RequestContext(request)
        ctx['path'] = request.path
        ctx['GET'] = request.GET

        out = portlet.render(ctx)
        self.assert_(out)
        self.assert_(portlet.context)
        self.assertEqual(portlet.context['path'], path)
        self.assertEqual(portlet.url, url)
        self.assertEqual(portlet.title, 'junit index')

        soup = BeautifulSoup(str(out))
        self.assert_(soup)
        # only body remains
        self.assertEqual(soup.find().name, 'div')
        self.assertEqual(soup.find('head'), None)
        # namespace is correct
        portlet_div = soup.find(id='%s_body' % portlet.namespace())
        self.assert_(portlet_div)

    #'''

    def __test_target1(self,portlet,href):
        portlet_url_query = '%s_href=%s' % (portlet.namespace(), 
            quote(href.encode('utf8'))
            )
        path = '/page/1' + '?' + portlet_url_query
        request = RequestFactory().get(path)
        ctx = RequestContext(request)
        ctx['path'] = request.path
        ctx['GET'] = request.GET

        out = portlet.render(ctx)
        self.assert_(out)
        self.assert_(portlet.context)
        self.assertEqual(portlet.context['path'],'/page/1')
        self.assertEqual(portlet.url, 
            self.junit_base+'/caterpillar/test_bench/junit/target1')

        soup = BeautifulSoup(str(out))
        self.assert_(soup)
        # only body remains
        self.assertEqual(soup.find().name, 'div')
        self.assertEqual(soup.find('head'), None)
        # namespace is correct
        portlet_div = soup.find(id='%s_body' % portlet.namespace())
        self.assert_(portlet_div)
        link = portlet_div.find('a')
        self.assert_(link)

    #'''

    def test_portlet_url(self):
        """ Portlet URL with absolute url
        """
        portlet = Marionet.objects.create(
            url=self.junit_url, title='junit index')
        href = self.junit_url + '/target1'
        self.__test_target1(portlet,href)

    def test_portlet_url__absolute_path(self):
        """ Portlet URL with absolute path
        """
        portlet = Marionet.objects.create(
            url=self.junit_url, title='junit index')
        href = '/caterpillar/test_bench/junit/target1'
        self.__test_target1(portlet,href)

    #'''

    def test_portlet_url__relative_path(self):
        """ Portlet URL with relative path
        """
        portlet = Marionet.objects.create(
            url=self.junit_url, title='junit index')
        portlet.session.set('base', self.junit_url) 
        href = 'target1'
        self.__test_target1(portlet,href)

        portlet = Marionet.objects.create(
            url=self.junit_url+'/', title='junit index')
        portlet.session.set('base', self.junit_url) 
        href = 'target1'
        self.__test_target1(portlet,href)


    ''' secret is not used yet
    def test_secret(self):
        """
        """
        mn_portlet = Marionet(session_secret=self.session_secret)
        self.assert_(mn_portlet)
        self.assertEqual(self.session_secret,mn_portlet.session_secret)
        out = mn_portlet.render() # calls filter + changes state!
        self.assertNotEqual(None,out)
    '''

