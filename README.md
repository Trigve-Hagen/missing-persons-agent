# Missing Persons Agent
On Off the cuff they talked about the suspect being someone who is doing ederly abuse or scamming the elderly. There are reports on the news about elderly people being coerced into moving their money from there accounts and loosing large amounts of money. You might want to investigate those to see if they might be connected. Also check if there is money being pulled from Nancy's accounts.

For the record I support the Pima County sheriffs department. I believe they and the FBI are doing a great job. I hope that everyone will work together to expidite finding Nancy Guthrie.

She would need a way to get medication possible in house doctor. Look for places selling the medicine she uses. People other than her filling her perscription. People other than the patient filling the prscription for people. Doctors or nurses missing days of work. A wheelchair to move her around. Search video survelance in the area for a person in a wheelchair.

Has anyone checked if there was a google maps request on the days before the Guthrie disappearance going to the Guthrie house? Everyone uses google maps for directions. Get a list of the people who went to her house if that's possible. Can phone or onstar systems be tracked in an area? Possible i-watch. Can you get a warrent for Apple and Google and other cell phone providers to possibly GPS track anyone in that area at the time of the doorbell camera? Other types of apps that could be used for directions besides google like hunting apps? And the car could have been parked a ways away. But they would need a car to take her away so any car roughly newer than 2010 has GPS tracking.

Almost any electronic device you carry or use regularly has GPS tracking or location-sharing capabilities. If police secure a warrant, they can utilize a vast network of personal devices, vehicle logs, and digital trails to definitively place a suspect at a specific crime scene or trace their exact route at any given time. Anything from computers to ez-pass to watches have GPS. Search google with: 'What all has GPS tracking? What could a criminal be carring that could give away where they where at a specific time if someone had a warrent?' It returns a list of electronics that could leave a trail.

The top navigation apps offer distinct advantages depending on your needs:
- Google Maps: The most comprehensive app with the best global coverage. It supports driving, cycling, walking, and public transit (like Metro and buses in the DC area), and offers great details on local businesses.
- Apple Maps: Built-in for all iOS devices, it features a clean interface, 3D city views, and helpful cycling details like steep hills.
- Waze: Highly regarded for commuting, it uses crowdsourced data to alert you of accidents, road hazards, and police activity.
- Specialty Apps: For off-the-grid trips without a data connection, offline apps like HERE WeGo work well. If you ride a bike frequently, specialized apps like Komoot are great for mapping trail

### Tracking Emails via C++
You cannot track a live email moving through the internet using C++, but you can write C++ code or analyze email binaries (raw .eml / .msg files) to uncover tracking mechanisms:
- 1. Parsing Email Headers - You can write a C++ program to parse the raw text header of an email. This reveals the digital footprint of the message:
  - Received Headers: Shows every server the email passed through.
  - IP Addresses: Exposes the originating server's location.
  - Timestamps: Tracks the exact time of transit between servers.
- 2. Detecting Tracking Pixels - Emails often contain hidden tracker images. You can use C++ to scan the binary or HTML content of an email for these elements:
  - Web Beacons: Tiny 1x1 transparent images embedded in HTML.
  - Unique URLs: Images hosted on strings like ://tracker.com.
  - Trigger Mechanism: When the victim opens the email, their client downloads the image, alerting the sender.
- 3. Analyzing Compiled Email Clients - If you are reverse-engineering a compiled binary (like a malicious email client or malware):
  - Hardcoded SMTP: Look for embedded strings showing server IPs or credentials.
  - API Calls: Search for network functions like connect() or socket libraries pointing to mail ports (25, 465, 587).

If someone is versed enough to remove tracking could they be a programmer?

### Does the video guy from Nancy Guthrie case hang out here in DC?

Today around 11:30am - 06/28/2026 I passed a guy who seemed to be around 28 years old, one arm sleeved with tattoos carring a black umbrella who seemed to have the same walk and feel as the guy in the Nancy Guthrie video. He was smoking weed. He was on Peabody Street one block from the Walmart as I was returning from the store on the McDonalds side of the street. I'm not sure whether to report this or not. It was more a sense than definitive and I don't want to be crying wolf if this is just some random chance that he resembles the guy. He seemed to be mexican, short hair on the side curled back on the top, 200 lbs 5 foot 10 inches.

This is the second time I thought I got a glimps of someone resembling the figure in the video. The first time was a couple of months ago and the person even entered the building I live in. Same body type and walk although then he had a hoody on.

Maybe video cameras on that Walmart corner can see if he is anything close to what they are looking for.

1:20pm I just reported it to the DC police.

