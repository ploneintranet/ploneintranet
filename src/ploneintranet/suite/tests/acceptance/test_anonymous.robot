*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Anonymous will not see some icon
    Disable autologin
    Go To  ${PLONE_URL}/test_rendering
    Then Element Should Not Be Visible  css=#hamburger
    Then Element Should Not Be Visible  css=#searchForm_gadget
