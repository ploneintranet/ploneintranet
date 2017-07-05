*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Anonymous get redirected to login page
    Given I'm logged in as a 'Site Administrator'
          Go to  ${PLONE_URL}/test_injection_on_insufficient_privileges
          Click Link  Test unauthorized pat-inject
          Wait Until Page Contains Element  css=.pat-notification.warning  5


Allan cannot access some apps
    Given I am logged in as the user allan_neece
     Then I can go to the application  App market
      And I see the modal  App not available
      But I cannot go to the application  Administrator Tool

*** Keywords ***

I see the modal
    [arguments]  ${title}
    Page should contain Element  jquery=h1:contains("${title}")
    Click button  jquery=#pat-modal .close-panel
