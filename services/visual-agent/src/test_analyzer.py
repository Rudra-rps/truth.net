"""
Quick test script for Visual Agent
Creates a test image and tests the analyzer
"""
import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from analyzer import VisualAnalyzer

def create_test_image(filename="test_image.jpg"):
    """Create a simple test image with a face-like shape"""
    # Create a blank image
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    
    # Draw a face-like circle (will be detected by MediaPipe)
    cv2.circle(img, (200, 200), 80, (255, 200, 150), -1)  # Face
    cv2.circle(img, (170, 180), 10, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (230, 180), 10, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (200, 220), (30, 15), 0, 0, 180, (100, 50, 50), 2)  # Mouth
    
    # Save image
    cv2.imwrite(filename, img)
    print(f"✅ Created test image: {filename}")
    return filename

def test_analyzer():
    """Test the visual analyzer"""
    print("\n🔍 Testing Visual Analyzer...")
    
    # Create test image
    test_img = create_test_image()
    
    # Initialize analyzer
    analyzer = VisualAnalyzer()
    
    try:
        # Analyze image
        print(f"\n📸 Analyzing {test_img}...")
        result = analyzer.analyze_image(test_img)
        
        print(f"\n📊 Results:")
        print(f"  - Faces detected: {result['faces_detected']}")
        print(f"  - Risk score: {result['risk_score']:.2f}")
        print(f"  - Artifacts found: {len(result['artifacts'])}")
        
        if result['artifacts']:
            print(f"\n⚠️ Artifacts detected:")
            for artifact in result['artifacts']:
                print(f"  - {artifact['type']}: {artifact['description']}")
                print(f"    Confidence: {artifact['confidence']:.2f}")
        else:
            print(f"\n✅ No artifacts detected")
        
        print(f"\n✅ Analyzer test PASSED!")
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        raise
    finally:
        analyzer.cleanup()
        # Clean up test file
        Path(test_img).unlink(missing_ok=True)

if __name__ == "__main__":
    test_analyzer()
