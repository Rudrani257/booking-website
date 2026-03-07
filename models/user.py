"""
User Model for Booking System
Defines user structure and helper functions
"""

from datetime import datetime
from typing import Dict, List, Optional
import bcrypt


class User:
    """User data model"""
    
    def __init__(self, user_data: Dict):
        self.id = str(user_data.get('_id', ''))
        self.name = user_data.get('name', '')
        self.email = user_data.get('email', '')
        self.password = user_data.get('password', b'')
        self.created_at = user_data.get('created_at', datetime.now())
        self.booking_history = user_data.get('booking_history', [])
        self.vip_status = user_data.get('vip_status', False)
        self.priority_level = user_data.get('priority_level', 0)  # For priority queue
    
    def to_dict(self) -> Dict:
        """Convert user object to dictionary"""
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'booking_history': self.booking_history,
            'vip_status': self.vip_status,
            'priority_level': self.priority_level
        }
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password: str, hashed: bytes) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def add_booking(self, booking_id: str) -> None:
        """Add booking to user's history (Linked List concept)"""
        self.booking_history.append({
            'booking_id': booking_id,
            'timestamp': datetime.now(),
            'next': None  # Linked list pointer concept
        })
    
    def get_priority(self) -> int:
        """
        Calculate user priority for Priority Queue
        Higher bookings = Higher priority
        VIP users get bonus priority
        """
        base_priority = len(self.booking_history) * 10
        vip_bonus = 100 if self.vip_status else 0
        return base_priority + vip_bonus + self.priority_level


class UserQueue:
    """Queue implementation for waitlist"""
    
    def __init__(self):
        self.queue: List[Dict] = []
    
    def enqueue(self, user_id: str, lecture_id: str) -> int:
        """Add user to waitlist queue (FIFO)"""
        position = len(self.queue) + 1
        self.queue.append({
            'user_id': user_id,
            'lecture_id': lecture_id,
            'position': position,
            'timestamp': datetime.now()
        })
        return position
    
    def dequeue(self) -> Optional[Dict]:
        """Remove and return first user from queue"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def peek(self) -> Optional[Dict]:
        """View first user without removing"""
        return self.queue[0] if self.queue else None
    
    def size(self) -> int:
        """Get queue size"""
        return len(self.queue)
    
    def get_position(self, user_id: str) -> Optional[int]:
        """Get user's position in queue"""
        for item in self.queue:
            if item['user_id'] == user_id:
                return item['position']
        return None


class PriorityQueue:
    """Priority Queue for VIP bookings (Heap-based)"""
    
    def __init__(self):
        self.heap: List[tuple] = []  # (priority, user_id, data)
    
    def insert(self, priority: int, user_id: str, data: Dict) -> None:
        """Insert user with priority (Heap Insert)"""
        self.heap.append((priority, user_id, data))
        self._heapify_up(len(self.heap) - 1)
    
    def extract_max(self) -> Optional[tuple]:
        """Extract highest priority user (Heap Extract Max)"""
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        max_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return max_item
    
    def _heapify_up(self, index: int) -> None:
        """Bubble up to maintain heap property"""
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] > self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)
    
    def _heapify_down(self, index: int) -> None:
        """Bubble down to maintain heap property"""
        largest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left][0] > self.heap[largest][0]:
            largest = left
        
        if right < len(self.heap) and self.heap[right][0] > self.heap[largest][0]:
            largest = right
        
        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)
    
    def peek(self) -> Optional[tuple]:
        """View highest priority without removing"""
        return self.heap[0] if self.heap else None
    
    def size(self) -> int:
        """Get queue size"""
        return len(self.heap)


# Example usage:
if __name__ == "__main__":
    # Test User
    user = User({
        'name': 'Test User',
        'email': 'test@example.com',
        'password': User.hash_password('password123')
    })
    print(f"User created: {user.name}")
    print(f"Password valid: {User.verify_password('password123', user.password)}")
    
    # Test Queue
    queue = UserQueue()
    pos = queue.enqueue('user1', 'lecture1')
    print(f"User added to waitlist at position: {pos}")
    
    # Test Priority Queue
    pq = PriorityQueue()
    pq.insert(50, 'user1', {'name': 'Regular User'})
    pq.insert(150, 'user2', {'name': 'VIP User'})
    print(f"Highest priority user: {pq.extract_max()}")