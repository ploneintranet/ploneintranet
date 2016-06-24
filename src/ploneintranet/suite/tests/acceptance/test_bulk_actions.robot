*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  ../lib/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  DebugLibrary

Test Setup  Prepare test browser
Test Teardown  Close all browsers

*** Test Cases ***

Content Editors can copy and paste content
   Given I am logged in as the user christian_stoney
     and I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
     and I can enter the Manage Information Folder
    when I toggle the bulk action controls
    then I can copy the Minutes word document
    when I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
    when I toggle the bulk action controls
    then I can paste the Minutes word document
    when I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
    then I can enter the Projection Materials Folder
    when I toggle the bulk action controls
    then I can paste the Minutes word document
    when I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
    when I toggle the bulk action controls
    then I can delete the Minutes word document
    when I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
     and I can enter the Projection Materials Folder
    when I toggle the bulk action controls
    then I can cut the Minutes word document
    when I go to the Open Market Committee Workspace
     and I open the sidebar documents tile
    when I toggle the bulk action controls
    then I can paste the Minutes word document

A member can only bulk delete the items they are allowed to delete
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I go to the Open Parliamentary Papers Guidance Workspace
      and I open the sidebar documents tile
      and I can create a new document  Deletable doc
      and I save the document
      and I toggle the bulk action controls
      and I add an item to the cart  Deletable doc
      and I choose to delete the items in the cart
     then I confirm to delete the items
      and I see a message that items have been deleted  "Deletable doc"
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I can see the document  Terms and conditions

A member can only cut items they are allowed to delete
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to cut the items in the cart
     then I see a message that I cannot cut  "Terms and conditions"

A member can paste items where they are allowed to add content
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to copy the items in the cart
      and I see a message that files have been copied
      and I see that the paste button is disabled
      and I go to the Open Parliamentary Papers Guidance Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I choose to paste the items in the cart
      and I see a message that items have been pasted

A member can send items by email
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to send the items in the cart
      and I choose to send items to alice_lindstrom
      and I choose to include a message
      and I send the items
     then I see a message that an email has been sent


*** Keywords ***

I toggle the bulk action controls
    # Yes, adding Sleep is very ugly, but I see no other way to ensure that
    # the sidebar and the element we need has really completely loaded
    Sleep  2
    Wait Until Element is Visible  xpath=//div[@id='selector-functions']//a[text()='Select']
    Click link  xpath=//div[@id='selector-functions']//a[text()='Select']
    Wait Until Element is Visible  xpath=//div[@class='batch-functions']//button[text()='Copy']

I can copy the Minutes word document
    I add an item to the cart  Minutes
    I choose to copy the items in the cart
    Wait Until Page Contains  1 Files were copied to your cloud clipboard.

I can paste the Minutes word document
    Wait Until Element is Visible  xpath=//div[@class='batch-functions']//button[text()='Paste']
    I choose to paste the items in the cart
    Wait Until Page Contains  Item(s) pasted

I can delete the Minutes word document
    Click Element  xpath=//strong[text()="Minutes"]//ancestor::label/input
    I choose to delete the items in the cart
    I confirm to delete the items
    Wait Until Page Contains  The following items have been deleted

I can cut the Minutes word document
    Click Element  xpath=//strong[text()="Minutes"]//ancestor::label/input
    I choose to cut the items in the cart
    Wait Until Page Contains  1 Files were cut and moved to your cloud clipboard.

I add an item to the cart
    [arguments]  ${title}
    Click Element  xpath=//strong[text()="${title}"]//ancestor::label/input

I choose to delete the items in the cart
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Delete']

I choose to cut the items in the cart
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Cut']

I choose to copy the items in the cart
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Copy']

I choose to paste the items in the cart
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Paste']

I choose to send the items in the cart
    Click Element  xpath=//div[@class='batch-functions']//button[text()='Send']

I choose to send items to alice_lindstrom
    Wait Until Page Contains Element  xpath=//input[@placeholder='Recipients...']
    Input Text  xpath=//input[@placeholder='Recipients...']/../div//input  alice
    Wait Until Page Contains Element  jquery=span.select2-match:last
    Click Element  jquery=span.select2-match:last

I choose to include a message
    Input Text  xpath=//textarea[@name='message']  You're gonna ♥ this

I send the items
    Click button  xpath=//button[@id='form-buttons-send']

I confirm to delete the items
    Wait Until Page Contains  I am sure, delete now
    Click button  I am sure, delete now

I save the document
    Click button  Save

I see a message that items have been deleted
    [arguments]  ${title}
    Wait Until Page Contains  The following items have been deleted: ${title}

I see a message that files have been copied
    Wait Until Page Contains  Files were copied to your cloud clipboard

I see a message that items have been pasted
    Wait Until Page Contains  Item(s) pasted

I see a message that I cannot cut
    [arguments]  ${title}
    Wait Until Page Contains  The following items could not be cut: ${title}

I see a message that an email has been sent
    Wait Until Page Contains  Email sent.

I see that the paste button is disabled
    Wait Until Element is Visible  xpath=//div[@class='batch-functions']//button[text()='Paste'][@disabled='disabled']
