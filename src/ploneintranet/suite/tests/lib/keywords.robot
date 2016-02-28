*** Keywords ***

Prepare test browser
    Open test browser
    Set window size  1024  900

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}

I am logged in as site administrator
    Element should be visible  css=body.userrole-site-administrator

I am logged in as the user ${userid}
    Go To  ${PLONE_URL}/login
    Input text  name=__ac_name  ${userid}
    Input text  name=__ac_password  secret
    Click button  Login

# add content keyword that supports
# both dexterity and archetypes
Add content item
    [arguments]  ${content_type}  ${title}
    Open add new menu
    Click link  link=${content_type}
    Fill text field  Title  ${title}
    Click button  name=form.buttons.save
    Page should contain  Item created
    Page should contain  ${title}
    ${location} =  Get Location
    [return]  ${location}

# Fill a text field
# Field is matched via a preceding <label>
Fill text field
    [arguments]  ${field_label}   ${text}
    Input Text  xpath=//form//div/input[preceding-sibling::label[contains(text(), '${field_label}')]]  ${text}

Add workspace
    [arguments]  ${title}
    Go to  ${PLONE_URL}/workspaces/++add++ploneintranet.workspace.workspacefolder
    Input text  name=form.widgets.IBasic.title  ${title}
    Click Button  Save
    Page Should Contain  Item created

Maneuver to
    [arguments]  ${title}
    Go to homepage
    Click link  jquery=a:contains("${title}")

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I am in a workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Market Committee Workspace

I am in a Producers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Parliamentary Papers Guidance Workspace

I am in a Producers workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Open Parliamentary Papers Guidance Workspace

I am in a Consumers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Shareholder Information Workspace

I am in a Consumers workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Shareholder Information Workspace

I am in a workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Open Market Committee Workspace

I am in an open workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Service Announcements Workspace

I am in an open workspace as a non-member
    I am logged in as the user alice_lindstrom
    I go to the Service Announcements Workspace

I go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Open Market Committee

I go to the Example Case
    Go To  ${PLONE_URL}/workspaces/example-case
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Example Case

I go to the Open Parliamentary Papers Guidance Workspace
    Go To  ${PLONE_URL}/workspaces/parliamentary-papers-guidance
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Parliamentary papers guidance

I go to the Shareholder Information Workspace
    Go To  ${PLONE_URL}/workspaces/shareholder-information
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Shareholder information

I go to the Service Announcements Workspace
    Go To  ${PLONE_URL}/workspaces/service-announcements
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Service announcements

I can go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee

I can go to the Example Case
    Go To  ${PLONE_URL}/workspaces/example-case

I am redirected to the login page
    Location Should Contain  require_login

I open the password reset form
    Go To  ${PLONE_URL}/pwreset_form

The page is not found
    Page should contain  This page does not seem to exist

# *** Workspace related keywords ***

I can create a new workspace
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  xpath=//input[@name='title']  text=${title}
    Input Text  xpath=//textarea[@name='description']  text=Random description
    Click Button  Create workspace
    Wait Until Element Is visible  css=div#activity-stream  timeout=10

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


I can open the workspace security settings tab
    Click Link  link=Workspace settings and about
    Wait until page contains  Security
    Click link  link=Security
    Wait until page contains  Workspace policy

I can open the workspace member settings tab
    Click Link  link=Workspace settings and about
    Click link  link=Members
    Wait until page contains element  css=#member-list

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

I can set the participant policy to Consume
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='participant_policy']")[0].value = 1
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  They cannot add

I can open Esmeralda's profile
    Click Element  css=a[href$='/profiles/esmeralda_claassen']
    Wait Until Element Is visible  css=#person-timeline .sidebar

I can follow Esmeralda
    Element should contain  css=.icon-eye  Follow Esmeralda Claassen
    Click Element  css=.icon-eye
    Wait Until Page contains element  css=button[title="You are now following Esmeralda Claassen. Click to unfollow."]

I can see upcoming events
    Page Should Contain Element  xpath=//ul[@class='event-list']//a/h4[text()[contains(.,'Plone Conf')]]

Older events are hidden
    Element should not be visible  jquery=div#older-events a

