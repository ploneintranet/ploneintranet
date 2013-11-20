*** Keywords ***

Add dexterity content
    [arguments]  ${content_type}  ${title}
    Open add new menu
    Click link  link=${content_type}
    Input Text  form.widgets.IBasic.title  ${title}
    Click button  name=form.buttons.save
    Page Should Contain  Item created
    Page should contain  ${title}
    ${location} =  Get Location
    [return]  ${location}
