<!DOCTYPE html>
<html>
<head>
  <Project Name>Rains - New Project Entry</Project Name>
</head>

<body>
  <h1>Cloud Research Automation for Infrastructure and Software - New Project Entry</h1>
  
<?php
///////////////////////
// SHOW ERRORS IN PHP
///////////////////////
#ini_set('display_errors', 1);
#ini_set('display_startup_errors', 1);
#error_reporting(E_ALL);



$setError = FALSE;
$host     ='localhost';
$username = "root";
$password = "password";
$port     = 3306;
$database = "Cloud";

$FirstNameErr = $LastNameErr = $EmailErr = $PhoneErr =  $ProjectNameErr = $FlavorSizeErr = "";
$nInstanceErr = $Deployment = $PlatformErr = $UserIDErr = $UserIDPassErr = $CommentErr = "";

$FirstName = $LastName = $Email = $Phone = $ProjectName = $FlavorSize = "";
$nInstance = $Deployment = $Platform = $UserID = $UserIDPass = $Comment = "";
try {
    $conn = new PDO("mysql:host=$host;dbname=$database", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "Connected successfully";
}
catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}

// create short variable names 
$FirstName   = test_input($_POST['FirstName']);
$LastName    = test_input($_POST['LastName']);
$Email       = test_input($_POST['Email']);
$Phone       = test_input($_POST['Phone']);
#$CustomerID  = test_input($_POST['CustomerID']);
$ProjectName = test_input($_POST['ProjectName']);
$FlavorSize  = test_input($_POST['FlavorSize']);
$nInstance   = test_input($_POST['nInstance']);
$Deployment  = test_input($_POST['Deployment']);
$Platform    = test_input($_POST['Platform']);
$UserID      = test_input($_POST['UserID']);
$UserIDPass  = test_input($_POST['UserIDPass']);
$Comment     = test_input($_POST['Comment']);
$TIMESTAMP   = "";

//Validate email format
if (!filter_var($Email, FILTER_VALIDATE_EMAIL)) {
    echo '<br>Invalid email format';
    $setError = TRUE;
}
if (!filter_var($Email, FILTER_SANITIZE_EMAIL)) {
    echo '<br>Invalid characters in email address';
    $setError = TRUE;
}


//Validate number of instances format
if (!filter_var($nInstance, FILTER_VALIDATE_INT)) {
    echo '<br>Please correct the number of instances as this is not valid';
    $setError = TRUE;
}

//Validate flavor size format
if (!filter_var($FlavorSize, FILTER_VALIDATE_INT)) {
    echo '<br>Please correct the flavor size as this is not valid';
    $setError = TRUE;
}

// Sanatize 
function test_input($data)
{
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

if ($setError == FALSE) {
    $query = "INSERT INTO BigTable(FirstName, LastName, Email, Phone, FlavorSize, nInstance, Deployment, Platform, ProjectName, UserID, UserIDPass, Comment) VALUES ('$FirstName', '$LastName', '$Email', $Phone, '$FlavorSize', '$nInstance', '$Deployment', '$Platform', '$ProjectName', '$UserID', '$UserIDPass', '$Comment')";
} else
    echo "<br>Project has NOT been submitted <a href=\"javascript:history.go(-1)\"><br>GO BACK</a>";


// GET FULL RECORD FROM DATABASE
$sql     = "SELECT ProjectID, TIMESTAMP, FirstName, LastName, Email, Phone, FlavorSize, nInstance, Deployment, Platform, ProjectName, UserID, UserIDPass, Comment FROM BigTable WHERE TIMESTAMP='$TIMESTAMP'";
$result1 = $conn->query($sql);

// DEBUGGING: Check it was submitted correctly.
$result = $conn->query($query);
if ($result)
    echo $conn->affected_rows . '<br>Project inserted into database.<br>';

// echo "<br><br>Attempting to enter python script...</br></br>";
$handle = popen("python main.py ", 'r');
while (!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer<br/>\n";
    ob_flush();
}
pclose($handle);

// echo "left python script main.py";

//CREATE ANSIBLE SCRIPT FOR OPENSTACK
$content = "
---
- hosts: openstack-local
  remote_user: root
  sudo: yes
  gather_facts: no

  tasks:
    - os_server:
      state: present
      auth:
          auth_url: http://192.168.56.20:5000/v2.0
          username: admin
          password: password
          project_name: ProjectName
      name: vm1
      image: 4f905f38-e52a-43d2-b6ec-754a13ffb529
      key_name: james
      timeout: 200
      flavor: nFlavor
      nics:
        - net-id: 34605f38-e52a-25d2-b6ec-754a13ffb723
        - net-name: another_network
      meta:
        hostname: test1
        group: test_group";

$playholder   = array(
    'UserIDPass',
    'UserID',
    'ProjectName',
    'nFlavor'
);
$inputparams  = array(
    $UserIDPass,
    $UserID,
    $ProjectName,
    $nFlavor
);
$finalcontent = str_replace($playholder, $inputparams, $content);


//WRITE ANSIBLE FILE
$fileLocation = getenv("DOCUMENT_ROOT") . "/myfile.yml";
//$fileLocation =  "/home/ubuntu/myfile.yml";
$file         = fopen($fileLocation, "w");
//$content = '"Your text here" . $UserID . $UserIDPass';
fwrite($file, $finalcontent);
fclose($file);
//$Email1 = "James.Benson@utsa.edu";
//$query1 = "SELECT ProjectID, Email FROM BigTable WHERE Email=" .$Email1;
//foreach($conn -> query($query1) as $row){
//    print $row['ProjectID'] . "\t";
//    print $row['Email'] . "\t";
//}


// CLOSE THE CONNECTION
try {
    $conn = null;
}
catch (PDOException $e) {
    echo $e->getMessage();
}
// DEBUGGING: 
echo "<br>Connection closed.<br>";


////////////////////////////
// DOWNLOAD PEM FILE
////////////////////////////
$link_address = 'http://10.3.100.43:81/Cloud-RAIN/download.php?f=' . $UserID . '.pem';
echo "<a href='$link_address'>PRIVATE PEM FILE DOWNLOAD NOW</a>";

echo "END OF FILE!";
?>

</body>
</html>

