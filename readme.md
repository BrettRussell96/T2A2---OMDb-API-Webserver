# OMDb API 
### T2A2 API Webserver 

## How to use

* Create a virtual environment ```python3 -m venv .venv && source .venv/bin/activate```

* Clone this repository 

* Create a datase called media_db in postgresql

* Create a user called media_dev in postgresql and grant database privileges

* Download the requirements for the API within the virtual environment using the command ```python3 -m pip install -r requirements.txt```

* Go to the OMDb API website and obtain a free API key. https://www.omdbapi.com/

* Create a .env file in the root directory and place the variables from .envsample into this file, for example: ```DATABASE_URI="postgresql+psycopg2://{your_postgres_user}:{passowrd_of_user}@localhost:5432/{your_database}"```  
```JWT_SECRET_KEY="secret"```  
```OMDB_API_KEY={your_api_key}```

* use the commands ```flask db create``` and ```flask db seed``` to create and seed the database tables

* use the command ```flask run``` the run the server

* if you wish to delete your tables and data use the command ```flask db drop```



## Identification of the problem I am trying to solve by building this app and why it needs to be solved
The problem that this API aims to address is in regards to the fragmentation and accessibility of information regarding movies and TV series from various sources. Users seeking information about this kind of media face the following challenges:

**Information Overload** - The amount of data available online can often become overwhelming when users are trying to find fast and reliable information about a specific movie or TV series. It can become time consuming navigating through multiple websites with varying levels of detail and reliability of information.

**Lack of Personalisation** - Many existing platforms with media information don't allow users to track their viewing history, rate titles, or maintain a personalised watchlist. This means users often have to resort to separate apps to track what they've watched or intend to watch.

**Inconsitancies Across Platforms** - information about media titles can vary significantly from one platform to another and this can often cause confusion. Differences in ratings, plot summaries, as well as cast information can make it tough for users to get a clear understanding of a titles reception and content.

**Integration with User Interactions** - Few platforms integrate information about movies and TV series' with user interactions such as watching history and ratings in a way that enhances the user's decision making process for what to watch.


## How I aim to solve it 
Through building this app, I aim to create a centralised, user friendly platform which addresses the issues mentioned previously by the following:

**Aggregating Information** - Offering a single point of access to comprehensive and reliable information about movies and TV series through use of the OMDb API to ensure users receive standardised data.

**Enhancing User Experience** - Allowing users to interact with records by rating titles, marking them as watched, addidng them to a watchlist, and viewing aggregated user interaction data such as average ratings and user popularity. This helps to personalise the user experience and well as aiding in discovery and recommendations.

**Creating a Community** - By integrating user interactions, allowing the creation of personal profiles, and providing a forum for reviews and discussion, this platform is able to foster a community of enthusiasts who contribute to the richness of the database through their own ratings, reviews and record additions. This makes for a more dynamic platform that reflects a broad range of opinions.



## Chosen Database System
The database system that my application utilises is PostgreSQL.

PostgreSQL is one of the oldest and most advanced database management systems. It is open source and can be run on various platforms such as Windows, Linux, and Mac. the reasons I selected this database system are as follows:

**Reliability and Performance** - postgres offers robustness and reliability, and is highly regarded for its performance in managing complex queries as well as large volumes of data. This is necessary in my application which requires the potential storage of an enourmous amount of categorised information about varous movies and tv series. Alot of the request filters also require the fulfillment of reasonably complex requests such as:
* retrieving comments with their associated user, media , and child comment instances.

* Aggrogating interaction data for specific media titles such as count of rating, watched, and watchlisted and average rating.

* creating and updating different relational records, such as user profiles, interactions, and comments

* retrieving media information based on the presence of multiple query parameters such as type, genre, actors, and directors

**ACID Compliance** - postgres ensures atomicity, consistency, isolation, and durability properties, making it reliable for transactions. This is very important given the operations performed on media records and interactions, to ensure data integrity.

**Advanced Data Types and Functions** - Postgres supports a variety of data types and sophisticated functions. One useful feature is JSON/JSONB support, this is helpful in managing the diverse data kept within my application such as media records that contain nested attributes. 

**Compatability** - postgres is highly extensible and allows for custom functions, types and languages. This results in a high level of adaptability. In the case of my application, its compatability with Flask is able to facilitate seamless interaction.

**Robust Security** - features such as strong access control mechanisms, SSL support, and low level security are cruicial for protecting sesitive user data and ensuring only authorised users can perform certain operations. 



