"""
SEO Enhancement Script for WebNotes
Updates all lesson pages with:
- Fixed canonical URLs (webnotes.site)
- Twitter Card meta tags
- hreflang tags
- BreadcrumbList schema
- LearningResource schema
"""

import os
import re
from pathlib import Path

# Configuration
BASE_URL = "https://webnotes.site"
SITE_NAME = "Webnotes"

# Course configurations
COURSES = {
    "CompTia-A-220-1201-Notes": {
        "name": "CompTIA A+ Core 1 (220-1201)",
        "short_name": "CompTIA A+",
        "path": "CompTia/CompTia-A-220-1201-Notes"
    },
    "CompTia-Network-220-1202-Notes": {
        "name": "CompTIA Network+ (220-1202)",
        "short_name": "CompTIA Network+",
        "path": "CompTia/CompTia-Network-220-1202-Notes"
    },
    "CompTia-Security-220-1203-Notes": {
        "name": "CompTIA Security+ (220-1203)",
        "short_name": "CompTIA Security+",
        "path": "CompTia/CompTia-Security-220-1203-Notes"
    },
    "CompTia-Cloud-220-1204-Notes": {
        "name": "CompTIA Cloud+ (220-1204)",
        "short_name": "CompTIA Cloud+",
        "path": "CompTia/CompTia-Cloud-220-1204-Notes"
    },
    "CompTia-Server-220-1205-Notes": {
        "name": "CompTIA Server+ (220-1205)",
        "short_name": "CompTIA Server+",
        "path": "CompTia/CompTia-Server-220-1205-Notes"
    },
    "Cisco-CCNA-210-2601-Notes": {
        "name": "Cisco CCNA (210-2601)",
        "short_name": "Cisco CCNA",
        "path": "Cisco/Cisco-CCNA-210-2601-Notes"
    },
    "Cisco-CCNP-210-2602-Notes": {
        "name": "Cisco CCNP (210-2602)",
        "short_name": "Cisco CCNP",
        "path": "Cisco/Cisco-CCNP-210-2602-Notes"
    },
    "Cisco-CCIE-210-2603-Notes": {
        "name": "Cisco CCIE (210-2603)",
        "short_name": "Cisco CCIE",
        "path": "Cisco/Cisco-CCIE-210-2603-Notes"
    }
}


def get_course_from_path(file_path):
    """Determine which course a file belongs to based on its path."""
    path_str = str(file_path)
    for course_key, course_info in COURSES.items():
        if course_key in path_str:
            return course_key, course_info
    return None, None


def extract_title(content):
    """Extract the page title from HTML content."""
    match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Study Notes"


def extract_description(content):
    """Extract meta description from HTML content."""
    match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Free IT certification study notes."


def extract_h1(content):
    """Extract the H1 heading from HTML content."""
    match = re.search(r'<h1>([^<]+)</h1>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Study Notes"


def generate_breadcrumb_schema(course_info, lesson_title, page_url):
    """Generate BreadcrumbList JSON-LD schema."""
    return f'''    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "{BASE_URL}/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "{course_info['short_name']}",
          "item": "{BASE_URL}/{course_info['path']}/"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "{lesson_title}"
        }}
      ]
    }}
    </script>'''


def generate_learning_resource_schema(course_info, lesson_title, description, page_url):
    """Generate LearningResource JSON-LD schema."""
    # Escape quotes in strings
    lesson_title_escaped = lesson_title.replace('"', '\\"')
    description_escaped = description.replace('"', '\\"')
    
    return f'''    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "LearningResource",
      "name": "{lesson_title_escaped}",
      "description": "{description_escaped}",
      "url": "{page_url}",
      "educationalLevel": "Beginner to Intermediate",
      "learningResourceType": "Study Notes",
      "isAccessibleForFree": true,
      "inLanguage": "en",
      "isPartOf": {{
        "@type": "Course",
        "name": "{course_info['name']}",
        "provider": {{
          "@type": "Organization",
          "name": "{SITE_NAME}",
          "url": "{BASE_URL}"
        }}
      }}
    }}
    </script>'''


def generate_twitter_cards(title, description):
    """Generate Twitter Card meta tags."""
    title_escaped = title[:70] if len(title) > 70 else title
    desc_escaped = description[:200] if len(description) > 200 else description
    
    return f'''    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title_escaped}">
    <meta name="twitter:description" content="{desc_escaped}">'''


def update_lesson_page(file_path, course_info):
    """Update a single lesson page with enhanced SEO."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Get page info
        title = extract_title(content)
        description = extract_description(content)
        h1_title = extract_h1(content)
        
        # Build the correct URL
        rel_path = str(file_path).replace('\\', '/')
        # Extract path from the course folder onwards
        if course_info['path'] in rel_path:
            path_from_course = rel_path.split(course_info['path'])[1]
            page_url = f"{BASE_URL}/{course_info['path']}{path_from_course}"
        else:
            page_url = f"{BASE_URL}/{course_info['path']}/pages/{file_path.name}"
        
        # Fix canonical URL (replace old GitHub URL with webnotes.site)
        content = re.sub(
            r'<link\s+rel="canonical"\s+href="https://shehan-fdo\.github\.io/[^"]+">',
            f'<link rel="canonical" href="{page_url}">',
            content
        )
        
        # Check if hreflang already exists
        if 'hreflang' not in content:
            # Add hreflang after canonical
            hreflang_tags = f'''
    <!-- Language -->
    <link rel="alternate" hreflang="en" href="{page_url}">
    <link rel="alternate" hreflang="x-default" href="{page_url}">'''
            
            content = re.sub(
                r'(<link\s+rel="canonical"\s+href="[^"]+"[^>]*>)',
                r'\1' + hreflang_tags,
                content
            )
        
        # Check if Twitter Cards already exist
        if 'twitter:card' not in content:
            twitter_cards = generate_twitter_cards(title, description)
            # Insert before </head>
            if '<link rel="stylesheet"' in content:
                content = content.replace(
                    '<link rel="stylesheet"',
                    twitter_cards + '\n\n    <link rel="stylesheet"'
                )
        
        # Check if BreadcrumbList schema already exists
        if 'BreadcrumbList' not in content:
            breadcrumb_schema = generate_breadcrumb_schema(course_info, h1_title, page_url)
            # Insert before </head>
            content = content.replace('</head>', breadcrumb_schema + '\n</head>')
        
        # Check if LearningResource schema already exists
        if 'LearningResource' not in content:
            learning_schema = generate_learning_resource_schema(course_info, h1_title, description, page_url)
            # Insert before </head>
            content = content.replace('</head>', learning_schema + '\n</head>')
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to update all lesson pages."""
    script_dir = Path(__file__).parent
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    print("=" * 60)
    print("WebNotes SEO Enhancement Script")
    print("=" * 60)
    
    # Process each course
    for course_key, course_info in COURSES.items():
        course_path = script_dir / course_info['path'].replace('/', os.sep)
        pages_path = course_path / 'pages'
        
        if not pages_path.exists():
            print(f"\n⚠ Skipping {course_info['short_name']} - no pages directory found")
            continue
        
        print(f"\n📚 Processing: {course_info['name']}")
        
        # Find all HTML files in pages directory
        html_files = list(pages_path.glob('*.html'))
        
        for html_file in html_files:
            result = update_lesson_page(html_file, course_info)
            if result:
                updated_count += 1
                print(f"  ✅ Updated: {html_file.name}")
            else:
                skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Updated: {updated_count} files")
    print(f"⏭ Skipped (already up-to-date): {skipped_count} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
