*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers


*** Test Cases ***

Content Editors can copy and paste content
   Given I am logged in as the user allan_neece
     and I go to the Open Market Committee Workspace
     and I can enter the Manage Information Folder
    when I toggle the bulk action controls
    then I can copy the Minutes word document
    then I go to the Open Market Committee Workspace
    when I toggle the bulk action controls
    then I can paste the Minutes word document


*** Keywords ***

I toggle the bulk action controls
    Click Element  css=a.pat-toggle.toggle-select
    Wait Until Page Contains Element  xpath=//div[@class='batch-functions']//button[@value='copy']

I can copy the Minutes word document
    Click Element  xpath=(//input[@id='cart-minutes'])
    Click Element  xpath=//div[@class='batch-functions']//button[@value='copy']
    Wait Until Page Contains  1 item(s) copied

I can paste the Minutes word document
    Click Element  xpath=//div[@class='batch-functions']//button[@value='paste']
    Wait Until Page Contains  Item(s) pasted

