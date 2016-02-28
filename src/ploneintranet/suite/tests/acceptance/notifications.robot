*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

Alice is notified about a post she is in
    Given I am logged in as the user guy_hackey
    When I open the Dashboard
    And I write a status update  Hello to you
    Then I can mention the user  Alice Lindström
    And I submit the status update
    Then I am logged in as the user alice_lindstrom
    And I can click the notifications toolbar
    And I can follow the notifications link
    And I can see the notification from Guy Hackey saying Hello to you


*** Keywords ***

I can click the notifications toolbar
    Click Link  css=header a#notification-link
    Wait until Page contains Element  css=ul.notifications

I can follow the notifications link
    Click Link  css=p.all-notifications a

I can see the notification from ${USER} saying ${TEXT}
    Page should contain  ${USER}
    Page should contain  ${TEXT}
