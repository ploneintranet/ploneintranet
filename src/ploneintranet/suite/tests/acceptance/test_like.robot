*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

Members can like status updates
   Given I am logged in as the user allan_neece
     and I go to the Open Market Committee Workspace
     and The first status update is not liked
    when I toggle like on the first status update
    then The first status update is liked once

   Given I am logged in as the user jorge_primavera
     and I go to the Open Market Committee Workspace
     and The first status update is liked once
    when I toggle like on the first status update
    then The first status update is liked 2 times

   Given I am logged in as the user dollie_nocera
     and I go to the Open Market Committee Workspace
    when I toggle like on the first status update
    then The first status update is liked 3 times
    when I toggle like on the first status update
    then The first status update is liked 2 times

# TODO:
# Members can like content items
# Members can like discussion items


*** Keywords ***

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
