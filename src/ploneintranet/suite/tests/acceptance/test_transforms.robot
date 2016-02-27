*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Page contains just one meta for viewport
    Disable autologin
    Go To  ${PLONE_URL}/test_rendering
    Then Xpath Should Match X Times  //meta[@name='generator']  1
    Then Xpath Should Match X Times  //meta[@name='viewport']  1
