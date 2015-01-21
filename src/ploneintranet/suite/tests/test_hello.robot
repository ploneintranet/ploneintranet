*** Settings ***

Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Site Administrator can access dashboard
    Given I'm logged in as a 'Site Administrator'
     Then I see the Dashboard

*** Keywords ***

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}

I see the Dashboard
    Element should be visible  css=#portlet-news
