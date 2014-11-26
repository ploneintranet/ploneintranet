*** Settings ***

Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Site Administrator can access sharing tab
    Given I'm logged in as a 'Site Administrator'
     Then I see the Sharing tab

*** Keywords ***

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}
    Go to  ${PLONE_URL}

I open the personal menu
    Click link  css=#user-name

I see the Sharing tab
    Element should be visible  css=li#contentview-local_roles a[href*='@@sharing']
