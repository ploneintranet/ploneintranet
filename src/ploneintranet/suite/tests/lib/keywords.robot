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
    Go to  ${PLONE_URL}/++add++ploneintranet.workspace.workspacefolder
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

I am in a Consumers workspace as a workspace member
    I am logged in as the user allan_neece
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

I try go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee

I am redirected to the login page
    Location Should Contain  require_login


