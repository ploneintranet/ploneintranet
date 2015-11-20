*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

Allan can view the stream
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    then I can see updates by  Christian Stoney

Allan can filter the stream on only people he is following
    Given I am logged in as the user allan_neece
    when I open the Dashboard
    and I filter the stream as  network
    then I cannot see updates by  Christian Stoney

Allan can filter the stream and switch back to show all again
    Given I am logged in as the user allan_neece
    and I open the Dashboard
    and I filter the stream as  network
    and I cannot see updates by  Christian Stoney
    when I filter the stream as  all
    then I can see updates by  Christian Stoney

*** Keywords ***

I can see updates by
    [arguments]  ${user_fullname}
    Element should be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='post-header']//h4[text()='${user_fullname}']/..

I cannot see updates by
    [arguments]  ${user_fullname}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='post-header']//h4[text()='${user_fullname}']/..

I filter the stream as
    [arguments]  ${stream_filter}
    Click element  xpath=//select[@name='stream_filter']
    Click element  xpath=//select[@name='stream_filter']//option[@value='${stream_filter}']
    Wait until element is visible  xpath=//select[@name='stream_filter']//option[@value='${stream_filter}'][@selected='selected']
