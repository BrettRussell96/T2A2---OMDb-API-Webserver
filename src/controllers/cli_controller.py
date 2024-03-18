from datetime import date

from flask import Blueprint

from init import db, bcrypt
from models.user import User
from models.media import Media
from models.interaction import Interaction
from models.comment import Comment


db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created")


@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables dropped")


@db_commands.cli.command('seed')
def seed_tables():
    users = [
        User(
            username="MelbourneAdmin",
            email="melbadmin@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Melbourne",
            is_admin=True
        ),

        User(
            username="SydneyAdmin",
            email="sydadmin@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Sydney",
            is_admin=True
        ),
        
        User(
            username="BrisbaneAdmin",
            email="brisadmin@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Brisbane",
            is_admin=True
        ),

        User(
            username="GarthoftheGalaxy",
            email="gg@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Melbourne"
        ),

        User(
            username="IronMatt",
            email="i&m@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Melbourne"
        ),

        User(
            username="Brooke99",
            email="b99@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Sydney"
        ),

        User(
            username="SuperNatalie",
            email="sprnat@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Sydney"
        ),

        User(
            username="PulpFintan",
            email="pfin@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Sydney"
        ),

        User(
            username="CaptainAmanda",
            email="captam@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Brisbane"
        ),

        User(
            username="GameofThomas",
            email="got@email.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            location="Brisbane"
        )
    ]

    db.session.add_all(users)

    media = [
        Media(
            title="Iron Man",
            year="2008",
            category="movie", 
            genre="Action, Adventure, Sci-Fi", 
            director="Jon Favreau", 
            writer="Derek Kolstad", 
            actors="Robert Downey Jr., Gwyneth Paltrow, Terrence Howard", 
            plot="Tony Stark. Genius, billionaire, playboy, philanthropist. Son of legendary inventor and weapons contractor Howard Stark. When Tony Stark is assigned to give a weapons presentation to an Iraqi unit led by Lt. Col. James Rhodes, he's given a ride on enemy lines. That ride ends badly when Stark's Humvee that he's riding in is attacked by enemy combatants. He survives - barely - with a chest full of shrapnel and a car battery attached to his heart. In order to survive he comes up with a way to miniaturize the battery and figures out that the battery can power something else. Thus Iron Man is born. He uses the primitive device to escape from the cave in Iraq. Once back home, he then begins work on perfecting the Iron Man suit. But the man who was put in charge of Stark Industries has plans of his own to take over Tony's technology for other matters.",
            country="United States, Canada", 
            ratings=[
				{
					"Source": "Internet Movie Database",
					"Value": "7.9/10"
				},
				{
					"Source": "Rotten Tomatoes",
					"Value": "94%"
				},
				{
					"Source": "Metacritic",
					"Value": "79/100"
				}
			],
            metascore="92", 
            box_office="$319,034,126"
        ),

        Media(
            title="Thor",
            year="2011",
            category="movie", 
            genre="Action, Fantasy", 
            director="Kenneth Branagh", 
            writer="Ashley Miller, Zack Stenz, Don Payne", 
            actors="Chris Hemsworth, Anthony Hopkins, Natalie Portman", 
            plot="The warrior Thor (Chris Hemsworth) is cast out of the fantastic realm of Asgard by his father Odin (Sir Anthony Hopkins) for his arrogance and sent to Earth to live amongst humans. Falling in love with scientist Jane Foster (Natalie Portman) teaches Thor much-needed lessons, and his new-found strength comes into play as a villain from his homeland sends dark forces toward Earth.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "7.0/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "77%"
		},
		{
			"Source": "Metacritic",
			"Value": "57/100"
		}
	],
            metascore="57", 
            box_office="$181,030,624"
        ),

        Media(
            title="Captain America",
            year="2011",
            category="movie", 
            genre="Action, Adventure, Sci-Fi", 
            director="Joe Johnston", 
            writer="Christopher Markus, Stephen McFeely, Joe Simon", 
            actors="Chris Evans, Hugo Weaving, Samual L. Jackson", 
            plot="It is 1942, America has entered World War II, and sickly but determined Steve Rogers is frustrated at being rejected yet again for military service. Everything changes when Dr. Erskine recruits him for the secret Project Rebirth. Proving his extraordinary courage, wits and conscience, Rogers undergoes the experiment and his weak body is suddenly enhanced into the maximum human potential. When Dr. Erskine is then immediately assassinated by an agent of Nazi Germany's secret HYDRA research department (headed by Johann Schmidt, a.k.a. the Red Skull), Rogers is left as a unique man who is initially misused as a propaganda mascot; however, when his comrades need him, Rogers goes on a successful adventure that truly makes him Captain America, and his war against Schmidt begins.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "6.9/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "80%"
		},
		{
			"Source": "Metacritic",
			"Value": "66/100"
		}
	],
            metascore="66", 
            box_office="$176,654,505"
        ),

        Media(
            title="The Avengers",
            year="2012",
            category="movie", 
            genre="Action, Sci-Fi", 
            director="Joss Whedon", 
            writer="Joss Whedon, Zak Penn", 
            actors="Robert Downey Jr., Chris Evans, Scarlett Johanson, Chris Hemsworth, Mark Ruffalo, Samual L. Jackson, Jeremy Renner", 
            plot="Loki, the adopted brother of Thor, teams-up with the Chitauri Army and uses the Tesseract's power to travel from Asgard to Midgard to plot the invasion of Earth and become a king. The director of the agency S.H.I.E.L.D., Nick Fury, sets in motion project Avengers, joining Tony Stark a.k.a. the Iron Man; Steve Rogers, a.k.a. Captain America; Bruce Banner, a.k.a. The Hulk; Thor; Natasha Romanoff, a.k.a. Black Widow; and Clint Barton, a.k.a. Hawkeye, to save the world from the powerful Loki and the alien invasion.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.0/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "91%"
		},
		{
			"Source": "Metacritic",
			"Value": "69/100"
		}
	],
            metascore="69", 
            box_office="$623,357,910"
        ),

        Media(
            title="Guardians of the Galaxy",
            year="2014",
            category="movie", 
            genre="Action, Adventure, Comedy", 
            director="James Gunn", 
            writer="James gunn, Nicole Perlman, Dan Abnett", 
            actors="Chris Pratt, Vin Diesel, Bradley Cooper", 
            plot="After stealing a mysterious orb in the far reaches of outer space, Peter Quill from Earth is now the main target of a manhunt led by the villain known as Ronan the Accuser. To help fight Ronan and his team and save the galaxy from his power, Quill creates a team of space heroes known as the \"Guardians of the Galaxy\" to save the galaxy.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.0/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "92%"
		},
		{
			"Source": "Metacritic",
			"Value": "76/100"
		}
	],
            metascore="76", 
            box_office="$333,718,600"
        ),

        Media(
            title="John Wick",
            year="2014",
            category="movie", 
            genre="Action, Crime, Thriller", 
            director="Chad Stahelski, David Leitch", 
            writer="Derek Kolstad", 
            actors="Keanu Reeves, Michael Nyqvist, Alfie Allen", 
            plot="With the untimely death of his beloved wife still bitter in his mouth, John Wick, the expert former assassin, receives one final gift from her--a precious keepsake to help John find a new meaning in life now that she is gone. But when the arrogant Russian mob prince, Iosef Tarasov, and his men pay Wick a rather unwelcome visit to rob him of his prized 1969 Mustang and his wife's present, the legendary hitman will be forced to unearth his meticulously concealed identity. Blind with revenge, John will immediately unleash a carefully orchestrated maelstrom of destruction against the sophisticated kingpin, Viggo Tarasov, and his family, who are fully aware of his lethal capacity. Now, only blood can quench the boogeyman's thirst for retribution.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "7.4/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "86%"
		},
		{
			"Source": "Metacritic",
			"Value": "68/100"
		}
	],
            metascore="68", 
            box_office="$43,037,835"
        ),

        Media(
            title="Pulp Fiction",
            year="1994",
            category="movie", 
            genre="Crime, Drama", 
            director="Quentin Tarantino", 
            writer="Quentin Tarantino, Roger Avary", 
            actors="John Travolta, Uma Thurman, Samual L. Jackson", 
            plot="Jules Winnfield (Samuel L. Jackson) and Vincent Vega (John Travolta) are two hit men who are out to retrieve a suitcase stolen from their employer, mob boss Marsellus Wallace (Ving Rhames). Wallace has also asked Vincent to take his wife Mia (Uma Thurman) out a few days later when Wallace himself will be out of town. Butch Coolidge (Bruce Willis) is an aging boxer who is paid by Wallace to lose his fight. The lives of these seemingly unrelated people are woven together comprising of a series of funny, bizarre and uncalled-for incidents.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.9/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "92%"
		},
		{
			"Source": "Metacritic",
			"Value": "95/100"
		}
	],
            metascore="95", 
            box_office="$107,928,762"
        ),

        Media(
            title="The Lord of the Rings: The Fellowship of the Ring",
            year="2001",
            category="movie", 
            genre="Action, Adventure, Drama", 
            director="Peter Jackson", 
            writer="J.R.R. Tolkien, Fran Walsh, Philippa Boyens", 
            actors="Elijah Wood, Ian Mckellen, Orlando Bloom", 
            plot="An ancient Ring thought lost for centuries has been found, and through a strange twist of fate has been given to a small Hobbit named Frodo. When Gandalf discovers the Ring is in fact the One Ring of the Dark Lord Sauron, Frodo must make an epic quest to the Cracks of Doom in order to destroy it. However, he does not go alone. He is joined by Gandalf, Legolas the elf, Gimli the Dwarf, Aragorn, Boromir, and his three Hobbit friends Merry, Pippin, and Samwise. Through mountains, snow, darkness, forests, rivers and plains, facing evil and danger at every corner the Fellowship of the Ring must go. Their quest to destroy the One Ring is the only hope for the end of the Dark Lords reign.",
            country="New Zealand, United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.9/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "91%"
		},
		{
			"Source": "Metacritic",
			"Value": "92/100"
		}
	],
            metascore="92", 
            box_office="$316,115,420"
        ),

        Media(
            title="Inception",
            year="2010",
            category="movie", 
            genre="Action, Adventure, Sci-Fi", 
            director="Christopher Nolan", 
            writer="Christopher Nolan", 
            actors="Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page", 
            plot="Dom Cobb is a skilled thief, the absolute best in the dangerous art of extraction, stealing valuable secrets from deep within the subconscious during the dream state, when the mind is at its most vulnerable. Cobb's rare ability has made him a coveted player in this treacherous new world of corporate espionage, but it has also made him an international fugitive and cost him everything he has ever loved. Now Cobb is being offered a chance at redemption. One last job could give him his life back but only if he can accomplish the impossible, inception. Instead of the perfect heist, Cobb and his team of specialists have to pull off the reverse: their task is not to steal an idea, but to plant one. If they succeed, it could be the perfect crime. But no amount of careful planning or expertise can prepare the team for the dangerous enemy that seems to predict their every move. An enemy that only Cobb could have seen coming.",
            country="United States, United Kingdom", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.8/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "87%"
		},
		{
			"Source": "Metacritic",
			"Value": "74/100"
		}
	],
            metascore="74", 
            box_office="$292,587,330"
        ),

        Media(
            title="Avatar",
            year="2009",
            category="movie", 
            genre="Action, Adventure, Fantasy", 
            director="James Cameron", 
            writer="James Cameron", 
            actors="Sam Worthington, Zoe Saldana, Sigourney Weaver", 
            plot="When his brother is killed in a robbery, paraplegic Marine Jake Sully decides to take his place in a mission on the distant world of Pandora. There he learns of greedy corporate figurehead Parker Selfridge's intentions of driving off the native humanoid \"Na'vi\" in order to mine for the precious material scattered throughout their rich woodland. In exchange for the spinal surgery that will fix his legs, Jake gathers knowledge, of the Indigenous Race and their Culture, for the cooperating military unit spearheaded by gung-ho Colonel Quaritch, while simultaneously attempting to infiltrate the Na'vi people with the use of an \"avatar\" identity. While Jake begins to bond with the native tribe and quickly falls in love with the beautiful alien Neytiri, the restless Colonel moves forward with his ruthless extermination tactics, forcing the soldier to take a stand - and fight back in an epic battle for the fate of Pandora.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "7.9/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "82%"
		},
		{
			"Source": "Metacritic",
			"Value": "83/100"
		}
	],
            metascore="83", 
            box_office="$785,221,649"
        ),

        Media(
            title="Game of Thrones",
            year="2011-2019",
            category="series", 
            genre="Action, Adventure, Drama", 
            writer="David Benioff, D.B Weiss", 
            actors="Emilia Clarke, Peter Dinklage, Kit Harington", 
            plot="In the mythical continent of Westeros, several powerful families fight for control of the Seven Kingdoms. As conflict erupts in the kingdoms of men, an ancient enemy rises once again to threaten them all. Meanwhile, the last heirs of a recently usurped dynasty plot to take back their homeland from across the Narrow Sea.",
            country="United States, United Kingdom", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "9.2/10"
		}
	]
        ),

        Media(
            title="Breaking Bad",
            year="2008-2013",
            category="series", 
            genre="Crime, Drama, Thriller", 
            writer="Vince Gilligan", 
            actors="Bryan Cranston, Aaron Paul, Anna Gunn", 
            plot="When chemistry teacher Walter White is diagnosed with Stage III cancer and given only two years to live, he decides he has nothing to lose. He lives with his teenage son, who has cerebral palsy, and his wife, in New Mexico. Determined to ensure that his family will have a secure future, Walt embarks on a career of drugs and crime. He proves to be remarkably proficient in this new world as he begins manufacturing and selling methamphetamine with one of his former students. The series tracks the impacts of a fatal diagnosis on a regular, hard working man, and explores how a fatal diagnosis affects his morality and transforms him into a major player of the drug trade.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "9.5/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "96%"
		}
	]
        ),

        Media(
            title="Stranger Things",
            year="2016-2025",
            category="series", 
            genre="Drama, Fantasy, Horror", 
            writer="Matt Duffer, Russ Duffer", 
            actors="Millie Bobby Brown, Finn Wolfhard, Winona Ryder", 
            plot="In a small town where everyone knows everyone, a peculiar incident starts a chain of events that leads to the disappearance of a child, which begins to tear at the fabric of an otherwise peaceful community. Dark government agencies and seemingly malevolent supernatural forces converge on the town, while a few of the locals begin to understand that there's more going on than meets the eye.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.7/10"
		}
	]
        ),

        Media(
            title="The Witcher",
            year="2019-",
            category="series", 
            genre="Action, Adventure, Drama", 
            writer="Lauren Schmidt Hissrich", 
            actors="Freya Allan, Henry Cavill, Anya Chalotra", 
            plot="The Witcher is a fantasy drama web television series created by Lauren Schmidt Hissrich for Netflix. It is based on the book series of the same name by Polish writer Andrzej Sapkowski. The Witcher follows the story of Geralt of Rivia, a solitary monster hunter, who struggles to find his place in a world where people often prove more wicked than monsters and beasts. But when destiny hurtles him toward a powerful sorceress, and a young princess with a special gift, the three must learn to navigate independently the increasingly volatile Continent.",
            country="Poland, Hungary, United States, United Kingdom", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.0/10"
		}
	]
        ),

        Media(
            title="The Big Bang Theory",
            year="2007-2019",
            category="series", 
            genre="Comedy, Romance", 
            writer="Chuck Lorre, Bill Prady", 
            actors="Johnny Galecki, Jim Parsons, Kaley Cuoco", 
            plot="Leonard Hofstadter and Sheldon Cooper are both brilliant physicists working at Cal Tech in Pasadena, California. They are colleagues, best friends, and roommates, although in all capacities their relationship is always tested primarily by Sheldon's regimented, deeply eccentric, and non-conventional ways. They are also friends with their Cal Tech colleagues mechanical engineer Howard Wolowitz and astrophysicist Rajesh Koothrappali. The foursome spend their time working on their individual work projects, playing video games, watching science-fiction movies, or reading comic books. As they are self-professed nerds, all have little or no luck with women. When Penny, a pretty woman and an aspiring actress from Omaha, moves into the apartment across the hall from Leonard and Sheldon's, Leonard has another aspiration in life, namely to get Penny to be his girlfriend.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.1/10"
		}
	]
        ),

        Media(
            title="Brooklyn Nine-Nine",
            year="2013-2021",
            category="series", 
            genre="Comedy Crime", 
            writer="Dan Goor, Michael Schur", 
            actors="Andy Samberg, Stephanie Beatriz, Terry Crews", 
            plot="Captain Ray Holt takes over Brooklyn's 99th precinct, which includes Detective Jake Peralta, a talented but carefree detective who's used to doing whatever he wants. The other employees of the 99th precinct include Detective Amy Santiago, Jake's over achieving and competitive partner; Detective Rosa Diaz, a tough and kept to herself coworker; Detective Charles Boyle, Jake's best friend who also has crush on Rosa; Detective Sergeant Terry Jeffords, who was recently taken off the field after the birth of his twin girls; and Gina Linetti, the precinct's sarcastic administrator.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.4/10"
		}
	]
        ),

        Media(
            title="The Simpsons",
            year="1989-2025",
            category="series", 
            genre="Animation, Comedy", 
            writer="James L. Brooks, Matt Groening, Sam Simon", 
            actors="Dan Castellaneta, Nancy Cartwright, Harry Shearer", 
            plot="This is an animated sitcom about the antics of a dysfunctional family. Homer is the oafish unhealthy beer loving father, Marge is the hardworking homemaker wife, Bart is the perpetual ten-year-old underachiever (and proud of it), Lisa is the unappreciated eight-year-old genius, and Maggie is the cute, pacifier loving silent infant.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.7/10"
		},
		{
			"Source": "Rotten Tomatoes",
			"Value": "85%"
		}
	]
        ),
        
        Media(
            title="South Park",
            year="1997-",
            category="series", 
            genre="Animation, Comedy", 
            writer="Trey Parker, Matt Stone, Brian Graden", 
            actors="Trey Parker, Matt Stone, Isaac Hayes", 
            plot="The curious, adventure-seeking, fourth grade group of 10 year old boys, Stan, Kyle, Cartman, and Kenny, all join in in buffoonish adventures that sometimes evolve nothing. Sometimes something that was simple at the start, turns out to get out of control. Everything is odd in the small mountain town, South Park, and the boys always find something to do with it.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.7/10"
		}
	]
        ),

        Media(
            title="Lucifer",
            year="2016-2021",
            category="series", 
            genre="Crime, Drama, Fantasy", 
            writer="Tom Kapinos", 
            actors="Tom Ellis, Lauren German, Kevin Alejandro", 
            plot="Lucifer Morningstar, bored from his sulking life in hell, comes to live in Los Angeles. While there, he helps humanity with its miseries through his experience and telepathic abilities to bring people's deepest desires and thoughts out of them. While meeting with a Detective in his nightclub (Lux), a shootout involving him and the Detective leads him to become an LAPD consultant who tries to punish people for their crimes through law and justice.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.1/10"
		}
	]
        ),

        Media(
            title="Supernatural",
            year="2005-2020",
            category="series", 
            genre="Drama, Fantasy, Horror", 
            writer="Erik Kripke", 
            actors="Jared Padalecki, Jensen Ackles, Jim Beaver", 
            plot="John Winchester raised his two sons Sam and Dean to hunt and kill all things that go \"bump in the night\" after his wife Mary was murdered by an evil supernatural being when the boys were little. 22 years later the brothers set out on a journey, fighting evil along the way, to find their recently-missing father; when they finally do he reveals he knows what demon killed their mother and has found a way to track and kill it. Meanwhile, Sam develops frightening abilities such as seeing visions of people dying before it actually happens. These visions are somehow connected to the demon that murdered his mother and its mysterious plans that seem to be all about Sam. When their father dies striking a deal with that very same demon, the brothers determine to finish his crusade. But disturbing revelations about Sam's part in the demon's apocalyptic plan are presented when John's dying last words to Dean are revealed.",
            country="United States", 
            ratings=[
		{
			"Source": "Internet Movie Database",
			"Value": "8.4/10"
		}
	]
        )

        
    ]

    db.session.add_all(media)

    interactions = [
        Interaction(
            watched="yes",
            rating=9,
            user_id=5,
            media_id=1
        ),

        Interaction(
            watchlist="yes",
            user_id=8,
            media_id=4
        ),

        Interaction(
            watchlist="yes",
            user_id=8,
            media_id=5
        ),

        Interaction(
            watched="yes",
            rating=7,
            user_id=6,
            media_id=11
        ),

        Interaction(
            watched="yes",
            rating=4,
            user_id=6,
            media_id=13
        ),

        Interaction(
            watchlist="yes",
            user_id=8,
            media_id=3
        ),

        Interaction(
            watchlist="yes",
            user_id=10,
            media_id=3
        ),

        Interaction(
            watched="yes",
            user_id=4,
            media_id=20
        ),

        Interaction(
            watched="yes",
            rating=8,
            user_id=7,
            media_id=19
        ),

        Interaction(
            watched="yes",
            rating=10,
            watchlist="yes",
            user_id=7,
            media_id=20
        )
    ]

    db.session.add_all(interactions)

    comments = [
        Comment(
            content="This is the best movie ever made, its a must see!",
            user_id=5,
            media_id=1
        ),

        Comment(
            content="Wasn't the biggest fan of this movie, certainly underwhelming compared to other marvel movies i've seen.",
            user_id=10,
            media_id=1
        ),

        Comment(
            content="Not sure if you can tell from my name but im a huge fan of this series. Great story, great cast, could not recommend this show more higly.",
            user_id=10,
            media_id=11
        ),

        Comment(
            content="This is a really entertaining series, it has witty dialogue, a charming cast and a gripping storyline. Lucifer is definitely one to binge.",
            user_id=7,
            media_id=19
        ),

        Comment(
            content="I think this movie is pretty good, although maybe a little too hard to follow at times.",
            user_id=4,
            media_id=9
        ),

        Comment(
            content="A true classic, this has to be Quentin Tarantino's finest work.",
            user_id=8,
            media_id=7
        ),

        Comment(
            content="Loved this series, so gripping and suspenseful. Henry Cavill plays the role of Geralt to perfection!",
            user_id=5,
            media_id=14
        ),

        Comment(
            content="Yeah ikr too bad hes gone next season lol.",
            user_id=7,
            media_id=14,
            parent_id=7
        ),

        Comment(
            content="How dare you, are you insane?",
            user_id=5,
            media_id=1,
            parent_id=2
        ),

        Comment(
            content="I've been really curious about this series, i think im gonna need to give it a watch!",
            user_id=9,
            media_id=19,
            parent_id=4
        )
    ]

    db.session.add_all(comments)
    db.session.commit()

    print("Tables seeded")
