*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

User can access the calendar app
    Given I am logged in as the user allan_neece
    I can go to the calendar application


*** Keywords ***

I can go to the calendar application
    I can Click the Apps tab
    Click Element  css=div.app-calendar
    Wait until element is visible  css=div.pat-calendar
    Wait until element is visible  css=div#calendar-my-calendars
    Wait until element is visible  css=button.view-week
    Wait until element is visible  css=div.calendar
    Wait until element is visible  css=select.timezone
