# Missing Persons Agent

I'm creating a installable application that is a tool to investigate a persons disappearance. It will initially use an Ollama RAG LLM and train it on any data that can be found on the people in the immediate family, friends, and acquaintances including the missing person. It will then look for connections to the person gone missing. Anyone will be able to download this and the idea is that you can get as many people as you can searching for the missing person. It will download and install both ollama and a model to use as the RAG LLM upon installation. The software is a website that runs in a browser so its immediately connected to use the internet for acquiring data. It will give you the ability to ethically scrape websites and add it to the LLM. It allows the user to create lists of people and aquire as much data as posible about them to cross reference and ask questions about using AI. I will keep updating this file as I come up with new ideas.

### Donate

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?hosted_button_id=J8WY5PDLWGK6Y)

I'm unemployed at the moment and looking for work. Help keep me going. Any support is appreciated. If you would be interested in helping or have ideas I'm open to help there also. If you are hiring I'm open to full time employment as a Full Stack Developer. Thanks.

### Links

Reading [Invisible Threads](https://blog.ry4n.org/invisible-threads-finding-missing-people-online-7dec4cb038e5).

### News Stations

- NBC News

LLM to take in news reports from news stations.
  - Look throuh news reports for people who may have been mad at you.
    - Gone to jail and got out recently.
    - Carear that may have been lost and could be looking for revenge.
    - If they lost family.
  - Get all information from reliable news outlets.
    - Look for missed information

### Social Media Accounts
  - Facebook

Build timeline for all family members and friend + in the immediate group and anyone they contacted.
  - Get any references to close friends.
  - Get all reference through bills to people she hired.
  - What services did she use?
    - Lawn Care
    - Pool Cleaners
    - Remodeling Contractors
    - Electricians
    - Sears
    - Delivery Drivers
    - Mail People
    - Phone
    - Internet and Cable.
    - etc..
  - Get list of phone calls she made.

Build out these timelines and then recursively build timelines for each person of interest found as a result of the initial investigation.
  - Look for people whos timeline ends in the close proximity of the missing person.
  - Check what they bought.
  - Who they called.
  - GPS of their phones.

### Image Recognition

- Look through images for people you do not know that show up multiple times.
- Make a list of the people and the number of times they are seen in all images
- Look for them on the public images in google to try to name them.

### Missing Persons Favorite Things
  - Favorite Websites?
  - What where their interests?
  - Favorite Stores
    - Get a list of the clerks that worked there before the disappearence.
    - See if any went missing in the days following the disappearance.

Get a list of phone calls and emails that the person missing called and/or sent.
  - Get the identities of the people they where talking to.

Create timelines on everyone.

Time of disappearance - get what people of interest are reported doing.
  - Looking for people with records.
  - People with motives.

### Ideas

Working on the database implementation.
 - Every time interval search for new data. Daily?
 - Have prompt ask a list of specific questions.
 - Flag recent updates of interest, save it to a database, notify user of entries.

List all people starting with the main family and working through everyone they know. Get their purchasing history for 3  to 6 months maybe a year before the person turns up missing. Seems like a few weeks would be a good start then go furthur back on the purchase history when nothing turns up.

List all the places that you or the missing individual have worked and get the archived text to feed to an LLM. Then through prompt enginearing create specific questions geared to uncovering people with motive.

Build the same for all the persons favorite events if there are recordings.

Build one for social media posts from each social media platform.

Somewhere out there there may be a person or group of people having a digital conversation about what they should be doing. What platforms might they use? Discord, Google Meet, Microsoft Teams, Messaging services, etc... Create RAG LLMs that can pull text that reference the missing persons name in it.. How can it be intercepted? Can you petition to look through records in the companies database for references that might suggest nefarious behavior?

There may be somebody trying to apply for life insurance, credit cards, and/or loans on them. Keep an eye on that.

### Plan

Think its better to use a single model that uses each of the line items as a feature.
  - buying products that could be used in a crime. Duck tape, rope, weapons, ski mask, gloves, etc..
  - large expense deducted from bank account in cash or transfered to another account.
  - Renting a rent a car
  - buying gas closer to the crime scene
  - mobile phone GPS tracking close to the crime scene
  - car GPS tracking close to the crime scene

Need a warrent to see peoples financial statements and gps of their whereabouts and you need probable cause to get the search warrent.

What other things can AI do before that happens?

Thought for a moment Web Scraping Web was illegal. But if done ethically and takes into consideration the robot.txt. onward!

Web Scraper Idea:
 - Create a RAG LLM like this - [Build a RAG web scraper using Langchain, Ollama, ChromaDB](https://www.youtube.com/watch?v=0zgYu_9WF7A)
 - Create a database to store sites to scrape so a user can add them.
 - Ask all your family, friends, relatives that can to create a list of sites to scape and coordinate between the searchers.
 - I'll work on some kind of a way to consolidation everyones searchs or you can just stay in touch with your team and review each others results.
 - Put the scrapper on a cron so it scrapes for any talk about the missing person every day.
 - You should ask people to help that own big sites like messenger or private messenging apps to keep an eye out for people talking about the missing person.
 - Have state hold a person and searching to work on the person held in state. Have searches for public records and other publicly accessable accounts.
 - Then Train the model on all the people involved so you can prompt the LLM to look for connections.
 - You define questions and Prompt the LLM everyday if you like with questons that are engineered to find the most relevant conversations.
 - Create an application style tool where none coders can use beatiful soup and model traning to scrape the internet for information.
 - Use pyinstaller once finished to create a executable so none programmers can install and use.
