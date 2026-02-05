# Missing Persons Agent
Create AI models for predicting behavior and define code that do tasks related to finding missing people.  
Need READ ONLY APIs that supply data for missing people and emergency alerts.  
Need the best up to date APIs.  

## Drupal Module
I just started work on this module as of 02-04-2026. [Sentinel](https://www.drupal.org/project/sentinel)

## Models

## Code
Define the area based upon distance able to travel in a time frame by car. Start from estimated time of found missing. Build circles starting from ground zero. Send email alerts to gas stations, markets, restaraunts, hotels, hospitals and shelters in those areas. Update to larger areas as the search progresses.  

## Ideas
Create an API endpoint that can load email lists to send the alerts to.  
Send it forward email campaign. Have every person who recieve the email alert send it to all of their people they send emails to..  
A bunch of downloadable modules and plugins for Wordpress, Drupal etc.. that can do all of the emailing from your website..  
The module could pull from a missing persons database and list people who are reported missing in your area, city, county, state. It could also warn if a flood is comming, hurricaine, tornadoes all of it.  
You then have an oportunity to send the link of the alert to your clients in an email.  
  
Surveillance that can be accessed by a program that takes available video footage and run facial recognition on it.  
Build a standard into security firmware that allows access via API so anyone searching can access it for read only.  
Have software on the camera that does the facial recognition and can be updated with new faces when an alert goes out.  

Search for people who have been missing for a long time in different countries. USA, Mexico, Canada etc..
Look up all places that have public records about people to search through.

## Data APIs
FEMA Public Alert Warning System - [FEMA](https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system)  
Missing Persons Database API - [namus](https://nij.ojp.gov/namus)  
FEMA Github Emaple API calls - [FEMA Github](https://github.com/FEMA/openfema-samples)  

## Updates
### FEMA update 02-05-2026
I signed up for the developer account at FEMA so I can use the IPAWS Api to build a page to warn people of **floods, huricaines and tornadoes** of every drupal site that uses the module. Its will also allow the admin to add alerts to emails so they can email their clients in the event of an emergency in their area. It should possibly have people check if their buildings are in a flood zone. Its going to take a couple days to get approved.  

### namus update 02-05-2026
**I asked google AI:** Write a php script to use NamUs API to get a list of missing persons in california that have only been missing in the last week.  
**I got this response:**
It is not possible to write a direct PHP script using the NamUs API as described because the
NamUs system does not have a public-facing API for automated data retrieval. While the database is publicly accessible and searchable by individuals and professionals, programmatic access through an API for fetching large, filterable datasets (such as missing persons in a specific state within a specific time frame) is not available to the general public.  
  
**Can we open an endpoint for read only data** so I can build a module that creates pages on all Drupal sites? I want to also have it train people to be on the lookout for people who are missing by having them look at peoples images, think about the image, then print and carry a paper with the missing peoples images with them to cross reference if they are unsure.  
