<html>
<head>
  <Project Name>Cloud Research Automation for Infrastructure and Software - New Project Entry</Project Name>
</head>

<body>
  <h1>Rains - New Project Entry</h1>







<form method="get" action="index.html">
    <select id="cd" name="cd">
        <?php
$setError = FALSE;
$host     ='localhost';
$username = "root";
$password = "password";
$port     = 3306;
$database = "glace";
try {
    $conn = new PDO("mysql:host=$host;dbname=$database", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "Connected successfully";
    }
catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
} 
 
        $sql="SELECT name FROM images";
        $imageIDresult=$conn->query($sql)
        while ($imageIDrow=mysql_fetch_array($imageIDresult)) {
        $name=$imageIDrow["name"];
            echo "<option>
                $name
            </option>";
        }
        ?>
    </select>
</form>










  <form action="insert_record.php" method="POST">
    <table border="0">
      <tr>
        <td>First Name</td>
        <td><input type="text" name="FirstName" maxlength="30" size="30" required></td>
      </tr>
      <tr>
        <td>Last Name</td>
        <td> <input type="text" name="LastName" maxlength="30" size="30" required></td>
      </tr>
      <tr>
        <td>E-mail</td>
        <td> <input type="text" name="Email" maxlength="80" size="30" required></td>
      </tr>
      <tr>
        <td>Phone</td>
        <td><input type="text" name="Phone" maxlength="15" size="15" required></td>
      </tr>


      <tr>
        <td>Project Name</td>
        <td><input type="text" name="ProjectName" maxlength="80" size="30"></td>
      </tr>
      <tr>
        <td>Number of Instances</td>
        <td><input type="text" name="nInstance" maxlength="2" size="7" required></td>
      </tr>
      <tr>
        <td>Flavor Size</td>
        <td>
            <input type="radio" name="FlavorSize" value="512">Tiny
            <input type="radio" name="FlavorSize" value="2048">Small
            <input type="radio" name="FlavorSize" value="4096" CHECKED>Medium
            <input type="radio" name="FlavorSize" value="8192">Large
            <input type="radio" name="FlavorSize" value="16384">XLarge
        </td>
      </tr>
      <tr>
        <td>Platform</td>
        <td>
            <input type="radio" name="Platform" value="3">CentOS
            <input type="radio" name="Platform" value="2" CHECKED>Ubuntu 14.04
            <input type="radio" name="Platform" value="1">CirrOS
        </td>
      </tr>
      <tr>
        <td>Deployment</td>
        <td>
            <input type="radio" name="Deployment" value="1" CHECKED>Hadoop
        </td>
      </tr>
      <tr>
        <td>UserID (abc123)</td>
        <td><input type="text" name="UserID" maxlength="6" size="30" required></td>
      </tr>
      <tr>
        <td>UserIDPass</td>
        <td><input type="password" name="UserIDPass" maxlength="20" size="30" required></td>
      </tr>
      <tr>
        <td>Comment</td>
        <td><textarea name="Comment" rows="5" cols="30"></textarea></td>
      </tr>


      <tr>
        <td colspan="2"><input type="submit" value="Create"></td>
      </tr>
    </table>
  </form>
</body>
</html>
