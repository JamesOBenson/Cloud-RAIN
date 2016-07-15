"""
Python3 code.
"""
#import datetime
import time
import sys
import select
import paramiko
#import os
from subprocess import call
import pymysql
#import mysql.connector
from keystoneclient.v2_0 import client
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client as nova_client
#from openstackclient.network.v2 import network as osnet
#import novaclient as ns
from neutronclient.v2_0 import client as qclient
from scp import SCPClient
import shutil
import os

#################################################################
#  This is the network ID where the Floating IP's
#  originate from "admin_floating_net" or "public" in DevStack
#################################################################
externalGateway = '93ac6df3-f4e9-4299-ac5f-26a147b17c9f'

#####################
# openRC infomation
#####################
username = 'admin'
password = 'password'
tenant_name = 'admin'
auth_url = 'http://192.168.0.24:5000/v2.0'

######################################
# Keystone authentication information
######################################
keystone = client.Client(username=username,
                         password=password,
                         tenant_name=tenant_name,
                         auth_url=auth_url,
                         version=2)

######################################
# Nova authentication information
######################################
auth = v2.Password(username=username,
                   auth_url=auth_url,
                   password=password,
                   tenant_name=tenant_name)
auth_session = session.Session(auth=auth)
nt = nova_client.Client(2, session=auth_session)

######################################
# Neutron authentication information
######################################
neutron = qclient.Client(username=username,
                         password=password,
                         tenant_name=tenant_name,
                         auth_url=auth_url)

######################################
# mySQL authentication information
######################################
#mySQLhost     = os.environ["mySQL_host"]
#mySQLusername = os.environ["mySQL_user"]
#mySQLpassword = os.environ["mySQL_password"]
#mySQLport     = os.environ["mySQL_port"]
#mySQLdatabase = os.environ["mySQL_database"]
mySQLusername = "root"
mySQLpassword = "password"
mySQLhost = "localhost"
mySQLport = "3307"
mySQLdatabase = "Cloud"


def GetTenantID(TenantName):
    tenants = keystone.tenants.list()
    my_tenant = [x for x in tenants if x.name == TenantName][0]
    tenantID = my_tenant.id
    return tenantID

def GetUserID(UserName):
    users = keystone.users.list()
    my_user = [x for x in users if x.name == UserName][0]
    userID = my_user.id
    return userID

def createUser(UserName, UserPassword=None, UserEmail=None, my_tenant_name=None):
    TenantID = GetTenantID(my_tenant_name)
    try:
        keystone.users.create(name=UserName, password=UserPassword,
                              tenant_id=TenantID, email=UserEmail,
                             )
        print "User created"
    except:
        print "Info: The user already exists."

def flavor(arg1):
    item = arg1
    server = nt.flavors.find(ram=item)
    return server    #Returns: <Flavor: m1.small>

def image(item):
    image = nt.images.find(name=item)
    return image  #Returns: <Image: Ubuntu 14.04.4 LTS>

def imageID(item):
    image = nt.images.find(name=item).id
    return image  #Returns: 385546f5-57fd-4c39-b7d4-493b8007db5d

def imageName(item):
    image = nt.images.find(name=item).name
    return image  #Returns: Ubuntu 14.04.4 LTS

def findkeypair(item):
    try:
        keypair = nt.keypairs.find(name=item)
        return keypair
    except:
        print "Keypair does not exist."

##  Create a keypair and write a file using the username.
def createkeypair(user, password, tenant, authURL=auth_url):
    nt2 = Login(user, password, tenant, authURL)
    username = user
    try:
        newkey = nt2.keypairs.create(username)
        privKey = newkey.private_key
        f = open('/var/www/Cloud-RAIN/tmp/'+username+'.pem', 'w')
        f.write(privKey)
        f.close
        shutil.copy2('/var/www/Cloud-RAIN/tmp/'+username+'.pem', '/root/.ssh/'+username+'.pem')
#        os.chmod('/root/.ssh/'+username+'.pem', 0600)
        database(option="UpdateUsers", UserID=username, SSHKey=privKey)
# DEBUG: View new private key.
#      print(nt.keypairs.get(newkey))
        print "KeyPair generated for", username
    except:
        print "Info: Keypair already exists for", username


def importkeypair(arg1, arg2, user, password, tenant, authURL=auth_url):
    username = arg1
    imported_keypair = arg2
    nt2 = Login(user, password, tenant, authURL)
    newkey = nt2.keypairs.create(username, imported_keypair)
    print "Keypair imported."

