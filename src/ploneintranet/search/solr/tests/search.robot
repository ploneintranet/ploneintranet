# SOLR search robot tests
    
*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ploneintranet/suite/tests/lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

# XXX These are currently duplicates of the
# basic search tests in the suite. They should be replaced
# with ones that test the advanced features of solr

Allan can see the search button in header
    Given I am logged in as the user allan_neece
    Then I can see the site search button

Allan can search and find the Budget Proposal
    Given I am logged in as the user allan_neece
    I can search in the site header for Budget
    And I can see the search result Budget Proposal
    And I can follow the search result Budget Proposal



