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

Member can change the title of a document
    Given I am in a workspace as a workspace member
    And I browse to a document
    And I change the title
    And I view the document
    The document has the new title

Member can change the description of a document
    Given I am in a workspace as a workspace member
    And I browse to a document
    And I change the description
    And I view the document
    Then the document has the new description

Member can tag a document
    Given I am in a workspace as a workspace member
    And I browse to a document
    And I tag the item  DocumentNewTag☃
    And I view the document
    Then the metadata has the new tag

Member can tag a document with a tag suggestion
    Given I am in a workspace as a workspace member
    And I browse to a document
    And I tag the item  SuggestDocumentNewTag☃
    And I clear the tag for an item
    And I tag the item with a suggestion  NewT  SuggestDocument
    Then the metadata has the new tag

Member can change the title of an image
    Given I am in a workspace as a workspace member
    And I browse to an image
    And I change the title
    And I view the image
    Then the document has the new title

Member can change the description of an image
    Given I am in a workspace as a workspace member
    And I browse to an image
    And I change the description
    And I view the image
    Then the document has the new description

Member can tag an image
    Given I am in a workspace as a workspace member
    And I browse to an image
    And I tag the item  ImageNewTag☃
    And I view the image
    Then the metadata has the new tag

Member can replace an image
    [Tags]  noncritical
    Given I am in a workspace as a workspace member
    And I browse to an image
    And I upload a new image

Member can tag an image with a tag suggestion
    Given I am in a workspace as a workspace member
    And I browse to an image
    And I tag the item  SuggestImageNewTag☃
    And I clear the tag for an item
    And I tag the item with a suggestion  NewT  SuggestImage
    Then the metadata has the new tag

Member can change the title of a file
    Given I am in a workspace as a workspace member
    And I browse to a file
    And I change the title
    And I view the file
    Then the document has the new title

Member can change the description of a file
    Given I am in a workspace as a workspace member
    And I browse to a file
    And I change the description
    And I view the file
    Then the document has the new description

Member can tag a file
    Given I am in a workspace as a workspace member
    And I browse to a file
    And I tag the item  FileNewTag☃
    And I view the file
    Then the metadata has the new tag

Member can replace a file
    [Tags]  noncritical
    Given I am in a workspace as a workspace member
    And I browse to a file
    And I upload a new file


Member can tag a file with a tag suggestion
    Given I am in a workspace as a workspace member
    And I browse to a file
    And I tag the item  SuggestFileNewTag☃
    And I clear the tag for an item
    And I tag the item with a suggestion  NewT  SuggestFile
    Then the metadata has the new tag

Member cannot see delete button on a read only document
    Given I am in a Consumers workspace as a workspace member
    Click link  link=Documents
    Wait Until Page Contains Element  jquery=#items .item.document .title:contains("Test Document")
    Click Element  jquery=#items .item.document .title:contains("Test Document")
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Wait Until Page Contains  Published
    Element should not be visible  xpath=//a[contains(@href, 'delete_confirmation#document-content')]

Member can see delete button on an editable document
    Given I am in a workspace as a workspace member
    And I browse to a document
    Wait Until Page Contains  Draft
    Click Element  css=div.quick-functions a.icon-ellipsis
    Wait until Page Contains Element  xpath=//a[contains(@href, 'delete_confirmation#document-content')]

Member can steal the lock of a document
    Given I am logged in as the user allan_neece
     Then I can lock a document
     When I am logged in as the user christian_stoney
     Then I can see the document is locked
      And I can see who locked the document
      And I can start a conversation with the lock owner
      And I can steal the lock

# Member can change the title of a folder
#     Given I am in a workspace as a workspace member
#     And I view the folder
#     And I change the title
#     And I view the folder
#     Then the document has the new title

# Member can change the description of a folder
#     Given I am in a workspace as a workspace member
#     And I view the folder
#     And I change the description
#     And I view the folder
#     Then the document has the new description

# Member can tag a folder
#     Given I am in a workspace as a workspace member
#     And I view the folder
#     And I tag the item
#     And I view the folder
#     Then the metadata has the new tag

*** Keywords ***

# See lib/keywords.robot in the section "workspace and case content related keywords"

I can lock a document
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/repurchase-agreements/@@plone_lock_operations/create_lock

I can see the document is locked
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/repurchase-agreements/
    Page should contain element  jquery=.saving-badge.locked

I click on the locked badge
    Click element  jquery=.saving-badge.locked
    Wait for injection to be finished

I can see who locked the document
    I click on the locked badge
    Click Element  css=.pat-message.warning > a.close-panel.pat-modal
    Wait for injection to be finished
    Click Element  css=#pat-modal button.close-panel

I can start a conversation with the lock owner
    I click on the locked badge
    Click element  css=.button-bar > a.icon-chat
    Select Window  chat
    Page Should Contain Element  jquery=#chat-bar [placeholder="Write a message"]
    Close Window
    Select Window    main
    I click on the locked badge

I can steal the lock
    I click on the locked badge
    Click button  Unlock
