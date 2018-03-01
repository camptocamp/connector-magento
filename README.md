[![Build Status](https://magnum.travis-ci.com/camptocamp/debonix_openerp.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://magnum.travis-ci.com/camptocamp/debonix_openerp)

# Debonix OpenERP

Private and customer specific branches for Debonix.

# BE CAREFUL: THIS MASTER BRANCH IS TEMPORARY!

In waiting that the customer switch on a new server, we can't use wheels.
So, the wheels have been deleted from master, and the master with wheels have been saved here:
https://github.com/camptocamp/debonix_openerp/tree/master_with_wheels

When the customer will have this new server,
we will need to add all commits done in master on the master_with_wheels branch,
and to replace the master branch by master_with_wheels branch.

## Installation:

Steps:

    ./bootstrap.sh profiles/dev.cfg
    bin/buildout

:warning: do not use the other configuration files if you do not know what you
are doing
