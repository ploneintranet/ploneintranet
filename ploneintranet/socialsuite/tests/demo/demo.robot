*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/annotate.robot
Resource  plone/app/robotframework/speak.robot
Library   Remote  ${PLONE_URL}/RobotRemote
Library   Dialogs

Test Setup     Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***
    
FullDemo
    [Tags]  demo fulldemo
    Set Selenium Speed  0.1 seconds
    Maximize browser window    
    Show note  This is a scripted demo video, using the Robot Framework.
    
    Demo anon home    
    Demo clare login
    Demo clare home
    Demo statusupdate    

    Demo stream explore
    Demo stream network empty
    Demo profile
    Demo follow    
    Demo stream network activated
    Demo stream tag    

    Demo workspace allowed
    Log out and log in as Kurt
    Demo workspace disallowed

    Go to homepage    
    Show note  This concludes the demo.
    Sleep  5 seconds

DevDemo
    [Tags]  demo devdemo    
    Login Clare
    Go to  ${PLONE_URL}/@@profile
#    Show note  Clare checks out her followers
    Click link  css=.followers a    
#    Click link explicitly  css=.followers a
#    Show h2 note  Follow some of these fans back        
#    Show dot  css=input[name=subunsub_follow]
    Click Button  name=subunsub_follow
#    Show dot  css=input[name=subunsub_follow]    
#    Click Button  name=subunsub_follow
#    Sleep  1 seconds    
    

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

DemoStreamNetworkEmpty
    [Tags]  demo macro streamnetworkempty
    Login Clare
    Demo stream network empty
    
DemoStreamNetworkActivated
    [Tags]  demo macro streamnetworkactivated
    Login Clare
    Go to  ${PLONE_URL}/@@profile        
    Demo follow
    Demo stream network activated

DemoStreamExplore
    [Tags]  demo macro streamexplore
    Login Clare
    Demo stream explore    

DemoStreamTag
    [Tags]  demo macro streamtag
    Login Clare
    Demo stream tag

DemoFollow
    [Tags]  demo macro demofollow
    Login Clare
    Go to  ${PLONE_URL}/@@profile
    Demo follow

## Clare has workspace access
    
DemoWorkspaceAllowed
    [Tags]  demo macro allowedhome
    Login Clare
    Demo workspace allowed

## Kurt has no workspace access

DemoLogOutAndLogInAsKurt
    [Tags]  demo macro logoutlogin
    Demo clare login
    Log out and log in as Kurt
        
DemoWorkspaceDisallowed
    [Tags]  demo macro nohome
    Login Kurt
    Demo workspace disallowed

*** Keywords ***

Demo anon home
    Go to homepage
    Show note  Not logged in so we cannot see the microblog. We do see content creation.

Demo clare login
    Set Selenium Speed  0.25 seconds
    Log in explicitly  clare_presler

Log out and log in as Kurt
    Set Selenium Speed  0.25 seconds
    Show note  Verify the security system by logging in as another user.
    Log out explicitly
    Log in explicitly  kurt_silvio

Demo clare home
    Go to homepage   
    Sleep  2 seconds

Demo statusupdate
    Set Selenium Speed  0.25 seconds
    Show note  Share status updates    
    Show dot  microblog
    Set Selenium Speed  1 seconds    
    Input Text  css=textarea  This is a microblog status update. With a #demo hashtag
    Add pointer  form-buttons-statusupdate    
    Set Selenium Speed  0.25 seconds    
    Click Button  id=form-buttons-statusupdate
    Sleep  1 seconds
    Show dot  css=.activityItem
    ${note} =  Add styled note  css=.activityItem  The new status update shows up.
    Sleep  2 seconds
    Remove elements  ${note}

Demo stream explore
    Click link explicitly  css=.explore a    
    Show note  "Explore" shows all updates from everybody.

Demo stream network empty
    Click link explicitly  css=.stream a
    Show note  Clare is not following anybody yet, so "My Network" shows only her own updates.

Demo stream network activated
    Click link explicitly  css=.stream a
    Show note  "My network" now shows updates from Clare's network.

Demo profile
    Click link explicitly  css=.profile a
    Show note  "Profile" pages show activity of a user.    

