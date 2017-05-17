#!/usr/bin/env python
# Zenoss-4.x JSON API Example (python)
#
# To quickly explore, execute 'python -i trig_notif_import_export.py
#
# >>> z = getTrigsWithJSON()
# >>> trigs = z.export_trigs_and_notifs()
# etc.

import json
import urllib
import urllib2
from optparse import OptionParser
import pprint
#import Globals

#from zenoss.protocols.jsonformat import from_dict
#from zenoss.protocols.protobufs.zep_pb2 import EventSummary
#from Products.ZenEvents.events2.proxy import EventSummaryProxy


#ZENOSS_INSTANCE = 'http://ZENOSS-SERVER:8080'
# Change the next line(s) to suit your environment
#
#ZENOSS_INSTANCE = 'http://zen42.class.example.org:8080'
#ZENOSS_INSTANCE = 'https://zen42.class.example.org'
ZENOSS_INSTANCE = 'http://zenny1:8080'
ZENOSS_USERNAME = 'admin'
ZENOSS_PASSWORD = 'zenoss'

ROUTERS = { 'MessagingRouter': 'messaging',
            'EventsRouter': 'evconsole',
            'DeviceRouter': 'device',
            'TriggersRouter': 'triggers',
            'ZenPackRouter': 'zenpack' }

class getTrigsWithJSON():
    #def __init__(self, debug=False):
    def __init__(self, debug=True):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        # Use the HTTPCookieProcessor as urllib2 does not save cookies by default
        self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
        self.reqCount = 1

        # Contruct POST params and submit login.
        loginParams = urllib.urlencode(dict(
                        __ac_name = ZENOSS_USERNAME,
                        __ac_password = ZENOSS_PASSWORD,
                        submitted = 'true',
                        came_from = ZENOSS_INSTANCE + '/zport/dmd'))
        self.urlOpener.open(ZENOSS_INSTANCE + '/zport/acl_users/cookieAuthHelper/login',
                            loginParams)

    def _router_request(self, router, method, data=[]):
        if router not in ROUTERS:
            raise Exception('Router "' + router + '" not available.')

        # Contruct a standard URL request for API calls
        req = urllib2.Request(ZENOSS_INSTANCE + '/zport/dmd/' +
                              ROUTERS[router] + '_router')

        # NOTE: Content-type MUST be set to 'application/json' for these requests
        req.add_header('Content-type', 'application/json; charset=utf-8')

        # Convert the request parameters into JSON
        reqData = json.dumps([dict(
                    action=router,
                    method=method,
                    data=data,
                    type='rpc',
                    tid=self.reqCount)])

        # Increment the request count ('tid'). More important if sending multiple
        # calls in a single request
        self.reqCount += 1

        # Submit the request and convert the returned JSON to objects
        return json.loads(self.urlOpener.open(req, reqData).read())


    def export_trigs_and_notifs(self, trigs=None, notifs=None):
        """ Use TriggersRouter action (Class) and importConfiguration / exportConfiguration  methods found
        in JSON API docs on Zenoss website:
        """

        # NB. JC - don't think the notificationIds selection works in exportConfiguration method in facade
        # triggerIds selection DOES work

        data = dict(triggerIds=trigs, notificationIds=notifs)
        return self._router_request('TriggersRouter', 'exportConfiguration', [data] )['result']

    def import_trigs_and_notifs(self, trigs=None, notifs=None):
        """ Use TriggersRouter action (Class) and importConfiguration / exportConfiguration  methods found
        in JSON API docs on Zenoss website:
        """

        # NB trigs is a list of dicts
        trig1 = {   u'enabled': True,
    u'globalManage': False,
    u'globalRead': False,
    u'globalWrite': False,
    u'name': u'zen42_badnews_trigger',
    u'rule': {   u'api_version': 1,
                 u'source': u'(evt.severity == 5) and (dev.production_state == 1000) and (evt.status == 0) and (evt.event_class == "/Skills/Badnews")',
                 u'type': 1},
    u'subscriptions': [   {   u'delay_seconds': 0,
                              u'repeat_seconds': 0,
                              u'send_initial_occurrence': True,
                              u'subscriber_uuid': u'477b482e-1c01-43ad-af85-bebb52f372ee',
                              u'trigger_uuid': u'85487556-b4eb-41f4-882b-d08c14126912',
                              u'uuid': u'000c29d9-f87b-b9e4-11e3-1478c989823f'}],
    u'userManage': 1,
    u'userRead': True,
    u'userWrite': 1,
    u'users': [],
    u'uuid': u'85487556-b4eb-41f4-882b-d08c14126912'}

        trig2 = {   u'enabled': True,
    u'globalManage': False,
    u'globalRead': False,
    u'globalWrite': False,
    u'name': u'Rig_down_test',
    u'rule': {   u'api_version': 1,
                 u'source': u'(evt.event_class.startswith("/Rig")) and (evt.event_class != "/Rig/Error") and (evt.event_class != "/Rig/Server_Config_Change") and (evt.status == 0) and (evt.severity > 2)',
                 u'type': 1},
    u'subscriptions': [   {   u'delay_seconds': 0,
                              u'repeat_seconds': 0,
                              u'send_initial_occurrence': False,
                              u'subscriber_uuid': u'0445fb10-9f96-4f51-bc15-c25e30de3faa',
                              u'trigger_uuid': u'b04dd556-4ca4-47de-a2c7-a6d4c9e39096',
                              u'uuid': u'000c29d9-f87b-a649-11e3-2b8f723aca72'}],
    u'userManage': 1,
    u'userRead': True,
    u'userWrite': 1,
    u'users': [],
    u'uuid': u'b04dd556-4ca4-47de-a2c7-a6d4c9e39096'}


        trigs = [trig1, trig2]
        print 'Trigs is %s ' % (trigs)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(trigs)

        data = dict(triggers=trigs, notifications=notifs)
        print 'Pretty print data'
        pp.pprint(data)
        return self._router_request('TriggersRouter', 'importConfiguration', [data] )['result']

