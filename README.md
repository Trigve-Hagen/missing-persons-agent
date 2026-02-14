# Missing Persons Agent
Create AI models for predicting behavior and define code that do tasks related to finding missing people.  
Need READ ONLY APIs that supply data for missing people and emergency alerts.  
Need the best up to date APIs.  

## Drupal Module
I just started work on this module as of 02-04-2026. [Sentinel](https://www.drupal.org/project/sentinel)  
**Sentinel** "A soldier or guard whose job is to stand and keep watch."

## Models
Model that takes all the persons social media accounts and predics if a friend would have something to do with it based upon posts.  
Model that looks for patterns in prior cases.  

## Code
Define the area based upon distance able to travel in a time frame by car. Start from estimated time of found missing. Build circles starting from ground zero. Send email alerts to gas stations, markets, restaraunts, hotels, hospitals and shelters in those areas. Update to larger areas as the search progresses. 

## Ideas
Create an API endpoint that can load email lists to send the alerts to them.  
Send it forward email campaign. Have every person who recieve the email alert send it to all of their people they send emails to..  
Modules and plugins for Wordpress, Drupal etc.. that can do all of the emailing from your website..  
The module could pull from a missing persons database and list people who are reported missing in your area, city, county, state. It could also warn if a flood is comming, hurricaine, tornadoes all of it.  
You then have an oportunity to send the link of the alert to your clients in an email.  

Search for people who have been missing for a long time in different countries. USA, Mexico, Canada etc..
Look up all places that have public records about people to search through.

## Data APIs
FEMA Public Alert Warning System - [FEMA](https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system)  
Missing Persons Database API - [NamUs](https://nij.ojp.gov/namus)  
FEMA Github Emaple API calls - [FEMA Github](https://github.com/FEMA/openfema-samples)  

## Updates
### FEMA update 02-05-2026
I signed up for the developer account at FEMA so I can use the IPAWS Api to build a page to warn people of **floods, huricaines and tornadoes** on every drupal site that uses the module. Its will also allow the admin to add alerts to emails so they can email their clients in the event of an emergency in their area. It should possibly have people check if their buildings are in a flood zone. Its going to take a couple days to get approved.  

### NamUs update 02-05-2026
**I asked google AI:** Write a php script to use NamUs API to get a list of missing persons in california that have only been missing in the last week.  
**I got this response:**
It is not possible to write a direct PHP script using the NamUs API as described because the
NamUs system does not have a public-facing API for automated data retrieval. While the database is publicly accessible and searchable by individuals and professionals, programmatic access through an API for fetching large, filterable datasets (such as missing persons in a specific state within a specific time frame) is not available to the general public.  
  
**Can we open an endpoint for read only data** so I can build a module that creates pages on all Drupal sites? I want to also have it train people to be on the lookout for people who are missing by having them look at peoples images, think about the image, then print and carry a paper with the missing peoples images with them to cross reference if they are unsure. I only need name, image, brief description of what they where last wearing, hair and eye color, height etc.. Anything that would help someone identify the individual. Thanks!  

### NamUs update 02-06-2026
Submitted a question asking for access to a public API for missing people.  
** Response same day: ** Thank you for your inquiry. Currently there is no endpoint access available for the National Missing and Unidentified Persons (NamUs) system.  

### FEMA update 02-12-2026
** Response: **  
Hello  
I am reaching out from FEMA IPAWS Technical Support Services.  
Are you interested in receiving and/or redistributing the alerts, warning and notification posted on the IPAWS All Hazards Information Feed?  
Here’s more information online for potential new vendors and developers Technology Vendors & Developers | FEMA.gov  
I can better assist once I understand if you are trying to be an Origination Developer and/or Redistribution Developer for IPAWS.  
The Alert Origination Software Providers (AOSP vendors) are the only Developer type required to complete MOA Application in the IPAWS Users Portal.  
Here’s a listing of AOSPs vendors that have successfully demonstration their IPAWS capabilities - Demonstrated IPAWS Capabilities - Alert Origination Software Providers  
Let me know if you have further IPAWS questions or concerns to further assist with your needs!  
Thank you  

** I Resonded: **  
I just want to be a  Redistribution Developer for IPAWS.I only need read access to display on a module developed for drupal called Sentinel:  
https://www.drupal.org/project/sentinel  
  
My plan is here.  
https://github.com/Trigve-Hagen/missing-persons-agent/blob/main/README.md  
  
Thanks.  

### NamUs update 02-14-2026
Registered to be a user on NamUs site so I can recieve content. Will see if I can talk with the people who run the website to get an API built that allows content that is released by Law Enforcement to be available on a read only API.  
If it was there now we could have the description of the Walmart backpack guy who abducted Nancy Guthrie up on every site that uses this module.  
** Response same day: ** They sent me an email almost immediately to register. Go to say they are awesomely prompt about stuff.  

** I Registered created a Contact Us where I asked **  
I would like to create an API endpoint for you. I work for the ** where I work ** as a Drupal developer. I would like to create the code block that would allow publicly viewable data via an API. If you send me the as parameters, you can make available and the type of code you need Module for Drupal, etc.. I can create the API endpoint as a module that you can install on whatever website you would use to offer up the API. My goal is to help find Nancy Guthrie and other missing people such as her. Thanks. I will build it for free.  
  
A request would resemble: https://developer.paypal.com/api/rest/requests/  
A response would resemble: https://developer.paypal.com/api/rest/responses/  



