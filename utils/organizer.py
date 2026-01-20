
import os
import shutil

def organize_files(folder_path):
    """Sorts files into categorical subfolders."""
    try:
        # Resolve path (handle 'downloads', 'desktop')
        if "downloads" in folder_path.lower():
            target_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        elif "desktop" in folder_path.lower() or "dextop" in folder_path.lower():
            target_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            target_dir = os.path.abspath(folder_path)
            
        if not os.path.exists(target_dir): return f"Folder not found: {target_dir}"
        
        print(f"📂 Organizing Folder: {target_dir}")
        
        # Categories
        EXT_MAP = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            "Documents": ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.csv', '.pptx', '.md'],
            "Video": ['.mp4', '.mkv', '.mov', '.avi', '.webm'],
            "Audio": ['.mp3', '.wav', '.aac', '.flac'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "Apps": ['.exe', '.msi', '.bat', '.iso', '.lnk'], 
            "Code_Projects": ['.py', '.js', '.html', '.css', '.java', '.cpp', '.json']
        }
        
        stats = {k: 0 for k in EXT_MAP.keys()}
        moved_count = 0
        
        # Create folders
        for cat in EXT_MAP:
            cat_path = os.path.join(target_dir, cat)
            if not os.path.exists(cat_path):
                os.makedirs(cat_path)

        # Move Files
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            
            # Skip directories and self
            if os.path.isdir(file_path): continue
            if filename.startswith("."): continue 
            if filename.lower() in ["desktop.ini", "thumbs.db"]: continue
            
            # Find Category
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            dest_cat = None
            for cat, extensions in EXT_MAP.items():
                if ext in extensions:
                    dest_cat = cat
                    break
            
            if dest_cat:
                dest_path = os.path.join(target_dir, dest_cat, filename)
                
                # Handle Duplicates
                if os.path.exists(dest_path):
                    base, ex = os.path.splitext(filename)
                    dest_path = os.path.join(target_dir, dest_cat, f"{base}_copy{ex}")
                
                try:
                    shutil.move(file_path, dest_path)
                    stats[dest_cat] += 1
                    moved_count += 1
                except Exception as e:
                    print(f"Skipped {filename}: {e}")
                
        report = f"Organization Complete for {os.path.basename(target_dir)}.\n"
        for cat, count in stats.items():
            if count > 0: report += f"- Moved {count} files to {cat}/\n"
            
        if moved_count == 0: return "Folder appears to be already organized or empty."
        return report

    except Exception as e:
        return f"Organization Failed: {e}"