## Drawbacks compared to others
**Performance Overhead for Simple Applications** - For more simple applications with minimal data manipulation needs, the advanced features of postgres can introduce unnecessary overhead. This can make lightweight databases such as SQLite a more suitable choice.

**Operational Complexity** - Managing a postgres database can often be more complex than with simpler database systems. It requires understanding its configuration, maintenance, and optimisation practices. This can present a steep learning curve for beginners.

**Resource Intensity** - As it scales up, postgres can become resource intensive when compared with NoSQL databases such as MongoDB. This may necessitate more powerful hardware to maintain performance as data volume and user load increase.


## Identify and discuss the key functionalities and benefits of an ORM
An Object Relational Mapping framework is used to interact between an application and a database. ORMs allow developers to manipulate the database using the programming language's own constructs without having to understand the complexities of SQL syntax and database operations. here are the key functionalities:

**Data Model Representation** - ORMs represent database tables as classes and rows as their instances. this object-oriented approach is present in my own application where my relational models are represented as classes making it more intuitive for me to interact with them and make adjustments where such as in the case of changing datatypes or removing columns.
```python
# create User model
class User(db.Model):
    # set tablename to users
    __tablename__ = "users"
    # use db to define columns and data types
    # set id as primary key
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
```

**CRUD Operations** - ORMs provide methods for creating, reading, updating, and deleting database records which eliminates any need for writing raw SQL queries for these operations. In my application these operations are handled throughout requests, below is a simple example of a GET request which handles the read method for user profiles:
```python
# request to get all current users
@user_bp.route("/", methods=["GET"])
def get_all_users():
    # query database and fetch all users
    users = User.query.all()
    # serialise users into JSON objects based on schema
    result = users_public_schema.dump(users)
    # return result as a response with successful status code
    return jsonify({"users": result}), 200
```

**Query Abstraction** - ORMs allow querying the database using the chosen programming languages syntax. This is more intuitive for developers and also less error prone than writing SQL queries. Here is one such example of a databse query made within my application:
```python
        # query the database to find the user
        user = User.query.get(current_user_id)
        # query the database to find the id of the
        # media record specified in the URL
        media = Media.query.get(media_id)
        # retrieve JSON data from request body
        body_data = request.get_json()
        # query the database to see if the user has
        # made an interaction record for this media
        existing = Interaction.query.filter_by(
            user_id=user.id, media_id=media.id
            ).first()
```

**Relationships and Associations** - ORMs can automatically handle table relationships through object properties making it easier to navigate and manipulate data. In the interaction model of my application the one to many relationship between 'user' and 'interaction' as well as 'media' and 'user' is represented in the following way:
```python
    # define foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    # set user and media relationship
    user = db.relationship(
        'User',
        back_populates='interactions'
    )
    media = db.relationship(
        'Media',
        back_populates='interactions'
    )
```

**Data Validation and Type Checking** - ORMs are able to enforce data validation rules and type checks based on class definition. This is done through the use of schemas in my application, in the interaction schema, data validation is enforced through the use of EnumField and validate.Range, EnumField is also an example of a type check, as is fields.Nested. here is the schema example below:
```python
class InteractionSchema(ma.Schema):
    # set field data type
    id = fields.Int()
    watched = EnumField(InteractionEnum, by_value=True)
    # set valid range for rating
    rating = fields.Integer(validate=validate.Range(min=0, max=10))
    watchlist = EnumField(InteractionEnum, by_value=True)
    user_id = fields.Int()
    media_id = fields.Int()
    # nested fields for foreign keys to show what fields will be shown
    user = fields.Nested(
        'UserSchema',
        only=['username']
    )
    media = fields.Nested(
        MediaSchema,
        only=('title', 'year', 'category')
    )
```



## Third Party Services
### Flask
Flask is a lightweight WSGI web application framework. It provides tools, libraries and technologies to build a web application. Flask also contains extensions for tasks such as database integration, form validation, upload handling, and open authentication technologies.  
Flask is used to build the API for this application.

### PostgreSQL
PostgreSQL is an advanced, open-source object-relational database system. It is known for its reliability, scalability, and support for advanced data types and SQL standard compliance.  
PostgreSQL is used to build and house the database for this application

### Marshmallow
Marshmallow is an ORM/ODM/framework-agnostic library for converting comlex data types, such as objects, to and from native Python data types.  
In this application, Marshmallow is used to load pre-defined schemas, serialise data into JSON friendly formats, facilitate the handling of nested relationships, and validate input data against schema constraints.

