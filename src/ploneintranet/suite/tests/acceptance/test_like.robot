*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Members can like status updates
    Given I'm logged in as a 'Member'
    when I go to the Open Market Committee Workspace
    then The first status update is not liked
    when I toggle like on the first status update
    then The first status update is liked once

    Given I'm logged in as a 'alice_lindstrom'
    when I go to the Open Market Committee Workspace
    then The first status update is liked once
    when I toggle like on the first status update
    then The first status update is liked 2 times

    Given I'm logged in as a 'allan_neece'
    when I go to the Open Market Committee Workspace
    when I toggle like on the first status update
    then The first status update is liked 3 times
    when I toggle like on the first status update
    then The first status update is liked 2 times

# TODO:
# Members can like content items
# Members can like discussion items


*** Keywords ***

I go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Open Market Committee

I toggle like on the first status update
    Click element  xpath=//button[contains(@class, 'like')][1]

The first status update is not liked
    Element should be visible  xpath=//button[@class='like'][1]//sup[@class='counter' and contains(text(), '(0)')]

The first status update is liked once
    Element should be visible  xpath=//button[contains(@class, 'like')][1]//sup[@class='counter' and contains(text(), '(1)')]

The first status update is liked 2 times
    Element should be visible  xpath=//button[contains(@class, 'like')][1]//sup[@class='counter' and contains(text(), '(2)')]

The first status update is liked 3 times
    Element should be visible  xpath=//button[contains(@class, 'like')][1]//sup[@class='counter' and contains(text(), '(3)')]
