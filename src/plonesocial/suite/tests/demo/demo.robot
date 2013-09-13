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
    Maximize browser window    
    Demo anon home    
    Demo clare login
    Demo clare home
    Demo statusupdate    
    Demo profile
    Demo stream network
    Demo stream explore
    Demo stream tag    
    Demo workspace allowed home
    Demo workspace allowed stream
    Demo workspace allowed folder
    Demo workspace allowed local stream
    Demo workspace allowed tag
    Log out and log in as Kurt
    Demo workspace no access home
    Demo workspace no access stream
    Demo workspace no access tag

DemoAnonHome
    [Tags]  demo macro anonhome
    Demo anon home

DemoClareLogin
    [Tags]  demo macro clarelogin
    Demo clare login

DemoClareHome
    [Tags]  demo macro clarehome
    Login Clare
    Demo clare home

DemoStatusUpdate
    [Tags]  demo macro statusupdate
    Login Clare
    Go to  ${PLONE_URL}/@@stream
    Demo statusupdate

DemoProfile
    [Tags]  demo macro demoprofile
    Login Clare
    Demo profile

DemoStreamNetwork
    [Tags]  demo macro streamnetwork
    Login Clare
    Demo stream network

DemoStreamExplore
    [Tags]  demo macro streamexplore
    Login Clare
    Demo stream explore    

DemoStreamTag
    [Tags]  demo macro streamtag
    Login Clare
    Demo stream tag

## Clare has workspace access
    
DemoWorkspaceAllowedHome
    [Tags]  demo macro allowedhome
    Login Clare
    Demo workspace allowed home

DemoWorkspaceAllowedStream
    [Tags]  demo macro allowedstream
    Login Clare
    Demo workspace allowed stream

DemoWorkspaceAllowedFolder
    [Tags]  demo macro allowedfolder
    Login Clare
    Demo workspace allowed folder

DemoWorkspaceAllowedLocalStream
    [Tags]  demo macro allowedlocal
    Login Clare
    Demo workspace allowed local stream

DemoWorkspaceAllowedTag
    [Tags]  demo macro allowedtag
    Login Clare
    Demo workspace allowed tag

## Kurt has no workspace access

DemoLogOutAndLogInAsKurt
    [Tags]  demo macro logoutlogin
    Demo clare login
    Log out and log in as Kurt
        
DemoWorkspaceNoaccessHome
    [Tags]  demo macro nohome
    Login Kurt
    Demo workspace no access home

DemoWorkspaceNoaccessStream
    [Tags]  demo macro nostream
    Login Kurt
    Demo workspace no access stream

DemoWorkspaceNoaccessTag
    [Tags]  demo macro notag
    Login Kurt
    Demo workspace no access tag



*** Keywords ***

Demo anon home
    Go to homepage
    ${note} =  Add styled note  content  Not logged in so we cannot see the microblog. We do see content creation.  position=right
    Sleep  2 seconds
    Remove elements  ${note}

Demo clare login
    Set Selenium Speed  0.25 seconds
    Log in   clare_presler  secret
    ${note} =  Add styled note  content  Now logged in as Clare.  position=top
    Sleep  2 seconds
    Remove elements  ${note}

Log out and log in as Kurt
    Set Selenium Speed  0.25 seconds
    ${note} =  Add styled note  content  Clare is logging out.  position=top
    Sleep  1 seconds        
    Log out
    ${note} =  Add styled note  content  We'll log in as Kurt.  position=top
    Sleep  1 seconds    
    Log in  kurt_silvio  secret
    ${note} =  Add styled note  content  Now logged in as Kurt.  position=top
    Sleep  2 seconds
    Remove elements  ${note}

Demo clare home
    Go to homepage   
    Sleep  2 seconds

Demo statusupdate
    Set Selenium Speed  0.25 seconds
    ${dot} =  Add styled dot  microblog  +
    ${note} =  Add styled note  microblog  Share status updates  position=right
    Remove elements  ${dot}  ${note}
    Input Text  css=textarea  This is a microblog status update. With a #demo hashtag
    Set Selenium Speed  0.5 seconds            
    Add pointer  form-buttons-statusupdate    
    Click Button  id=form-buttons-statusupdate
    Set Selenium Speed  0.25 seconds    
    ${dot} =  Add styled dot  css=.activityItem  +
    ${note} =  Add styled note  css=.activityItem  The new status update shows up.
    Remove elements  ${dot}  ${note}

Demo profile
    Go to  ${PLONE_URL}/@@profile
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}
    

Demo stream explore
    Go to  ${PLONE_URL}/@@stream        
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo stream network
    Go to  ${PLONE_URL}/@@stream/network
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo stream tag
    Go to  ${PLONE_URL}/@@stream            
    Click Link  \#demo
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace allowed home
    Go to  ${PLONE_URL}
    Page should contain link  Secure Workspace
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace allowed stream
    Go to  ${PLONE_URL}/@@stream
    Page should contain  local microblogs and activitystreams
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace allowed folder
    Go to  ${PLONE_URL}/workspace
    Page should contain link  Secure Workspace updates
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace allowed local stream
    Go to  ${PLONE_URL}/workspace/@@stream
    Page should contain  local microblogs and activitystreams    
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should contain  local microblogs and activitystreams    
    Page should contain  Dollie Nocera
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace allowed tag
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should contain  local microblogs and activitystreams    
    Page should contain  Dollie Nocera
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace no access home
    Go to  ${PLONE_URL}
    Page should not contain  Secure Workspace
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace no access stream
    Go to  ${PLONE_URL}/@@stream
    Page should not contain  local microblogs and activitystreams    
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}

Demo workspace no access tag
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should not contain  Dollie Nocera    
    Page should not contain  local microblogs and activitystreams    
    Page should not contain  Secure Workspace
    ${note} =  Add styled note  content  TODO
    Sleep  1 seconds
    Remove elements  ${note}


    
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
    Update element style  ${note}  font-size  24px
    Update element style  ${note}  line-height  36px    
    Update element style  ${note}  opacity  0
    Update element style  ${note}  display  block
    Update element style  ${note}  -moz-transition  opacity 1s
    Update element style  ${note}  opacity  1
    Sleep  2s
    [return]  ${note}

Login Clare
    Enable autologin as  Member
    Set autologin username  clare_presler
    Maximize browser window
    Set Selenium Speed  0.5 seconds            

Login Kurt
    Enable autologin as  Member
    Set autologin username  kurt_silvio
    Maximize browser window
    Set Selenium Speed  0.5 seconds            


