*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Manager can post a status update
    Given I'm logged in as a 'Manager'
    and I open the Dashboard
    then I can post a status update  I am so excited, this is süper!

*** Keywords ***

I can post a status update
    [arguments]  ${message}
    Wait Until Element Is visible  css=textarea.pat-comment-box
    Element should not be visible  css=button[name='form.buttons.statusupdate']
    Click element  css=textarea.pat-comment-box
    Wait Until Element Is visible  css=button[name='form.buttons.statusupdate']
    Input Text  css=textarea.pat-comment-box  ${message}
    Click button  css=button[name='form.buttons.statusupdate']
    Wait Until Element Is visible  xpath=//div[@class='post status item']/section[@class='post-content' and contains(text(), '${message}')]