Demo follow
    Show note  Clare checks out her followers
    Click link explicitly  css=.followers a
    Show h2 note  Follow some of these fans back        
    Show dot  css=input[name=subunsub_follow]
    Click Button  name=subunsub_follow
    Show dot  css=input[name=subunsub_follow]    
    Click Button  name=subunsub_follow
    Sleep  1 seconds    

Demo stream tag
    Click link explicitly  css=.explore a    
    Show note  Hashtags are hyperlinked
    Click Link explicitly  css=.tag-demo
    Show note  This shows all updates tagged "demo"


Demo workspace allowed
    Go to  ${PLONE_URL}
    Page should contain link  Secure Workspace
    Show note  Clare has access to a secure workspace
    Click link explicitly  css=a[href='${PLONE_URL}/workspace']
    Sleep  1 seconds
    Click link explicitly  css=a[href='${PLONE_URL}/workspace/@@sharing']
    Show note  Only some users are allowed here
    Click link explicitly  css=a[href='${PLONE_URL}/workspace/@@stream']
    Show note  The workspace has its own protected activity stream
    Click Link explicitly  css=.tag-girlspace
    Show note  Workspace updates are integrated into the sitewide activity stream and tag views.

Demo workspace disallowed
    Show note  Kurt doesn't even see the Secure Workspace, because he doesn't have access.
    Go to  ${PLONE_URL}/@@stream/tag/girlspace        
    Show h2 note  Kurt can't see any "#girlspace" items because he cannot access the Secure Workspace.


    
Add styled dot
    [Arguments]  ${locator}  ${number}
    ${dot} =  Add dot  ${locator}  ${number}  display=none
    ...  background=\#8c6cd0  color=\#fecb00    
    Update element style  ${dot}  font-family  Arial, Verdana, Sans-serif
    Update element style  ${dot}  -moz-transform  scale(4)
    Update element style  ${dot}  display  block
    Update element style  ${dot}  -moz-transition  all 1s
    Update element style  ${dot}  -moz-transform  scale(1)
    [return]  ${dot}

Show dot
    [Arguments]  ${locator}
    ${dot} =  Add styled dot  ${locator}  +
    Sleep  1 seconds
    Remove elements  ${dot}    

Show pointer
    [Arguments]  ${locator}
    ${id} =  Add pointer  ${locator}
    Update element style  ${id}  opacity  0.6        
    Update element style  ${id}  background  \#8c6cd0
    Update element style  ${id}  color  \#fecb00

Show note
    [Arguments]  ${message}
    ${note} =  Add styled note  content  ${message}  position=top
    Sleep  4 seconds
    Remove elements  ${note}   
    Sleep  1 seconds 

Show h2 note
    [Arguments]  ${message}
    ${note} =  Add styled note  css=\#content h2  ${message}  position=top
    Sleep  4 seconds
    Remove elements  ${note}   
    Sleep  1 seconds 
    
Add styled note
    [Arguments]  ${locator}  ${message}  ${position}=${EMPTY}
    ${note} =  Add note  ${locator}  ${message}
    ...  width=400  background=\#8c6cd0  color=\#fecb00
    ...  display=none  position=${position}
    Update element style  ${note}  font-family  Arial, Verdana, Sans-serif    
    Update element style  ${note}  font-size  24px
    Update element style  ${note}  line-height  36px    
    Update element style  ${note}  opacity  0
    Update element style  ${note}  display  block
    Update element style  ${note}  -moz-transition  opacity 1s
    Update element style  ${note}  opacity  1
    [return]  ${note}

Login Clare
    Enable autologin as  Member
    Set autologin username  clare_presler
    Maximize browser window
    Go to homepage       
    Set Selenium Speed  0.1 seconds            

Login Kurt
    Enable autologin as  Member
    Set autologin username  kurt_silvio
    Go to homepage       
    Maximize browser window
    Set Selenium Speed  0.1 seconds            

Log in explicitly
    [Arguments]  ${user}
    Show note  Log in as ${user}    
    Show pointer  personaltools-login
    Log in  ${user}  secret
    Show note  Now logged in as ${user}    
    Click Link explicitly  css=#content-core a    
    
Log out explicitly
    Show note  Log out
    Click Link explicitly  css=#secondary-nav a.dropdown-toggle
    Click Link explicitly  css=#personaltools-logout a
    Sleep  1 seconds
    
Click Link explicitly
    [Arguments]  ${locator}
    Show dot  ${locator}    
    Sleep  1 seconds    
    Click Link  ${locator}

    