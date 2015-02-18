*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
# Library  DebugLibrary

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Manager can create a workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new workspace

Breadcrumbs are not borked
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    Then the breadcrumbs show the name of the workspace

Traverse Folder in sidebar navigation
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    Then I can enter the Manage Information Folder
    And Go back to the workspace by clicking the parent button

Search for objects in sidebar navigation
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    Then I can search for items

Create document
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a new document

Create folder
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a new document


# XXX: The following tests derive from ploneintranet.workspace and still
# need to be adapted to our current state of layout integration

# Site Administrator can add example user as member of workspace
#     Given I'm logged in as a 'Site Administrator'
#      Add workspace  Example Workspace
#      Maneuver to  Example Workspace
#      Click Link  jquery=a:contains('View full Roster')
#      Input text  edit-roster-user-search  Example User
#      Click button  Search users

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


*** Keywords ***

I am logged in as the user ${userid}
    Go To  ${PLONE_URL}/login?__ac_name=${userid}&__ac_password=secret&form.submitted=1

I can create a new workspace
    Go To  ${PLONE_URL}/workspaces.html
    Click Link  link=Create Workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=New Workspace
    Input Text  name=form.widgets.IBasic.description  text=A new Workspace
    Click Element  css=button.icon-ok-circle.confirmative
    Wait Until Element Is visible  css=div.post.item  timeout=5

I go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Open Market Committee

The breadcrumbs show the name of the workspace
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-2' and text()='Open Market Committee']

I can enter the Manage Information Folder
	Page Should Contain  Manage Information
	Click Element  xpath=//form[@id='items']/fieldset/label[1]/a
	Wait Until Page Contains  Preparation of Records
	Wait Until Page Contains  How to prepare records

Go back to the workspace by clicking the parent button
	Page Should Contain Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
	Click Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
	Page Should Contain  Projection Materials

I can search for items
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']
    Input Text  xpath=//input[@name='sidebar-search']  Info
    Wait Until Page Contains Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']

I can create a new document
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  name=title  text=My Humble Document
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input[value="My Humble Document"]

I can create a new folder
    Click link  Functions
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  name=title  text=My Humble Folder
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input[value="My Humble Folder"]
