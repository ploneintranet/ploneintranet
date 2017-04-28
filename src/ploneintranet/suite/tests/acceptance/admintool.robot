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

Admin can use the administrator tool app
    Given I'm logged in as a 'Site Administrator'
     Then I can go to the application  Administrator Tool
      And I can deactivate  Jorge Primavera
      And I can activate  Jorge Primavera
      And I can filter the users


*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"

I can deactivate
    [arguments]  ${fullname}
    Wait for injection to be finished
    Click Element  jquery=li:contains(${fullname}) > .functions > a.user-status:contains(Enabled)
    Wait for injection to be finished
    Click Button  Deactivate user

I can activate
    [arguments]  ${fullname}
    Wait for injection to be finished
    Click Element  jquery=li:contains(${fullname}) > .functions > a.user-status:contains(Disabled)
    Wait for injection to be finished
    Click Button  Activate user

I can filter the users
    Wait for injection to be finished
    Input text  jquery=#group-management-group-filter [name=SearchableText]  st
    Wait for injection to be finished
    Page should contain Element  jquery=li:contains('Christian Stoney')
    Page should not contain Element  jquery=li:contains('Dollie Nocera')
    Input text  jquery=#group-management-group-filter [name=SearchableText]  strange
    Wait for injection to be finished
    Page should contain Element  jquery=#directory .notice:contains('No users found')
