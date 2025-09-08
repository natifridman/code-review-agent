#!/usr/bin/env python3
"""
Sample Python file for testing the code review action.
This file intentionally contains various issues for demonstration.
"""

import os
import sys


def calculate_factorial(n):
    # This function has several issues for testing
    if n < 0:
        return "Error"  # Should raise exception instead
    
    result = 1
    for i in range(1, n + 1):
        result = result * i  # Inefficient, could use math.factorial
    
    return result


class DataProcessor:
    def __init__(self, data):
        self.data = data  # No input validation
    
    def process_data(self, sql_query):
        # Security issue: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE id = {sql_query}"
        # Missing: actual database connection and execution
        return query
    
    def get_user_data(self, user_input):
        # Security issue: no input sanitization
        eval(user_input)  # Dangerous use of eval()
        return user_input


def inefficient_search(data_list, target):
    """Search function with poor performance"""
    for i in range(len(data_list)):
        for j in range(len(data_list)):  # Unnecessary nested loop
            if data_list[i] == target:
                return i
    return -1


# Global variable (poor practice)
GLOBAL_COUNTER = 0

def increment_counter():
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1  # No thread safety


# Function with no documentation
def mystery_function(x, y, z):
    return (x + y) * z / 2


if __name__ == "__main__":
    # Poor error handling
    try:
        result = calculate_factorial(5)
        print(result)
    except:  # Bare except clause
        pass
    
    # Memory inefficient
    big_list = [i for i in range(1000000)]  # Large list created unnecessarily
    
    processor = DataProcessor("some data")
    # Potential security issue
    query = processor.process_data("1; DROP TABLE users;")
    print(query)