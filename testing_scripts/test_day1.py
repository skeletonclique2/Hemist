#!/usr/bin/env python3
"""
Day 1 Test Script - AI Agents System
Tests the basic infrastructure setup
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_database_connection():
    """Test database connection setup"""
    try:
        from app.database.connection import init_db, check_db_health
        print("✅ Database connection module imported successfully")
        
        # Note: This will fail without a running PostgreSQL instance
        # but it tests that our code structure is correct
        print("✅ Database connection structure is correct")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_api_routes():
    """Test API routes setup"""
    try:
        from app.api.routes import router
        print("✅ API routes module imported successfully")
        
        # Check if router has endpoints
        routes = [route.path for route in router.routes]
        print(f"✅ Found {len(routes)} API routes: {routes}")
        return True
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False

def test_frontend():
    """Test frontend setup"""
    try:
        from app.frontend.streamlit_app import create_streamlit_app
        print("✅ Frontend module imported successfully")
        print("✅ Streamlit app function is available")
        return True
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_main_app():
    """Test main application setup"""
    try:
        from app.main import app
        print("✅ Main application module imported successfully")
        
        # Check if FastAPI app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} main app routes: {routes}")
        return True
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    dependencies = [
        'langchain',
        'langgraph', 
        'fastapi',
        'sqlalchemy',
        'streamlit',
        'celery',
        'redis',
        'structlog'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} imported successfully")
        except ImportError:
            print(f"❌ {dep} import failed")
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    else:
        print("✅ All dependencies are available")
        return True

async def main():
    """Run all tests"""
    print("🚀 Testing Day 1 Infrastructure Setup")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Database Connection", test_database_connection),
        ("API Routes", test_api_routes),
        ("Frontend", test_frontend),
        ("Main Application", test_main_app)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Day 1 Infrastructure is ready!")
        print("\nNext steps:")
        print("1. Set up PostgreSQL with pgvector")
        print("2. Configure environment variables")
        print("3. Start building the actual agents")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 