#!/usr/bin/env python3
"""
Quick test script to check available Gemini models and test summarization
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔍 Listing available Gemini models...")
print("=" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")
        print()

print("=" * 80)
print("\n🧪 Testing a simple summary with models/gemini-pro...")

try:
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content("Summarize: The quick brown fox jumps over the lazy dog.")
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
