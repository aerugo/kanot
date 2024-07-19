# Kanot
## An AI-powered annotation tool by Knowbe

![Kanot Logo](https://github.com/user-attachments/assets/38d7af27-11ce-4ba6-941a-07218e6dbe8a)

## TODO 

### Path to preview launch

- [x] Refactor project to use SvelteKit
- [x] Enable batch removal of tags
- [ ] Automatic code creation and annotation flow with LLM
- [ ] Command line scripts for auto annotion
- [ ] Show project code co-occurrence graph, filter by co-occurrence count
- [ ] Export project as static site dashboard with data in JSON

### All tasks

Refactoring
- [x] Refactor project to use SvelteKit

UX and Actions
- [x] Enable batch removal of tags
- [ ] Create and apply new code through dropdown
- [ ] Project switching
- [ ] Show code and its annotations

Autoannotate
- [ ] Automatic code creation and annotation flow with LLM
  - [ ] Add JSON few shot examples of annotations and codes to use when not enough examples in project
- [ ] UX to select elements for automatic annotation
- [ ] Automatic annotation processing task queue
- [ ] Implement action history log to track task progress
- [ ] Autoannotate task progress
- [ ] Autoannotate task running cost
- [ ] Autoannotate cancel task
- [ ] Autoannotate pick model
- [ ] Autoannotate configure prompt
  
Import 
- [ ] Upload transcript and split to elements
- [ ] Upload audio and transcribe to transcript and split to elements

Graph Viz
- [ ] Show project code co-occurrence graph, filter by co-occurrence count
- [ ] Enable filtering by series and segment

Code View
- [ ] Sort by number of annotations

Project Settings
- [ ] Define code fields on project level
- [ ] Define code types on project level
- [ ] Set which code fields to show as columns in list
  
Styles
- [ ] Harmonize styles across components
  
Kanot Cloud
- [ ] Make project multi-user
- [ ] Define user roles for projects
- [ ] Define workspaces
- [ ] Invite user to workspace
- [ ] Invite user to project

Publish 
- [ ] Export project as static site dashboard with data in JSON