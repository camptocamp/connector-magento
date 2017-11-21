[![Build Status](https://magnum.travis-ci.com/camptocamp/debonix_openerp.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://magnum.travis-ci.com/camptocamp/debonix_openerp)

# Debonix OpenERP

Private and customer specific branches for Debonix.

## Installation:

Requirements
------------


        pip install invoke --user

or
 

        sudo pip install invoke


Steps
-----

1. Clone the github repository

        git clone git@github.com:camptocamp/camptocamp_openerp.git


1. Initialize the tasks repo required by invoke: 


        git submodule update --init


1. Buildout the wheel: 

    
        invoke env.init -s -r -p profiles/dev.cfg
 

1. Finally: 


        ./bin/buildout


:warning: do not use the other configuration files if you do not know what you
are doing
