<?php
start_session();
header('Cache-Control: no-store');
$success=isset($_SESSION['lead_success']);$reference=$_SESSION['lead_success']??null;unset($_SESSION['lead_success']);
if($_SERVER['REQUEST_METHOD']==='POST'){
 $success=false;
 foreach(['name','email','phone','description','website'] as $key)$old[$key]=is_string($_POST[$key]??null)?trim($_POST[$key]):'';
 if(!verify_csrf())$errors[]='Your session has expired. Please submit the form again.';
 if(!throttle('contact:'.($_SERVER['REMOTE_ADDR']??'unknown'),5,3600)){$errors[]='Too many enquiries have been submitted. Please try again in an hour or contact us by email.';http_response_code(429);}
 if($old['website']!=='')$errors[]='Unable to submit this enquiry. Please contact us by email.';
 if(mb_strlen($old['name'])<2||mb_strlen($old['name'])>100)$errors[]='Please enter your name (2–100 characters).';
 if($old['email']!==''&&(!filter_var($old['email'],FILTER_VALIDATE_EMAIL)||strlen($old['email'])>254||preg_match('/[\r\n]/',$old['email'])))$errors[]='Please enter a valid email address.';
 if(!preg_match('/^\+?[0-9 ()\-.]{7,30}$/',$old['phone']))$errors[]='Please enter a valid phone number, including your country code.';
 if(mb_strlen($old['description'])>10000)$errors[]='Please keep your project description within 10,000 characters.';
 if(!$errors){
  try{
   $values=array_intersect_key($old,array_flip(['name','email','phone','description']));
   $values['created_at']=gmdate('c');
   $query=$db->prepare('INSERT INTO leads(name,email,phone,description,created_at) VALUES(:name,:email,:phone,:description,:created_at)');$query->execute($values);
   $id=(int)$db->lastInsertId();
   // Coordinate with the retry worker to avoid concurrently sending the same alert.
   $notificationLock=fopen($config['storage'].'/notifications.lock','c');
   if($notificationLock && flock($notificationLock,LOCK_EX|LOCK_NB)){
    $pending=$db->prepare('SELECT mail_status FROM leads WHERE id=?');$pending->execute([$id]);
    if($pending->fetchColumn()==='pending'&&send_lead_email(array_merge($values,['id'=>$id])))$db->prepare('UPDATE leads SET mail_status="accepted" WHERE id=?')->execute([$id]);
    flock($notificationLock,LOCK_UN);
   }
   if($notificationLock)fclose($notificationLock);
   $_SESSION['lead_success']=$id;$_SESSION['csrf']=bin2hex(random_bytes(32));header('Location: /contact',true,303);exit;
  }catch(Throwable $exception){error_log('Portfolio enquiry failed: '.$exception->getMessage());$errors[]='We couldn’t save your enquiry. Please try again, or email '.$config['email'].'.';http_response_code(503);}
 }elseif(http_response_code()!==429){http_response_code(422);}
}
