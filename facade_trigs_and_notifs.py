#!/usr/bin/env python

# Author:               Jane Curry
# Date                  Dec 13th 2013
# Description:          This doesn't provide pretty output as a notification may have several triggers
#                       You get all TRIGGERNAMEs, followed by all TRIGGERUUIDs, followed by all TRIGGERRULEs
#                       However, it provides the linkage between notifications and the triggers that drive them
#                       and shows the use of the trigger uuid from the notification being used to access the
#                       trigger rule
# Parameters:           File name for output
# Updates:              Feb 5th 2016
#                       Finally sorted out subscription linkages from triggers and notifications
#                       Note that some triggers appear to have subscribers that don't link back to a name
#                         through the subscriber_uuid and these pairings do NOT appear in the GUI
#

import Globals
import sys
import time
import pprint
from optparse import OptionParser
from Products.ZenUtils.ZenScriptBase import ZenScriptBase

parser = OptionParser()
parser.add_option("-f", "--file", dest="outputFile",
                          help="Please specify full path to output file", metavar="FILE")

(options, args) = parser.parse_args()

if not options.outputFile:
        parser.print_help()
        sys.exit()

of = open(options.outputFile, "w")
localtime = time.asctime( time.localtime(time.time()) )
of.write(localtime + "\n\n")

dmd = ZenScriptBase(connect=True, noopts=True).dmd

from Products.Zuul import getFacade
facade = getFacade('triggers')
 

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
trigs = [ trig1, trig2 ]
pprint.pprint(trigs)

#result = facade.importConfiguration(triggers=trigs, notifications=None)
#result = facade.importConfiguration(triggers=[trigs], notifications=None)
result = facade.importConfiguration(triggers=trigs, notifications=None)
print result

exit

of.write('NOTIFICATION LIST\n\n') 
of.write('=================\n')


# get sorted list of notifications
notiflist = []
for note in facade.getNotifications():
    notiflist.append(note)
newnotiflist = sorted(notiflist, key=lambda p: str(p.name))

#for note in facade.getNotifications():
for note in newnotiflist:
    # Notification is an object
    # Recipients is a list of user dictionaries where user is
    #   { label , manage, type, value (UUID), write }
    recip_string = ''
    substrigrule = ''
    try:
      if len(note.recipients) == 0:
        recip_string = 'No Users'
      else:
        for rp in note.recipients:
          recip_string = recip_string + rp['label'] + "    "
    except:
      pass

    try:
      # Subscriptions is a list of trigger dictionary links where
      #    subscriptions is { name, UUID }
      for s in note.subscriptions:
        # Use the note.subscriptions[s]['uuid'] field to access other data about the trigger
        trig = facade.getTrigger(s['uuid'])
        substrigrule = substrigrule + '    ' + trig['name'] + '  ' + str(trig['rule']['source']) + '\n'
    except:
      pass
    of.write('NOTIFICATION Name %s  Enabled %s Description %s Action %s Delay Secs %s Repeat %s  _guid %s  \n ' % (str(note.name), str(note.enabled), str(note.description), str(note.action), str(note.delay_seconds), str(note.repeat_seconds), str(note._object._guid) ))
    of.write('Recipients (users)  %s \n' % (recip_string))
    pprint.pprint(note.recipients, of)
    of.write('\n')
    of.write('Subscriptions (ie. Triggers) \n')
    pprint.pprint(note.subscriptions, of)
    of.write('\n')
    #of.write('Subscriber trigger rules %s \n \n ' % (substrigrule))
    of.write('Subscriber trigger rules \n ')
    of.write('%s \n\n ' % (substrigrule))

# get sorted list of triggers
triglist = []
for trig in facade.getTriggers():
    triglist.append(trig)
newtriglist = sorted(triglist, key=lambda p: str(p['name']))

of.write('\n\nTRIGGER LIST\n\n') 
of.write('============\n')
#for trig in facade.getTriggers():
for trig in newtriglist:
    # trig is a dictionary with
    #    { name, uuid, enabled, rule, subscriptions, users}
    #        where rule is a dictionary { api_version, source, type}
    #        and subscriptions is a list of dictionaries of notifications with
    #             { delay_seconds, repeat_seconds, send_initial_occurrence, subscriber_uuid, trigger_uuid, uuid }
    #                where trigger_uuid matches this trigger's uuid field and subscriber_uuid matches notification uuid
    #        and users is a list of dictionaries of users with
    #             { label , manage, type, value (UUID), write }

    if 'subscriptions' in trig:
      for n in trig['subscriptions']:
          # Note that there seem to be old? redundant? subscriptions that still exist
          # They are the ones whose subscriber_uuid does not match any notification object _guid
          try:  
              #of.write(' subscriber_uuid is %s and uuid is %s \n' % (n['subscriber_uuid'], n['uuid']))
              for n1 in facade.getNotifications():  
                  if n1._object._guid == n['subscriber_uuid']:
                      #of.write(' subscriber notification name is %s \n' % (n1._object.id))
                      n['notif_name'] = n1._object.id
          except:
            pass  

    of.write('TRIGGER name is %s  Enabled is %s UUID is %s  \n' % (trig['name'], trig['enabled'], trig['uuid']))
    if 'rule' in trig:
      of.write('Trigger rule is \n')
      pprint.pprint(trig['rule'], of)
    else:
      of.write(' No Trigger rules')
    of.write('\n')
    if 'subscriptions' in trig:
      of.write('Subscriptions (ie. Notifications) \n')
      for n in trig['subscriptions']:
        if 'notif_name' in n:
          pprint.pprint(n, of)
        else:
          of.write('No notification name for notification subscriber with subscriber_uuid %s \n' % (n['subscriber_uuid']))
    else:
      of.write('No Subscriptions (ie. Notifications) ')
    of.write('\n')
    if 'users' in trig:
      of.write('Users  \n')
      pprint.pprint(trig['users'], of)
    else:
      of.write(' No users')
    of.write('\n\n')
