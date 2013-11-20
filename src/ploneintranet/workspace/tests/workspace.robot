*** Settings ***

Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Site Administrator can create Workspace
    Given I'm logged in as a 'Site Administrator'
    Create workspace 'Example Workspace'


*** Keywords ***

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}
    Go to  ${PLONE_URL}


Create workspace '${TITLE}'
    Go to  ${PLONE_URL}
    