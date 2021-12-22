<!-- The purpose of this document will be to remind ourselves as well as inform other developers of the workflow and processes of this project. A wiki will be created at a later date that hosts all of the information, so we're going to try to keep this document as lightweight as possible. -->

# MIE-MCServer
MIE-MCServer is intended to be a "one-stop shop" for running a private/public Minecraft server on any Linux system. This project should almost completely replace the need for a third-party service for anyone comfortable using terminal. Interacting with this application should be both as simple and as concise as possible.

## Project Setup and Requirements
Installing, running, and developing this project requires Python 3.9 installed on your system. Setup for this project is as easy as cloning the project and calling `python main.py` from the root directory of this project.

## New Features and Helping Out
This project is intended to be completely open-source and everyone is welcome to submit feature requests and implementations as well as any issues they find amongst it. 

If you intend to help out, please see the sections below on Feature Requirements and Pull Requests. If you've found an issue but don't want to solve it yourself for whatever reason, feel free to open an issue, but please read the Issues section below before you do.

### Feature Requirements
As features are added, please keep the following requirements in mind:
- The feature should have a simple accessor, typically in the form of a command argument
- The feature should fill a purpose or role that would typically otherwise be accomplished via one of the following methods:
    - Opening Minecraft, logging into the world, and issuing commands via Minecraft's chat
    - Using a file browser to manually move and/or edit files
    - Issuing other terminal commands to interact with the server and associated files
- More to come?

### Pull Requests
Big or small, we welcome any pull request that stands to make this project even better. When submitting your PR, please use the supplied [pull request template](link_to_pull_request_template). When a PR is reviewed, we will use the [pull request review template](link_to_pull_request_review_template), so please make sure that you follow the guidelines contained within the template.

### Issues
Bug reports and other issues are also welcome. If you encounter any issues while developing and/or using this project, please open an issue. When submitting your issue, please use the supplied [issue template](link_to_issue_template).