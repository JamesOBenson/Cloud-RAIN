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
* Copy all files to the /var/www/
* Deploy cloud database.
* Update insert_record.php, cloudrain.py, and main.py with credentials

##Current workflow:
![flowchart.pdf](https://github.com/JamesOBenson/Cloud-RAIN/blob/master/docs/flowchart.pdf)
*Figure 1: Flowchart*

Deployment of additional software over infrastructure is being developed and will be added into the flowchart once completed.

##How is this playbook licensed?

It's licensed under the Apache License 2.0. The quick summary is:

> A license that allows you much freedom with the software, including an explicit right to a patent. State changes means that you have to include a notice in each file you modified. 

[Pull requests](https://github.com/JamesOBenson/Cloud-RAIN/pulls) and [Github issues](https://github.com/JamesOBenson/Cloud-RAIN/issues) are welcome!

-- James