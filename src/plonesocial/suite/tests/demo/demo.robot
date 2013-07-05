*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/annotate.robot
Resource  plone/app/robotframework/speak.robot
Library   Remote  ${PLONE_URL}/RobotRemote
#Library   Dialogs

Test Setup     Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***
    
FullDemo
    [Tags]  demo fulldemo
    Set Selenium Speed  0.5 seconds            

    Demo anon home    
    Demo clare login
    Demo clare home
    Demo statusupdate    
    Demo profile
    Demo stream network
    Demo stream explore

DemoAnonHome
    [Tags]  demo macro    
    Demo anon home

DemoClareLogin
    [Tags]  demo macro    
    Demo clare login

DemoClareHome
    [Tags]  demo macro    
    Login Clare
    Demo clare home

DemoStatusUpdate
    [Tags]  demo macro    
    Login Clare
    Go to  ${PLONE_URL}/@@stream    
    Demo statusupdate

DemoProfile
    [Tags]  demo macro    
    Login Clare
    Demo profile

DemoStreamExplore
    [Tags]  demo macro    
    Login Clare
    Demo stream explore
    
DemoStreamNetwork
    [Tags]  demo macro    
    Login Clare
    Demo stream network

DemoStreamTag
    [Tags]  demo macro    
    Login Clare
    Demo stream tag




*** Keywords ***

Demo anon home
    Go to homepage
    ${note} =  Add styled note  content  Not logged in so we cannot see the microblog. We do see content creation.  position=right
    Sleep  2 seconds
    Remove elements  ${note}

Demo clare login
    Set Selenium Speed  0.1 seconds                
    Log in   clare_presler  secret
    ${note} =  Add styled note  content  Now logged in as Clare.  position=top
    Sleep  2 seconds
    Remove elements  ${note}

Demo clare home
    Go to homepage   
    Sleep  2 seconds

Demo statusupdate
    Set Selenium Speed  0.25 seconds            
    ${dot} =  Add styled dot  microblog  +
    ${note} =  Add styled note  microblog  Share status updates  position=righ
    Remove elements  ${dot}  ${note}
    Input Text  css=textarea  This is a microblog status update. With a #demo hashtag
    Set Selenium Speed  0.5 seconds            
    Add pointer  form-buttons-statusupdate    
    Click Button  id=form-buttons-statusupdate
    ${dot} =  Add styled dot  css=.activityItem  +
    ${note} =  Add styled note  css=.activityItem  The new status update shows up.
    Remove elements  ${dot}  ${note}

Demo profile
    Go to  ${PLONE_URL}/@@profile    

Demo stream explore
    Go to  ${PLONE_URL}/@@stream        

Demo stream network
    Go to  ${PLONE_URL}/@@stream/network

Demo stream tag
    Go to  ${PLONE_URL}/@@stream            
    Click Link  \#demo
    
Add styled dot
    [Arguments]  ${locator}  ${number}
    ${dot} =  Add dot  ${locator}  ${number}  display=none
    ...  background=\#8c6cd0  color=\#fecb00    
    Update element style  ${dot}  font-family  Arial, Verdana, Sans-serif
    Update element style  ${dot}  -moz-transform  scale(4)
    Update element style  ${dot}  display  block
    Update element style  ${dot}  -moz-transition  all 1s
    Update element style  ${dot}  -moz-transform  scale(1)
    Sleep  1s
    [return]  ${dot}
    
Add styled note
    [Arguments]  ${locator}  ${message}  ${position}=${EMPTY}
    ${note} =  Add note  ${locator}  ${message}
    ...  width=200  background=\#8c6cd0  color=\#fecb00
    ...  display=none  position=${position}
    Update element style  ${note}  font-family  Arial, Verdana, Sans-serif    
    Update element style  ${note}  opacity  0
    Update element style  ${note}  display  block
    Update element style  ${note}  -moz-transition  opacity 1s
    Update element style  ${note}  opacity  1
    Sleep  2s
    [return]  ${note}

Login Clare
    Enable autologin as  Member
    Set autologin username  clare_presler
    Set Selenium Speed  0.5 seconds            
      

