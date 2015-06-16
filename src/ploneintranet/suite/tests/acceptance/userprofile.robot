*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can view her own profile
    Given I am logged in as the user alice_lindstrom
    Then I can open the personal tools menu
    And I can follow the link to my profile

Allan can view Alice's profile
    Given I am logged in as the user allan_neece
    Then I can view the profile for user alice_lindstrom
    And I can see details for Alice Lindström

*** Keywords ***

I can open the personal tools menu
    Click Element  css=header #user-avatar
    Wait Until Element Is Visible  css=.tooltip-container #portal-personaltools a#user-name

I can follow the link to my profile
    Click Element  css=.tooltip-container #portal-personaltools a#user-name

I can view the profile for user ${USERID}
    Go To  ${PLONE_URL}/profiles/${USERID}

I can see details for ${NAME}
    Page should contain  ${NAME}
