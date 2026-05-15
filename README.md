# Missing Persons Agent

I'm creating a installable application that is a tool to investigate a persons disappearance. its built in python and uses pywebview to turn a flask website into a desktop application and then bundle it with pyinstaller into an executable that is installed using Inno. The models its going to use are [Ollama](https://ollama.com/download/windows) models. Ollama lets you build and work on an LLM model locally on your computer so you maintain your privacy.

It will use ChromaDB for storing data for the LLM to allow you to clean the data and minimize or completely remove hallucinations. It is open-source with no usage limits on local machines.

It also uses Sqlite3 both as a storage for initial search data. I am will probably also create a separate model for deciding what to choose when dealing with duplicate data.

My hopes is that 1000s of people will work together using this tool to search through the tons of video footage for the missing person in the first couple days of their disappearance and find them because with everyone using it we were able to do something faster.

I would love to convince the people behind the cameras to have the data saved on a servers backed up for at least a month with a front facing domain and website that can support a read only API to view the videos so this program can run images against them.

Ill create a list of the Camera and Missing persons APIs that people can use here when I find them.

I would think that using the RSS method described in the youtube video [Turn Facebook Pages or Groups Into RSS Feeds](https://www.youtube.com/watch?v=Nt2pc1IIESI&t=4s) and collecting as much data as you can from every social media platform you can apply this to, you could build a sort of profile for each individual in the social group of the missing individual. Then train the agent with it and have it create a probability distribution on who it thinks fits the bill.

Continue to collect and agregate the data daily to look for more clues.

Was thinking this morning about having the program continue out wards in the tree from ground zero and automatically as it finds new acquaintances get an RSS feed for them and pull in their data. Your computer would always be searching and indexing new people in hope of finding a connection. I could set up a parameter for levels out. Also was thinking about a fine tunner agent that gives suggestions for fine tuning the LLM and your work on finding the person using this tool. The interesting concept is an agent that improves itself.

### Donate

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?hosted_button_id=J8WY5PDLWGK6Y)

I'm unemployed at the moment and looking for work. Help keep me going. Any support is appreciated. If you would be interested in helping or have ideas I'm open to help there also. If you are hiring I'm open to full time employment as a Full Stack Developer that can also code AI in both Python and C. Thanks.

I'm not done yet but this will be the downloads page.
Download: [Missing Persons](https://globalwebmethods.com/missing-persons)

## Helping me build

If you are interested in contributing please do! You are welcome to build in features to help get this done.

## The Build

### Stage 1
Build out the database for Person and Categories.
- Eack link is a separate entity.
  - Categories - You can have different categories for people, phones, emails and addresses. Define your categories for each and they will show up in each of them when you add or edit rows.
  - Person - A person is anyone you will search for information on through the APIs(next stage). The initial category I created for person was 'Missing Person'. You can change it or create others like 'Person of Interest' etc..
  - The rest are parts of a person, addresses, emails, phones and alias. They all have an owner which is a person entity.
  - View Person - A page to view people. Going to finish the main work first.

### Stage 2
Build out the database and pages for consuming APIs. Users use a form to run the API to get data from whatever API they choose to use.
- Api, ApiFields and State. I have just finished the basics and added Nancy Guthrie as an example of how to use it. There is still alot of work to do on this part of the system. Im going to move on though and complete the minimum of each Stage so I can have a fully working app before I go back and fully complete everything. This allows U.S to help if you want by taking on a section of it. Thanks.
  - Api - Fill in the information about the api here. Put the full url into the url field including the https:// and the url endpoint.
  - ApiFields - Fill in each field that will be used in the api call. Field is a query parameter and is used to filter results. The field is the query parameter name, value is the value that needs to be there. Everything associated with a person will eventually be an option in the value list. Right now there is only the persons name.
  - State - The appication state is saved to help guild your workflow. The state form is included with every item listed in Person, Model, Api, prompt and question. Only one of each can be set at any time. Hit Set State to set an item in state. CPU/GPU is in the upper right corner. When you create ApiFields or call Apis you need to have the Person and the Api selected and saved in state. When using the Optomize buttons in notices you need to have some data stored in the Chroma vector database, the Prompt set and the question set.

### Stage 3

Build out the vector database to save the API data for the Ollama model. Users can refine the data.
- The vector database is Chroma.
- The databases are in the database folder.
- There is the SqlAchemy database for everything not vectorized.
- chroma_db for saving vectorized data for the RAG LLM.
- When you save data to the SqlAlchemy database, you also create a entry into the chroma vector database
  - For text entered into the person or tables owned by person a chunk is created and saved to the vector database containing all information of that person entity, phone entity etc.. via a ValueObject class.
  - For Documents the chunks are created and stored under the file name. Only finished pdf for the moment. Will work on more type soon.
  - The collection name is missing_persons.
  - You can edit and delete the chunks in the edit link of whatever entity you saved it in. Working on all this now.

### Stage 4
Build out training functionality for the Ollama LLM. Users can train and retrain models as they build and refine the data.
- Ollama models can be downloaded on the Models page by creating an Ollama model.
- Models can be deleted on the Resources page but be careful you are not using them somewhere else on your computer.
When you start the application it checks for Ollama models downloaded and adds them automatically to the Models database.
- The models are RAG LLM so they are pretrained and use the vector database as RAG Retrieval-Augmented Generation data source.
- You will be able to choose any model you like when I'm done.
- There is a setting for selecting the type of processor you are using in state.
Look through the available models and choose models that are pretrained in the field you want them trained in.

Im using ***HuggingFaceEmbeddings sentence-transformers/all-MiniLM-L6-v2*** for the RAG LLM. Will open this up for you to choose your emmbedings. This is used to chop the text of a document into smaller chunks that are saved into the vector database. The chunks are what the LLM uses when it searches for answers. There are chunking stategies you need to learn about when using this application. I will also add the ability for you to change chunking strategies.

#### Chunk Strategies:
#### ***Resumes: Thematic & Structural Chunking***

Resumes are highly structured, data-dense, and context-sparse. Standard overlapping token chunking frequently shatters meaning across boundaries.
 - Strategy: Use element-aware or section-level chunking. Instead of slicing text blindly, treat sections as indivisible units of information.
#### ***Novels: Narrative & Semantic Chunking***
Novels are continuous, unstructured narrative texts where meaning bleeds fluidly across paragraphs and chapters.
 - Strategy: Use Semantic Chunking or Recursive Character Splitting. You are prioritizing the flow of ideas, character development, and plot points over hard structural layouts.

### Stage 5
Build out prompt functionality for the Ollama LLM. Users can create questions to use when prompting the LLM.
- Users can create prompts and questions to use when prompting the LLM on The Prompts and Questions page.

### Stage 6
Use the data gathered from the APIs to build timelines for each person.

### Stage 7
Add images and video to the person object to use when looking though images and videos for matching.

### Stage 8
Build ability to train a model on video and images.

### Stage 8
Build out functionality for testing and viewing data from videos and images.

### Stage 9
A messaging system like Linkedins where people who are searching for someone can share notes.

### Links

Reading [Invisible Threads](https://blog.ry4n.org/invisible-threads-finding-missing-people-online-7dec4cb038e5).
