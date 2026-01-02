import os
import datetime

# Configuration
BASE_URL = "https://webnotes.site"
BASE_DIR = r"C:\Users\Laptop Outlet\Desktop\WebNotes"
OUTPUT_FILE = os.path.join(BASE_DIR, "sitemap.xml")

# Files/Dirs to ignore
IGNORE_DIRS = {".git", ".gemini", "_template", "images", "css", "js"}
IGNORE_FILES = {"google", "ads.txt", "CNAME", "robots.txt", "style.css", "index-style.css", ".gitignore"}

def generate_sitemap():
    print(f"Generating sitemap for {BASE_URL}...")
    
    urls = []
    
    # Walk the directory
    for root, dirs, files in os.walk(BASE_DIR):
        # Filter directories in place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if not file.endswith(".html"):
                continue
                
            if any(ign in file for ign in IGNORE_FILES):
                continue

            # Calculate relative path
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
            
            # Construct URL
            final_url = f"{BASE_URL}/{rel_path}"
            
            # Determine priority and changefreq
            priority = "0.5"
            changefreq = "monthly"
            
            if rel_path == "index.html":
                priority = "1.0"
                changefreq = "weekly"
            elif file == "index.html": # Course Pillar Pages
                priority = "0.8"
                changefreq = "weekly"
            else: # Lesson Pages
                priority = "0.6"
                
            # Get last modified time
            mtime = os.path.getmtime(full_path)
            lastmod = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            url_entry = f"""  <url>
    <loc>{final_url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
            urls.append(url_entry)

    # Build XML
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
        
    print(f"Sitemap generated with {len(urls)} URLs at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_sitemap()
