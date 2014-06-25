*** Keywords ***

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


Navigate to
    [arguments]  ${title}
    Go to homepage
    Click Contents In edit bar
    Click link  ${title}


Add workspace
    [arguments]  ${title}
    Log in as site owner
    Go to homepage
    Add content item  Workspace  ${title}
    Element should be visible  xpath=//ul[@id="portal-globalnav"]/li[a="${title}"]


Maneuver to
    [arguments]  ${title}
    Go to homepage
    Click link  ${title}
