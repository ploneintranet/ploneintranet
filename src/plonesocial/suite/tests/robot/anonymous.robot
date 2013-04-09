*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
#Library   Dialogs

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***
Home view
    [Tags]  anon  home
    Go to homepage
    Page should contain  Powered by Plon
    Element should not be visible  id=plonesocialsuite-navigation
    Element should be visible  id=portaltab-f1
    Element should be visible  css=.activityItem.content
    Page should contain link  link=Test Document 1
    Click link   link=Test Document 1
    Element should be visible  css=div.reply form input.standalone
    Click button  css=div.reply form input.standalone
    Page should contain  Forgot your password?
#    Pause execution

      

