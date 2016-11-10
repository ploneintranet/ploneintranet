*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Variable ***

${ID1}    fusce-fames


*** Test Cases ***

Magazine portal tab should be visible
    I browse to the news magazine

Magazine shows sections and news items
    Given I browse to the news magazine
    I can see the section navigation  Company News
    I can see the newsfeed item  ${ID1}

Publisher app should be visible
    I browse to the news publisher

Publisher shows sidebar and newsfeed
    Given I browse to the news publisher
    I can see the sidebar item  ${ID1}
    I can see the newsfeed item  ${ID1}


*** Keywords ***

I browse to the news magazine
    I am logged in as the user alice_lindstrom
    Go To  ${PLONE_URL}
    Click Link  News

I browse to the news publisher
    I am logged in as the user alice_lindstrom
    Go To  ${PLONE_URL}
    Click Link  Apps
    Click Element  css=div.app-news a

I can see the section navigation
    [arguments]  ${title}
    Page should contain element  xpath=//nav[@class='canvas-subnav']/a[contains(text(), '${title}')]
    
I can see the newsfeed item
    [arguments]  ${id}
    Page should contain element  xpath=//div[@class='news-feed']//a[contains(@href, '${id}')]

I can see the sidebar item
    [arguments]  ${id}
    Page should contain element  xpath=//div[@id='sidebar-content']//a[contains(@href, '${id}')]