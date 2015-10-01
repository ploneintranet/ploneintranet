*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Allan can see the search button in header
    Given I am logged in as the user allan_neece
    Then I can see the site search button

Allan can search and find the Budget Proposal
    Given I am logged in as the user allan_neece
    I can search in the site header for Budget
    And I can see the search result Budget Proposal
    And I can follow the search result Budget Proposal

Allan can search and find multiple documents
    Given I am logged in as the user allan_neece
    I can search in the site header for minutes
    And I can see the search result Minutes Overview
    And I can see the search result Minutes

Allan can search and filter by content type
    Given I am logged in as the user allan_neece
    I can search in the site header for minutes
    Then I can filter content of type Word 2007 document
    And the search results do not contain /manage-information/minutes-overview
    And I can see the search result Minutes

Allan can search and filter by date
    Given I am logged in as the user allan_neece
    I can search in the site header for minutes
    Then I can set the date range to before-last-month
    And I can see the search result Minutes Overview
    And I cannot see the search result Minutes

Allan can search only for images
    Given I am logged in as the user allan_neece
    I can search in the site header for budget
    Then I can click the Images tab
    And I can see the search result Budget Proposal

Allan can search only for files
    Given I am logged in as the user allan_neece
    I can search in the site header for minutes
    Then I can click the Files tab
    And I can see the search result Minutes

Allan can search for user Guy Hackey
    Given I am logged in as the user allan_neece
    I can search in the site header for Guy Hackey
    Then I can click the People tab
    And I can see the search result Guy Hackey