### SQLAlchemy
SQLAlchemy is a SQL toolkit and Object-Relational Mapping library for Python. It provides a full suite of enterprise-level persistence patterns and is designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language.  
In this application, SQLAlchemy is used to query the database, manage relationships between models, manipulate data records to perform CRUD operations, and handle exceptions.

### Flask JWT Extended
JWT Extended is an extension for flask that adds support for JSON Web Tokens (JWT). I allows for secure and coonvenient authentication mechanisms and can be used to protect routes and endpoints.  
JWT Extended is used within this app to create web acces tokens, and check these tokens for identification and authorisation in order to secure routes.

### Bcrypt
Bcrypt is a password hashing library which helps with the safe storage of passwords. The Bcrypt algorithm is designed to be resistant to brute-force search attacks and is a key factor in building secure flask applications.  
In this application, Bcrypt is used to hash passwords so they are not stored in plain text thus improving user security.

### Psycopg2
Psycopg2 is a PostgreSQL database adapter for Python. It is designed for multi-threaded applications and provides both synchrocous and asynchronous operations. It is the most popular PostgreSQL adapter for the Python programming language. 
In this application, Psycopg2 allows the connection to a postgreSQL database to execute SQL queries, fetch data, and perform database operations.

### OMDb API
The Open Movie Database API is a web service that allows developers to retrieve information about movies, TV shows and other cinematic content. the API is able to be accessed over the internet using standard HTTP requests, making it easy to integrate into web applications.  
The OMDb API is used to supply the media information for this application. 



## Task allocation and tracking
For the planning and task management of this application, I made use of Trello. I used Trello to separate the development process into phases, the first being for planning activities, and the second being for development.

![trello board](./docs/trello_board.png)

### Planning Phase
In the planning phase I had two activities:

**Requirements** - where I detailed the file structure of my application as well as the necessary third party services that would be required.
![trello req1](./docs/trello_requirements1.png)
![trello req2](./docs/trello_requirements2.png)

**ERD and Requests** - where I planned out the tables and columns to be used for the application as well as listing as many requests I could potentially include into the apps functionality as possible.

### Development Phase 
I seperated this phase into five sections, the first section being devoted to the 'boilerplate' code necessary to build the structure of the application, and the other four being each individual model and its associated route and endpoints. 
![trello foundation](./docs/trello_foundation.png)

As I worked on each model, I would frequently refer back to my plan to check which requests needed to be created in order to fulfil my desired functionality. In each activity, I would make comments as I started a new request to keep track of the goal response I required. At the end of each section, I would test for errors before marking it as complete and moving on.
![trello user](./docs/trello_user.png) 
![trello interaction](./docs/trello_interaction.png)

Throughout the development process I also made regular commits to a github repository for source control and project tracking. This was generally done at the end of each request or if any major adjustments were made. 



## App ERD
The Entity Relationship Diagram represents the 4 relational models for my flask application. They are as follows:

### User
#### Tablename: users
#### Attributes
* **id** - Integer, primary key, unique ID for each user
* **username** - String, unique username associated with the user
* **email** - String, unique email registered to the user
* **password** - String, password for accessing user account 
* **location** - String, optional location info
* **is_admin** - Boolean, admin status check for authorisation
#### Associations
* **Interaction** - One to many
* **Comment** - One to many

### Media
#### Tablename: media
#### Attributes
* **id** - Integer, primary key, unique ID for each media record
* **title** - String, name of the movie or series being stored
* **year** - String, year the media was created
* **category** - Enum, category definition of either movie or series
* **genre** - String, genre of the media
* **director** - String, name of the medias director
* **writer** - String, name of the medias writer
* **actors** - String, names of the actors in the media
* **plot** - Text, storyline information for the media record
* **country** - String, country the media was filmed in
* **ratings** - JSONB, list of ratings from different critics
* **metascore** - String, metascore rating
* **box_office** - String, box office profit for the media\
#### Associations
* **Interaction** - One to Many
* **Comment** - One to many

### Interaction
#### Tablename: interaction
#### Attributes
* **id** - Integer, primary key, unique ID for each interaction
* **watched** - Enum, can be either yes or no value
* **rating** - Integer, can be any number from 0 - 10
* **watchlist** - Enum, can be either yes or no value
* **user_id** - Integer, foreign key, ID of user making the interaction
* **media_id** - Integer, foreign key, ID of media the interaction is for
#### Associations
* **User** - many to one
* **Media** - many to one

