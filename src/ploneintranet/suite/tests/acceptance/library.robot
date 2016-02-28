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

#Library tag view is enabled
#    Given I browse to the library
#    When I switch to the by-tags listing
#    Wait until page contains  I ♥ UTF-8

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

I switch to the by-tags listing
    Click element  css=select[name=groupby]
    Click element  css=option[value=tag]
