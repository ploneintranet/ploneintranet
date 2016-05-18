*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Anonymous get redirected to login page
    Given I'm logged in as a 'Site Administrator'
          Go to  ${PLONE_URL}/test_injection_on_insufficient_privileges
          Click Link  Test unauthorized pat-inject
          Wait Until Page Contains Element  css=.pat-notification.warning  5

*** Keywords ***
