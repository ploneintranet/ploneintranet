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
    Then I can exclude content of type Page
    And I cannot see the search result Minutes Overview
    And I can see the search result Minutes

Allan can search and filter by date
    Given I am logged in as the user allan_neece
    I can search in the site header for minutes
    Then I can set the date range to before-last-month
    And I can see the search result Minutes Overview
    And I cannot see the search result Minutes

*** Keywords ***

I can see the site search button
    Page Should Contain Element  css=#global-header input.search

I can search in the site header for ${SEARCH_STRING}
    Input text  css=#global-header input.search  ${SEARCH_STRING}
    Submit Form  css=#global-header form#searchGadget_form

I can see the search result ${SEARCH_RESULT_TITLE}
    Element should be visible  link=${SEARCH_RESULT_TITLE}

I cannot see the search result ${SEARCH_RESULT_TITLE}
    Element should not be visible  link=${SEARCH_RESULT_TITLE}

I can follow the search result ${SEARCH_RESULT_TITLE}
    Click Link  link=${SEARCH_RESULT_TITLE}
    Page should contain  ${SEARCH_RESULT_TITLE}

I can exclude content of type ${CONTENT_TYPE}
    Unselect Checkbox  css=input[type="checkbox"][value="${CONTENT_TYPE}"]
    Select From List By Value  css=select[name="created"]  today
    Wait Until Element is Visible  css=dl.search-results[data-search-string*="created=today"]

I can set the date range to ${DATE_RANGE_VALUE}
    Select From List By Value  css=select[name="created"]  ${DATE_RANGE_VALUE}
    Wait Until Element is Visible  css=dl.search-results[data-search-string*="created=${DATE_RANGE_VALUE}"]
