# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 15:11:36 2016

@author: boucherv
"""


from cloudify import ctx
from cloudify.decorators import operation
import designateclient.v2.client as dgclient
from keystoneauth1 import session as keystone_session


def get_client(dns_ip):
    session = keystone_session.Session()
    return dgclient.Client(endpoint_override="http://" + dns_ip + ":9001/v2", session=session)

def create_zone(designate_client, zone_name, email=None, ttl=None):
    zones = designate_client.zones.list()
    zone_exist = False
    for zone in zones:
        if zone['name'] == zone_name:
            zone_exist = True

    if not zone_exist:
        if not email:
            email = "admin@" + zone_name
        return designate_client.zones.create(zone_name, email=email[:-1], ttl=ttl)

def delete_zone(designate_client, zone_name):
   recordsets = designate_client.recordsets.list(zone_name)
 
   if len(recordsets) < 3:
       return designate_client.zones.delete(zone_name)

@operation
def add_zones(**kwargs):
    dns_ips = ctx.node.properties['dns_ips']
    designate_client = get_client(dns_ips[0])

   	domains = ctx.node.properties['domains']
   	for domain in domains:
   		zone_name = domain + "."
   		ctx.logger.debug(create_zone(designate_client, zone_name))

@operation
def del_zones(**kwargs):
    dns_ips = ctx.node.properties['dns_ips']
    designate_client = get_client(dns_ips[0])

   	domains = ctx.node.properties['domains']
   	for domain in domains:
   		zone_name = domain + "."
   		ctx.logger.debug(delete_zone(designate_client, zone_name))