@debonix  @migration  @company

Feature: Define report configs

  @report_webkit
  Scenario: Define webkit headers
    Given I execute the SQL commands
    """
    UPDATE ir_header_webkit SET html = '<!-- empty -->', footer_html = '<!-- empty -->'
        WHERE name IN ('Financial Portrait Header', 'Financial Landscape Header')
    """
