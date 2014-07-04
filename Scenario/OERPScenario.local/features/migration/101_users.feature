@users_groups_setup

Feature: Configure users and groups

  Scenario: Configure groups for Admins
    Given we select users below
      | login      |
      | admin      |
      | dbudun     |
      | slecaillet |
    Then we assign all groups to the users

  Scenario: Configure groups for Purchase Managers
    Given we select users below
      | login        |
      | mbelville    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name               |
      | Debonix Purchase Manager |

  Scenario: Configure groups for Purchase Users
    Given we select users below
      | login        |
      | sdumoulin    |
      | mdelcroix    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name            |
      | Debonix Purchase User |

  Scenario: Configure groups for Sales Managers
    Given we select users below
      | login        |
      | cdasilva     |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name           |
      | Debonix Sale Manager |

  Scenario: Configure groups for Sales Users
    Given we select users below
      | login        |
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
      | group_name        |
      | Debonix Sale User |

  Scenario: Configure groups for Warehouse Managers
    Given we select users below
      | login       |
      | agallina    |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name                |
      | Debonix Warehouse Manager |

  Scenario: Configure groups for Accounting Managers
    Given we select users below
      | login        |
      | ndupin       |
      | frousselle   |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name              |
      | Debonix Account Manager |

  Scenario: Configure groups for Accounting Users
    Given we select users below
      | login        |
      | deng-yi      |
      | eleger       |
      | alaouisset   |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name              |
      | Debonix Account Manager |

  Scenario: Configure groups for Aftersales
    Given we select users below
      | login   |
      | fgauger |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name         |
      | Debonix Aftersales |

  Scenario: Configure groups for Contractors
    Given we select users below
      | login |
      | scemi |
    Then we remove all groups from the users
    And we assign to users the groups below:
      | group_name         |
      | Debonix Contractor |
