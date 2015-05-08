*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

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

Manager can view sidebar info
    given I'm logged in as a 'Manager'
    I can go to the sidebar info tile

Alice can view sidebar events
    given I am logged in as the user alice_lindstrom
    I can go to the sidebar events tile
    I can see upcoming events
    Older events are hidden

# Alice can delete sidebar events
#     given I am logged in as the user alice_lindstrom
#     I can go to the sidebar events tile
#     I can delete an old event

Manager can view sidebar tasks
    given I'm logged in as a 'Manager'
    I can go to the sidebar tasks tile

Traverse Folder in sidebar navigation
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    Then I can enter the Manage Information Folder
    And Go back to the workspace by clicking the parent button

Search for objects in sidebar navigation
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    Then I can search for items

The manager can modify workspace security policies
    Given I'm logged in as a 'Manager'
    And add workspace  Policy Workspace
    And maneuver to  Policy Workspace
    I can open the workspace security settings tab
    And I can set the external visibility to Open
    And I can set the join policy to Admin-Managed
    And I can set the participant policy to Moderate

The manager can invite Alice to join the Open Market Committee Workspace
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    And I can open the workspace member settings tab
    I can invite Alice to join the workspace

The manager can invite Alice to join the Open Market Committee Workspace from the menu
    Given I'm logged in as a 'Manager'
    And I go to the Open Market Committee Workspace
    And I can open the workspace member settings tab
    I can invite Alice to join the workspace from the menu

Create document
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a new document

Create folder
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a new folder

Create image
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a new image

Create structure
    Given I am logged in as the user christian_stoney
      And I go to the Open Market Committee Workspace
     Then I can create a structure

Alice can upload a file
    Given I am logged in as the user alice_lindstrom
      And I go to the Open Market Committee Workspace
      And I select a file to upload
     Then the file appears in the sidebar


# XXX: The following tests derive from ploneintranet.workspace and still
# need to be adapted to our current state of layout integration

# Site Administrator can add example user as member of workspace
#     Given I'm logged in as a 'Site Administrator'
#      Add workspace  Example Workspace
#      Maneuver to  Example Workspace
#      Click Link  jquery=a:contains('View full Roster')
#      Input text  edit-roster-user-search  Example User
#      Click button  Search users

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

I can create a new workspace
    Go To  ${PLONE_URL}/workspaces.html
    Click Link  link=Create Workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=New Workspace
    Input Text  name=form.widgets.IBasic.description  text=A new Workspace
    Click Element  css=button.icon-ok-circle.confirmative
    Wait Until Element Is visible  css=div#activity-stream  timeout=10

I select a file to upload
    [Documentation]  We can't drag and drop from outside the browser so it gets a little hacky here
    Execute JavaScript  jQuery('.pat-upload.upload .accessibility-options').show()
    Execute JavaScript  jQuery('.pat-upload.upload').siblings('button').show()
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Element  xpath=//button[text()='Upload']

I can go to the sidebar info tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Workspace settings and about
    Wait Until Page Contains  General
    Wait Until Page Contains  Workspace title
    Wait Until Page Contains  Workspace brief description

I can go to the sidebar events tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Events
    Wait Until Element Is visible  xpath=//h3[.='Upcoming events']


I can open the workspace security settings tab
    Click Link  link=Workspace settings and about
    Click link  link=Security
    Wait until page contains  Workspace policy

I can open the workspace member settings tab
    Click Link  link=Workspace settings and about
    Click link  link=Members
    Wait until page contains  Members

I can set the external visibility to Open
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='external_visibility']")[0].value = 3
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  The workspace can be explored by outsiders.

I can set the join policy to Admin-Managed
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='join_policy']")[0].value = 1
    Submit form  css=#sidebar-settings-security
    Click link  link=Security
    Wait until page contains  Only administrators can add workspace members.

I can set the participant policy to Moderate
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='participant_policy']")[0].value = 4
    Submit form  css=#sidebar-settings-security
    Click link  link=Security
    Wait until page contains  Workspace members can do everything

I can see upcoming events
    Page Should Contain Element  xpath=//a[.='Future Event']

Older events are hidden
    Element should not be visible  jquery=div#older-events a

I can delete an old event
    Click Element  css=div#older-events h3
    Mouse Over  xpath=//div[@id='older-events']//li[@class='cal-event']
    Focus  xpath=//div[@id='older-events']//li[@class='cal-event']
    Click Element  css=div#older-events button[type='submit']
    Wait Until Page Contains  Do you really want to delete this item
    Click Button  Delete

I can go to the sidebar tasks tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  xpath=//p[.='No tasks created yet']

I can invite Alice to join the workspace
    Click Link  css=div.button-bar.create-buttons a.icon-user-add
    I can invite Alice to the workspace

I can invite Alice to join the workspace from the menu
    Click Link  link=Functions
    Click Link  xpath=//ul[@class='menu']//a[.='Add user']
    I can invite Alice to the workspace

I can invite Alice to the workspace
    Wait until page contains  Invitations
    Input Text  css=#form-widgets-user-widgets-query  Alice
    Click Button  Ok
    Select Radio Button  form.widgets.user  alice_lindstrom
    Click Button  Ok

The breadcrumbs show the name of the workspace
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-2' and text()='Open Market Committee']

I can enter the Manage Information Folder
    Click Link  link=Documents
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
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Humble Document
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input[value="My Humble Document"]



I can create a new folder
    Click link  Documents
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Humble Folder
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble folder
    Click Button  css=#form-buttons-create
    # We cannot jet test the folders existence without reloading
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    # On reload the navbar is closed by default - open it
    Click link  Documents
    Page Should Contain Element  css=a.pat-inject[href$='/open-market-committee/my-humble-folder']

I can create a new image
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Image
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble image
    Click Element  css=label.icon-file-image
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input.doc-title[value='My Image']

I can create a structure
    Click link  Documents
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Another Folder
    Click Button  css=#form-buttons-create
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Element  xpath=//a[contains(@data-pat-inject,'/open-market-committee/another-folder/@@sidebar.default#workspace-documents')]
    Wait Until Page Contains Element  css=a.pat-inject[href$='/open-market-committee/@@sidebar.default']
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Document in subfolder
    Click Button  css=#form-buttons-create
    # This must actually test for the document content of the rendered view
    Wait Until Page Contains Element  css=#content input[value="Document in subfolder"]
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click element  xpath=//a/strong[contains(text(), 'Another Folder')]
    Wait Until Page Contains Element  xpath=//a[@class='pat-inject follow'][contains(@href, '/document-in-subfolder')]

The file appears in the sidebar
    Wait until Page contains Element  xpath=//input[@name='bartige_flosser.odt']  timeout=20 s

The upload appears in the stream
    Wait until Page contains Element  xpath=//a[@href='activity-stream']//section[contains(@class, 'preview')]//img[contains(@src, 'bartige_flosser.odt')]  timeout=20 s
