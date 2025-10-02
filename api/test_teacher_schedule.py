#!/usr/bin/env python3
"""
Test script for teacher schedule endpoints
"""

import asyncio
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_login_as_teacher():
    """Login as a teacher to get authentication token"""
    login_data = {
        "email": "hada.siham@example.com",  # Teacher email
        "password": "motdepasse123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful for: {data.get('user', {}).get('nom', 'Unknown')}")
        return data.get('access_token')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_teacher_stats(token):
    """Test teacher stats endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/teacher/stats", headers=headers)
    print(f"\nTeacher stats response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Stats data: {json.dumps(data, indent=2)}")
    else:
        print(f"Stats failed: {response.text}")

def test_teacher_today_schedule(token):
    """Test teacher today's schedule endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
    print(f"\nToday's schedule response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Today's schedule count: {len(data)}")
        if data:
            print(f"First schedule: {json.dumps(data[0], indent=2)}")
        else:
            print("No schedules for today")
    else:
        print(f"Today's schedule failed: {response.text}")

def test_teacher_schedule_range(token):
    """Test teacher schedule with date range"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test current week
    from datetime import datetime, timedelta
    today = datetime.now()
    start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=6-today.weekday())).strftime('%Y-%m-%d')
    
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    response = requests.get(f"{BASE_URL}/teacher/schedule", headers=headers, params=params)
    print(f"\nWeek schedule response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Week schedule data: {json.dumps(data, indent=2)}")
    else:
        print(f"Week schedule failed: {response.text}")

def main():
    print("Testing Teacher Schedule Endpoints")
    print("=" * 50)
    
    # Login as teacher
    token = test_login_as_teacher()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Test endpoints
    test_teacher_stats(token)
    test_teacher_today_schedule(token)
    test_teacher_schedule_range(token)

if __name__ == "__main__":
    main()