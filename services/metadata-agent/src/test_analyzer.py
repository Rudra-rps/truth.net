"""
Test script for Metadata Agent
Creates test images and analyzes their metadata
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from PIL import Image, PngImagePlugin
import os
from datetime import datetime
from analyzer import MetadataAnalyzer


def create_test_images():
    """Create test images with different metadata scenarios"""
    test_dir = Path(__file__).parent / "test_images"
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Clean image with EXIF
    print("\n📸 Creating test image 1: Clean image with EXIF...")
    img1 = Image.new('RGB', (100, 100), color='blue')
    img1_path = test_dir / "clean_with_exif.jpg"
    img1.save(img1_path, "JPEG", quality=95)
    print(f"   ✓ Saved to {img1_path}")
    
    # Test 2: Image without EXIF (stripped)
    print("\n📸 Creating test image 2: Image without EXIF (stripped)...")
    img2 = Image.new('RGB', (100, 100), color='red')
    img2_path = test_dir / "stripped_exif.jpg"
    img2.save(img2_path, "JPEG", quality=95, exif=b'')
    print(f"   ✓ Saved to {img1_path}")
    
    # Test 3: PNG with metadata
    print("\n📸 Creating test image 3: PNG with metadata...")
    img3 = Image.new('RGB', (100, 100), color='green')
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Software", "Adobe Photoshop CC 2023")
    meta.add_text("Created", datetime.now().isoformat())
    img3_path = test_dir / "edited_image.png"
    img3.save(img3_path, "PNG", pnginfo=meta)
    print(f"   ✓ Saved to {img3_path}")
    
    # Test 4: Mismatched extension
    print("\n📸 Creating test image 4: PNG saved as .jpg...")
    img4 = Image.new('RGB', (100, 100), color='yellow')
    img4_path = test_dir / "fake_jpg.jpg"
    img4.save(img4_path, "PNG")  # PNG format but .jpg extension
    print(f"   ✓ Saved to {img4_path}")
    
    return [img1_path, img2_path, img3_path, img4_path]


def test_metadata_analysis():
    """Test the metadata analyzer"""
    print("\n" + "="*60)
    print("🔍 METADATA AGENT TEST")
    print("="*60)
    
    # Create test images
    test_images = create_test_images()
    
    # Initialize analyzer
    print("\n🚀 Initializing Metadata Analyzer...")
    analyzer = MetadataAnalyzer()
    print("   ✓ Analyzer ready")
    
    # Test each image
    for idx, image_path in enumerate(test_images, 1):
        print(f"\n{'='*60}")
        print(f"Test {idx}: {image_path.name}")
        print(f"{'='*60}")
        
        try:
            result = analyzer.analyze_image(str(image_path))
            
            print(f"\n📊 Analysis Results:")
            print(f"   Risk Score: {result['risk_score']:.2f}")
            print(f"   Signals Detected: {len(result['signals'])}")
            
            if result['signals']:
                print(f"\n⚠️  Detected Signals:")
                for signal in result['signals']:
                    print(f"   • {signal['type']}: {signal['description']}")
                    print(f"     Confidence: {signal['confidence']:.2f}")
            else:
                print(f"\n✓ No suspicious signals detected")
            
            if result.get('metadata', {}).get('exif'):
                exif_count = len(result['metadata']['exif'])
                print(f"\n📋 EXIF Tags Found: {exif_count}")
                if exif_count > 0:
                    print(f"   Sample tags: {list(result['metadata']['exif'].keys())[:5]}")
            
        except Exception as e:
            print(f"\n❌ Error analyzing {image_path.name}: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ METADATA AGENT TESTS COMPLETE")
    print("="*60)
    print("\n💡 Interpretation Guide:")
    print("   • Risk Score 0.0-0.3: Low risk (AUTHENTIC)")
    print("   • Risk Score 0.3-0.6: Medium risk (SUSPICIOUS)")
    print("   • Risk Score 0.6-1.0: High risk (HIGH_RISK)")


if __name__ == "__main__":
    test_metadata_analysis()
