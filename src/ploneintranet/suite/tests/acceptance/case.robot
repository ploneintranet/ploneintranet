*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Variables  variables.py

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Manager can create a case workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new case    A case for outer space
     Then I can delete a case  a-case-for-outer-space

Manager can change the workflow of a case workspace
    Given I'm logged in as a 'Manager'
     Then I can create a new case  Workflow case
     Then I can go to the sidebar tasks tile
     Then I can close the first milestone
     Then I can delete a case  workflow-case

Non-member cannot see into a workspace
    Given I am logged in as the user alice_lindstrom
     when I try go to the Minifest
     then I am redirected to the login page

Breadcrumbs are not borked
    Given I am in a case workspace as a workspace member
    And I am in a case workspace as a workspace member
    Then the breadcrumbs show the name of the workspace

Manager can view sidebar info
    Given I am in a case workspace as a workspace admin
    I can go to the sidebar info tile

Member can view sidebar info
    Given I am in a case workspace as a workspace member
    I can go to the sidebar info tile

Member can view sidebar events
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar events tile
      And I can see upcoming events
    Older events are hidden

Owner can delete sidebar events
    Comment  In the test setup, we made the workspace member allen_neece owner of an old event
    Given I am in a case workspace as a workspace member
    I can go to the sidebar events tile
    I can delete an old event

Manager can view sidebar tasks
    Given I am in a case workspace as a workspace admin
    Then I can go to the sidebar tasks tile

Member can view sidebar tasks
    Given I am in a case workspace as a workspace member
     Then I can go to the sidebar tasks tile

Manager can add a new task
    Given I am in a case workspace as a workspace admin
     Then I can go to the sidebar tasks tile
     Then I can add a new task  Make a plan

Manager can mark a new task complete on dashboard
    Given I am in a case workspace as a workspace admin
     Then I can go to the sidebar tasks tile
     Then I can add a new task  Todo soon
     Then I go to the dashboard
     Then I mark a new task complete
     Then I go to the dashboard
     Then I do not see the completed task is not listed

Traverse Folder in sidebar navigation
    Given I am in a case workspace as a workspace member
     Then I can enter the Supporting Materials Folder
     And Go back to the workspace by clicking the parent button

Search for objects in sidebar navigation
    Given I am in a case workspace as a workspace member
     Then I can search for items

The manager can modify workspace security policies
    Given I am in a case workspace as a workspace admin
     Then I can open the workspace security settings tab
      And I can set the external visibility to Open
      And I can set the join policy to Admin-Managed
      And I can set the participant policy to Moderate

The manager can invite Alice to join the Minifest
    Given I am in a case workspace as a workspace admin
     Then I can open the workspace member settings tab
      And I can invite Alice to join the workspace

The manager can invite Alice to join the Minifest from the menu
    Given I am in a case workspace as a workspace admin
      And I can open the workspace member settings tab
     Then I can invite Alice to join the workspace from the menu

Create document
    Given I am in a case workspace as a workspace member
     Then I can create a new document    My Humble document

Create folder
    Given I am in a case workspace as a workspace member
     Then I can create a new folder

Create image
    Given I am in a case workspace as a workspace member
     Then I can create a new image

Create structure
    Given I am in a case workspace as a workspace member
     Then I can create a structure

Member can upload a file
    Given I am in a case workspace as a workspace member
      And I select a file to upload
     Then the file appears in the sidebar

Member can submit a document
    Given I am in a case workspace as a workspace member
     When I can create a new document    My awesome document
     Then I can edit the document
     When I submit the content item
     Then I cannot edit the document

Member can submit and retract a document
    Given I am in a case workspace as a workspace member
     When I can create a new document    My substandard document
     Then I can edit the document
     When I submit the content item
     Then I cannot edit the document
     When I retract the content item
     Then I can edit the document

Member can publish a document in a Publishers workspace
    Given I am in a case workspace as a workspace member
     When I can create a new document    My publishing document
     When I submit the content item
     Then I can publish the content item

Member cannot publish a document in a Producers workspace
    Given I am in a Producers workspace as a workspace member
     When I can create a new document    My non-publishing document
     When I submit the content item
     Then I cannot publish the content item


*** Keywords ***

I can create a new case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=${title}
    Input Text  name=description  text=Let's get organized
    Select From List  portal_type  ploneintranet.workspace.case
    Select Radio Button  workflow  todo_workflow
    Click Button  Create workspace
    Wait Until Element Is visible  css=div#activity-stream  timeout=10

I can delete a case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/workspaces/${case_id}/delete_confirmation
    Click Button  Delete
    Page Should Contain  has been deleted

