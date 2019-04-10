============================
Debonix Supplier Invoice EDI
============================

This module adds a scheduled action to connect to FTP and retrieve EDIFACT
files to import supplier invoices from the supplier SOGEDESCA
(Descours et Cabaud)

Workflow
========

The ir.cron is run once a day and do following actions :

1. Connect to FTP using server and credentials defined on the company (edifact_host, edifact_user, edifact_password)

2. Retrieve files from the FTP server in the folder defined by company.edifact_supplier_invoice_import_path

3. Parse files and do the following (according to the invoice_type) :

   a. If the invoice type is a customer invoice

      1. Find the related invoice
      2. Delete existing invoice lines
      3. Create lines according to imported edifact file
      4. Validate the invoice

   b. If the invoice type is a customer refund

      1. Create the refund according to imported edifact file

4. If something went wrong (see below possible `Errors types`_ below), create a crm.claim of type SOGEDESCA with errors messages as description and failed chunks as attachment.

5. Connect to FTP and do the following :

   1. Create success file (merged chunks) in the folder defined by company.edifact_supplier_invoice_import_success_path
   2. Create failed file (merged chunks) in the folder defined by company.edifact_supplier_invoice_import_error_path
   3. Commit the Database transaction to persist the changes done
   4. Delete processed edifact files.

Errors types
============

The following exceptions and their possible reasons are defined by the module :

- EdifactPurchaseInvoiceParsingError :

 - The processed edifact chunk is not formatted correctly

- EdifactPurchaseInvoiceNotFound :

 - The purchase order defined in edifact cannot be found
 - The purchase order defined in edifact has no invoice
 - The purchase order defined in edifact has multiple invoices

- EdifactPurchaseInvoiceProductNotFound

 - There is no products matching the product code defined in edifact
 - The product is found but does not appear on the found invoice

- EdifactPurchaseInvoiceTotalDifference

 - The line total defined in edifact is different than the subtotal computed by OpenERP.


Manual Testing
==============

As the module works with an ir.cron connecting to a FTP server, unittests are
quite limited. However, it's quite easy to set up a local FTP server using
Docker to test it manually.

Following courtesy of : `Docker Pure-ftpd Server <https://hub.docker.com/r/stilliard/pure-ftpd/>`_

1. Launch server ::

    docker pull stilliard/pure-ftpd:hardened
    docker run -d --name ftpd_server -p 21:21 -p 30000-30009:30000-30009 -e "PUBLICHOST=localhost" stilliard/pure-ftpd:hardened

2. Create user sogedesca_edi_test with access to /home/ftpusers/edi_supplier ::

    docker exec -it ftpd_server /bin/bash
    pure-pw useradd sogedesca_edi_test -f /etc/pure-ftpd/passwd/pureftpd.passwd -m -u ftpuser -d /home/ftpusers/edi_supplier

3. Connect to your server ::

    ftp -p localhost 21

   Enter credentials defined above.

4. Create folders ::

    mkdir edi_supplier
    cd edi_supplier
    mkdir archive
    mkdir erreur

5. Upload edifact files and wait for the scheduled task to start.
