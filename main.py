import os
import shutil
from enum import Enum
from markdown_parser import markdown_to_html_node, extract_title
import traceback

if os.path.exists("public"):
    shutil.rmtree("public")
    os.makedirs("public", exist_ok=True)

def copy_contents_recursive(source_dir, dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)
    source_list = os.listdir(source_dir)
    for item in source_list:
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        print(f"Copying: {source_path} to {dest_path}")

        if os.path.isfile(source_path) == False:
            os.mkdir(dest_path)
            copy_contents_recursive(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)

    
def main():
    source_static_dir = "static"
    dest_public_dir = "public"

    print(f"Starting copy from {source_static_dir} to {dest_public_dir}...")
    copy_contents_recursive(source_static_dir, dest_public_dir)
    print("Copy complete!")

    generate_pages_recursive("content", "template.html", "public")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    try:
        with open(from_path, "r") as f:
            markdown_content = f.read()
        print("Loaded markdown content")

        with open(template_path, "r") as f:
            template_content = f.read()
        print("Loaded template content")

        html_node = markdown_to_html_node(markdown_content)
        print("Converted markdown to html_node")


        print("About to call to_html()")
        html_content = html_node.to_html()
        print("Generated html_content")

        print("About to call title")
        title = extract_title(markdown_content)
        print(f"Extracted title: {title}")

        page = template_content.replace("{{ Title }}", title)
        page = page.replace("{{ Content }}", html_content)
        print("Replaced template placeholders")

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        print(f"Writing to {dest_path}")

        with open(dest_path, "w") as f:
            f.write(page)
        print("Write complete")

    except Exception as e:
        print("ERROR in generate_page:", e)
        traceback.print_exc()
   

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    dir_list = os.listdir(dir_path_content)
    for path in dir_list:
        if os.path.isfile(os.path.join(dir_path_content, path)):
            if path.endswith(".md"):
                generate_page(os.path.join(dir_path_content, path), template_path, os.path.join(dest_dir_path, (path[:-3] + ".html")))
        else:
            os.makedirs(os.path.join(dest_dir_path, path), exist_ok=True)
            generate_pages_recursive(os.path.join(dir_path_content, path), template_path, os.path.join(dest_dir_path, path))


      
if __name__ == "__main__":
    main()