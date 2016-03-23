# Cloud RAINS Deploy
This is a website that is designed to work in conjunction with OpenStack as a simplified hypervisor for an end user.  It is designed to be deployed on the controller node. Once deployed this software will deploy a new project, new user, keypair, and networking. Once the infrastructure is deployed, the software will be deployed.  Essentially this is akin to HEAT however, due to the nature of ansible, can be deployed upon any environment once the infrastructure is deployed. 

##Word of Caution. 
This project is still in development.  I will indicate what is functional below:
Website:
- Project Creation
- User Creation
- Keypair Creation
- Network Creation
- Router Creation

Cloudrain.py
- All functions work properly except for:

* Connecting interfaces to network and router


**Requirements:**
* Ansible

##How to deploy?
* Copy all files to the /var/www/
* Update insert_record & main.py with credentials


##How is this playbook licensed?

It's licensed under the Apache License 2.0. The quick summary is:

> A license that allows you much freedom with the software, including an explicit right to a patent. âState changesâ means that you have to include a notice in each file you modified. 

[Pull requests](https://github.com/JamesOBenson/Cloud-RAIN/pulls) and [Github issues](https://github.com/JamesOBenson/Cloud-RAIN/issues) are welcome!

-- James