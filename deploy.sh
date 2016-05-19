function deployDB () {
    echo ""
    echo "Adding the Cloud Database and BigTable and LookUp tables."
    echo ""
    mysql -u root -p << EOF   
    DROP DATABASE Cloud;
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
    
    CREATE TABLE LookUp (
      ID int(11) NOT NULL,
      Image_Name tinytext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
      Image_ID varchar(36) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
    );
    DESCRIBE LookUp;

    INSERT INTO LookUp (ID, Image_Name, Image_ID) VALUES
    (1, 'CirrOS', 'cc307f92-33db-43d6-936b-3375206ebe51'),
    (2, 'Ubuntu', '9cb0cc56-8d3b-41ca-a2f8-99525e11c5af');

    SELECT * FROM LookUp;
EOF
}

function copywebsite(){
    sudo mkdir /var/www/Cloud-RAIN
    sudo cp *.py /var/www/Cloud-RAIN
    sudo cp *.html /var/www/Cloud-RAIN
    sudo cp *.php /var/www/Cloud-RAIN
}

function installSoftware(){
    apt-get install -y libapache2-mod-php5 php5-mysql
    service apache2 restart
}

function enableWebsite(){
    echo "<VirtualHost *:81>" >> /etc/apache2/sites-available/000-default.conf 
    echo "    DocumentRoot "/var/www/Cloud-RAIN"" >> /etc/apache2/sites-available/000-default.conf 
    echo "    ServerName site1" >> /etc/apache2/sites-available/000-default.conf 
    echo "</VirtualHost>" >> /etc/apache2/sites-available/000-default.conf 

    echo "Listen *:81" >> /etc/apache2/ports.conf

    echo "ServerName site1" >> /etc/apache2/apache2.conf

}



function usage (){
    echo ""
    echo "Usage: $0 {Any of the options below}"
    echo ""
    echo " deploy_all <database password>"
    echo "     - Will run all of the commands below and set up the website for DevStack  - must be run on controller node(s)"
    echo " deployDB <database password>"
    echo " copywebsite"
    echo " enableWebsite"
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
#    if [ -z $2 ]; then
#       echo ""
#       echo "Missing the database password"
#       echo ""
#       usage 
#       exit 1
#    fi
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
         *)
           usage
           exit 1
      esac
    fi
}

main $1 