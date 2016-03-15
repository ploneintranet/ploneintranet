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
   Given I am logged in as the user christian_stoney
     and I go to the Open Market Committee Workspace
     and I can enter the Manage Information Folder
    when I toggle the bulk action controls
    then I can copy the Minutes word document
    when I go to the Open Market Committee Workspace
    when I toggle the bulk action controls
    then I can paste the Minutes word document
    when I go to the Open Market Committee Workspace
    then I can enter the Projection Materials Folder
    when I toggle the bulk action controls
    then I can paste the Minutes word document
    when I go to the Open Market Committee Workspace
    when I toggle the bulk action controls
    then I can delete the Minutes word document
    when I go to the Open Market Committee Workspace
     and I can enter the Projection Materials Folder
    when I toggle the bulk action controls
    then I can cut the Minutes word document
    when I go to the Open Market Committee Workspace
    when I toggle the bulk action controls
    then I can paste the Minutes word document


*** Keywords ***

I toggle the bulk action controls
    # Yes, adding Sleep is very ugly, but I see no other way to ensure that
    # the sidebar and the element we need has really completely loaded
    Sleep  2
    Wait Until Element is Visible  xpath=//div[@id='selector-functions']//a[text()='Select']
    Click link  xpath=//div[@id='selector-functions']//a[text()='Select']
    Wait Until Element is Visible  xpath=//div[@class='batch-functions']//button[text()='Copy']

I can copy the Minutes word document
    Click Element  xpath=//strong[text()="Minutes"]//ancestor::label/input
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Copy']
    Wait Until Page Contains  1 Files were copied to your cloud clipboard.

I can paste the Minutes word document
    Wait Until Element is Visible  xpath=//div[@class='batch-functions']//button[text()='Paste']
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Paste']
    Wait Until Page Contains  Item(s) pasted

I can delete the Minutes word document
    Click Element  xpath=//strong[text()="Minutes"]//ancestor::label/input
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Delete']
    Wait Until Page Contains  I am sure, delete now
    Click button  I am sure, delete now
    Wait Until Page Contains  The following items have been deleted

I can cut the Minutes word document
    Click Element  xpath=//strong[text()="Minutes"]//ancestor::label/input
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Cut']
    Wait Until Page Contains  1 Files were cut and moved to your cloud clipboard.
