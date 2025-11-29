#!/usr/bin/env python3
"""
Reinforcement Learning Agent for Embedding Optimization

This module implements a reinforcement learning agent that optimizes embedding generation
based on feedback from the system performance.
"""

import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from embedcore_v3 import generate_embedding

class RLEmbeddingAgent:
    """Reinforcement Learning Agent for optimizing embeddings."""
    
    def __init__(self, db_path: str = "assistant_core.db"):
        """
        Initialize the RL agent.
        
        Args:
            db_path (str): Path to the database file
        """
        self.db_path = db_path
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self.q_table = {}  # State-action value table
        
    def _get_db_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def store_experience(self, state: str, action: str, reward: float, next_state: str):
        """
        Store an experience in the database.
        
        Args:
            state (str): Current state
            action (str): Action taken
            reward (float): Reward received
            next_state (str): Resulting state
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rl_experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reward REAL NOT NULL,
                    next_state TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Insert experience
            timestamp = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO rl_experiences (state, action, reward, next_state, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (state, action, reward, next_state, timestamp))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error storing experience: {e}")
            return False
    
    def get_experiences(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve experiences from the database.
        
        Args:
            limit (int): Maximum number of experiences to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of experiences
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT state, action, reward, next_state, timestamp
                FROM rl_experiences
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            experiences = []
            for row in rows:
                state, action, reward, next_state, timestamp = row
                experiences.append({
                    'state': state,
                    'action': action,
                    'reward': reward,
                    'next_state': next_state,
                    'timestamp': timestamp
                })
            
            return experiences
        except Exception as e:
            print(f"Error retrieving experiences: {e}")
            return []
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """
        Update Q-value using Q-learning update rule.
        
        Args:
            state (str): Current state
            action (str): Action taken
            reward (float): Reward received
            next_state (str): Resulting state
        """
        # Initialize Q-values if not present
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
            
        if next_state not in self.q_table:
            self.q_table[next_state] = {}
        
        # Get max Q-value for next state
        max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        
        # Q-learning update rule
        current_q = self.q_table[state][action]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def select_action(self, state: str, possible_actions: List[str]) -> str:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state (str): Current state
            possible_actions (List[str]): List of possible actions
            
        Returns:
            str: Selected action
        """
        # Initialize Q-values for this state if not present
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in possible_actions}
        else:
            # Add any new actions that aren't in the Q-table yet
            for action in possible_actions:
                if action not in self.q_table[state]:
                    self.q_table[state][action] = 0.0
        
        # Epsilon-greedy action selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(possible_actions)
        else:
            # Exploit: best known action
            q_values = [self.q_table[state][action] for action in possible_actions]
            best_action_idx = np.argmax(q_values)
            return possible_actions[best_action_idx]
    
    def train_from_experiences(self):
        """Train the agent from stored experiences."""
        experiences = self.get_experiences()
        
        if not experiences:
            print("No experiences to train on")
            return
        
        print(f"Training on {len(experiences)} experiences...")
        
        for exp in experiences:
            self.update_q_value(
                exp['state'],
                exp['action'],
                exp['reward'],
                exp['next_state']
            )
        
        print("Training completed")
    
    def get_optimized_embedding_params(self, text: str) -> Dict[str, Any]:
        """
        Get optimized parameters for embedding generation based on learned policies.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Optimized parameters
        """
        # In a real implementation, this would use the learned Q-table to
        # determine optimal embedding generation parameters
        # For now, we'll return default parameters
        return {
            'dimensions': 384,  # Standard for sentence transformers
            'normalize': True,
            'technique': 'standard'  # Could be 'advanced' based on learning
        }

# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = RLEmbeddingAgent()
    
    # Example training loop
    print("RL Embedding Agent initialized")
    print(f"Using database: {agent.db_path}")
    
    # Train from existing experiences
    agent.train_from_experiences()
    
    # Example of storing an experience
    state = "high_latency_request"
    action = "use_cached_embedding"
    reward = 0.8  # Positive reward for reduced latency
    next_state = "request_completed"
    
    success = agent.store_experience(state, action, reward, next_state)
    if success:
        print("Experience stored successfully")
    else:
        print("Failed to store experience")