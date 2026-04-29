# Missing Persons Agent
This will run on any person who downloads its local computer and without coding you will be able to get it up and running and manage it from a form allowing anyone you want to help you work with it.

Create AI models for predicting behavior and define code that do tasks related to finding missing people.
Need READ ONLY APIs that supply data for missing people and emergency alerts.
Need the best up to date APIs.

### Update 04-25-2026

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

### Update 04-26-2026

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

### Update 04-28-2026

Think its better to use a single model that uses each of the line items as a feature.
  - buying products that could be used in a crime. Duck tape, rope, weapons, ski mask, gloves, etc..
  - large expense deducted from bank account in cash or transfered to another account.
  - Renting a rent a car
  - buying gas closer to the crime scene
  - mobile phone GPS tracking close to the crime scene
  - car GPS tracking close to the crime scene

Need a warrent to see peoples financial statements and gps of their whereabouts and you need probable cause to get the search warrent.

What other things can AI do before that happens?

Thought for a moment Web Scraping Web was illegal. But if done ethically and takes into consideration the robot.txt. So onward!

Web Scraper Idea:
 - Create a RAG LLM like this - [Build a RAG web scraper using Langchain, Ollama, ChromaDB](https://www.youtube.com/watch?v=0zgYu_9WF7A)
 - Create a database to store sites to scrape so a user can add them.
 - Ask all that can to take a list of sites to scape and coordinate between the searchers.
 - Put the scrapper on a cron so it scrapes for any talk about the missing person every day.
 - Ask people to help that own big sites so it can be done legally.
 - You define questions and Prompt the LLM everyday if you like with questons that are engineered to find the most relevant conversations.
 - Create an application style tool where none coders can use beatiful soup and model traning to scrape the internet for information.
 - Use pyinstaller once finished to create a executable so none programmers can install and use.
