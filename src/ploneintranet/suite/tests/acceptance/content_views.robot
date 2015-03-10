*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can change the title of a document
    Given I'm logged in as a 'alice_lindstrom'
    And I view a document
    And I change the title
    And I view a document
    The document has the new title

*** Keywords ***
I view a document
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/public-bodies-reform

I change the title
    Input Text  title  New title
    Click Button  Save

The document has the new title
    Textfield Should Contain  title  New title
