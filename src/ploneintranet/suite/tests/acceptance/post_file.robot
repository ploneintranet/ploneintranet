*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can attach a file to a post
    Given I am logged in as the user alice_lindstrom
      And I open the Dashboard
      And I see the Dashboard


*** Keywords ***

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I see the Dashboard
    Element should be visible  css=#portlet-news

