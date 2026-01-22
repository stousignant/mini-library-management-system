"""
Application-wide constants and configuration values.

This module centralizes all static values, magic numbers, and configuration
to maintain a single source of truth and prevent hardcoded values throughout
the codebase.
"""

from app.models.enums import BookStatus

# Application Metadata
APP_TITLE = "Library Management System"
APP_DESCRIPTION = "MVP API for managing books, users, and borrow logs"
APP_VERSION = "0.1.0"

# API Endpoints
ROOT_MESSAGE = "Library Management System API"
HEALTH_STATUS_HEALTHY = "healthy"

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# Book Configuration
DEFAULT_BOOK_STATUS = BookStatus.AVAILABLE
BOOK_TITLE_MAX_LENGTH = 255
BOOK_AUTHOR_MAX_LENGTH = 255
BOOK_ISBN_MAX_LENGTH = 20
BOOK_COVER_IMAGE_MAX_LENGTH = 500
BOOK_SUMMARY_MAX_LENGTH = 1000
BOOK_FIELD_MIN_LENGTH = 1

# Database Configuration
DB_TEST_CONNECT_ARGS = {"server_settings": {"jit": "off"}, "ssl": "disable"}
DEFAULT_TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test"

# CORS Configuration
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_METHODS = ["*"]
CORS_ALLOW_ALL_HEADERS = ["*"]

# Open Library API Configuration
OPEN_LIBRARY_API_BASE_URL = "https://openlibrary.org"
OPEN_LIBRARY_COVERS_BASE_URL = "https://covers.openlibrary.org"

