# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 15:11:36 2016

@author: boucherv
"""


from cloudify import ctx
import designateclient.v2.client as dgclient
from keystoneauth1 import session as keystone_session


def get_client(dns_ip):
    session = keystone_session.Session()
    return dgclient.Client(endpoint_override="http://" + dns_ip + ":9001/v2", session=session)

def init():
	pass