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
    # injection
     Then I can see the file preview in the stream
      And I can open the file from the stream preview
    # reload to verify
     When I open the Dashboard
     Then I can see the file preview in the stream
      And I can open the file from the stream preview

Alice can submit a post with a UTF-8 file attachment
    Given I am logged in as the user alice_lindstrom
      And I open the Dashboard
     When I create a new post
      And I add a UTF-8 file
      And I can see the UTF-8 file preview in the post box
      And I submit the new post
    # Injection barfs UTF-8 but only in the testrunner (works fine in real site). Skip.
    # Actual page load works fine
     When I open the Dashboard
     Then I can see the UTF-8 file preview in the stream
      And I can open the UTF-8 file from the stream preview

Alice can submit a post with a file attachment and no text
    Given I am logged in as the user alice_lindstrom
      And I open the Dashboard
     When I add a file
      And I can see the file preview in the post box
      And I submit the new post
    # test injection working
     Then I can see the file preview in the stream


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

I add a UTF-8 file
    Click Element   css=#microblog input[name='form.widgets.attachments']
    Choose File     css=#microblog input[name='form.widgets.attachments']    ${UPLOADS}/bärtige_flößer.odt

I can see the UTF-8 file preview in the post box
    Wait Until Element Is visible   css=#microblog #post-box-attachment-previews img    timeout=60

I can see the UTF-8 file preview in the stream
    Wait Until Element Is visible   css=#activity-stream .preview img[src$='/bärtige_flößer.odt/thumb']

I can open the UTF-8 file from the stream preview
   Wait Until Element Is visible   css=#activity-stream .preview a[href$='/bärtige_flößer.odt']
   # clicking the link downloads the .odt rather than rendering it in-browser. Skip.
