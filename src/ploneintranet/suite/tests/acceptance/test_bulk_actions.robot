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

A member can only bulk change the metadata the items they are allowed to edit
    Given I am logged in as the user guy_hackey
      And I go to the Open Market Committee Workspace
      And I open the sidebar documents tile
      And I can create a new document  Do not touch me
      And I submit the content item
      And I can create a new document  Change me
      And I toggle the bulk action controls
      And I add an item to the cart  Do not touch me
      And I add an item to the cart  Change me
      And I choose to change the metadata for the items in the cart
     Then I cannot change the metadata for Do not touch me
      And I can change the metadata for Change me

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

A content editor can bulk rename an item
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


A member can bulk publish documents
    Given I am logged in as the user christian_stoney
      and I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      When I open the document  Customer satisfaction survey
      then I can see the item is in state  Draft
      When I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Terms and conditions
      and I add an item to the cart  Customer satisfaction survey
      and I choose to change the workflow state of the items to  Published
      Then I go to the Service Announcements Workspace
      and I open the sidebar documents tile
      When I open the document  Customer satisfaction survey
      then I can see the item is in state  Published


A member can bulk publish documents in a subfolder
      Given I am logged in as the user christian_stoney
      and I go to the Open Market Committee Workspace
      When I browse to a file
      then I can see the item is in state  Draft
      Then I go to the Open Market Committee Workspace
      and I open the sidebar documents tile
      and I toggle the bulk action controls
      and I add an item to the cart  Manage Information
      and I add an item to the cart  Files for application 2837
      and I choose to change the workflow state of the items to  Published
      When I browse to a file
      then I can see the item is in state  Published

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
    I add an item to the cart  Minutes
    I choose to delete the items in the cart
    I confirm to delete the items
    Wait Until Page Contains  The following items have been deleted

I can cut the Minutes word document
    I add an item to the cart  Minutes
    I choose to cut the items in the cart
    Wait Until Page Contains  1 Files were cut and moved to your cloud clipboard.

I add an item to the cart
    [arguments]  ${title}
    Click Element  xpath=//strong[text()[contains(., "${title}")]]//ancestor::label/input

I choose to delete the items in the cart
    # Click Element  css=div#batch-more  ## For whatever reason, this doesn't work in test, only in live
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  css=div.panel-content button.icon-trash
    Wait for injection to be finished

I choose to change the metadata for the items in the cart
    # Click Element  css=div#batch-more  ## For whatever reason, this doesn't work in test, only in live
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  css=div.panel-content button.icon-pencil
    Wait for injection to be finished

I cannot change the metadata for Do not touch me
     Page should contain  You cannot change the metadata of the following items.
     Page should contain element   jquery=.change-metadata label:contains('Do not touch me')

I can change the metadata for Change me
    Input Text  jquery=.change-metadata .title > input  I changed you
    Input Text  jquery=.change-metadata textarea  and I added a description
    Input Text  xpath=//input[@placeholder='Enter a label']/../div//input  press
    Wait Until Element is Visible  jquery=.select2-match:contains('press')
    Click element  jquery=.select2-match:contains('press')
    Click element  css=#form-buttons-send
    Wait Until Page Contains  The following items have been updated: I changed you

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
    Wait for injection to be finished
    Input Text  xpath=//input[@placeholder='Enter a label']/../div//input  ${tag},
    Click button  Tag

I choose to rename the items in the cart
    [arguments]  ${old_title}  ${title}
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Rename']
    Wait for injection to be finished
    Input Text  xpath=//input[@placeholder='${old_title}']  ${title}
    Click button  form-buttons-send

I choose to archive the items in the cart
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Archive']

I choose to download the items in the cart
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Download']

I choose to change the workflow state of the items to
    [arguments]  ${transition}
    Execute Javascript  $('#batch-more .panel-content').show()
    Click Element  xpath=//div[contains(@class, 'batch-functions')]//button[text()='Change the workflow state']
    Wait for injection to be finished
    Select From List  css=select[name=transition]  Published
    Click button  form-buttons-send
    Wait until page contains  The workflow state of the following items has been changed:

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
    Wait until page does not contain element  xpath=//strong[@class='title'][text()[contains(., '${title}')]]//abbr[text()='(Archived)']
I do see an archived item
    [arguments]  ${title}
    Wait until page contains element  xpath=//strong[@class='title'][text()[contains(., '${title}')]]//abbr[text()='(Archived)']

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

I can download items
    Wait Until Page Contains  will be downloaded

I cannot download items
    Wait Until Page Contains  This object is a folder and cannot be downloaded
