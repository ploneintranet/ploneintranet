*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Demo content is imported
    Given I'm logged in as a 'Manager'
     then I can see an existing workspace
     and I can see an existing user

*** Keywords ***

I can see an existing workspace
    Go To                           ${PLONE_URL}/workspaces/open-market-committee
    Wait Until Element Is visible   xpath=//a/strong[text()='Manage Information']   timeout=5

I can see an existing user
    Go To                           ${PLONE_URL}/acl_users/source_users/manage_users
    Wait Until Element Is visible   xpath=//a[text()='alice_lindstrom']   timeout=5