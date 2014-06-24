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

Site User can join self managed workspace
    Add workspace  Demo Workspace
    Log in as test user
    Go to homepage
    Element should not be visible  xpath=//ul[@id=portal-globalnav]/li/a[text()='Demo Workspace']
    Logout
    Log in as site owner
    Go to homepage
    Navigate to  Demo Workspace
    Click Policies In edit bar
    Select From List  xpath=//select[@name="form.widgets.external_visibility:list"]  open
    Select From List  xpath=//select[@name="form.widgets.join_policy:list"]  self
    Click button  Ok
    Logout
    Log in as test user
    Maneuver to  Demo Workspace
    Click button  Join right here, right now
    Logout
    Log in as site owner
    Go to homepage
    Navigate to  Demo Workspace
    Click Roster In edit bar
    Element should be visible  xpath=//table[@id="edit-roster"]/tbody/tr/td[normalize-space()="test_user_1_"]
