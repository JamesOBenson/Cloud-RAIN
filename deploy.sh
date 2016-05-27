function deployDB () {
    echo ""
    echo "Adding the Cloud Database and BigTable and LookUp tables."
    echo ""
    {
    mysql -u root -p << EOF
    DROP DATABASE Cloud;
EOF
    } || {
    echo "Cloud Database does not exist, continuing..."
    }
    mysql -u root -p << EOF   
    CREATE DATABASE Cloud;
    USE Cloud;
    CREATE TABLE BigTable(
      ProjectID int(11) NOT NULL AUTO_INCREMENT,
      TIMESTAMP timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FirstName varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      LastName varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      Email varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      FlavorSize int(11) NOT NULL,
      nInstance int(11) NOT NULL,
      nIPs tinytext,
      Deployment varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
      Platform int(11) NOT NULL,
      ProjectName varchar(80) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      UserID varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      UserIDPass varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      Phone varchar(25) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      Comment longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      UNIQUE KEY TIMESTAMP (TIMESTAMP),
      PRIMARY KEY(ProjectID)
    );
    DESCRIBE BigTable;

    CREATE TABLE Details (
      Project_Number smallint(5) UNSIGNED NOT NULL,
      Instance_Name varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      Internal_IP varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      External_IP varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
    );
    DESCRIBE Details;
EOF
}

function copywebsite(){
    echo ""
    echo "Copying website to /var/www/Cloud-RAIN"
    echo ""
    sudo mkdir /var/www/Cloud-RAIN
    sudo cp *.py /var/www/Cloud-RAIN
    sudo cp *.html /var/www/Cloud-RAIN
    sudo cp *.php /var/www/Cloud-RAIN
}

function installSoftware(){
    echo ""
    echo "Install libapache2-mod-php5 & php5-mysql python-(keystone, nova, neutron, openstack) client"
    echo ""
    apt-get install -qqy libapache2-mod-php5 php5-mysql python-keystoneclient python-novaclient python-neutronclient python-openstackclient
    service apache2 restart
}

function enableWebsite(){
    echo ""
    echo "Enabling website (modifying /etc/apache2/sites-available/000-default.conf"
    echo "                            /etc/apache2/ports.conf"
    echo "                            /etc/apache2/apache2.conf" 
    echo ""
    echo "<VirtualHost *:81>" >> /etc/apache2/sites-available/000-default.conf 
    echo "    DocumentRoot "/var/www/Cloud-RAIN"" >> /etc/apache2/sites-available/000-default.conf 
    echo "    ServerName site1" >> /etc/apache2/sites-available/000-default.conf 
    echo "</VirtualHost>" >> /etc/apache2/sites-available/000-default.conf 

    echo "Listen *:81" >> /etc/apache2/ports.conf

    echo "ServerName site1" >> /etc/apache2/apache2.conf
}

function setVariables(){
    source vars
}

function usage (){
    echo ""
    echo "Usage: $0 {Any of the options below}"
    echo ""
    echo " deploy_all"
    echo "     - Will run all of the commands below and set up the website for DevStack  - must be run on controller node(s)"
    echo " deployDB"
    echo " copywebsite"
    echo " installSoftware"
    echo " enableWebsite"
    echo " setVariables"
    echo ""
}
function main() {
    echo ""
    echo "Welcome to the Deploy Script"
    echo "Don't forget to update the Openstack credentials!"
    echo "Your website will be deployed on: http://<IP>:81/Cloud-RAIN/"
    if [ -z $1 ]; then
       usage
       exit 1
       fi

       if [ $1 == "deploy_all" ]; then
          deployDB
          copywebsite
          installSoftware
          enableWebsite
          setVariables
    else
      case $1 in 
         "deployDB")
            deployDB
            ;;
         "copywebsite")
            copywebsite
            ;;
         "installSoftware")
           installSoftware 
            ;;
         "enableWebsite")
            enableWebsite
            ;; 
         "setVariables")
            setVariables 
            ;;
         *)
           usage
           exit 1
      esac
    fi
}

main $1 
