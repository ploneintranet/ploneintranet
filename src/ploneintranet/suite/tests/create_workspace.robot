*** Settings ***

Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Manager can create a workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new workspace

*** Keywords ***

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}

I can create a new workspace
    Go To  ${PLONE_URL}/workspaces.html
    Click Link  link=Create Workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=New Workspace
    Input Text  name=form.widgets.IBasic.description  text=A new Workspace
    Click Element  css=button.icon-ok-circle.confirmative
    Debug
    Wait Until Element Is visible  css=div.post.content  timeout=5
