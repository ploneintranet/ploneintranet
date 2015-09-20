*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

Test Setup  Prepare test browser
Test Teardown  Close all browsers

# Suite Setup  Set Selenium speed  0.5s

*** Test Cases ***

Manager can create a workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new workspace    My new workspace

Alice can create a workspace
    Given I am logged in as the user alice_lindstrom
     Then I can create a new workspace    My user workspace

Non-member cannot see into a workspace
    Given I am logged in as the user alice_lindstrom
     when I can go to the Open Market Committee Workspace
     then I am redirected to the login page

Breadcrumbs are not borked
    Given I am in a workspace as a workspace member
    And I am in a workspace as a workspace member
    Then the breadcrumbs show the name of the workspace

Member can access a user profile from sidebar and follow the user
    Given I am in a workspace as a workspace member
      And I can open the workspace member settings tab
     Then I can open Esmeralda's profile
      And I can follow Esmeralda

Member can view sidebar events
    Given I am in a workspace as a workspace member
     Then I can go to the sidebar events tile
      And I can see upcoming events
    Older events are hidden

# The following tests are commented out, since we currently have no concept
# for adding tasks in a workspace. Relying on globally available tasks (the
# reason why these tests used to be passing) is not valid.

Manager can add a task for Allan and Allan cannot modify it
    Given I am in a workspace as a workspace admin
     Then I create a task for  Allan
          Go to  ${PLONE_URL}/logout
     When I am logged in as the user allan_neece
     Then Task is read only for user  Allan

# Manager can view sidebar tasks
#     Given I am in a workspace as a workspace admin
#     Then I can go to the sidebar tasks tile

# Member can view sidebar tasks
#     Given I am in a workspace as a workspace member
#      Then I can go to the sidebar tasks tile

Traverse Folder in sidebar navigation
    Given I am in a workspace as a workspace member
     Then I can enter the Manage Information Folder
     And Go back to the workspace by clicking the parent button

Search for objects in sidebar navigation
    Given I am in a workspace as a workspace member
     Then I can search for items

The manager can modify workspace security policies
    Given I am in a workspace as a workspace admin
     Then I can open the workspace security settings tab
      And I can set the external visibility to Open
      And I can set the join policy to Admin-Managed
      And I can set the participant policy to Moderate

The manager can invite Alice to join the Open Market Committee Workspace
    Given I am in a workspace as a workspace admin
     Then I can open the workspace member settings tab
      And I can invite Alice to join the workspace

The manager can invite Alice to join the Open Market Committee Workspace from the menu
    Given I am in a workspace as a workspace admin
      And I can open the workspace member settings tab
     Then I can invite Alice to join the workspace from the menu

Create document
    Given I am in a workspace as a workspace member
     Then I can create a new document    My Humble document

Create folder
    Given I am in a workspace as a workspace member
     Then I can create a new folder

Create image
    Given I am in a workspace as a workspace member
     Then I can create a new image

Create structure
    Given I am in a workspace as a workspace member
     Then I can create a structure

Member can upload a file
    Given I am in a workspace as a workspace member
      And I select a file to upload
     Then the file appears in the sidebar

Member can submit a document
    Given I am in a workspace as a workspace member
     When I can create a new document    My awesome document
     Then I can edit the document
     When I submit the content item
     Then I cannot edit the document

Member can create an event
    Given I am in a workspace as a workspace member
     When I can create a new event  Christmas  2014-12-25  2014-12-26
     Then I can edit an event  Christmas  2120-12-25  2121-12-26  Europe/Rome
     Then I can delete an event  Christmas (updated)

Member cannot create an event with invalid dates
    Given I am in a workspace as a workspace member
     When I cannot create a new event  Invalid dates  2014-12-25  2010-12-22

Member cannot edit an event with invalid data
    Given I am in a workspace as a workspace member
     When I can create a new event  Easter  2014-12-25  2014-12-26
     Then I cannot edit an event because of validation  Easter  2121-12-25  2120-12-26  Europe/Rome

Member can submit and retract a document
    Given I am in a workspace as a workspace member
     When I can create a new document    My substandard document
     Then I can edit the document
     When I submit the content item
     Then I cannot edit the document
     When I retract the content item
     Then I can edit the document

Member can publish a document in a Publishers workspace
    Given I am in a workspace as a workspace member
     When I can create a new document    My publishing document
     When I submit the content item
     Then I can publish the content item

Member cannot publish a document in a Producers workspace
    Given I am in a Producers workspace as a workspace member
     When I can create a new document    My non-publishing document
     When I submit the content item
     Then I cannot publish the content item

Member cannot create content in a Consumers workspace
    Given I am in a Consumers workspace as a workspace member
     Then I cannot create a new document

Member cannot create content in a workspace changed from Produce to Consume
    Given I am logged in as the user christian_stoney
      And I go to the Open Parliamentary Papers Guidance Workspace
     Then I can open the workspace security settings tab
      And I can set the participant policy to Consume
     When I am logged in as the user allan_neece
      And I go to the Open Parliamentary Papers Guidance Workspace
     Then I cannot create a new document

Non-Member can view published content in an open workspace
    Given I am in an open workspace as a non-member
     Then I can see the document  Terms and conditions
      And I cannot see the document  Customer satisfaction survey

Site Administrator can add example user as member of workspace
    Given I'm logged in as a 'Site Administrator'
     Add workspace  Example Workspace
     Click Link  Workspace settings and about
     Click Link  Members
     Wait Until Page Contains  Add user
     Click Link  Add user
     Wait Until Page Contains Element  css=li.select2-search-field input
     Input Text  css=li.select2-search-field input  alice
     Wait Until Element Is Visible  css=span.select2-match
     Click Element  css=span.select2-match
     Click Button  Ok
     Wait Until Page Contains  Alice

The manager can grant the Producer role in a Consumer workspace
    Given I am in a Consumers workspace as a workspace admin
      And I give the Producer role to Allan
     When I am in a Consumers workspace as a workspace member
     Then I see the option to create a document

The manager can grant the Consumer role in a Producer workspace
    Given I am in a Producers workspace as a workspace admin
      And I give the Consumer role to Allan
     When I am in a Producers workspace as a workspace member
     Then I cannot create a new document

The manager can remove a special role from a workspace member
    Given I am in a Consumers workspace as a workspace admin
      And I give the Producer role to Allan
     When I am in a Consumers workspace as a workspace admin
     Then I can remove the Producer role from Allan

The manager can change a special role
    Given I am in a Consumers workspace as a workspace admin
      And I give the Producer role to Allan
     Then I can change Allan's role to Moderator

The manager can add other workspace admins
    Given I am in a Consumers workspace as a workspace admin
     Then I give the Admin role to Allan

The manager can remove a workspace member
    Given I am in a workspace as a workspace admin
     Then I can remove Allan from the workspace members

# XXX: The following tests derive from ploneintranet.workspace and still
# need to be adapted to our current state of layout integration
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


*** Keywords ***

# See lib/keywords.robot in the section "workspace related keywords"
