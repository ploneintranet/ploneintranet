*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Library shows sections and subsections
    Given I browse to the library
    Page should contain  Human Resources
    Page should contain  Leave policies

Library section shows subsections and sub-subsections
    Given I browse to a section
    Page should contain  Leave policies
    Page should contain  Holidays

Library folder shows documents
    Given I browse to a folder
    Page should contain  Holidays

Library document shows navigation
    Given I browse to a document
    Page should contain  Leave policies
    Page should contain  Sick Leave
    Page should contain  Human Resources
    Page should contain  All topics
    Page should contain  Library
    Page should contain  l♥ve

*** Keywords ***

I browse to the library
    I am logged in as the user allan_neece
    Go To  ${PLONE_URL}
    Click Link  Library

I browse to a section
    I browse to the library
    Click Link  Human Resources

I browse to a folder
    I browse to the library
    Click Link  Leave policies

I browse to a document
    I browse to a section
    Click Link  Holidays
    Wait until page contains element  xpath=//h1[@class='title' and text()='Holidays']  1