def CreateTenant(tenantName, descrip=None, enabled=True):
    try:
        tenant = keystone.tenants.create(tenant_name=tenantName,
                                         description=descrip, enabled=True)
        print "Tenant Created."
    except Exception:
        print "Info: Tenant already exists."

## Change primary project for user (may remove access from previous project)
def ChangePrimaryProject(tenantName, Username):
    try:
        tenants = keystone.tenants.list()
        my_tenant = [x for x in tenants if x.name == tenantName][0]
        tenantID = my_tenant.id

        users = keystone.users.list()
        my_user = [x for x in users if x.name == Username][0]
        userID = my_user.id

        keystone.users.update_tenant(user=userID, tenant=tenantID)
        print "Primary project for user has been changed."
    except:
        print "WARNING: ChangePrimaryProject ERROR"

def Login(user, password, tenant, authURL=auth_url):
    auth = v2.Password(username=user,
                       auth_url=auth_url,
                       password=password,
                       tenant_name=tenant)

    auth_session = session.Session(auth=auth)
    nt2 = nova_client.Client(2, session=auth_session)
    return nt2

def CreateInstances(no_of_inst, myfl, myim, mykey, networkID, user, password,
                    tenant, authURL=auth_url, gateway=externalGateway, nProject="0"):
    no_of_inst = int(no_of_inst)
    cur_time = time.strftime('%y%m%d-%H%M%S', time.localtime())
    nicsInfo = [{'net-id':networkID}]

    userdatacmd="#!/bin/bash " \
                " \n echo 127.0.0.1 localhost $HOSTNAME >> /etc/hosts \n " \
                " apt-get -qqy update \n " \
                " apt-get -qqy install python-pip ansible git " \
                " \n echo StrictHostKeyChecking no >> /etc/ssh/ssh_config"

    for n in range(0, no_of_inst):
        name_vars = [str(n), '-', cur_time]
        server_name = ''.join(name_vars)
        nt2 = Login(user, password, tenant, authURL)
        try:
            instance = nt2.servers.create(server_name, flavor=myfl,
                                          image=myim, key_name=mykey, nics=nicsInfo,
                                          userdata=userdatacmd)
            print("Info: Server", server_name, " created.")
        except:
            print "ERROR: Cannot create server(s)"
        try:
            tenantID = GetTenantID(tenant)
            FloatingIPaddr = str(AllocateIP(tenantID, gateway))
            AssignFloatingIP(FloatingIPaddr, server_name, user, password, user)
            instanceID = instance.id
            database(option="Update", nProject=nProject, InstanceName=server_name,
                     InstanceID=instanceID, ExternalIP=FloatingIPaddr)
            write_host_file(nProject, FloatingIPaddr)

#           print("INFO: Instance ID: ",instanceID)
        except:
            print "ERROR: Floating IP address cannot be allocated."
    #    database(option="Update", nProject=nProject, InstanceName=server_name,
    #                 InstanceID=instanceID, ExternalIP=FloatingIPaddr)
#        write_host_file(nProject, FloatingIPaddr)

    try:
        UpdateSecurityGroups(user, password, tenant, proto='tcp', fport=22, tport=22)
    except:
        print "Security group has SSH access."

    with open(str(nProject)) as f:
        nhosts = f.read().splitlines()
    hosts = [str(host) for host in nhosts]
    SSH(hosts=hosts,user='ubuntu',pkeylocation='tmp/'+user+'.pem',key=None,files=None,commands=None)
    SSH(hosts=hosts,user='ubuntu',pkeylocation='tmp/'+user+'.pem',key=None,files='tmp/'+user+'.pem',commands=None)
    SETUPSSH="sudo cp %s.pem ~/.ssh/id_rsa; sudo chmod 600 ~/.ssh/id_rsa; chown whoami:whoami ~/.ssh/id_rsa" % (user)
    SSH(hosts=hosts,user='ubuntu',pkeylocation='tmp/'+user+'.pem',key=None,files=None,commands=SETUPSSH)
    SSH(hosts=hosts,user='ubuntu',pkeylocation='tmp/'+user+'.pem',key=None,files=str(nProject),commands=None)
    

def write_host_file(nproject, ip):
    ip = str(ip)+"\n"
    f = open(str(nproject), 'a')
    f.write(ip)
    f.close()
    a = "INFO: %s has been added to the file: %s" % (ip, nproject)
    print a