def printTriggers(out):
    pp = pprint.PrettyPrinter(indent=4)
    for t in out['triggers']:
        pp.pprint(t)

def printNotifications(out):
    pp = pprint.PrettyPrinter(indent=4)
    for n in out['notifications']:
        pp.pprint(n)


def main():
    usage = 'python %prog --triggers=triggers --notifs=notifs'

    parser = OptionParser(usage)
    parser.add_option("--triggers", dest='triggers', default=None,
                        help='triggers to import / export eg. ')
    parser.add_option("--notifs", dest='notifs', default=None,
                        help='notifications to import / export eg. ')

    (options, args) = parser.parse_args()

    # options is an object - we want the dictionary value of it
    # Some of the options need a little munging...

    option_dict = vars(options)
    if option_dict['triggers']:
        triggers = option_dict['triggers'].split(',')
    else: 
        triggers = option_dict['triggers']
    if option_dict['notifs']:
        notifs = option_dict['notifs'].split(',')
    else:
        notifs = option_dict['notifs']
    print 'triggers are %s and notifs are %s' % (triggers, notifs)

    trigs = getTrigsWithJSON()
    #allStuff =  trigs.export_trigs_and_notifs(triggers, notifs)
    impResult =  trigs.import_trigs_and_notifs(triggers, notifs)
    print 'Import result is %s ' % (impResult)
    print 'Message is %s ' % impResult['msg']
    print 'Success result is  is %s ' % impResult['success']

    """
    print 'Triggers \n'
    printTriggers(allStuff)
    print '\n \n End of Triggers \n \n'

    print 'Notifications \n'
    printNotifications(allStuff)
    
    print 'Message is %s ' % allStuff['msg']
    print 'Success result is  is %s ' % allStuff['success']
    """
if __name__ == "__main__":
    main()


