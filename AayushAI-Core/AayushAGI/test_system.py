#!/usr/bin/env python3
"""
Test script for AayushAGI system to verify no segmentation faults occur
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from utils.helper import speak, load_json, save_json
        print("✅ Helper utilities imported successfully")
        
        from utils.encryption import verify_password, set_password
        print("✅ Encryption utilities imported successfully")
        
        from brain import AayushAGI, brain_ai
        print("✅ Brain module imported successfully")
        
        from main import show_banner, authenticate_user
        print("✅ Main module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_speak_function():
    """Test the speak function"""
    print("\n🔊 Testing speak function...")
    
    try:
        from utils.helper import speak
        speak("Testing AayushAGI voice system")
        print("✅ Speak function works without segmentation fault")
        return True
    except Exception as e:
        print(f"❌ Speak function error: {e}")
        return False

def test_agi_initialization():
    """Test AayushAGI initialization"""
    print("\n🧠 Testing AayushAGI initialization...")
    
    try:
        from brain import AayushAGI
        agi = AayushAGI()
        print("✅ AayushAGI initialized successfully")
        
        # Test a simple input processing
        result = agi.process_input("hello")
        print("✅ Input processing works")
        
        return True
    except Exception as e:
        print(f"❌ AayushAGI initialization error: {e}")
        return False

def test_banner():
    """Test banner display"""
    print("\n🎨 Testing banner display...")
    
    try:
        from main import show_banner
        show_banner()
        print("✅ Banner displayed successfully")
        return True
    except Exception as e:
        print(f"❌ Banner display error: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 AayushAGI System Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_speak_function,
        test_agi_initialization,
        test_banner
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AayushAGI is ready to use.")
        print("\n💡 To enable actual voice output, run:")
        print("   export AAYUSH_TTS_ENABLED=true")
        print("   python3 main.py")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
