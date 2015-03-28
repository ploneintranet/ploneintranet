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
     When I create a new post
      And I add a file
     Then I can see the file preview in the post box

Alice can submit a post with a file attachment
    Given I am logged in as the user alice_lindstrom
      And I open the Dashboard
     When I create a new post
      And I add a file
      And I can see the file preview in the post box
      And I submit the new post
     Then I can see the file preview in the stream
      And I can open the file from the stream preview


*** Keywords ***

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I create a new post
    Input Text      css=#microblog textarea  Look at this new doc

I add a file
    Click Element   css=#microblog input[name='form.widgets.attachments']
    Choose File     css=#microblog input[name='form.widgets.attachments']    ${UPLOADS}/basic.txt

I can see the file preview in the post box
    Wait Until Element Is visible   css=#microblog #post-box-attachment-previews img    timeout=60

I submit the new post
    Click Element  css=button[name='form.buttons.statusupdate']

I can see the file preview in the stream
    Wait Until Element Is visible   css=#activity-stream .preview img[src$='/basic.txt/thumb']

I can open the file from the stream preview
   Wait Until Element Is visible   css=#activity-stream .preview a[href$='/basic.txt']
   Click Link  css=#activity-stream .preview a[href$='/basic.txt']
   Wait until page contains  Proin at congue nisl