### Comment
#### Tablename: comments
#### Attributes
* **id** - Integer, primary key, unique ID for each comment
* **content** - Text, body of the comment
* **created** - Datetime, time of comments creation
* **parent_id** - Integer, foreign key, ID of parent comment for replies
* **media_id** - Integer, foeign key, ID of the media being commented on
* **user_id** - Integer, foreign key, ID of the user making the comment
#### Associations
* **User** - many to one
* **Media** - many to one 



## Database relations to be implemented
the models housed within my models folder make up the table representation for a relational database using SQLAlchemy. they are as follows:

### User
The ```User``` model represents the user profiles in the database. It has no foreign keys itself, however, it serves as a foreign key in the ```Interaction``` and ```Comment``` models where it has a one to many relationship. These relationships represent that one user can have multiple comments, and one user can have multiple media interactions.
```python
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
```

### Media
The ```Media``` model represents media records that are stored in the database. It contains all the information for the media records which are retrieved from the OMDb API. Like the ```User``` model, the ```Media``` model has no foreign keys but serves as a foreign key to the ```Interaction``` and ```Comment``` models. Their one to many relationship indicates that one media record can have many interactions and many comments. 
```python
class Media(db.Model):
    __tablename__ = "media"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String)
    category = db.Column(Enum(MediaEnum))
    genre = db.Column(db.String)
    director = db.Column(db.String)
    writer = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    country = db.Column(db.String)
    ratings = db.Column(JSONB)
    metascore = db.Column(db.String)
    box_office = db.Column(db.String)
```

### Interaction
The ```Interaction``` model represents each interaction instance that a user makes with a media record. The columns are made of three specific attributes, ```watched```, ```rating```, and ```watchlist```. The foreign keys for the ```Interaction``` model are ```user_id``` which specifies a user, and ```media_id``` which specifies a media record. The relationships that exist with these two entities are many to one, meaning that many interactions can belong to one user and many interactions can belong to one media instance.
```python
class Interaction(db.Model):
    __tablename__ = "interaction"
    
    id = db.Column(db.Integer, primary_key=True)
    watched = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)
    rating = db.Column(db.Integer)
    watchlist = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
```

### Comment
The ```Comment``` model represents each comment that a user makes on a media record. The only input data column is ```content``` which contains the body of each comment instance.  
The foreign keys for comment are:
*  ```user_id``` which represents the many to one relationship with the ```User``` model as many comments can be made by one user
* ```media_id``` which represents the many to one relationship with the ```Media``` model as many comments can be made for one media record.
* ```parent_id``` which represents nested comments in the form of replies, where one parent comment can have many child comments. 
```python
class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
```



## Endpoint Documentation

### POST Register User /user/register
* Registers a new user profile to the database, responds with user information and admin status.

![register user](./docs/register_user.png)
* **Body Data**
    * *username* is a required field of 5-25 unspaced alphanumeric characters, underscores, dashes, and periods are also allowed.

    * *email* is a required field of at least 10 characters

    * *password* is a required field of at least 5 unspanced alphanumeric characters, underscores, dashes and periods are also allowed.

    * *location* is an optional field and can be any string value


### POST Login User /user/login
* Responds with user information and a JWT session token.

![Login user](./docs/login_user.png)
* **Body Data**
    * *username/email* is a required field and must be either a valid email or username.

    * *password* is a required field and must be the password assigned to the username or email in the request


### GET Get all users /user
* Responds with a list of all current users, displays id, username, and location.

![Get all users](./docs/get_users.png)
* No parameters or body data is required


### GET Get all users by location /user/location
* Responds with all users id, location, and username fields that match the specified location.

![Get users by location](./docs/get_users_location.png)
* **Parameters**
    * *location* is required, must be a valid location


### PATCH Update user info /user/update
* updates user info based on body data, responds with the updated fields.
* **Requires a valid JWT token**

![Update user info](./docs/update_user.png)
* **Body Data**
    * *username* optional field

    * *email* optional field

    * *location* optional field

    * *password* optional field


### DELETE Delete user /user/<int:user_id>
* Deletes user record from the database, responds with a confirmation message
* User profile can be deleted by itself or by a profile with admin status
* **User ID to delete must be specified in the URL**
* **Requires a valid JWT token**

![Delete user](./docs/delete_user.png)


### GET Get movie info /media/movie
* Searches the database for a movie title matching the query parameter, if none is found, the OMDb API is accessed to retrieve the data which is then stored as a new media record in the database. Responds with the full information of the specified movie record.
* **Requires a valid JWT token**

