import os
import re

# Base directory for WebNotes
BASE_DIR = r"C:\Users\Laptop Outlet\Desktop\WebNotes"

# List of courses to update
COURSES = [
    r"CompTia\CompTia-A-220-1201-Notes",
    r"CompTia\CompTia-Network-220-1202-Notes",
    r"CompTia\CompTia-Security-220-1203-Notes",
    r"CompTia\CompTia-Cloud-220-1204-Notes",
    r"CompTia\CompTia-Server-220-1205-Notes",
    r"Cisco\Cisco-CCNA-210-2601-Notes",
    r"Cisco\Cisco-CCNP-210-2602-Notes",
    r"Cisco\Cisco-CCIE-210-2603-Notes"
]

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_pillar_page(course_dir):
    """
    Parses index.html to map lessons to their domains.
    Returns a dict: { 'page_filename': {'title': '...', 'domain': '...', 'siblings': []} }
    """
    index_path = os.path.join(BASE_DIR, course_dir, "index.html")
    if not os.path.exists(index_path):
        print(f"Skipping {course_dir}: index.html not found.")
        return None, None

    content = read_file(index_path)
    
    # regex to find domains and their lists
    # Looking for <div class="topic-section"> ... <h2>Domain ...</h2> ... <ul> ... </ul>
    domain_map = {} # domain_name -> list of {href, text}
    page_info = {} # filename -> {domain, title, course_title}

    # Extract Course Title
    course_title_match = re.search(r'<h1>(.*?)</h1>', content)
    course_title = course_title_match.group(1) if course_title_match else "Course"

    sections = re.findall(r'<div class="topic-section">.*?<h2>(.*?)</h2>(.*?)</ul>', content, re.DOTALL)
    
    for domain_title, list_content in sections:
        links = re.findall(r'<a href="pages/(.*?)">(.*?)</a>', list_content)
        clean_domain = re.sub(r'<.*?>', '', domain_title).strip()
        
        domain_links = []
        for filename, link_text in links:
            domain_links.append({'file': filename, 'text': link_text})
            page_info[filename] = {
                'domain': clean_domain,
                'text': link_text,
                'course_title': course_title
            }
        
        domain_map[clean_domain] = domain_links

    return page_info, domain_map

def update_pillar_page(course_dir):
    """
    Adds FAQ section to index.html if missing.
    """
    index_path = os.path.join(BASE_DIR, course_dir, "index.html")
    if not os.path.exists(index_path):
        return

    content = read_file(index_path)
    
    # Check if FAQ already exists
    if "Frequently Asked Questions" in content:
        return

    # Create FAQ Section
    faq_html = f"""
        <!-- === FAQ Section === -->
        <div class="topic-section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-content" style="padding: 10px;">
                <p><strong>Is this course free?</strong><br>Yes, this is a completely free study guide.</p>
                <p><strong>How do I use these notes?</strong><br>Start from Domain 1.0 and work your way through the lessons. Each lesson links to the next.</p>
                <p><strong>Is this updated?</strong><br>We regularly update content to match the latest exam objectives.</p>
            </div>
        </div>
    """
    
    # Insert before footer
    if "<footer>" in content:
        content = content.replace("<footer>", faq_html + "\n        <footer>")
        write_file(index_path, content)
        print(f"Updated Pillar: {course_dir}")

def update_lesson_pages(course_dir, page_info, domain_map):
    """
    Updates each page in pages/ directory with navigation and SEO links.
    """
    pages_dir = os.path.join(BASE_DIR, course_dir, "pages")
    if not os.path.exists(pages_dir):
        return

    for filename in os.listdir(pages_dir):
        if not filename.endswith(".html"):
            continue
            
        file_path = os.path.join(pages_dir, filename)
        content = read_file(file_path)
        
        info = page_info.get(filename)
        if not info:
            continue # Page not linked in index, skip to avoid errors

        domain = info['domain']
        course_title = info['course_title']
        
        # 1. Inject "Back to Course Hub" (Pillar Link)
        # We put this near the top, after the h1/header if possible, or in the footer
        # User requested "This topic is part of Course A -> link to /a/"
        
        pillar_link_html = f"""
        <div class="course-nav-top" style="margin-bottom: 20px; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff;">
            <p>This topic is part of the <strong><a href="../index.html">{course_title}</a></strong> study guide.</p>
        </div>
        """
        
        # Insert after <div class="header"> or <h1> if header div not found
        if '<div class="course-nav-top"' not in content:
            if '<div class="header">' in content:
                content = content.replace('</div>\n        <div class="section">', '</div>\n' + pillar_link_html + '\n        <div class="section">', 1)
            elif '</h1>' in content:
                 content = content.replace('</h1>', '</h1>\n' + pillar_link_html, 1)

        # 2. Inject "Related Lessons" (Topic Cluster) at the bottom
        siblings = domain_map.get(domain, [])
        related_links_html = '<div class="related-lessons" style="margin-top: 30px;">\n<h3>Related Lessons in ' + domain + '</h3>\n<ul>'
        
        count = 0
        for sib in siblings:
            if sib['file'] == filename:
                continue # Skip self
            if count >= 5: # Limit to 5 related links to avoid clutter
                break
            related_links_html += f'\n<li><a href="{sib["file"]}">{sib["text"]}</a></li>'
            count += 1
            
        related_links_html += '\n</ul>\n</div>'
        
        if '<div class="related-lessons"' not in content:
            # Insert before footer container div or </body>
            if '<div class="footer">' in content:
                 content = content.replace('<div class="footer">', related_links_html + '\n<div class="footer">')
            else:
                 content = content.replace('</body>', related_links_html + '\n</body>')

        write_file(file_path, content)
        print(f"Updated Lesson: {filename} in {course_dir}")


def optimize_performance(file_path):
    """
    Injects performance optimizations like preconnect tags.
    """
    content = read_file(file_path)
    

    # AdSense Preconnect
    preconnect_tag = '<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>'
    
    # Check if Ads are present but Preconnect is missing
    if "adsbygoogle.js" in content and preconnect_tag not in content:
        # Inject before the script or end of head
         content = content.replace("</head>", f"    {preconnect_tag}\n</head>")
         write_file(file_path, content)
         print(f"Optimized (Preconnect): {os.path.basename(file_path)}")


def main():
    print("Starting SEO Updates...")
    for course_dir in COURSES:
        try:
            print(f"Processing {course_dir}...")
            page_info, domain_map = parse_pillar_page(course_dir)
            
            # Update Pillar Page SEO & Performance
            if page_info:
                update_pillar_page(course_dir)
                optimize_performance(os.path.join(BASE_DIR, course_dir, "index.html"))
                
                # Update Lessons
                update_lesson_pages(course_dir, page_info, domain_map)
                
                # Optimize Lessons Performance
                pages_dir = os.path.join(BASE_DIR, course_dir, "pages")
                if os.path.exists(pages_dir):
                    for filename in os.listdir(pages_dir):
                        if filename.endswith(".html"):
                             optimize_performance(os.path.join(pages_dir, filename))

        except Exception as e:
            print(f"Error processing {course_dir}: {e}")
    print("Done.")


if __name__ == "__main__":
    main()
