*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variable ***

${MESSAGE}    I am so excited, this is süper!


*** Test Cases ***

Manager can post a status update
    Given I'm logged in as a 'Manager'
    when I open the Dashboard
    and I post a status update    ${MESSAGE}
    then The message is visible as top element    ${MESSAGE}
    and The status update only appears once

*** Keywords ***

I post a status update
    [arguments]  ${message}
    Wait Until Element Is visible  css=textarea.pat-comment-box
    Element should not be visible  css=button[name='form.buttons.statusupdate']
    Click element  css=textarea.pat-comment-box
    Wait Until Element Is visible  css=button[name='form.buttons.statusupdate']
    Input Text  css=textarea.pat-comment-box  ${message}
    Click button  css=button[name='form.buttons.statusupdate']


The message is visible as top element
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']/div[@class='post status item']/section[@class='post-content' and contains(text(), '${message}')][1]

The status update only appears once
    Element should be visible  xpath=//div[@id='activity-stream']/div[@class='post status item'][1]
    Element should not be visible  xpath=//div[@id='activity-stream']/div[@class='post status item'][2]