![Get movie](./docs/get_movie.png)
* **Parameters**
    * *title* is required, must be a valid movie title


### GET Get TV info /media/tv
* performs the same functionality as the movie endpoint, I created separate endpoints to handle the case of a title having records for both the movie and series categories.
* **Requires a valid JWT token**

![Get tv](./docs/get_tv.png)
* **Parameters**
    * *title* is required, must be a valid tv series title


### GET Filter media info /media
* Searches the database for media records matching the filter query parameters, responds with varied amount of information depending on the info parameter specified.

![Filter media info](./docs/filter_media.png)
* **Parameters**
    * *info* is required, can be either 'title', 'rating', 'plot', or 'all'

    * *media* is optional, can be either 'movie', or 'series'

    * *genre* is optional

    * *actor* is optional

    * *director* is optional


### DELETE Delete media /media/<int:media_id>
* deletes a media record specified by the URL ID.
* only admin users can delete media records.
* **Requires a valid JWT token**

![Delete media](./docs/delete_media.png)


### POST Create Interaction /interaction/<int:media_id>
* Creates an interaction record in the database for the media specified by ID in the URL
* **Requires a valid JWT token**

![Create interaction](./docs/create_interaction.png)
* **Body data**
    * *watched* is optional, can either be 'yes' or 'no'

    * *rating* is optional, must be an integer between 0-10

    * *watchlist* is optional, can either be 'yes' or 'no'


### GET Interaction summary /interaction/summary 
* Queries the database to retrieve the total number of watched, ratings, and in watchlist as well as the average rating for the title specified in the query parameter.

![Interaction summary](./docs/interaction_summary.png)
* **Query Parameters**
    * *title* is required


### GET User listed interactions /interaction/user
* Queries the database for a specified user and then retrieves all interaction records that include the specified filters if any exist.
* **Rerquires a valid JWT token**

![user interactions](./docs/user_interactions.png)
* **Query parameters**
    * *username* is required, must be a valid username

    * *watched* is optional, can only be 'yes'

    * *ratings* is optional, can only be 'yes'

    * *watchlist* is optional, can only be 'yes'


### GET Media listed interactions /interactions/media
* Queries the database for a specified media record and retrieves all interaction records that include the specified filters if any exist
* **Requires a valid JWT token**

![media interactions](./docs/media_interactions.png)
* **Query parameters**
    * *title* is required, must be a valid title

    * *watched* is optional, can only be 'yes'

    * *ratings* is optional, can only be 'yes'

    * *watchlist* is optional, can only be 'yes'


### PATCH Edit interaction /interaction/<int:media_id>
* Updates interaction record for the media ID specified in the URL, fields are updated based on request body data. Response shows the updated data.
* user is identified based on their JWT token.
* **Requires a valid JWT token**

![edit interaction](./docs/update_interaction.png)
* **Body data**
    * *watched* is optional, can be 'yes' or 'no'

    * *rating* is optional, must be an integer from 0-10

    * *watchlist* is optional, can be 'yes' or 'no'


### DELETE Interaction /interaction/<int:interaction_id>
* Deletes the interaction record specified by the interaction ID in the URL. Response shows a confirmation message.
* Interactions can be deleted by the user who created them or by an admin user\
* **Requires a valid JWT token**

![delete interaction](./docs/delete_interaction.png)


### POST Create comment /comment/create
* Creates a new comment record for the media specified by title in the request body data.
* **Requires a valid JWT token**

![create comment](./docs/create_comment.png)
* **Body data**
    * *title* is required, must be a valid title

    * *category* is rerequired, must be either 'movie' or 'series'

    * *content* is required, must be a string.


### GET Get comments /comment
* Searches database for comments matching either the username or title specified in the query parameters. Response displays a list of all comments that match the search criteria, title comments will display replies nested as child comments.

![get comments](./docs/get_comments.png)
* **Query parameters**
    * *username* is optional, must be a valid unername
    * *title* is optional, must be a valid title


### PATCH Update comment /comment/<int:comment_id>
* Updates comment record with data found in the request body.
* identifies user based on JWT token
* **Requires a valid JWT token**

![update comment](./docs/update_comment.png)
* **Body data**
    * *content* is required, must be a valid string


### DELETE Delete comment /comment/<int:comment_id>
* deletes the comment specified by the ID in the URL
* comments can be deleted by the user who created them or by an admin user
* **Requires a valid JWT token**

![delete comment](./docs/delete_comment.png)

















