*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Site Administrator can add example user as member of workspace
    Log in as site owner
    Go to homepage
    Add content item  Workspace  Example Workspace
    Navigate to  Example Workspace
    Click Roster In edit bar
    Input text  edit-roster-user-search  Example User
    Click button  Search users

Site Administrator can modify policies
    Log in as site owner
    Go to homepage
    Add content item  Workspace  Example Workspace
    Navigate to  Example Workspace
    Click Policies In edit bar
    Select From List  xpath=//select[@name="form.widgets.external_visibility:list"]  private
    Click button  Ok

Site Administrator can edit roster
    Log in as site owner
    Go to homepage
    Add content item  Workspace  Example Workspace
    Navigate to  Example Workspace
    Click Roster In edit bar
    Input text  edit-roster-user-search  test
    Click button  Search users
    Click button  Save

