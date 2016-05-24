# Cloud RAINS Deploy
This is a website that is designed to work in conjunction with OpenStack as a simplified hypervisor for an end user.  It is designed to be deployed on the controller node. Once deployed this software will deploy a new project, new user, keypair, and networking. Once the infrastructure is deployed, the software will be deployed.  Essentially this is akin to HEAT however, due to the nature of ansible, can be deployed upon any environment once the infrastructure is deployed. 

##Word of Caution. 
This project is still in development.  I will indicate what is functional below:
Website:
- Infrastructure is completely functional including:
 - Project & user creation
 - Keypair creation
 - Networking creation
 - Subnet creation
 - router creation
 - linkage between subnet, router, and world
 - spawning n instances
 

Cloudrain.py
- All functions work properly.
- Infrastructure deploys successfully and creates instances.


**Requirements:**
* Ansible

##How to deploy?
* In openstack, create a m1.xlarge instance and use [my cloud-init script](https://github.com/JamesOBenson/cloud-init) to deploy a new liberty devstack instance with neutron.
* git clone https://github.com/JamesOBenson/Cloud-RAIN.git
* ./deploy.sh deploy_all
* Update /var/www/Cloud-rain/cloudrain.py with openstack credentials (will be updated in the future) and externalGateway ID (Shown in Figure 1)
* Update /var/www/Cloud-rain/insert_record.php with mySQL database credentials (will be updated in the future)
* Update /var/www/Cloud-rain/main.py with mySQL database credentials and instance ID, instance name exactly as from openstack image name  
* Once deployed, the website is visible under:  http://\<devstack IP\>:81/Cloud-RAIN/

![alt tag](https://github.com/JamesOBenson/Cloud-RAIN/blob/master/docs/NetworkID.png)
*Figure 1: OpenStack Network Details indicating public network ID*

##Current workflow:
![flowchart.jpg](https://github.com/JamesOBenson/Cloud-RAIN/blob/master/docs/flowchart.jpg)
*Figure 2: Flowchart*

Deployment of additional software over infrastructure is being developed and will be added into the flowchart once completed.

##How is this playbook licensed?

It's licensed under the Apache License 2.0. The quick summary is:

> A license that allows you much freedom with the software, including an explicit right to a patent. State changes means that you have to include a notice in each file you modified. 

[Pull requests](https://github.com/JamesOBenson/Cloud-RAIN/pulls) and [Github issues](https://github.com/JamesOBenson/Cloud-RAIN/issues) are welcome!

-- James
