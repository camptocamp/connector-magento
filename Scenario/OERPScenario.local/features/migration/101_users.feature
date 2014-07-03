@users_groups

Feature: Configure users and groups

  @users_groups_purchase_manager
  Scenario: Configure groups for Purchase Managers
    Given we select users below
      | login        |
      | mbelville    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Purchases / Manager                         |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Manufacturing / User                        |
      | Accounting & Finance / Invoicing & Payments |
      | Point of Sale / User                        |
      | Connector / Connector Manager               |
      | Manage Secondary Unit of Measure            |
      | Product Variant (not supported)             |
      | Costing Method                              |
      | Manage Fund Raising                         |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Multi Currencies                            |
      | Purchase Pricelists                         |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Check Total on supplier Invoices            |
      | Manage Serial Numbers                       |
      | Manage Inventory valuation                  |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Manage Routings                             |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_purchase_user
  Scenario: Configure groups for Purchase Users
    Given we select users below
      | login        |
      | sdumoulin    |
      | mdelcroix    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Manufacturing / User                        |
      | Accounting & Finance / Invoicing & Payments |
      | Purchases / Manager                         |
      | Point of Sale / User                        |
      | Sharing / User                              |
      | Manage Secondary Unit of Measure            |
      | Costing Method                              |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Purchase Pricelists                         |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Check Total on supplier Invoices            |
      | Manage Serial Numbers                       |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Manage Routings                             |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_sales_manager
  Scenario: Configure groups for Sales Managers
    Given we select users below
      | login        |
      | cdasilva     |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Sales / Manager                             |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Accounting & Finance / Invoicing & Payments |
      | Point of Sale / User                        |
      | Sharing / User                              |
      | Manage Secondary Unit of Measure            |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_sales_user
  Scenario: Configure groups for Sales Users
    Given we select users below
      | login        |
      | sdumoulin    |
      | aguldasi     |
      | anavrez      |
      | lebissonnais |
      | ilanternier  |
      | chuger       |
      | jgarcia      |
      | mtartik      |
      | qlafon       |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Accounting & Finance / Invoicing & Payments |
      | Point of Sale / User                        |
      | Sharing / User                              |
      | Manage Secondary Unit of Measure            |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_warehouse_user
  Scenario: Configure groups for Warehouse Managers
    Given we select users below
      | login       |
      | agallina    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / Manager                         |
      | Human Resources / Employee                  |
      | Sharing / User                              |
      | Manage Product Packing                      |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Addresses in Sales Orders                   |
      | Manage Serial Numbers                       |
      | debonix_employee                            |

  @users_groups_accounting_manager
  Scenario: Configure groups for Accounting Managers
    Given we select users below
      | login        |
      | ndupin       |
      | frousselle   |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Purchases / User                            |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Manufacturing / User                        |
      | Accounting & Finance / Financial Manager    |
      | Point of Sale / User                        |
      | Human Resources / Manager                   |
      | Manage Secondary Unit of Measure            |
      | Costing Method                              |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Multi Currencies                            |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Check Total on supplier Invoices            |
      | Manage Serial Numbers                       |
      | Manage Inventory valuation                  |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Manage Routings                             |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_accounting_user
  Scenario: Configure groups for Accounting Users
    Given we select users below
      | login        |
      | deng-yi      |
      | eleger       |
      | alaouisset   |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Purchases / User                            |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Manufacturing / User                        |
      | Accounting & Finance / Accountant           |
      | Point of Sale / User                        |
      | Human Resources / Manager                   |
      | Manage Secondary Unit of Measure            |
      | Costing Method                              |
      | Manage Logistic Serial Numbers              |
      | Manage Multiple Locations and Warehouses    |
      | Enable Invoicing Delivery orders            |
      | Multi Currencies                            |
      | Manage Multiple Units of Measure            |
      | Manage Properties of Product                |
      | Check Total on supplier Invoices            |
      | Manage Serial Numbers                       |
      | Manage Inventory valuation                  |
      | Enable Invoicing Sales order lines          |
      | Properties on lines                         |
      | Manage Routings                             |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | Stock worker invoices auto-validation       |
      | Product / Manager                           |
      | debonix_employee                            |
      | Invoice                                     |
      | Purchase                                    |

  @users_groups_aftersales
  Scenario: Configure groups for Aftersales
    Given we select users below
      | login   |
      | fgauger |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                                  |
      | Purchases / User                            |
      | Sales / See all leads                       |
      | Knowledge / User                            |
      | Warehouse / User                            |
      | Manufacturing / User                        |
      | Accounting & Finance / Accountant           |
      | Point of Sale / User                        |
      | Manage Logistic Serial Numbers              |
      | Enable Invoicing Delivery orders            |
      | Manage Properties of Product                |
      | Manage Serial Numbers                       |
      | Properties on lines                         |
      | Technical Features                          |
      | Partner Manager                             |
      | Accounting / Payments                       |
      | debonix_manager                             |
      | debonix_employee                            |
      | Invoice                                     |
      | POS - Confirmation                          |

  @users_groups_contractor
  Scenario: Configure groups for Contractors
    Given we select users below
      | login   |
      | scemi   |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name          |
      | Knowledge / User    |
      | Technical Features  |
