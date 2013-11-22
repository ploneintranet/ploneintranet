*** Keywords ***

Add dexterity content
    [arguments]  ${content_type}  ${title}
    Open add new menu
    Click link  link=${content_type}
    Input Text  xpath=//form//div/input[preceding-sibling::label[contains(text(), 'Title')]]  ${title}
    Click button  name=form.buttons.save
    Page should contain  Item created
    Page should contain  ${title}
    ${location} =  Get Location
    [return]  ${location}