def TenantID(tenantName):
    tenants = keystone.tenants.list()
    try:
        my_tenant = [x for x in tenants if x.name == tenantName][0]
        tenantID = my_tenant.id
        print "Info: TenantID captured ..."
        return tenantID
    except:
        print "ERROR: Could not find tenant id."

def CheckNetworking(networkname, TenantID):
    try:
        my_networks = neutron.list_networks(name=networkname)['networks'][0]['id']
        print "Info: Network exists"
        return  True
    except IndexError:
        print "Info: Network does not exist... continuing."
        return False

def CreateNetwork(networkname, TenantID):
    try:
        network = {'name': networkname,
                   'tenant_id': TenantID,
                   'admin_state_up': True}
        netw = neutron.create_network({'network': network})
        net_dict = netw['network']
        print("Network created: ", network['name'])
        network_id = net_dict['id']
        return network_id
    except:
        print "WARNING: NETWORK CREATION FAILED. "

def CheckNetworkID(networkname):
    network_id = neutron.list_networks(name=networkname)['networks'][0]['id']
    print("Network ID is: ", network_id)
    return network_id

def CreateSubNetwork(networkname, network_id, TenantID):
    try:
        subnetname = ''.join(['sub-', networkname])
        subnetwork = {'name': subnetname,
                      'ip_version': '4',
                      'network_id': network_id,
                      'tenant_id': TenantID,
                      'cidr': '192.168.0.0/24'}
        subnetw = neutron.create_subnet({'subnet': subnetwork})
        subnetw_name = subnetwork['name']
        print("Subnet Created: ", subnetwork['name'])
        subnetid = neutron.list_subnets(name=subnetw_name)['subnets'][0]['id']
        return subnetid
    except:
        print "WARNING: SUBNETWORK CREATION FAILED. "

def CheckSubNetworkID(networkname):
    subnetname = ''.join(['sub-', networkname])
    subnetid = neutron.list_subnets(name=subnetname)['subnets'][0]['id']
    print("SubNetwork ID is: ", subnetid)
    return subnetid

def CreateRouter(networkname, network_id, TenantID):
    try:
        routername = ''.join([networkname, '-router'])
        router = {'admin_state_up': True,
                  'tenant_id': TenantID,
                  'name': routername}
        rout = neutron.create_router({'router': router})
        print("Router Created: ", router['name'])
        rout_dict = rout['router']
        routerid = neutron.list_routers(name=routername)["routers"][0]["id"]
        return routerid
    except:
        print "WARNING: ROUTER CREATION FAILED."

def CreateRouterGatewayLink(routerid, externGateway=externalGateway):
    try:
        externalgw = {'network_id': externalGateway}
        neutron.add_gateway_router(routerid, body=externalgw)
        print "Router-gateway link created ..."
    except:
        print "WARNING: ROUTER-GATEWAY LINK CREATION FAILED."

def CreateSubnetRouterLink(routerid, subnetid):
    try:
        router_id = {"subnet_id": routerid}
        subnet_id = {"subnet_id": subnetid}
        neutron.add_interface_router(routerid, body=subnet_id)
        print "Subnet-router link created ..."
    except:
        print "WARNING: SUBNET-ROUTER LINK CREATION FAILED."

def AllocateIP(tenantID, externalGateway=externalGateway):
    floaters = {'tenant_id': tenantID,
                'floating_network_id': externalGateway}
    ip = neutron.create_floatingip({'floatingip': floaters})
    IPaddr = ip.get('floatingip').get('floating_ip_address')
    IPaddrID = ip.get('floatingip').get('id')
    print("INFO: ", IPaddr, "has been allocated.")
    print IPaddrID
    return IPaddr

def AssignFloatingIP(IPaddr, servername, user, password, tenant):
    nt2 = Login(user, password, tenant)
    time.sleep(3)
    instance = nt2.servers.find(name=servername)
    instance.add_floating_ip(address=IPaddr)
    print "INFO: Floating IP assigned"

def UpdateSecurityGroups(user, password, tenant, proto=None, fport=None, tport=None):
    nt2 = Login(user, password, tenant)
    time.sleep(3)
    group = nt2.security_groups.find(name="default")
    nt2.security_group_rules.create(group.id, ip_protocol=proto,
                                 from_port=fport, to_port=tport)
    print "INFO: Security Groups updated"