I can go to the sidebar tasks tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  xpath=//p[.='No tasks created yet']

I create a task for
    [arguments]  ${name}
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  css=[title="Create new task"]
    Click Element  css=[title="Create new task"]
    Wait Until Page Contains Element  css=.wizard-box
    Input Text  css=.wizard-box input[name=title]  Ciao ${name}
    Input Text  css=.wizard-box textarea[name=description]  This is for you ${name}
    Click Element  css=.wizard-box .assignee .select2-choices input
    Input Text  css=.wizard-box .assignee .select2-choices input  ${name}
    Wait Until Page Contains Element  jquery=span.select2-match:last
    Click Element  jquery=span.select2-match:last
    Input Text  css=.wizard-box input[name=due]  2020-12-31
    Click Element  css=.wizard-box #form-buttons-create
    Wait Until Page Contains Element  css=a[title="Ciao ${name}"]

Task is read only for user
    [arguments]  ${name}
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Page Contains Element  css=a[title="Ciao ${name}"]
    Click Element  css=a[title="Ciao ${name}"]
    Wait Until Page Contains  This is for you ${name}
    Element Should Be Visible  jquery=input:disabled[name=due]

I can invite Alice to join the workspace
    Wait Until Page Contains Element  css=div.button-bar.create-buttons a.icon-user-add
    Click Link  css=div.button-bar.create-buttons a.icon-user-add
    I can invite Alice to the workspace

I can invite Alice to join the workspace from the menu
    Wait Until Page Contains Element  link=Functions
    Click Link  link=Functions
    Wait until element is visible  xpath=//div[@id='member-list-more-menu']/div[@class='panel-content']
    Click Link  xpath=//ul[@class='menu']//a[.='Add user']
    I can invite Alice to the workspace

I can invite Alice to the workspace
    Wait until element is visible  xpath=//div[contains(@class, 'pat-modal')]//h1[text()='Add users']
    Input Text  css=li.select2-search-field input  alice
    Wait Until Element Is visible  css=span.select2-match
    Click Element  css=span.select2-match
    Click Button  Ok

I give the Consumer role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Consumers
    Click Button  css=.pat-modal button[type=submit]
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Consume']

I give the Producer role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible   xpath=//div[@class='batch-functions']//button[@value='role']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Producers
    Click Button  css=.pat-modal button[type=submit]
    Wait until page contains  Role updated
    Click button  Close
    Page Should Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Produce']

I give the Admin role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible   xpath=//div[@class='batch-functions']//button[@value='role']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Admins
    Click Button  css=.pat-modal button[type=submit]
    Wait until page contains  Role updated
    Click button  Close
    Page Should Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Admin']

I can remove the Producer role from Allan
    I can open the workspace member settings tab
    Click element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    Wait until page contains  Remove special role
    Click Link  Remove special role
    Wait until element is visible  xpath=//div[@class='panel-content']//button[@value='role']
    Click Button  I am sure, remove role now
    Wait until page contains  Role updated
    Click button  Close
    Page Should Not Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Produce']

I can change Allan's role to Moderator
    I can open the workspace member settings tab
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    # Yes, adding Sleep is very ugly, but I see no other way to ensure that
    # the sidebar and the element we need has really completely loaded.
    # This heisenbug has already cost us numerous failures in jenkins for otherwise
    # healthy test suites. Anybody who removes this Sleep statement is responsible
    # for ensuring that the test still works 100% reliably. [pysailor]
    Sleep  0.5
    Click element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    Wait until page contains element  xpath=//*[contains(@class, 'tooltip-container')]//a[text()='Change role']
    Click Link  xpath=//*[contains(@class, 'tooltip-container')]//a[text()='Change role']
    Select From List  css=select[name=role]  Moderators
    Click Button  css=.pat-modal button[type=submit]
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Moderate']

I can remove Allan from the workspace members
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible    css=button[value='remove']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Remove
    Wait until element is visible  css=.pat-modal button[type=submit]
    Click Button  Ok
    Wait until element is visible   css=div.pat-notification-panel.success
    Page Should Not Contain Element  xpath=//input[@value='allan_neece']/..

The breadcrumbs show the name of the workspace
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-2' and text()='Open Market Committee']

