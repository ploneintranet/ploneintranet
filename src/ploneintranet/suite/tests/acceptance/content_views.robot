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
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'test-document')]
    Click Element  xpath=//a[contains(@href, 'test-document')]
    Wait Until Page Contains  Published
    Element should not be visible  xpath=//a[contains(@href, 'delete_confirmation#content')]

Member can see delete button on an editable document
    Given I am in a workspace as a workspace member
    And I browse to a document
    Wait Until Page Contains  Draft
    Element should be visible  xpath=//a[contains(@href, 'delete_confirmation#content')]

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
