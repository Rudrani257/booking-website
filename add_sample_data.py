from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client['booking_website']
lectures_collection = db['lectures']

# Clear existing lectures
lectures_collection.delete_many({})

# Sample Lectures Data with Real Teacher Images
sample_lectures = [
    {
        'youtuber_name': 'Striver (Raj Vikramaditya)',
        'youtuber_photo': 'https://i.postimg.cc/28JrYThd/striver.jpg',  # Add actual image
        'topic': 'DSA',
        'lecture_title': 'Arrays & Hashing Masterclass',
        'date': datetime.now() + timedelta(days=1),
        'duration': '3 Hours',
        'venue': 'Mumbai Tech Hub, Andheri',
        'topics_covered': [
            'Arrays Deep Dive - All Patterns',
            'HashMap & HashSet Techniques',
            '15+ Problem Solving (Easy to Hard)',
            'Live Doubt Clearing Session'
        ],
        'total_seats': 60,
        'available_seats': 45,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 12},
            'mid': {'total': 20, 'available': 18},
            'back': {'total': 20, 'available': 15}
        }
    },
    {
        'youtuber_name': 'Apna College (Aman Dhattarwal)',
        'youtuber_photo': 'https://i.postimg.cc/gcXm8Nqy/apna-college.jpg',
        'topic': 'Python',
        'lecture_title': 'Python for Beginners - Full Course',
        'date': datetime.now() + timedelta(days=2),
        'duration': '3 Hours',
        'venue': 'Delhi Tech Center, Noida',
        'topics_covered': [
            'Python Basics - Variables, Data Types',
            'Functions & OOP Concepts',
            'File Handling & Exception Handling',
            'Build 3 Mini Projects'
        ],
        'total_seats': 60,
        'available_seats': 52,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 16},
            'mid': {'total': 20, 'available': 18},
            'back': {'total': 20, 'available': 18}
        }
    },
    {
        'youtuber_name': 'Code with Harry',
        'youtuber_photo': 'https://i.postimg.cc/Fz5rK8pN/harry.jpg',
        'topic': 'Java',
        'lecture_title': 'Java Full Stack Development',
        'date': datetime.now() + timedelta(days=3),
        'duration': '3 Hours',
        'venue': 'Bangalore Tech Park, Whitefield',
        'topics_covered': [
            'Core Java - OOP Principles',
            'Spring Boot Basics',
            'REST API Development',
            'Database Integration with MySQL'
        ],
        'total_seats': 60,
        'available_seats': 38,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 8},
            'mid': {'total': 20, 'available': 15},
            'back': {'total': 20, 'available': 15}
        }
    },
    {
        'youtuber_name': 'Kunal Kushwaha',
        'youtuber_photo': 'https://i.postimg.cc/W4yRLhY5/kunal.jpg',
        'topic': 'DSA',
        'lecture_title': 'Recursion & Backtracking Bootcamp',
        'date': datetime.now() + timedelta(days=5),
        'duration': '3 Hours',
        'venue': 'Pune IT Hub, Hinjewadi',
        'topics_covered': [
            'Recursion - Pattern Recognition',
            'Backtracking Problems',
            'N-Queens, Sudoku Solver',
            '20+ Practice Problems'
        ],
        'total_seats': 60,
        'available_seats': 28,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 5},
            'mid': {'total': 20, 'available': 10},
            'back': {'total': 20, 'available': 13}
        }
    },
    {
        'youtuber_name': 'Tanay Pratap',
        'youtuber_photo': 'https://i.postimg.cc/j5Lh9KQs/tanay.jpg',
        'topic': 'Python',
        'lecture_title': 'Web Development with Django',
        'date': datetime.now() + timedelta(days=7),
        'duration': '3 Hours',
        'venue': 'Hyderabad Cyber City, Madhapur',
        'topics_covered': [
            'Django Framework Setup',
            'MVC Architecture',
            'Database Models & ORM',
            'Build a Blog Application'
        ],
        'total_seats': 60,
        'available_seats': 55,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 18},
            'mid': {'total': 20, 'available': 19},
            'back': {'total': 20, 'available': 18}
        }
    },
    {
        'youtuber_name': 'Love Babbar',
        'youtuber_photo': 'https://i.postimg.cc/XYzK5nmp/love-babbar.jpg',
        'topic': 'DSA',
        'lecture_title': 'Graph Algorithms - BFS, DFS & Dijkstra',
        'date': datetime.now() + timedelta(days=10),
        'duration': '3 Hours',
        'venue': 'Chennai Tech Center, OMR',
        'topics_covered': [
            'Graph Representation (Adjacency List/Matrix)',
            'BFS & DFS Traversal',
            'Dijkstra\'s Shortest Path Algorithm',
            '25+ Graph Problems'
        ],
        'total_seats': 60,
        'available_seats': 42,
        'price_front': 860,
        'price_mid': 700,
        'price_back': 600,
        'seats_layout': {
            'front': {'total': 20, 'available': 10},
            'mid': {'total': 20, 'available': 16},
            'back': {'total': 20, 'available': 16}
        }
    }
]

# Insert lectures
result = lectures_collection.insert_many(sample_lectures)
print(f"✅ Successfully added {len(result.inserted_ids)} lectures!")
print("Lecture IDs:", result.inserted_ids)