def GetInstanceID(FloatingIPaddr, user, password, tenant):
    nt2 = Login(user, password, tenant)
    instances = nt2.servers.list()
    for instance in instances:
        #if instance.
        print("INFO: Instance ID: ", instance.id)

"""
host =  either a FQDN that is pingable or preferrably an IP
user =  username that should be used to log into the systems
pkeylocation = full working dir to the private key including pem file
key = the contents of the private key (currently a space holder and not used)
files = files that should be transfered (both full path or local dir work)
        Also, multiple files can be transferred using a comma  seperated list...
commands = command that should be executed.

Currently, this will attempt to ssh into the instance 60 times with 10 seconds
before each try, totalling 600 seconds or 10 minutes
"""
def SSH(hosts, user, pkeylocation=None, key=None, files=None, commands=None):
#    i = 1
    ntimestotry = 60
    sleeptime = 10
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for host in hosts:
#            i = 1
            host = str(host)
            for i in xrange(ntimestotry):
		    print "Trying to connect to %s (%i/%i)" % (host, i, ntimestotry)
		    try:
#			ssh = paramiko.SSHClient()
#			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(host, username=user,key_filename=pkeylocation)
			print "Connected to %s" % host
			break
		    except paramiko.AuthenticationException:
			print "Authentication failed when connecting to %s" % host
			sys.exit(1)
		    except:
			print "Could not SSH to %s, waiting for it to start" % host
			i += 1
			time.sleep(sleeptime)
		    # If we could not connect within time limit
		    if i == ntimestotry:
			print "Could not connect to %s. Giving up" % host
			sys.exit(1)
		#
		# SCP files over using paramiko protocol
		#
	    if files is not None:
		scp = SCPClient(ssh.get_transport())
		scp.put(files)
		#scp.get('test2.txt')
		scp.close
		print "File has been transferred."
	    if commands is not None:
			# Send the command (non-blocking)
		stdin, stdout, stderr = ssh.exec_command(commands)
			# Wait for the command to terminate
		while not stdout.channel.exit_status_ready():
		    # Only print data if there is data to read in the channel
		    if stdout.channel.recv_ready():
			rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
			if len(rl) > 0:
			    # Print data from stdout
			    print stdout.channel.recv(1024),
		print "Command done, closing SSH connection"
	    #
	    # Disconnect from the host
	    #
	    print "Closing SSH connection"
            ssh.close()

#SSH(hosts=['172.24.4.200','172.24.4.199','172.24.4.198'], user='ubuntu', pkeylocation='aaa112.pem', key=None, files=None, commands=None)

def ansible(hostsfile, deployment):
    print "Ansible"
    if deployment == "openmpi":
        deploy = "scripts/openMPI/OpenMPI.yml"
    cmds = "sudo apt-get update; sudo apt-get -y install ansible; ansible-playbook -i %s %s" % (hostsfile, deploy)
    print cmds
    return cmds

def database(option, nProject=None, InstanceName=None,
             InstanceID=None, ExternalIP=None, UserID=None, SSHKey=None):
    mySQLusername = "root"
    mySQLpassword = "password"
    mySQLhost = "localhost"
    mySQLport = "3307"
    mySQLdatabase = "Cloud"
    cnx = pymysql.connect(user=mySQLusername,
                          password=mySQLpassword,
                          host=mySQLhost,
                          unix_socket="/var/run/mysqld/mysqld.sock",
                          port=mySQLport,
                          db=mySQLdatabase)
    cursor = cnx.cursor()

    if option == "Update":
        add_instance_info = ("INSERT INTO Details  "
                             "(Project_Number, Instance_Name, Instance_ID, External_IP) "
                             "VALUES (%s, %s, %s, %s)")
        Instance_info = (nProject, InstanceName, InstanceID, ExternalIP)
        cursor.execute(add_instance_info, Instance_info)
        cnx.commit()
        cursor.close()
        cnx.close()
        print "INFO: Instance information inserted into the 'Details' table..."
    else:
        print "WARNING: Instance information not inserted into the 'Details' table..."

    if option == "UpdateUsers":
        add_user_info = ("INSERT INTO Users  "
                         "(UserID, SSHKey) "
                         "VALUES (%s, %s)")
        User_info = (UserID, SSHKey)
        cursor.execute(add_user_info, User_info)
        cnx.commit()
        cursor.close()
        cnx.close()
        print "INFO: User info was updated into the 'Users' table...."
