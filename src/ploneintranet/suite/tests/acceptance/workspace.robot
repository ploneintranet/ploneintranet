*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

# I outcomment these tests as they were written for barceloneta.
# We need to
#  a) Rewrite them for ploneintranet.theme and
#  b) Move them to ploneintranet.suite so that we can test
#     for all integrated packages.
# We don't delete them yet so that we have a reference
# [pilz]

Site Administrator can add example user as member of workspace
    Given I'm logged in as a 'Site Administrator'
     Add workspace  Example Workspace
     Maneuver to  Example Workspace
     Click Link  jquery=a:contains('View full Roster')
     Input text  edit-roster-user-search  Example User
     Click button  Search users

# Site Administrator can modify policies
#     Log in as site owner
#     Add workspace  Policy Workspace
#     Maneuver to  Policy Workspace
#     ${url}    Get Location
#     Go to  ${url}/policies
#     Select From List  jquery=select[name="form.widgets.external_visibility:list"]  private
#     Click button  Ok

# Site Administrator can edit roster
#     Log in as site owner
#     Add workspace  Example Workspace
#     Maneuver to  Example Workspace
#     Click Link  jquery=a:contains('View full Roster')
#     Input text  edit-roster-user-search  test
#     Click button  Search users
#     Click button  Save

# Site User can join self managed workspace
#     Log in as site owner
#     Add workspace  Demo Workspace
#     Logout
#     Go to homepage
#     Element should not be visible  jquery=a:contains('Demo Workspace')
#     Log in as site owner
#     Maneuver to  Demo Workspace
#     ${url}  Get Location
#     Go to  ${url}/policies
#     Select From List  xpath=//select[@name="form.widgets.external_visibility:list"]  open
#     Select From List  xpath=//select[@name="form.widgets.join_policy:list"]  self
#     Click button  Ok
#     Logout
#     Log in as test user
#     Maneuver to  Demo Workspace
#     Click button  Join now
#     Logout
#     Log in as site owner
#     Go to homepage
#     Maneuver to  Demo Workspace
#     Click Link  jquery=a:contains('View full Roster')
#     Element should be visible  xpath=//table[@id="edit-roster"]/tbody/tr/td[normalize-space()="test_user_1_"]

# Sharing Tab is usable
#     Log in as site owner
#     Add workspace  Demo Workspace
#     Maneuver to  Demo Workspace
#     Go To  ${PLONE_URL}/demo-workspace/@@sharing
#     Input text  sharing-user-group-search  test
#     Click button  sharing-search-button
#     Element should be visible  xpath=//table[@id="user-group-sharing"]/tbody/tr/td[normalize-space()="test_user_1_ (test-user)"]
