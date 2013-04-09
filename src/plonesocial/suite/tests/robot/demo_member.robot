*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
#Library   Dialogs
Library   Remote  ${PLONE_URL}/RobotRemote

Test Setup     Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***
Demo
    [Tags]  demo
    Log in as member
    Set Selenium Speed  1.5 seconds
    Go to  ${PLONE_URL}    
    Input Text  css=textarea  This is a microblog status update. With a #demo hashtag.
    Click Button  id=form-buttons-statusupdate
    Click Element  xpath=//a[@href="@@stream/tag/demo"]    
    Go to  ${PLONE_URL}/@@profile    
    Go to  ${PLONE_URL}/@@stream    
    Go to  ${PLONE_URL}/@@stream/explore
    Sleep  3s


*** Keywords ***
Log in as member
    Enable autologin as  Member
    Set autologin username  clare_presler



      

