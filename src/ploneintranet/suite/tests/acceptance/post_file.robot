*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Alice can attach a file to a post
    Given I am logged in as the user alice_lindstrom
      And I open the Dashboard
      And I see the Dashboard
      And I create a new post
      And I add a file
      And I can see a preview


*** Keywords ***

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I see the Dashboard
    Element should be visible  css=#portlet-news

I create a new post
    Input Text      css=#microblog textarea  Look at this new doc

I add a file

    Choose file     css=#microblog input[name='form.widgets.attachments']    ${UPLOADS}/basic.txt

I can see a preview
    Wait Until Element Is visible   css=#microblog #post-box-attachment-previews img    timeout=60