I can enter the Manage Information Folder
    Click Link  link=Documents
    Page Should Contain  Manage Information
    Click Element  xpath=//form[@id='items']/fieldset/label/a[contains(@href, 'open-market-committee/manage-information')]
    Wait Until Page Contains  Preparation of Records
    Wait Until Page Contains  How to prepare records

I can enter the Projection Materials Folder
    Click Link  link=Documents
    Page Should Contain  Projection Materials
    Click Element  xpath=//form[@id='items']/fieldset/label/a[contains(@href, 'open-market-committee/projection-materials')]
    Wait Until Page Contains  Projection Material
    Wait Until Page Contains  Projection Materials
    Wait Until Page Contains  Open Market Committee

Go back to the workspace by clicking the parent button
    Page Should Contain Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
    Click Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
    Wait Until Page Contains  Projection Materials

I can search for items
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']
    Input Text  xpath=//input[@name='sidebar-search']  Info
    Wait Until Page Contains Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']

I see the option to create a document
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content input[name=title]

I can create a new document
    [arguments]  ${title}
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content input[name=title]
    Input Text  css=.panel-content input[name=title]  text=${title}
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div[1]/span/textarea[text()='${title}']

I cannot create a new document
    Click link  Documents
    Wait until page contains  Expand sidebar
    Page Should Not Contain   Create document
    Page Should Not Contain Link  Functions

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
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div/span/textarea[text()='My Image']

I can create a structure
    Click link  Documents
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Another Folder
    Click Button  css=#form-buttons-create
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click Element  css=a.pat-inject[href$='/open-market-committee/another-folder']
    Wait Until Page Contains Element  css=a.pat-inject[href$='/open-market-committee']
    Click link  Documents
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Document in subfolder
    Click Button  css=#form-buttons-create
    # This must actually test for the document content of the rendered view
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div[1]/span/textarea[text()='Document in subfolder']
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click element  xpath=//a/strong[contains(text(), 'Another Folder')]
    Wait Until Page Contains Element  xpath=//a[@class='pat-inject follow pat-switch'][contains(@href, '/document-in-subfolder')]

I can create a new event
    [arguments]  ${title}  ${start}  ${end}  ${organizer}=Allan Neece  ${invitees}=Dollie Nocera
    Click link  Events
    Click Link  Create event
    Wait Until Page Contains Element  css=.panel-content form .panel-body
    Input Text  css=.panel-content input[name=title]  text=${title}
    Input Text  css=.panel-content input[name=end]  text=${end}
    Input Text  css=.panel-content input[name=start]  text=${start}
    Input text  xpath=//input[@placeholder='Name of organiser']/../div//input  ${organizer}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${organizer}']
    Click Element  xpath=//span[@class='select2-match'][text()='${organizer}']
    Input text  xpath=//input[@placeholder='Invitees']/../div//input  ${invitees}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Element  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Button  css=#form-buttons-create
    Wait Until Page Contains  Item created
    Click Button  Close


I cannot create a new event
    [arguments]  ${title}  ${start}  ${end}  ${organizer}=Allan Neece  ${invitees}=Dollie Nocera
    Click link  Events
    Click Link  Create event
    Wait Until Page Contains Element  css=.panel-content form .panel-body
    Input Text  css=.panel-content input[name=title]  text=${title}
    Input Text  css=.panel-content input[name=end]  text=${end}
    Input Text  css=.panel-content input[name=start]  text=${start}
    Input text  xpath=//input[@placeholder='Name of organiser']/../div//input  ${organizer}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${organizer}']
    Click Element  xpath=//span[@class='select2-match'][text()='${organizer}']
    Input text  xpath=//input[@placeholder='Invitees']/../div//input  ${invitees}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Element  xpath=//span[@class='select2-match'][text()='${invitees}']
    Element Should Be Visible  jquery=#form-buttons-create:disabled

