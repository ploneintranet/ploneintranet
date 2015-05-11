*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Anonymous get redirected to login page
    Disable autologin
    Given I open the Dashboard
     then I am on the login page
     Do login as  allan_neece
     Wait Until Element Is visible  css=#activity-stream  timeout=5
     I see the Dashboard

*** Keywords ***

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I am on the login page
    Element should be visible  css=#__ac_name

I see the Dashboard
    Element should be visible  css=#activity-stream

Do login as
    [arguments]  ${username}
    Page should contain element  __ac_name
    Input text  __ac_name  ${username}
    Input text  __ac_password  secret
    Click Button  css=fieldset.button-bar button[type='submit']