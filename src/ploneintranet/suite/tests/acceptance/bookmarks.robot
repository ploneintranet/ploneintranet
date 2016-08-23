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

User can bookmark an app
    Given I am logged in as the user allan_neece
     Then I can bookmark the application  Case manager

User can unbookmark an app
    Given I am logged in as the user allan_neece
     Then I can unbookmark the application  Bookmarks

User can bookmark a workspace
    Given I am logged in as the user allan_neece
     Then I can bookmark the workspace  Service announcements

User can unbookmark a workspace
    Given I am logged in as the user allan_neece
     Then I can unbookmark the workspace  Shareholder information

User can bookmark a workspace document
    Given I am in a workspace as a workspace member
     Then I can bookmark the workspace document  Public bodies reform

User can unbookmark a workspace document
    Given I am in a workspace as a workspace member
     Then I can unbookmark the workspace document  Budget Proposal

User can bookmark a task
    Given I am logged in as the user allan_neece
     Then I can bookmark the task  Budget

User can unbookmark a task
    Given I am logged in as the user allan_neece
     Then I can unbookmark the task  Draft proposal

User can filter bookmarked applications
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can filter bookmarked application

User can filter bookmarked contents
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can filter bookmarked content

User can see bookmarks grouped by workspace
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can see bookmark grouped by workspace

User can see bookmarks grouped by creation date
    Given I am logged in as the user allan_neece
    Then I can go to the bookmark application
    Then I can see bookmark grouped by creation date

User can see bookmarked applications
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can see the bookmarked applications

User can see bookmarked workspaces
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can see the bookmarked workspaces

User can see bookmarked documents
    Given I am logged in as the user allan_neece
     Then I can go to the bookmark application
     Then I can see the bookmarked documents

User can use the bookmarks tile
    Given I am logged in as the user allan_neece
     Then I can see the bookmarks tile in the dashboard
     Then I can query the bookmarks tile for  minutes
      And I can see in the bookmark tile that the last bookmark is  Minutes Overview
     Then I can query the bookmarks tile for  walrus
      And I can see in the bookmark tile that we have no bookmarks matching  walrus

*** Keywords ***

# See lib/keywords.robot in the section "case related keywords"