I can edit an event
    [arguments]  ${title}  ${start}  ${end}  ${timezone}
    Wait Until Page Contains Element  xpath=//h3[text()='Older events']
    Click Element  xpath=//h3[text()='Older events']
    Wait until element is visible  jquery=.event-list a:contains("${title}")
    Click Element  jquery=.event-list a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    Input Text  css=.meta-bar textarea[name=title]  text=${title} (updated)
    Input Text  css=div.event-details input[name=start]  text=${start}
    Input Text  css=div.event-details input[name=end]  text=${end}
    Click Element   css=input[name='location']
    Select From List  timezone  ${timezone}
    Click Button  Save
    Wait Until Element Is Visible  css=div.pat-notification-panel.success
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close
    Wait Until Page Contains Element  jquery=#workspace-events a:contains(updated)
    Textfield Value Should Be  start  ${start}
    List selection should be  timezone  ${timezone}
    Element should contain  css=#workspace-events [href$="open-market-committee/christmas#document-body"]  ${title} (updated)

I cannot edit an event because of validation
    [arguments]  ${title}  ${start}  ${end}  ${timezone}
    Reload Page
    Click link  Events
    Click Element  xpath=//h3[text()='Older events']
    Wait until element is visible  jquery=.event-list a:contains("${title}")
    Click link  jquery=a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    Input Text  css=.meta-bar textarea[name=title]  text=${title} (updated)
    Input Text  css=div.event-details input[name=start]  text=${start}
    Input Text  css=div.event-details input[name=end]  text=${end}
    Select From List  timezone  ${timezone}
    Element Should Be Visible  jquery=#save-event:disabled

Then I can delete an event
    [arguments]  ${title}
    Click link  jquery=a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    ### The following sleep statement addresses the StaleElementReferenceException that sometimes occurs
    ### Solutions proposed on the web address this programmatically with a combination of looping
    ### and exception handling. I wouldn't know of an equivalent solution in robot.
    sleep  2
    Wait until element is visible  css=.meta-bar .icon-trash
    Click Element  css=.meta-bar .icon-trash
    Wait until page contains element    xpath=//div[@class='panel-content']//button[@name='form.buttons.Delete']
    Click Button  I am sure, delete now
    Wait Until Page Contains  has been deleted
    Element should not be visible  css=#workspace-documents
    Element should be visible  css=#workspace-events
    Element should not be visible  jquery=a:contains("${title}")

The file appears in the sidebar
    Wait until Page contains Element  xpath=//fieldset/label/a/strong[text()='bärtige_flößer.odt']  timeout=20

The upload appears in the stream
    Wait until Page contains Element  xpath=//a[@href='activity-stream']//section[contains(@class, 'preview')]//img[contains(@src, 'bärtige_flößer.odt')]  timeout=20

# The self-healing Close messages below are a source of Heisenbugs in the test

I submit the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Pending')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

I retract the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

I can publish the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]
    Wait Until Element Is Visible   xpath=//fieldset[@id='workflow-menu']//select/option[@selected='selected' and contains(text(), 'Published')]
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

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

I can see the document
    [arguments]  ${title}
    Click link  Documents
    Page should contain  ${title}

I cannot see the document
    [arguments]  ${title}
    Click link  Documents
    Page should not contain  ${title}

Allan has the option to create a document
    I am logged in as the user allan_neece
    I go to the Shareholder Information Workspace
    I see the option to create a document

# *** workspace and case content related keywords ***

I browse to a workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Documents
    Click Link  link=Manage Information

I browse to a Consumer workspace
    Go To  ${PLONE_URL}/workspaces/service-announcements
    Click Link  link=Documents

I browse to a document
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'repurchase-agreements')]
    Click Link  xpath=//a[contains(@href, 'repurchase-agreements')]

I view the document
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/repurchase-agreements

I browse to an image
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'budget-proposal')]
    Click Link  xpath=//a[contains(@href, 'budget-proposal')]

I view the image
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/budget-proposal/view

I upload a new image
    Wait Until Page Contains Element  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Choose File  css=input[name=image]  ${UPLOADS}/vision-to-product.png
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close

I browse to a file
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'minutes')]
    Click Link  xpath=//a[contains(@href, 'minutes/view')]

I view the file
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/minutes/view

I upload a new file
    Wait Until Page Contains Element  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close

I view the folder
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/projection-materials/view

I view the task
    Go To  ${PLONE_URL}/workspaces/example-case/populate-metadata