## phi4
This is the best model I found to use for my laptop that has 8 + 16 GB RAM, 1 Terabyte of ROM and running on a CPU.

Missing Persons is a tool to investigate missing persons. Its built in python and uses pywebview to turn a flask website into a desktop application and then bundle it with pyinstaller into an executable that is installed using Inno. It uses [Ollama](https://ollama.com/download/windows) models. Ollama lets you build and work on an LLM model locally on your computer so you maintain your privacy.

If you are looking to upgrade to a new computer and you want to use missing persons I would recommend to get a computer with at least 16GB of VRAM and a Nvidia GPU proccessor. If you want ultra fast get one with 32 or 64 GB of VRAM. The GPU can range in price based upon size. That being said:

You will need to download Ollama first. They have a great selection of models to use. The different parts of the application rely on the values you set in Application State. Fill them in before running any part of the application.<br /><br />
Gathered information is saved to Person, Phones, Emails, Addresses, Aliases, Events and Reports first so you can edit it. The data once cleaned up and validated needs to be then saved to the vector database for the LLM to use. There is a file entity to use to upload any image, Pdfs, Excels or Word docs.

You can change models so when you get a better computer with VRAM and NVIDIA GPU you can run larger models.
You can change the system_prompts(prompts) if you are a prompt engineer and know how to fine tune them. There is a default that no matter what you can always revert to.
You can change user_querys(questions) if you are a prompt engineer and know how to fine tune them. There is a default that no matter what you can always revert to.

## The Build
If you are good with python
- clone the repo
- run 'cd missing-persons-agent'
- optional - create .venv and activate it
- run 'pip install -r requirements.txt'
- run 'python app.py'

### Person and Categories.
- Eack link is a separate entity.
  - Categories - You can have different categories for people, phones, emails and addresses. Define your categories for each and they will show up in each of them when you add or edit rows.
  - Person - A person is anyone you will search for information on through the APIs(next stage). The initial category I created for person was 'Missing Person'. You can change the name of it or create others like 'Person of Interest' etc.. I would keep it in place though because it identifies the person as being missing. Every thing you save into the app is saved with a missing person as an owner. Every person besides the missing person must be owned by a missing person. Missing people will have 0 as an owner.
  - The rest are parts of a person, addresses, emails, phones and alias. They all have an owner which is a person entity.

![Person Page](./assets/person.png)

### Document uploads, API and RSS feeds.
- Api, ApiFields and State.
  - Api - Fill in the information about the api here. Put the full url into the url field including the https:// and the url endpoint.
  - ApiFields - Fill in each field that will be used in the api call. Field is a query parameter and is used to filter results. The field is the query parameter name, value is the value that needs to be there. Everything associated with a person will eventually be an option in the value list. Right now there is only the persons name.
  - State - The appication state.

![Chat Inspector Page](./assets/inspector.png)

### Outside installed app data storage.
- Preserves data when updating.
- The vector database is Chroma.
- There is the SqlAchemy database for everything not vectorized.
- When you save data to the SqlAlchemy database, you have to then create a entry from it into the chroma vector database.
  - For Documents the chunks are created and stored under the file name. Only finished pdf for the moment.
  - You can delete the chunks in the edit link of whatever entity you saved it in and the chunks page. There is no editing yet. Will circle back to it soon.

![Data saves to AppData](./assets/saved_data.png)

### Ollama for local and future access to Grok, OpenAi and Claude
- Ollama models can be downloaded on the Models page by creating an Ollama model.
- Models can be deleted on the Resources page but be careful you are not using them somewhere else on your computer.
- There is a setting for selecting the type of processor you are using in state.
Look through the available models and choose models that are pretrained in the field you want them trained in.

![Resources Page](./assets/resources.png)

### Prompts
Build out prompts and questions for LLMs.
- Users can create prompts and questions to use when prompting the LLM on The Prompts and Questions page.

![Prompts Page](./assets/promts.png)

### Questions

![Questions Page](./assets/questions.png)

### Data Center
Build out Data Center
- Run Apis, RSS Feeds or Page Scrapes
- Filter the data if the feed relies on loose keyword matching.
- When the user is happy they can save the JSON data to the Feed Logs database.
- View feed log page
  - Use agent to scan and create leads out of the json
    - name
    - email
    - phone
    - context of the lead
  - Pull out and list all document or image Links with FQDN(fully qualified domain name)
    - view link
    - save link to files

![Data Center Page](./assets/data_center.png)

![Feed Logs Page](./assets/feed_logs.png)

![View Feed Logs Page](./assets/view_feed_log.png)

![Extract Leads](./assets/extract_leads.png)

![Extract Timeline Events](./assets/extract_timeline_events.png)

![Extract Links](./assets/extract_and_save_links.png)

![Leads Page](./assets/leads.png)

### Timeline for each Person
A list of events recorded for each person who has a role in the investigation ordered in a timeline.

### Agent UI
A list of Tasks created.

Form to set the Agent working.
- list saved api content  - select content to process
- Process Content button

List of logs to watch while the agent work.

Keep the APIs separate so other people can continue to work on it.
Offer the ability to save the raw responses to a database table.

On the first set of passes it looks for leads and adds them as tasks.
On the second set of passes it looks for information on events.
On the third set of passes it looks for contact information.

You pass it an API, RSS Feed or a scraped content and it processes the whole unit.
It recursively checks each task against the data stored in SqlAlchemy database and the task list, if its not present creates a task to insert it.
Have the agent always log where its pulling the data from.

### Agent
Build an agent that operates continuously with stop options
- Possibly create a nodes table that the user can define the nodes. This might be too much. Still trying to create the perfect idea.
  - Create tools that can be used by the agent.
  - Create an MCP server that the agent can use. MCP servers standardalize connecting to external data.
    - Resources, Tools and prompts
    - Elicit - allows the tool to pause for user input
  - Load the Chroma database with person, emails, phones, addresses and aliases.
  - Load the Chroma database with Events and notes.
  - Load the Chroma database with Documents including documents, images, audio and videos.
  - Connect to APIs and Rss Feeds to pull data in as json.

With the idea of
  - Find new people of interest and accessing data points for them.
  - Parse the returned json and save new data to the database related to the case.
  - Prompting the model for connections that could lead to finding the person.
  - When new data is found the data is added to the entity as a [OSINT](https://github.com/cipher387/API-s-for-OSINT) row.

Collections.
  - database - Stores data for the RAG LLM to determine the table and column to save data pulled from the API and Rss Feed json.
  - investigation - Stores data from the person, email, phone, alias, address, event and note table data for investigating.
  - investigator - Stores data from pdfs and documentation on how to investigate. You can create a pdf here with your own private methods.
  - vehicles_of_interest - Stores vehicle descriptions.
  - witness_statements - Stores witness statements.

### edge cases -
someone has the same set of clothing as an unidentified man/women at the crime scene. How would the agent connect the two?

### Add in Autosearch
Andrej Karpathy revolutionized prompt and AI optimization by introducing the "Autoresearch" pattern (often dubbed "The Karpathy Loop"). Instead of humans manually tweaking prompts, an AI agent optimizes them by iteratively modifying a prompt, running a test against a strict evaluation rubric, keeping changes if the score improves, and discarding failures.
- Add auto search to the agent to aid in optimizing prompts if possible.

### Add in Audio to text
Use a package that can listen to audio and video and convert the talking to text to be searched for clues, leads and connections.
- @TODO need to get llama-liquid-audio-cli set up.

### Events to construct a Timeline
- Use the data gathered from the APIs to build timelines for each person.

### Images and Videos
- Add images and video to the person object to use when looking though images and videos for matching.
- Build ability to train a model on video and images.
- Build out functionality for testing and viewing data from videos and images.

### Linkedin / Facebook Style Messaging
- A messaging system like Linkedins where people who are searching for someone can share notes.

### Central Data Store
- A central data storage where all data on an investigation can be accessed by any one using Missing Persons.

## Section Details

- Categories - Work and in testing.
  - Categories - You can have different categories for people, phones, emails, addresses and events. Define your categories for each and they will show up in each of the entities as Type when you add or edit rows. I created two categories for person. They are 'Missing Person' and 'Person of Interest'. You can change them or create others but you will be unable to delete them because they are going to be used by the system.
- Person - Work in SqlAlchemy, working on the save and update functions for Chroma Db now.
  - Person - A person is the Missing Person or anyone that came in contact with them; Person of Interest. Each Person will either be at the top of a Tree type of structure;  think department where the boss is at the top, departments under the Boss and workers under a department. The 'Missing Person' is the Boss the rest of their contacts will have a parent child relationship with another Person in the Tree.<br /><br />The Person only describes the individual. If you have more data than form elements use the description field.<br /><br />All Persons have one or more Emails, Addresses, Aliases, Phones, Events and Reports that you can create for them. First create a person. Then go to and add Emails, Addresses, Aliases, Phones, Events and Reports and fill in the data you have on the person. Once your done adding data go back to the edit page of the person you added the data for and save the person again. The data will be consolidated into a single chunk of text and saved in the Chroma vector database.<br /><br />Make sure to choose the person you want to add the data to when filling in Emails, Addresses, Aliases, Phones, Events and Report.<br /><br />
  - Addresses - Addresses is any address used by the person. Create a Type for it in Categories first. Example Category: Home, Work, etc..
  - Emails - Emails are any emails used by the person. Create a Type for it in Categories first. Example Category: Personal, Work, etc..
  - Phones - Phones are any phone number used by the person. Create a Type for it in Categories first. Example Category: Cell, Work, etc..
  - Aliases - Alias are any aliases used by the person.
  - Events - Events are any event that happens related to the person. Create a Type for it in Categories first. Example Category: Alibi, Court Date, etc..
  - Reports - Reports are any other data related to the person.

- Files - Added as data for the LLM.
  - Pdf - Save works but needs update.
  - Excel - Coming soon..
  - Csv - Coming soon..
  - Word - Coming soon..
  - Image - Works, will continue to test.
  - mp3 - Audio files - Coming soon..
  - mp4 - Movie files - Coming soon..

- Data APIs - Working on the save functions now.
  - RSS Feeds - Use RSS Feeds to gather data. You can select data by json nodes. Then turn the results into chunks by clicking the save button provided on each row. This will open a Modal that allows you to save the value of that node to any field you want in the SqlAlchemy database. From there you will need to save the edited version in edit person.
  - Data APIs - Use APIs to gather data. You can select data by json nodes. Then turn the results into chunks by clicking the save button provided on each row. This will open a Modal that allows you to save the value of that node to any field you want in the SqlAlchemy database. From there you will need to save the edited version in edit person.

- Model APIs - Only Ollama works.
  - Ollama - This is the initial Model I used because it all runs on local and is testable without paid subscription. Can be a bit slow.. You can speed this up by selecting GPU in the form on the upper right corner.
  - OpenAI - If you don't have GPUs then I plan to give you the ability to connect with OpenAI so you can run data on their models with their GPUs if you like.
  - Grok - Same with Grok.
  - Claude - Same with Claude.</li>

## ideas

05/27/2026 - It needs to have a central store of all data pertaining to an investigation. A vector database where anyone using Missing Persons or other software like Missing Persons can plug into and use the data stored there in their investigation. The information should be submitted to be added in the style of git. Then merged into the main branch when validated. The nice thing about this is the data can be valid, deduplicated and always ready.

06/14/2026 -  Had new idea to build a Nodes table so a user can define a list of tasks for the model to work on.

It uses Langchain Chroma for storing data for the LLM. It is open-source with no usage limits on local machines.

It also uses sqlite with Sql Alchemy ORM for storing data so you can adjust the data before saving it to the vector database. I am will probably also create a sub model for deciding what to choose when dealing with duplicate data.

My hopes is that 1000s of people will work together using this tool to search through the tons of video footage for the missing person in the first couple days of their disappearance and find them because with everyone using it we were able to do something faster.

I would love to convince the people behind the cameras to have the data saved on a servers backed up for at least a month with a front facing domain and website that can support a read only API to view the videos so this program can run images against them.

Ill create a list of the Camera and Missing persons APIs that people can use here when I find them.

I would think that using the RSS method described in the youtube video [Turn Facebook Pages or Groups Into RSS Feeds](https://www.youtube.com/watch?v=Nt2pc1IIESI&t=4s) and collecting as much data as you can from every social media platform you can apply this to, you could build a sort of profile for each individual in the social group of the missing individual. Then train the agent with it and have it create a probability distribution on who it thinks fits the bill.

Continue to collect and agregate the data daily to look for more clues.

Was thinking this morning about having the program continue out wards in the tree from ground zero and automatically as it finds new acquaintances get an RSS feed for them and pull in their data. Your computer would always be searching and indexing new people in hope of finding a connection. I could set up a parameter for levels out. Also was thinking about a fine tunner agent that gives suggestions for fine tuning the LLM and your work on finding the person using this tool. The interesting concept is an agent that improves itself.

It would be a good idea I would think to add as many missing people as you can find and the immediate people groups they will have so you can look for people that are in every group. In case the person is involved in a ring of abductions where the same person is doing recruiting or abducting. Search for deleted or blocked accounts in the missing persons list of contacts or accounts that where deleted by the owners who were once friends with the missing person.

I decided on building tools and skills that use MCP when possible to get lists of articles and posts from social media to construct timelines, people who have had contact with the missing person to construct persons of interest and accessing public databases for any other information that could be helpful in the investigation. This seems to be the most robust and scalable way to move forward.

I'm also only going to focus on text, capturing audio as text and running the agents to search for clues and connections for now because it seems that images and videos in the scope of gas station cameras will not be so accessible.

What would work wonderfully is a server with pedabytes of storage. A person researching and finding/building API endpoints, RSS Feeds, and scraping web pages. A person working tasks and adding the data found by: The main computer that doing the constant searching by APIs, Rss Feeds and saved data that constantly runs and creates new tasks, the LLM agents. Another person is tweaking and prompting another set of LLMS that are searching the data for clues, leads and connections. Each one of the team is hooked into the server which is the storage unit for all the collected data. Each one of the team has a computer that halls a** with at least a Terabyte of storge and 64 to 132 GB of RAM. The Computer running the Agents needs to have VRAM ad Nvidia GPUs the bigger the better. You can add more people too to have it go faster.

Each API is unique in ways.
The official FBI Wanted API does not provide a dedicated exact match parameter for keyword queries. It relies on loose keyword matching. If you search for 'John Smith', it will return all references to John and Smith and not the exact match of 'John Smith'.

I asked AI: If I have an API like the official FBI Wanted API that does not provide a dedicated exact match parameter for keyword queries. I need data that I can pass to a agent for processing about an investigation. Should I clean the data before passing it to the agent or have the agent pick relevant data from the respose?

It answered: You should clean and filter the data before passing it to the AI agent rather than relying on the agent to pick relevant data from a raw API response. Because the FBI Wanted API relies on loose keyword matching, a query for a specific name can return a massive JSON payload filled with unrelated fugitives, partial matches, or long-closed cases. Passing this raw noise directly to an agent introduces major operational risks and inefficiencies.

In the new age of agents APIs will need to offer exact data options to aid in AI development. It would be awesome if all APIs could offer a parameter that sets all matching to exact match. exact_match=True

### Links

[Invisible Threads](https://blog.ry4n.org/invisible-threads-finding-missing-people-online-7dec4cb038e5).

[Best Practices for Text-to-SQL Use Cases with LLMs](https://www.linkedin.com/pulse/best-practices-text-to-sql-use-cases-llms-dave-thibault-mr9ac/)

[Gen AI Agent Resource](https://github.com/NirDiamant/GenAI_Agents)

[IBMTechnology](https://www.youtube.com/@IBMTechnology/playlists)

[CLI vrs MCP Servers](https://www.youtube.com/watch?v=g9JIUM0MHgQ)

[The Best LOCAL Agentic Coding Workflow](https://www.youtube.com/watch?v=hfba9dAT6xE)

- System Prompt
- AGENT.md
  - It is loaded into the conversation history very frequently (often at the start of every session or turn). This could be using alot of tokens.
  - Keep it short (ideally under 200 lines). The immutable rules of the agent.
- Saving static data from pdfs or relational databases in chunks to vector database so it can be used by a RAG LLM.
- CLI Commands
  - Cli commands are built into its training data.
  - Good when commands map directly to jobs.
  - Can be chained together on one line.
- MCP servers
  - The LLM (The Brain): It evaluates when it needs external help or data. It does not need to be hard-coded with tool APIs.
  - The MCP Host/Client (The Broker): This is the application you are running (e.g., Cursor, Claude Desktop, or an agent framework like LangChain). It brokers the connection between the LLM and the external world.
  - The MCP Servers (The Hands): These are distinct, external services (e.g., GitHub, Google Drive, Postgres, Slack, or local file systems). You plug these servers into your MCP Host so your LLM can interact with them.
    - Resources like files.
    - Tools @mcp.tool()
    - Prompts - In the Model Context Protocol (MCP), servers act as pre-defined prompt templates that expose reusable workflows and instructions to your AI client. Instead of forcing users to repeatedly type complex instructions, the MCP server packages these guidelines into ready-to-use menu options, often appearing in your AI interface as slash commands or clickable UI templates.
    - [MCP Registry](https://github.com/mcp)
- LSP
- Skill.md
  - Skills use Progressive Disclosure to save tokens.
  - Metadata & Discovery (~100 tokens): The agent only reads the summary (name, description, and triggers) from the skill's frontmatter at the start.
  - Activation (<5,000 tokens): Only when the agent decides it needs that specific skill does it load the full instruction body
  - [Agent Skills IO](https://agentskills.io/home)
  - [Anthropics Skills](https://github.com/anthropics/skills)
  - [Azure Skills](https://github.com/microsoft/azure-skills)
  - [DotNet Skills](https://github.com/dotnet/skills)
- Tools
  - @tool
- CrewAI
  - Works with langgraph and ollama.
  - Allows you to use sub agents to handle task simultaniously.
- Agent2Agent Protocol
  - [a2a-protocol](https://a2a-protocol.org/latest/)
  - [Agent2Agent](https://github.com/a2aproject/a2a-samples)

[Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
