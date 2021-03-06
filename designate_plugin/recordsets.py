# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 15:11:36 2016

@author: boucherv
"""

import re
from cloudify import ctx
from cloudify.decorators import operation
import designateclient.v2.client as dgclient
from keystoneauth1 import session as keystone_session


def get_client(dns_ip):
    session = keystone_session.Session()
    return dgclient.Client(endpoint_override="http://" + dns_ip + ":9001/v2", session=session)

def create_record(designate_client, zone_name, recordset_name, type_, new_record):
    recordsets = designate_client.recordsets.list(zone_name)
    recordset_exist = False
    for recordset in recordsets:
        if recordset['name'] == recordset_name and recordset['type'] == type_:
            recordset_exist = True
            records = recordset.get('records')
            recordset_id = recordset.get('id')

    if not recordset_exist:
        return designate_client.recordsets.create(zone_name, recordset_name, type_, [new_record])
    else:
        records.append(new_record)
        data = {
                'name': recordset_name,
                'type': type_,
                'records': records
        }
        return designate_client.recordsets.update(zone_name, recordset_id, data)

def delete_record(designate_client, zone_name, recordset_name, type_, new_record):
    recordsets = designate_client.recordsets.list(zone_name)
    records = []
    for recordset in recordsets:
        if recordset['name'] == recordset_name and recordset['type'] == type_:
            records = recordset.get('records')
            recordset_id = recordset.get('id')
    if len(records)<2:
        return designate_client.recordsets.delete(zone_name, recordset_id)
    else:
        records.remove(new_record)
        data = {
                'name': recordset_name,
                'type': type_,
                'records': records
        }
        return designate_client.recordsets.update(zone_name, recordset_id, data)

@operation
def add_node(domain, other_roles, other_records, record_ip="", **kwargs):
    zone_name = domain + "."
    instance_name = ctx.source.instance.id
    role = re.split(r'_',instance_name)[0]
    if record_ip == "":
        record_ip = ctx.source.instance.host_ip

    dns_ips = ctx.target.node.properties['dns_ips']
    designate_client = get_client(dns_ips[0])

    recordset_name = instance_name + "." + zone_name
    ctx.logger.debug(create_record(designate_client, zone_name, recordset_name, "A", record_ip))

    if role == "bono":
        recordset_name = zone_name
    elif role == "homestead":
        recordset_name = "hs." + zone_name
    else:
        recordset_name = role + "." + zone_name 
    ctx.logger.debug(create_record(designate_client, zone_name, recordset_name, "A", record_ip))

    for other_role in other_roles:
        recordset_name = other_role + "." + role + "." + zone_name
        ctx.logger.debug(create_record(designate_client, zone_name, recordset_name, "A", record_ip))

    for type_ in other_records:
        for record_name in other_records[type_]:
            recordset_name = record_name + "." + zone_name
            record_value = other_records[type_][record_name] + " " + instance_name + "." + zone_name
            ctx.logger.debug(create_record(designate_client, zone_name, recordset_name, type_, record_value))        

@operation
def del_node(domain, other_roles, other_records, record_ip="", **kwargs):
    zone_name = domain + "."
    instance_name = ctx.source.instance.id
    role = re.split(r'_',instance_name)[0]
    if record_ip == "":
        record_ip = ctx.source.instance.host_ip

    dns_ips = ctx.target.node.properties['dns_ips']
    designate_client = get_client(dns_ips[0])

    recordset_name = instance_name + "." + zone_name
    ctx.logger.debug(delete_record(designate_client, zone_name, recordset_name, "A", record_ip))

    if role == "bono":
        recordset_name = zone_name
    elif role == "homestead":
        recordset_name = "hs." + zone_name
    else:
        recordset_name = role + "." + zone_name 
    ctx.logger.debug(delete_record(designate_client, zone_name, recordset_name, "A", record_ip))

    for other_role in other_roles:
        recordset_name = other_role + "." + role + "." + zone_name
        ctx.logger.debug(delete_record(designate_client, zone_name, recordset_name, "A", record_ip))

    for type_ in other_records:
        for record_name in other_records[type_]:
            recordset_name = record_name + "." + zone_name
            record_value = other_records[type_][record_name] + " " + instance_name + "." + zone_name
            ctx.logger.debug(delete_record(designate_client, zone_name, recordset_name, type_, record_value))     