I change the title
    Comment  Toggle the metadata to give the JavaScript time to load
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Input Text  title  New title ♥
    Wait Until Page Contains  New title ♥
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The document has the new title
    Wait Until Page Contains Element  xpath=//div[@id='document-body']//textarea[@name='title'][text()='New title ♥']

I change the description
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input Text  xpath=//textarea[@name='description']  New description ☀
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The document has the new description
    Page Should Contain  New description ☀

I tag the item
    [arguments]  ${tag}
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input Text  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]  ${tag},
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

I tag the item with a suggestion
    [arguments]  ${search_for}  ${selection}
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input text  xpath=//input[@placeholder='Tags']/../div//input  ${search_for}
    Wait until element is visible  xpath=//div[@class='select2-result-label'][contains(text(), '${selection}')]
    Click Element  xpath=//div[@class='select2-result-label'][contains(text(), '${selection}')]
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

I clear the tag for an item
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Click Link  css=.select2-search-choice-close
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The metadata has the new tag
    Click Link  link=Toggle extra metadata
    Page Should Contain  NewTag☃

# *** case related keywords ***

I am in a case workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Example Case

I am in a case workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Example Case

I move the example workspace to state prepare
      I can go to the Example Case
      I can go to the sidebar tasks tile of my case
      I can open a milestone task panel  prepare
      I select the task check box  Draft proposal
      I select the task check box  Budget
      I select the task check box  Stakeholder feedback

I move the example workspace to state complete
      I move the example workspace to state prepare
      I can close a milestone  prepare
      I can open a milestone task panel  complete
      I select the task check box  Quality check

Admin moves the example workspace to state complete
      I am in a case workspace as a workspace admin
      I move the example workspace to state complete

I can create a new case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  name=title  text=${title}
    Input Text  name=description  text=Let's get organized
    Select From List  portal_type  ploneintranet.workspace.case
    Wait Until Page Contains  Case Template
    Click Button  Create workspace
    Wait Until Page Contains  Populate Metadata

I can create a new template case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/templates/++add++ploneintranet.workspace.case
    Input Text  form.widgets.IBasic.title  New template
    Click Button  Save
    Go To  ${PLONE_URL}/workspaces

I can create a new case from a template
    [arguments]  ${template}  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  name=title  text=${title}
    Input Text  name=description  text=Something completely different
    Select From List  portal_type  ploneintranet.workspace.case
    Wait Until Page Contains  New template
    Select Radio Button  template_id  new-template
    Click Button  Create workspace
    Wait Until Page Contains  Item created

I can delete a case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/workspaces/${case_id}/delete_confirmation
    Wait until page contains element    xpath=//div[@class='panel-content']//button[@name='form.buttons.Delete']
    Click Button    I am sure, delete now
    Wait Until Page Contains    has been deleted    5

I can delete a template case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/templates/${case_id}/delete_confirmation
    Wait until page contains element    xpath=//div[@class='panel-content']//button[@name='form.buttons.Delete']
    Click Button    I am sure, delete now
    Wait Until Page Contains    has been deleted    5

I go to the dashboard
    Go To  ${PLONE_URL}

I select the task centric view
    Select From List  dashboard  Task centric view
    Wait Until Page Contains  Tasks

I mark a new task complete
    Wait until element is visible  xpath=(//a[@title='Todo soon'])
    Select Checkbox  xpath=(//a[@title='Todo soon'])[1]/preceding-sibling::input[1]
    Wait until Page Contains  Task state changed

I select the task check box
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])
    Select Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]
    ### Without the following sleep statement the 'Wait until' statement that follows it
    ### is executed quickly and selenium sometimes leaves the page before autosave can happen.
    ### This leads to errors later on when the box is assumed to be checked.
    sleep  4
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])

I unselect the task check box
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])
    Unselect Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]
    ### Without the following sleep statement the 'Wait until' statement that follows it
    ### is executed quickly and selenium sometimes leaves the page before autosave can happen.
    ### This leads to errors later on when the box is assumed to be checked.
    sleep  4
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])

I see a task is complete
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])

I see a task is open
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])