I select a file to upload
    [Documentation]  We can't drag and drop from outside the browser so it gets a little hacky here
    Execute JavaScript  jQuery('.pat-upload.upload .accessibility-options').show()
    Execute JavaScript  jQuery('.pat-upload.upload').siblings('button').show()
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Element  xpath=//button[text()='Upload']

I can go to the sidebar info tile
    Click Link  link=Workspace settings and about
    Wait Until Page Contains  General
    Wait Until Page Contains  Workspace title
    Wait Until Page Contains  Workspace brief description

I can go to the sidebar events tile
    Click Link  link=Events
    Wait Until Element Is visible  xpath=//h3[.='Upcoming events']

I go to the dashboard
    Go To  ${PLONE_URL}

I mark a new task complete
    Select Checkbox  xpath=(//a[@title='Todo soon'])[1]/preceding-sibling::input[1]
    Wait Until Page Contains  Changes applied

I do not see the completed task is not listed
    Page Should Not Contain  Todo soon

I can open the workspace security settings tab
    Click Link  link=Workspace settings and about
    Wait until page contains  Security
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
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  Only administrators can add workspace members.

I can set the participant policy to Moderate
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='participant_policy']")[0].value = 4
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  Workspace members can do everything

I can see upcoming events
    Page Should Contain Element  xpath=//a[.='Future Council Meeting']

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
    Click Link  link=Tasks
    Wait Until Page Contains  General tasks

I can add a new task
    [arguments]  ${title}
    Click Link  Create task
    Wait Until Page Contains  Create task
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    Element Should Contain  xpath=//label[@class='initiator']//li[@class='select2-search-choice']/div  Christian Stoney
    Select From List  milestone  new
    Click Button  Create
    Wait Until Page Contains  Make a plan

I can close the first milestone
    Click Element  xpath=//h4[text()='New']
    Click Link  Close milestone
    Page Should Contain  Item state changed

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
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-2' and text()='Minifest']

I can enter the Supporting Materials Folder
    Click Link  link=Documents
	Page Should Contain  Supporting Materials
	Click Element  xpath=//form[@id='items']/fieldset/label[1]/a
	Wait Until Page Contains  Supporting Materials


Go back to the workspace by clicking the parent button
	Page Should Contain Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Minifest']
	Click Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Minifest']
	Page Should Contain  Supporting Materials

I can create a new document
    [arguments]  ${title}
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=${title}
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input[value="${title}"]

I can create a new folder
    Click link  Documents
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Humble Folder
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble folder
    Click Button  css=#form-buttons-create
    # We cannot jet test the folders existence without reloading
    Go To  ${PLONE_URL}/workspaces/minifest
    # On reload the navbar is closed by default - open it
    Click link  Documents
    Page Should Contain Element  css=a.pat-inject[href$='/minifest/my-humble-folder']

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
    Go To  ${PLONE_URL}/workspaces/minifest
    Click link  Documents
    Click Element  css=a.pat-inject[href$='/minifest/another-folder']
    Wait Until Page Contains Element  css=a.pat-inject[href$='/minifest']
    Click link  Documents
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Document in subfolder
    Click Button  css=#form-buttons-create
    # This must actually test for the document content of the rendered view
    Wait Until Page Contains Element  css=#content input[value="Document in subfolder"]
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Go To  ${PLONE_URL}/workspaces/minifest
    Click link  Documents
    Click element  xpath=//a/strong[contains(text(), 'Another Folder')]
    Wait Until Page Contains Element  xpath=//a[@class='pat-inject follow'][contains(@href, '/document-in-subfolder')]

The file appears in the sidebar
    Wait until Page contains Element  xpath=//input[@name='bartige_flosser.odt']  timeout=20 s

The upload appears in the stream
    Wait until Page contains Element  xpath=//a[@href='activity-stream']//section[contains(@class, 'preview')]//img[contains(@src, 'bartige_flosser.odt')]  timeout=20 s

I submit the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Pending')]
    Wait until page contains  The workflow state has been changed
    Click button  Close

I retract the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Wait until page contains  The workflow state has been changed
    Click button  Close

I can publish the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close

I cannot publish the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Element should be visible   xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Element should not be visible   xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]

I can edit the document
    Element should be visible  xpath=//div[@id='document-body']//div[@id='editor-toolbar']
    Element should be visible  xpath=//div[@id='document-body']//div[@class='meta-bar']//button[@type='submit']

I cannot edit the document
    Element should not be visible  xpath=//div[@id='document-body']//div[@id='editor-toolbar']
    Element should not be visible  xpath=//div[@id='document-body']//div[@class='meta-bar']//button[@type='submit']

