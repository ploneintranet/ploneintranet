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

# https://github.com/quaive/ploneintranet/issues/617
A member can only bulk delete the items they are allowed to delete
    [Tags]  fixme
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

# https://github.com/quaive/ploneintranet/issues/617
A content editor can bulk rename an item
    [Tags]  Heisenbug
    Given I am logged in as the user christian_stoney
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to rename the items in the cart  Terms and conditions  Terms and conditions 1
      and I see a message that some items have been renamed
      and I add an item to the cart  Terms and conditions 1
      and I choose to rename the items in the cart  Terms and conditions 1  Terms and conditions
     then I see a message that some items have been renamed

A viewer cannot bulk retag an item
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to retag the items in the cart  bulk_tag
     then I see a message that no items have been tagged

A content editor can bulk retag an item
    Given I am logged in as the user christian_stoney
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to retag the items in the cart  bulk_tag
     then I see a message that some items have been tagged

A content editor can bulk archive an item
    Given I am logged in as the user christian_stoney
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I can create a new document  Archivable doc
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Archivable doc
      and I choose to archive the items in the cart
     then I see a message that items have been archived
      and I open the sidebar documents tile
     then I don't see an archived item  Archivable doc
      and I show archived items
     then I do see an archived item  Archivable doc

A member can subscribe to changes of a document
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to subscribe the items in the cart
     then I see a message that I am subscribed

A member can bulk download a document
    Given I am logged in as the user guy_hackey
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I choose to download the items in the cart
     then I can download items

A member can't bulk download a folder
    Given I am logged in as the user guy_hackey
      and I go to the Open Market Committee Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Projection Materials
      and I choose to download the items in the cart
     then I cannot download items


*** Keywords ***

I toggle the bulk action controls
    # Yes, adding Sleep is very ugly, but I see no other way to ensure that
    # the sidebar and the element we need has really completely loaded
    Sleep  2
    Wait Until Element is Visible  xpath=//div[@id='selector-functions']//a[text()='Select']
    Click link  xpath=//div[@id='selector-functions']//a[text()='Select']
    Wait Until Element is Visible  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Copy']

I can copy the Minutes word document
    I add an item to the cart  Minutes
    I choose to copy the items in the cart
    Wait Until Page Contains  1 Files were copied to your cloud clipboard.

I can paste the Minutes word document
    Wait Until Element is Visible  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Paste']
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
    # Click Element  css=div#batch-more  ## For whatever reason, this doesn't work in test, only in live
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  css=div.panel-content button.icon-trash
    Wait until element is visible  xpath=//div[@class="pat-modal"]//h1[text()="Batch delete"]

I choose to cut the items in the cart
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Cut']

I choose to copy the items in the cart
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Copy']

I choose to paste the items in the cart
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Paste']

I choose to send the items in the cart
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Send']

I choose to send items to alice_lindstrom
    Wait Until Page Contains Element  xpath=//input[@placeholder='Recipients...']
    Input Text  xpath=//input[@placeholder='Recipients...']/../div//input  alice
    Wait Until Page Contains Element  jquery=span.select2-match:last
    Click Element  jquery=span.select2-match:last

I choose to include a message
    Input Text  xpath=//textarea[@name='message']  You're gonna ♥ this

I choose to retag the items in the cart
    [arguments]  ${tag}
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Re-tag']
    Wait until element is visible  xpath=//div[@class="pat-modal"]//h1[text()="Batch (re)tagging"]
    Input Text  xpath=//input[@placeholder='Enter a label']/../div//input  ${tag},
    Click button  Tag

I choose to rename the items in the cart
    [arguments]  ${old_title}  ${title}
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Rename']
    Wait until element is visible  xpath=//div[@class="pat-modal"]//h1[text()="Batch rename"]
    Input Text  xpath=//input[@placeholder='${old_title}']  ${title}
    Click button  form-buttons-send

I choose to archive the items in the cart
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Archive']

I choose to subscribe the items in the cart
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Subscribe']

I choose to download the items in the cart
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Download']

I send the items
    Click button  xpath=//button[@id='form-buttons-send']

I confirm to delete the items
    Wait Until Page Contains  I am sure, delete now
    Click button  I am sure, delete now

I save the document
    Click button  Save
    Wait until page does not contain element  xpath=//div[@id='application-body' and contains(@class, 'injecting-content')]

I show archived items
    Execute Javascript  jquery=$('#more-menu .panel-content').show()
    Select checkbox  xpath=//input[@name='show_archived_documents']

I don't see an archived item
    [arguments]  ${title}
    Wait until page does not contain element  xpath=//strong[@class='title'][text()='${title}']

I do see an archived item
    [arguments]  ${title}
    Wait until page contains element  xpath=//strong[@class='title'][text()='${title}']

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

I see a message that no items have been tagged
    Wait Until Page Contains  No items could be (re)tagged

I see a message that some items have been tagged
    Wait Until Page Contains  The following items have been (re)tagged

I see a message that no items have been renamed
    Wait Until Page Contains  No items could be renamed

I see a message that some items have been renamed
    Wait Until Page Contains  The following items have been renamed

I see a message that items have been archived
    Wait Until Page Contains  The following items have been archived

I see a message that I am subscribed
    Wait Until Page Contains  You have been subscribed to this item

I can download items
    Wait Until Page Contains  will be downloaded

I cannot download items
    Wait Until Page Contains  This object is a folder and cannot be downloaded
