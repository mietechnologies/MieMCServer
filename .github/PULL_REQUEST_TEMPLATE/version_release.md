---
name: Version Release
about: Please use this pull request template when preparing for a version release.
---

## Release Version
<!--Please indicate what version you are preparing for release below.-->


## Further Steps
After this pull request has been approved and merged, certain steps should be completed. 
These are listed in order below for your convenience:
- Create release for this version via GitHub.
  - Use this version for release tag and title (i.e, v1.3.0).
  - Write short description of changes and copy CHANGELOG for this version for body.
  - **IMPORTANT:** If there are any breaking changes contained when installing this version from the last, please:
    - Note these between the short description and CHANGELOG.
    - If there are any known fixes that the user can do to overcome these breaking changes, note them.
  - Use latest commit for release target (**NOT latest main**).
- Prune any dev and release branches related to this version.
- Close the project board associated with the release version **PRIOR** to this version.
  - For example, if you are releasing v1.6.0, the v1.5.0 board should be closed.
- Create new release branch for the next major version number from latest main.
  - For example, `v1.3.0` or `v1.4.0`, but never a patch version (i.e., `v1.3.1`).
