# -*- coding: utf-8 -*-
@upgrade_from_1.1 @debonix

Feature: upgrade to 1.2.0

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | connector                            |
      | magentoerpconnect                    |
      | server_env_magentoerpconnect         |
      | specific_magento                     |
      | elasticsearch_view_export            |
      | sql_view                             |
      | sql_view_purchase                    |
      | sql_view_sale                        |
      | sql_view_stock                       |
      | server_env_elasticsearch_view_export |
    Then my modules should have been installed and models reloaded

    Given I need a "elasticsearch.host" with oid: scenario.elasticsearch_host_kibana
    And having:
      | key  | value |
      | code | ELK   |
    And I need a "elasticsearch.view.index" with oid: scenario.elasticsearch_index_purchase
    And having:
      | key      | value                          |
      | name     | odoo-purchase-lines            |
      | host_id  | by code: ELK                   |
      | sql_view | sql_view_purchase_order_report |
    And I need a "elasticsearch.view.index" with oid: scenario.elasticsearch_index_sale
    And having:
      | key      | value                      |
      | name     | odoo-sale-lines            |
      | host_id  | by code: ELK               |
      | sql_view | sql_view_sale_order_report |
    And I need a "elasticsearch.view.index" with oid: scenario.elasticsearch_index_stock_turnover
    And having:
      | key      | value                        |
      | name     | odoo-stock-turnover          |
      | host_id  | by code: ELK                 |
      | sql_view | sql_view_stock_move_turnover |
    And having the following index configuration:
    """
    {
      "mappings": {
        "_default_": {
          "properties": {
            "month": {
              "type": "date",
              "format": "yyyy-MM-dd HH:mm:ss"
            }
          }
        }
      }
    }
    """

    Given I need an Elasticsearch template named "odoo" on host with oid "scenario.elasticsearch_host_kibana" having template:
    """
    {
      "template" : "*odoo*",
      "order" : 0,
      "settings" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 1
      },
      "mappings" : {
        "_default_" : {
          "dynamic_templates" : [ {
            "string_fields" : {
              "mapping" : {
                "type" : "multi_field",
                "fields" : {
                  "raw" : {
                    "index" : "not_analyzed",
                    "type" : "string"
                  },
                  "{name}" : {
                    "index" : "analyzed",
                    "norms" : { "enabled" : false },
                    "type" : "string"
                  }
                }
              },
              "match_mapping_type" : "string",
              "match" : "*"
            }
          } ],
          "properties" : {
          }
        }
      }
    }
    """


    Given I set the version of the instance to "1.2.0"
