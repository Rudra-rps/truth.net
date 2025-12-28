"""
End-to-End Test for TruthNet API
Tests the complete pipeline: API -> Agents -> Verdict
"""
import requests
import json
from pathlib import Path
from PIL import Image

def test_truthnet_api():
    print("=" * 60)
    print("🧪 TRUTHNET END-TO-END TEST")
    print("=" * 60)
    
    # Check services
    print("\n📡 Checking services...")
    
    services = [
        ("Visual Agent", "http://localhost:8001/health"),
        ("Metadata Agent", "http://localhost:8002/health"),
        ("API Server", "http://localhost:8000/health"),
    ]
    
    for name, url in services:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                print(f"   ✓ {name}: Running")
            else:
                print(f"   ✗ {name}: Error ({resp.status_code})")
                return False
        except Exception as e:
            print(f"   ✗ {name}: Not running ({str(e)})")
            return False
    
    # Create test image
    print("\n📸 Creating test image...")
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    test_image = test_dir / "test_upload.jpg"
    img = Image.new('RGB', (800, 600), color='blue')
    img.save(test_image, 'JPEG')
    print(f"   ✓ Test image created: {test_image}")
    
    # Upload and analyze
    print("\n🚀 Uploading file to API...")
    print(f"   File: {test_image}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image.name, f, 'image/jpeg')}
            response = requests.post(
                'http://localhost:8000/analyze',
                files=files,
                timeout=60
            )
        
        if response.status_code != 200:
            print(f"\n❌ API call failed with status {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Display verdict with color
        verdict = result['verdict']
        verdict_colors = {
            'AUTHENTIC': '\033[92m',  # Green
            'SUSPICIOUS': '\033[93m',  # Yellow
            'HIGH_RISK': '\033[91m',  # Red
        }
        color = verdict_colors.get(verdict, '\033[0m')
        print(f"\n🎯 VERDICT: {color}{verdict}\033[0m")
        
        print(f"📊 Risk Score: {result['risk_score']:.2f}")
        print(f"🎲 Confidence: {result['confidence']:.2f}")
        print(f"⏱️  Processing Time: {result['processing_time_ms']}ms")
        
        print("\n📋 Agent Breakdown:")
        for agent in result['agent_breakdown']:
            print(f"   • {agent['agent_type']}: Risk={agent['risk_score']:.2f}, Signals={len(agent['signals'])}")
            if agent.get('error'):
                print(f"     Error: {agent['error']['message']}")
        
        print("\n💡 Top Reasons:")
        for reason in result['reasons']:
            print(f"   • {reason}")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Full pipeline working!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_truthnet_api()
    exit(0 if success else 1)
