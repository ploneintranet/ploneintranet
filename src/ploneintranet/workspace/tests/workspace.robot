*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

#Site Administrator can create example user
#    Log in as site owner
#    Add content User 'Example User'


#Site Administrator can create workspace
#    Log in as site owner
#    Go to homepage
#    Add content item  Workspace  Example Workspace

Site Administrator can add example user as member of workspace
    Log in as site owner
    Go to homepage
    Add content item  Workspace  Example Workspace
    Navigate to  Example Workspace
    Click Roster In edit bar
    Click link  + Add person to roster
    Input text  form.widgets.user.widgets.query  'Example User'

Site Administrator can modify policies
    Log in as site owner
    Go to homepage
    Add content item  Workspace  Example Workspace
    Navigate to  Example Workspace
    Pause
    Click Policies In edit bar
    #Select From List  xpath=//select[@name="form.widgets.external_visibility:list"]  private
    #Submit Form  xpath=//#form
    #Click link  + Add person to roster
    #Input text  form.widgets.user.widgets.query  'Example User'

#Example User can access workspace
#    Log in as test user
#	Navigate to 'Example Workspace'
#    Page should contain element css=#contentview-view

