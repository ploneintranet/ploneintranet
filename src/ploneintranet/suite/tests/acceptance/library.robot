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

Library document shows tags
    Given I browse to a document
    Page should contain  foo
    Page should not contain  baz

Library document tag links to tag view    
    Given I browse to a document
    Click link  foo
    Page should contain  Holidays
    Page should contain  Sick Leave
    Page should not contain  Pregnancy
    Click link  baz
    Page should not contain  Holidays
    Page should contain  Sick Leave
    Page should contain  Pregnancy
    Click link  Pregnancy
    Page should contain  bar
    Page should contain  baz
    Page should not contain  foo

Library shows themeswitcher to editor
    Given I browse to the library as an editor
    Page should contain element  css=a[href$='/@@switch_theme']

Library hides themeswitcher from user
    Given I browse to the library
    Page should not contain element  css=a[href$='/@@switch_theme']

Library document shows themeswitcher to editor
    Given I browse to a document as an editor
    Page should contain element  css=a[href$='/@@switch_theme/edit']

Library document hides themeswitcher from user
    Given I browse to a document
    Page should not contain element  css=a[href$='/@@switch_theme/edit']


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

I browse to the library as an editor
    I am logged in as the user alice_lindstrom
    Go To  ${PLONE_URL}
    Click Link  Library

I browse to a document as an editor
    I browse to the library as an editor
    Click Link  Human Resources
    Click Link  Holidays
