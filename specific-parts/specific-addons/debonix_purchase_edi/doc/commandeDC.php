<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
	<head>
		<meta http-equiv="Content-Type" content="text/html"; charset="UTF-8" />
		<title>Debonix France : Dashboard</title>
			<link rel="stylesheet" href="./menu.css"/>
			<link rel="stylesheet" href="./design.css"/>
			<link rel="stylesheet" href="./tableau.css"/>
	
		<!-- Pour le menu d�roulant -->	
		<script type="text/javascript" src="./dynMenu.js"></script>
		
		<!-- D�tection du navigateur -->
		<script src="browserdetect.js"></script>
		
		<!-- Partie relative aux graphiques -->
		<!--[if lt IE 9]><script language="javascript" type="text/javascript" src="excanvas.js"></script><![endif]-->
		<script language="Javascript" type="text/javascript" src="./js/jquery.min.js"></script>
		<script language="JavaScript" type="text/javascript" src="./js/jquery.jqplot.min.js"></script>
		
		<script type="text/javascript" src="./js/plugins/jqplot.barRenderer.min.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.categoryAxisRenderer.min.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.pointLabels.min.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.highlighter.min.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.cursor.min.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.enhancedLegendRenderer.js"></script>
		<script type="text/javascript" src="./js/plugins/jqplot.dateAxisRenderer.min.js"></script>
		
		<script type="text/javascript" src="./js/plugins/jqplot.json2.min.js"></script>

		<!-- Style propre aux graphiques jqPlot -->
		<link rel="stylesheet" type="text/css" href="./js/jquery.jqplot.css" />		
	</head>
	<body>
		<?php include('header.html'); ?>
		<br/>
		<form method="post" action="commandeDC.php">
			<p>
				<br/>
				<label for="name" style="float:left;">Commande numéro </label><input name="commande" type="text" placeholder="CF1307126473" maxlength="14" />
				<input id="Valider" type="submit" value="Valider" />
			 </p>
		</form>
		
		<?php
		if(!empty($_POST['commande'])){
			require('tools.php');
		try {
					$dbconnect = new PDO('pgsql:host=192.168.0.71;port=5432;dbname=openerp_prod_debonix;user=openerp_ro;password=UK7ooLooze4ahXetofe');
					$dbconnect->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
					// la table res partner address n existe plus en v7
					$req = $dbconnect->query("select po.*, rpa.fax, rpa.street, rpa.street2, rpa.phone, rpa.city, rpa.name as client, rpa.zip
											from purchase_order po, res_partner rpa 
											where po.name Like '%".$_POST['commande']."%' and po.dest_address_id=rpa.id");
				    $req->setFetchMode(PDO::FETCH_OBJ);
				    while ( $donnees = $req->fetch() ) {
				    	$cmd = new commande;
		    	
				    	$dateCmd = preg_split('/ /',$donnees->create_date);
				    	$heureCmd = preg_replace('/:/','',$dateCmd[1]);
				    	$heureCmd = substr($heureCmd,0,6);
				    	$dateCmd = preg_replace('/-/','',$dateCmd[0]);
				    	
				    	$dateLivraison = preg_split('/ /',$donnees->minimum_planned_date);
				    	$dateLivraison = preg_replace('/-/','',$dateLivraison[0]);
				    	
						/* addDEB Paramètres : code filiale, siret filiale, date cmd , heure cmd */
						//$cmd->addDEB("DR","42482122100282",$dateCmd,$heureCmd);
						$cmd->addDEB("PLN","52789590800012",$dateCmd,$heureCmd);
						
						/* addDMS Paramètres : code agence, siret agence, siret debonix */
						//$cmd->addDMS("000","42482122100027","00000540599990");
						$cmd->addDMS("928","52789590800012","49039922700035");
						
						/* add100 Paramètres : compte Debonix, numéro de commande, reference de la commande, date de livraison souhaitée */
						//$cmd->add100("0000980572",$donnees->name,$donnees->name,$dateLivraison);
						$cmd->add100("0000175000",$donnees->name,$donnees->name,$dateLivraison);
						
						/* add140 Paramètres : champ adr1,adr2,adr3,adr4,adr5, code postal, ville, tel, fax */
						(empty($donnees->street2)) ? $street2 ="" : $street2 = $donnees->street2;
						(empty($donnees->fax)) ? $fax ="" : $fax =$donnees->fax;
						$cmd->add130(utf8_decode($donnees->client),"",utf8_decode($donnees->street),utf8_decode($street2),"",utf8_decode($donnees->zip),utf8_decode($donnees->city),utf8_decode($donnees->phone),utf8_decode($fax));
						$cmd->add140(utf8_decode($donnees->client),"",utf8_decode($donnees->street),utf8_decode($street2),"",utf8_decode($donnees->zip),utf8_decode($donnees->city),utf8_decode($donnees->phone),utf8_decode($fax));
						
						/* add160 Paramètres : commentaire */
						if($donnees->notes) $cmd->add160(utf8_decode($donnees->notes));
						 

                       $req1 = $dbconnect->query("select pol.*, psi.product_code as code, pt.name as libelle
                       	from purchase_order_line pol,product_product pp,
                       	product_template pt, product_supplierinfo psi
                      	where pol.product_id = pp.id and
                      	pp.product_tmpl_id = pt.id and
                      	psi.product_id = pt.id and
                      psi.name =
                      (Select partner_id
                       from supplier_code
                        where code = 'SOGEDESCA') and
                          pol.order_id =".$donnees->id);
      
					    $req1->setFetchMode(PDO::FETCH_OBJ);
					    while ( $products = $req1->fetch() ) {
							$code = $products->code;
					    	(strlen($products->libelle)>70) ? $libelle = substr($products->libelle,0,70) : $libelle = $products->libelle;
					    	/* add200 Paramètres : codag, libéllé, prix unitaire, quantité, reférence fournisseur, unité, unité d'expression du prix (conditionnement) */
							$cmd->add200(utf8_decode($code),utf8_decode($libelle),utf8_decode($products->price_unit),utf8_decode($products->product_qty),utf8_decode($products->code),"P",1);
				    	}
						
						/*export du pivot*/
						$cmd->dump();
				    }
					
					$req->closeCursor();
					$dbconnect = NULL;
			}
				catch (Exception $e) {
				echo "Erreur : ". $e->getMessage();
			}


?>
	<form method="post" action="main.php">
			<p>
				<br/>
				<input name="numcommande" type="hidden" value="<?php echo $_POST['commande'];?>" />
				<input id="Valider" type="submit" value="Valider" />
			 </p>
	</form>
<?php }?>

<br/><br/><br/>	
		
		<div class="footerholder">
		<div class="footer">
		Copyrigth Debonix France - 2014
		</div></div>
