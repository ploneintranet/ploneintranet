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


Homepage
    [Tags]  member  home
    Log in as member
    Go to  ${PLONE_URL}    
    Element should be visible  id=plonesocialsuite-navigation
    Element should be visible  id=microblog
    Element should be visible  css=div.activityItem.status
    Input Text  css=textarea  This is a microblog status update. With a #demo hashtag.
    Click Button  id=form-buttons-statusupdate
    Element should be visible  xpath=//a[@href="@@stream/tag/demo"]

Tag
    [Tags]  member  tag
    Log in as member
    Go to  ${PLONE_URL}/@@stream/tag/demo
    Element Should Contain  css=h2  Updates tagged #demo
    Page Should Contain  kurt_silvio    

Profile
    [Tags]  member  profile
    Log in as member
    Go to  ${PLONE_URL}/@@profile
    Element Should Contain  css=div.description  Status updates by Clare Presler:
    Page Should Not Contain  kurt_silvio    

My Network Empty
    [Tags]  member  mynetwork
    Log in as member
    Go to  ${PLONE_URL}/@@stream    
    Page Should Not Contain  kurt_silvio    

Explore
    [Tags]  member  explore
    Log in as member
    Go to  ${PLONE_URL}/@@stream/explore
    Page Should Contain  kurt_silvio        

FollowUnfollow
    [Tags]  member  follow
    Log in as member
    Go to  ${PLONE_URL}/author/kurt_silvio
    Sleep  3s



*** Keywords ***
Log in as member
    Enable autologin as  Member
    Set autologin username  clare_presler



      

