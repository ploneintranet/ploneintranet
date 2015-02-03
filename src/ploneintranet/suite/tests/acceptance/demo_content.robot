*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Workspaces have been created
    Given I'm logged in as a 'Manager'
    Then Go to homepage
    ${url}    Get Location
    Go to  ${url}/workspaces
    Go to  ${url}/open-market-committee
    Wait Until Element Is visible  css=a[title="Projection Material"]   timeout=5

