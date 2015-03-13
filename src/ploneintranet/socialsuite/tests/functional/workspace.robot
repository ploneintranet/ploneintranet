*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
#Library   Dialogs
Library   Remote  ${PLONE_URL}/RobotRemote

Test Setup     Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***

## Clare has access
    
WorkspaceAllowedHome
    [Tags]  workspace clare home
    Log in as Clare
    Go to  ${PLONE_URL}
    Page should contain link  Secure Workspace

WorkspaceAllowedStream
    [Tags]  workspace clare stream
    Log in as Clare
    Go to  ${PLONE_URL}/@@stream
    Page should contain  local microblogs and activitystreams

WorkspaceAllowedFolder
    [Tags]  workspace clare folder
    Log in as Clare
    Go to  ${PLONE_URL}/workspace
    Page should contain link  Secure Workspace updates

WorkspaceAllowedLocalStream
    [Tags]  workspace clare local
    Log in as Clare
    Go to  ${PLONE_URL}/workspace/@@stream
    Page should contain  local microblogs and activitystreams    
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should contain  local microblogs and activitystreams    
    Page should contain  Dollie Nocera

WorkspaceAllowedTag
    [Tags]  workspace clare tag
    Log in as Clare
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should contain  local microblogs and activitystreams    
    Page should contain  Dollie Nocera


## Kurt has no access
    
WorkspaceNoaccessHome
    [Tags]  workspace kurt home
    Log in as Kurt
    Go to  ${PLONE_URL}
    Page should not contain  Secure Workspace

WorkspaceNoaccessStream
    [Tags]  workspace kurt stream
    Log in as Kurt
    Go to  ${PLONE_URL}/@@stream
    Page should not contain  local microblogs and activitystreams    

WorkspaceNoaccessTag
    [Tags]  workspace kurt tag
    Log in as Kurt
    Go to  ${PLONE_URL}/@@stream/tag/girlspace
    Page should not contain  Dollie Nocera    
    Page should not contain  local microblogs and activitystreams    
    Page should not contain  Secure Workspace



*** Keywords ***
Log in as Clare
    Enable autologin as  Member
    Set autologin username  clare_presler

Log in as Kurt
    Enable autologin as  Member
    Set autologin username  kurt_silvio



      

