"""
Perform GET request on every external channel to check for availability
"""

import requests
import gevent

ENV = 'integration'

channels = ['cf_internal','adept_test','b2rbpo','bitcoinget','capestart','clickworker','clickworker_en','clixsense','colemandata','content_runner','csedit','crowdguru','crowdworks','ddd_dev','daproimafrica','digitalcampusconnect','datahouse','datapure','earnably','eup_slw','feca','elite','fusioncash','fusioncashsafe','getpaid','gifthunterclub','gifthulk','grabpoints','hiving','humanintheloop','indivillagetest','infosearchbpo','infosourcebulgaria','kaycaptions','keeprewarding','kinetic','kudzoy','listia','mena_it','memolink','neodev','opsify','pactera','points2shop','prizerebel','proximo','redial_bpo','smartone','superrewards','prodege','sykes','taqadam_cf','telefetask','timebucks','trueaccord','vivatic','wannads','zen3infosolutions','imerit_india','instagc','oworkers','test_rprocess','vcare','vcareindia','vcareusa','37degreedata','brian_channel','coinworker','crowdguru2','crowdreason_channel','crowdworks_dev','gptking','gengo_test','getpaidto','ligayembolo','netpoint','points4rewards','prizezombie','sharecashgpt','sparkgrid','stormx','tasks4dollars','tremorgames','imerit_solution','isoftstone','tom','training',]


def get_c(c):
    resp = requests.get(f'https://tasks.{ENV}.cf3.work/channels/{c}/tasks?uid=testing_channels')
    gevent.sleep(1)
    print(f"{c} -- {resp.status_code}")


def gather(cur_c):
    gevent.joinall([gevent.spawn(get_c, c) for c in cur_c])


concurrency = 5

if __name__ == '__main__':
    while channels:
        c_channels = []
        for i in range(concurrency):
            try:
                c_channels.append(channels.pop())
            except IndexError:
                break
        gather(c_channels)

