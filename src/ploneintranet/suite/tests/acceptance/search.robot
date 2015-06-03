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
    And I can find the search result Budget Proposal

*** Keywords ***

I can see the site search button
    Page Should Contain Element  css=#global-header input.search

I can search in the site header for ${SEARCH_STRING}
    Input text  css=#global-header input.search  ${SEARCH_STRING}
    Submit Form  css=#global-header form#searchGadget_form

I can find the search result ${SEARCH_RESULT_TITLE}
    Element should be visible  link=${SEARCH_RESULT_TITLE}
    Click Link  link=${SEARCH_RESULT_TITLE}
    Location Should Contain  /workspaces/open-market-committee/manage-information/budget-proposal
    Page should contain  ${SEARCH_RESULT_TITLE}