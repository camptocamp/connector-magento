@debonix  @migration  @intrastat_users

Feature: Configure users

  Scenario: Assign all finance users to Intrastat group
    Given we select users below
      | login        |
      | admin        |
      | dbudun       |
      | mguldasi     |
      | slecaillet   |
      | mbelville    |
      | scemi        |
      | ndupin       |
      | frousselle   |
      | mlaplace     |
      | deng-yi      |
      | mdelcroix    |
      | aprost       |
      | ilanternier  |
      | cravello     |
      | jgarcia      |
      | eleger       |
      | ascarpellino |
      | sroger       |
      | bzenuni      |
      | alaurent     |
      | cveuillet    |
      | bgil         |
      | ookmen       |
      | alaouisset   |
      | mmoulin      |
    Then we assign to users the groups below:
      | group_name                 |
      | Detailed Intrastat Product |