I see the task quality check has state
    [arguments]  ${state}
    Go To  ${PLONE_URL}/workspaces/example-case/quality-check
    Element should be visible  xpath=//fieldset[@id='workflow-menu']/label[@data-option='${state}']

I do not see the completed task is not listed
    Page Should Not Contain  Todo soon

I can go to the sidebar tasks tile of my case
    Click Link  link=Tasks
    Wait Until Page Contains  General tasks

I can add a new task
    [arguments]  ${title}  ${milestone}=
    Click Link  Create task
    Wait Until Page Contains Element  css=.panel-body
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    Element Should Contain  xpath=//label[@class='initiator']//li[@class='select2-search-choice']/div  Allan Neece
    Input Text  css=label.assignee li.select2-search-field input  neece
    Wait Until Element Is visible  xpath=//span[@class='select2-match'][text()='Neece']
    Click Element  xpath=//span[@class='select2-match'][text()='Neece']
    Select From List  milestone  ${milestone}
    Click Button  Create
    Wait Until Page Contains  ${title}

I can close a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Wait Until Page Contains Element  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']
    Click Link  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']
    # auto-closes current, reopen
    I can open a milestone task panel  ${milestone}
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//h4[contains(@class, 'state-finished')]

I cannot close a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Element should not be visible  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']

I can reopen a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Reopen milestone']
    Click Link  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Reopen milestone']
    # auto-closes current, reopen
    I can open a milestone task panel  ${milestone}
    ### The following sleep statement addresses the StaleElementReferenceException that sometimes occurs
    ### Solutions proposed on the web address this programmatically with a combination of looping
    ### and exception handling. I wouldn't know of an equivalent solution in robot.
    sleep  2
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//h4[contains(@class, 'state-finished')]

I can open a milestone task panel
    [arguments]  ${milestone}
    # panel 'open' state is session dependent, force open
    Run Keyword And Ignore Error  Click Element  css=#milestone-${milestone}.closed h4

I write a status update
    [arguments]  ${message}
    Wait Until Element Is visible  css=textarea.pat-content-mirror
    Element should not be visible  css=button[name='form.buttons.statusupdate']
    Click element  css=textarea.pat-content-mirror
    Wait Until Element Is visible  css=button[name='form.buttons.statusupdate']
    Input Text  css=textarea.pat-content-mirror  ${message}

I post a status update
    [arguments]  ${message}
    I write a status update    ${message}
    I submit the status update

I submit the status update
    Click button  css=button[name='form.buttons.statusupdate']

I can mention the user
    [arguments]  ${username}
    Click link    link=Mention people
    Wait Until Element Is visible    xpath=//form[@id='postbox-users']
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '@${username}')][1]  2
    Click element    css=textarea.pat-content-mirror

# *** search related keywords ***

I can see the site search button
    Page Should Contain Element  css=#global-header input.search

I can search in the site header for ${SEARCH_STRING}
    Input text  css=#global-header input.search  ${SEARCH_STRING}
    Submit Form  css=#global-header form#searchGadget_form

I can see the search result ${SEARCH_RESULT_TITLE}
    Element should be visible  link=${SEARCH_RESULT_TITLE}

I cannot see the search result ${SEARCH_RESULT_TITLE}
    Element should not be visible  link=${SEARCH_RESULT_TITLE}

I can follow the search result ${SEARCH_RESULT_TITLE}
    Click Link  link=${SEARCH_RESULT_TITLE}
    Page should contain  ${SEARCH_RESULT_TITLE}

I can filter content of type ${CONTENT_TYPE}
    Select Checkbox  css=input[type="checkbox"][value="${CONTENT_TYPE}"]

The search results do not contain ${STRING_IN_SEARCH_RESULTS}
    Wait Until Keyword Succeeds  1  3  Page should not contain  ${STRING_IN_SEARCH_RESULTS}

I can set the date range to ${DATE_RANGE_VALUE}
    Select From List By Value  css=select[name="created"]  ${DATE_RANGE_VALUE}
    Wait Until Element is Visible  css=dl.search-results[data-search-string*="created=${DATE_RANGE_VALUE}"]

I can click the ${TAB_NAME} tab
    Click Link  link=${TAB_NAME}

# *** END search related keywords ***
