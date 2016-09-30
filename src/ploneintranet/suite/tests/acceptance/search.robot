*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  robot.libraries.DateTime
Library  DebugLibrary

Variables  variables.py

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Allan can see the search button in header
    Given I am logged in as the user allan_neece
    Then I can see the site search button

# https://github.com/quaive/ploneintranet/issues/772
Allan can search and find the Budget Proposal
    [tags]  fixme
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
    I can set the date range to \ ${YESTERDAY}
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

Allan can search and toggle previews
    Given I am logged in as the user allan_neece
    I can search in the site header for Budget
    And I can see the search result previews
    Then I toggle the search previews
    And I cannot see the search result previews
    Then I toggle the search previews
    And I can see the search result previews
    Then I can filter content of type Image
    And I can see the search result previews
    I can unfilter content of type Image
    And I can see the search result previews

Allan can search and sort results
    Given I am logged in as the user allan_neece
    I can search in the site header for Proposal
    Then I can see that the first search result is Draft
    Then I can sort search results by date
    Then I can see that the first search result is Budget
    Then I can sort search results by relevancy
    Then I can see that the first search result is Draft
