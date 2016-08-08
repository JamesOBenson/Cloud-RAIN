#
# Copyright 2016 James Benson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#!/usr/bin/env pntIDython
# -*- coding: utf-8 -*-
""" This program will download the data from the mySQL DB and execute another
python script and ansible script.
To execute: python main.py
"""

import pymysql
import cloudrain

CNX = pymysql.connect(user='root',
                      password="password",
                      host='localhost',
                      unix_socket="/var/run/mysqld/mysqld.sock",
                      port=3307,
                      db='Cloud')

CURSOR = CNX.cursor()

query = ("SELECT * FROM BigTable ORDER BY TIMESTAMP DESC LIMIT 1")

CURSOR.execute(query)

for ProjectID in CURSOR:
#    print(ProjectID[0], ProjectID[1], ProjectID[2],ProjectID[3],
#          ProjectID[4], ProjectID[5], ProjectID[6], ProjectID[7],
#          ProjectID[8], ProjectID[9], ProjectID[10], ProjectID[11],
#          ProjectID[12], ProjectID[13], ProjectID[14], ProjectID[15],
#)
    #print ProjectID, cursor[ProjectID]
    nProject = ProjectID[0]
    TimeStamp = ProjectID[1]
    FirstName = ProjectID[2]
    LastName = ProjectID[3]
    Email = ProjectID[4]
    FlavorSize = ProjectID[5]
    nInstance = ProjectID[6]
    nIPs = ProjectID[7]
    Deployment = ProjectID[8]
    Platform = ProjectID[9]
    ProjectName = ProjectID[10]
    UserID = ProjectID[11]
    UserIDPass = ProjectID[12]
    Phone = ProjectID[13]

print("nProject:", nProject)
#Platform_ID = ""
#Platform_name = ""

Platform_name = cloudrain.imageName(Platform)
Platform_ID = cloudrain.imageID(Platform)

#if Platform == 1:  ## CentOS-6
#    Platform_ID = "e2af8797-739b-4777-8382-f43c24d8c261"
#    Platform_name = "CentOS 6"
#    print Platform_name
#elif Platform == 2:  ## UBUNTU 14.04.4 LTS
#    Platform_ID = "385546f5-57fd-4c39-b7d4-493b8007db5d"
#    Platform_name = "Ubuntu 14.04.4 LTS"
#    print Platform_name

#################
# CREATE TENANT
#################
TenantDescription = """%(FirstName)s %(LastName)s %(Email)s %(Phone)s"""%{
    'FirstName': FirstName,
    'LastName': LastName,
    'Email': Email,
    'Phone': Phone}
TenantName = UserID
cloudrain.CreateTenant(TenantName, TenantDescription)

#################
# CREATE USER
#################
#CreateUser(my_user_name,my_user_password,my_user_email,my_tenant_name)
UserDescription = """%(FirstName)s %(LastName)s %(Phone)s"""%{
    'FirstName': FirstName,
    'LastName': LastName,
    'Phone': Phone}

cloudrain.createUser(UserID, UserIDPass, Email, TenantName)

#################
# CREATE KEYPAIR
#################
cloudrain.createkeypair(UserID, UserIDPass, UserID)

####################
# CREATE NETWORKING
####################
TenantID = cloudrain.TenantID(TenantName)
net_name = ''.join([str(nProject), '-PrivateNetwork'])
if cloudrain.CheckNetworking(net_name, TenantID) is False:
    networkID = cloudrain.CreateNetwork(net_name, TenantID)
    subnetID = cloudrain.CreateSubNetwork(net_name, networkID, TenantID)
    routerID = cloudrain.CreateRouter(net_name, networkID, TenantID)
    cloudrain.CreateRouterGatewayLink(routerID)
    cloudrain.CreateSubnetRouterLink(routerID, subnetID)
else:
    networkID = cloudrain.CheckNetworkID(net_name)
    subnetID = cloudrain.CheckSubNetworkID(net_name)

####################
# CREATE INSTANCES
####################
FL = cloudrain.flavor(FlavorSize)
#IM = cloudrain.image(Platform_name)
instanceID = cloudrain.CreateInstances(nInstance, FL, Platform_ID, UserID,
                                       networkID, UserID, UserIDPass, UserID,
                                       nProject=nProject)


AnsibleScript = """
# 
# This document was created automatically for %(FirstName)s %(LastName)s
# on %(TIMESTAMP)s.
# 
---
- hosts: openstack-local
  remote_user: root
  become: yes
  gather_facts: no

  tasks:
#  - shell: export OS_USERNAME=admin
#  - shell: export OS_PASSWORD=password
  - shell: openstack project create --description 'Project 1' JamesBensonProject #--os-username=admin --os-auth-url=http://192.168.56.20:5000/v2.0

  - os_server:
      state: present
      auth:
          auth_url: http://192.168.56.20:5000/v2.0
          username: admin
          password: password
          project_name: %(ProjectName)s
      name: vm1
      image: %(Platform)s
      key_name: james
      timeout: 200
      flavor: %(FlavorSize)s
      nics:
        - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
        - net-name: another_network
      meta:
        hostname: test1
        group: test_group


""" % {'FirstName': FirstName, 'LastName': LastName, 'TIMESTAMP': TimeStamp,
       'ProjectName': ProjectName, 'Platform': Platform, 'FlavorSize':FlavorSize}

# Write Ansible script
FileName = repr(nProject)+'.yml'
text_file = open(FileName, "w")
text_file.write(AnsibleScript)
text_file.close()


CURSOR.close()
CNX.close()

#project.project()
#os.system("ansible-playbook "+FileName+" --ask-pass")