# Seed Data Configuration - 100 Curated Books by Genre
SEED_BOOK_ISBNS = [
    # Programming & Tech (20 books)
    "9780132350884",  # Clean Code - Robert C. Martin
    "9780201616224",  # The Pragmatic Programmer - Andy Hunt
    "9780321125217",  # Domain-Driven Design - Eric Evans
    "9780134685991",  # Effective Java - Joshua Bloch
    "9780596007126",  # Head First Design Patterns - Freeman
    "9780201633610",  # Design Patterns - Gang of Four
    "9781491950296",  # Python Crash Course - Eric Matthes
    "9781617294136",  # The Go Programming Language - Donovan
    "9780131103627",  # The C Programming Language - Kernighan
    "9781449355739",  # Learning Python - Mark Lutz
    "9780134494166",  # Clean Architecture - Robert C. Martin
    "9780137081073",  # The Clean Coder - Robert C. Martin
    "9781491904244",  # You Don't Know JS - Kyle Simpson
    "9780596517748",  # JavaScript: The Good Parts - Crockford
    "9780134757599",  # Refactoring - Martin Fowler
    "9780201835953",  # The Mythical Man-Month - Brooks
    "9780596805838",  # Programming Pearls - Jon Bentley
    "9780321934116",  # Peopleware - DeMarco & Lister
    "9781680502398",  # The Pragmatic Programmer (20th Ed) - Hunt
    "9780135957059",  # The Pragmatic Programmer (New) - Hunt
    # Classic Literature (25 books)
    "9780451524935",  # 1984 - George Orwell
    "9780743273565",  # The Great Gatsby - F. Scott Fitzgerald
    "9780061120084",  # To Kill a Mockingbird - Harper Lee
    "9780141439518",  # Pride and Prejudice - Jane Austen
    "9780141439556",  # Jane Eyre - Charlotte Bronte
    "9780486280615",  # Wuthering Heights - Emily Bronte
    "9780141439600",  # Great Expectations - Charles Dickens
    "9780143107569",  # Anna Karenina - Leo Tolstoy
    "9780142437339",  # Moby-Dick - Herman Melville
    "9780486411095",  # The Odyssey - Homer
    "9780140449136",  # The Brothers Karamazov - Dostoevsky
    "9780140283334",  # Crime and Punishment - Dostoevsky
    "9780141439662",  # Frankenstein - Mary Shelley
    "9780141439846",  # Dracula - Bram Stoker
    "9780307594006",  # The Picture of Dorian Gray - Wilde
    "9780141182568",  # Of Mice and Men - John Steinbeck
    "9780141182957",  # The Grapes of Wrath - Steinbeck
    "9780679783268",  # Brave New World - Aldous Huxley
    "9780141187761",  # Lord of the Flies - William Golding
    "9780143039990",  # Catch-22 - Joseph Heller
    "9780140186475",  # One Hundred Years of Solitude - Marquez
    "9780679732242",  # The Catcher in the Rye - J.D. Salinger
    "9780141182803",  # Animal Farm - George Orwell
    "9780141394619",  # Emma - Jane Austen
    "9780141441146",  # Sense and Sensibility - Jane Austen
    # Science Fiction (20 books)
    "9780441013593",  # Dune - Frank Herbert
    "9780345391803",  # The Hitchhiker's Guide - Douglas Adams
    "9780307474278",  # Ender's Game - Orson Scott Card
    "9780553293357",  # Foundation - Isaac Asimov
    "9780441569595",  # Neuromancer - William Gibson
    "9780553283686",  # Snow Crash - Neal Stephenson
    "9780553573404",  # A Fire Upon the Deep - Vernor Vinge
    "9780441007462",  # Starship Troopers - Robert Heinlein
    "9780441172719",  # Stranger in a Strange Land - Heinlein
    "9780765342294",  # Old Man's War - John Scalzi
    "9780316129084",  # The Left Hand of Darkness - Le Guin
    "9780441569588",  # The Diamond Age - Neal Stephenson
    "9781857231380",  # Consider Phlebas - Iain M. Banks
    "9780553418026",  # Red Mars - Kim Stanley Robinson
    "9780441013579",  # Hyperion - Dan Simmons
    "9780812550702",  # Ender's Shadow - Orson Scott Card
    "9780441005482",  # Do Androids Dream of Electric Sheep - Dick
    "9780441478125",  # The Mote in God's Eye - Niven
    "9780441569564",  # Cryptonomicon - Neal Stephenson
    "9780316219013",  # The Forever War - Joe Haldeman
    # Fantasy (10 books)
    "9780547928227",  # The Hobbit - J.R.R. Tolkien
    "9780547928210",  # The Fellowship of the Ring - Tolkien
    "9780439708180",  # Harry Potter and the Sorcerer's Stone - Rowling
    "9780439064873",  # Harry Potter and the Chamber of Secrets - Rowling
    "9780756404079",  # The Name of the Wind - Patrick Rothfuss
    "9780765326355",  # The Way of Kings - Brandon Sanderson
    "9780553381689",  # A Game of Thrones - George R.R. Martin
    "9780765348784",  # Mistborn - Brandon Sanderson
    "9780316055437",  # The Blade Itself - Joe Abercrombie
    "9780441012688",  # American Gods - Neil Gaiman
    # Business & Self-Help (15 books)
    "9780735211292",  # Atomic Habits - James Clear
    "9781400067084",  # Zero to One - Peter Thiel
    "9780307887894",  # The Lean Startup - Eric Ries
    "9780062316110",  # Sapiens - Yuval Noah Harari
    "9781476753850",  # The 7 Habits of Highly Effective People - Covey
    "9780307465351",  # Thinking, Fast and Slow - Kahneman
    "9780062301239",  # Outliers - Malcolm Gladwell
    "9780062301253",  # The Tipping Point - Malcolm Gladwell
    "9781594484803",  # Drive - Daniel H. Pink
    "9780143126560",  # Grit - Angela Duckworth
    "9780812993011",  # The Power of Habit - Charles Duhigg
    "9781591846444",  # Start with Why - Simon Sinek
    "9780062457714",  # The Subtle Art of Not Giving a F*ck - Manson
    "9780143127741",  # Educated - Tara Westover
    "9780525656654",  # Talking to Strangers - Malcolm Gladwell
    # Non-Fiction & History (10 books)
    "9780385537858",  # Homo Deus - Yuval Noah Harari
    "9780345816023",  # Born a Crime - Trevor Noah
    "9780385490818",  # The Immortal Life of Henrietta Lacks - Skloot
    "9781476751061",  # Steve Jobs - Walter Isaacson
    "9780307720979",  # Unbroken - Laura Hillenbrand
    "9780399590504",  # Becoming - Michelle Obama
    "9780307455253",  # The Wright Brothers - David McCullough
    "9780812974492",  # The Devil in the White City - Erik Larson
    "9780385490813",  # The Boys in the Boat - Daniel James Brown
    "9780385537728",  # When Breath Becomes Air - Paul Kalanithi
]
