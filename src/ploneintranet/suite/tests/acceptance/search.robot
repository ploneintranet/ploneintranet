*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can search
    given I am logged in as the user alice_lindstrom
    I can see the site search button
    I can search in the site header for Bristol

*** Keywords ***

I can see the site search button
    Page Should Contain Element  css=#global-header input[name="SearchableText"]

I can search in the site header for ${SEARCH_STRING}
     Input text  css=#global-header input[name="SearchableText"]  '${SEARCH_STRING}'
     Submit Form  css=#global-header form#searchGadget_form
