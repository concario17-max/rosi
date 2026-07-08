import zipfile
import os

def inspect_odt():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    odt_path = os.path.join(workspace_dir, "장미 2-1.odt")
    
    if not os.path.exists(odt_path):
        print(f"File {odt_path} does not exist.")
        return
        
    print(f"Inspecting {odt_path}...")
    with zipfile.ZipFile(odt_path, 'r') as zip_ref:
        image_files = [info.filename for info in zip_ref.infolist() if info.filename.startswith("Pictures/")]
        print(f"Total image files in ODT Pictures/ folder: {len(image_files)}")
        for img in image_files[:10]:
            print(f"  - {img}")
        if len(image_files) > 10:
            print("  ...")

if __name__ == "__main__":
    inspect_odt()
