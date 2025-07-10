from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode
from htmlnode import ParentNode
from enum import Enum
import unittest
import re


class BlockType(Enum):
    PARAGRAPH = 1
    HEADING = 2
    CODE = 3
    QUOTE = 4
    UNORDERED_LIST = 5
    ORDERED_LIST = 6

def block_to_block_type(markdown):
    if markdown.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if markdown.startswith("```") and markdown.endswith("```"):
        return BlockType.CODE

    split_lines = markdown.splitlines()
    is_quote_block = True
    for i in split_lines:
        if not i.startswith(">"):
            is_quote_block = False
            break   
    if is_quote_block:
        return BlockType.QUOTE
    
    is_unordered_list = True
    for i in split_lines:
        if not i.startswith("- "):
            is_unordered_list = False
            break
    if is_unordered_list:
        return BlockType.UNORDERED_LIST
    
    is_ordered_list = True
    counter = 1
    for line in split_lines:
        dot_index = line.find(".")

        if dot_index == -1 or dot_index == 0:
            is_ordered_list = False
            break
        number_str = line[0:dot_index]
        if len(line) <= dot_index + 1 or line[dot_index + 1] != " ":
            is_ordered_list = False
            break
        if not number_str.isdigit() or int(number_str) != counter:
            is_ordered_list = False
            break
        counter += 1
          
    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for object in old_nodes:
        if object.text_type == TextType.TEXT:
            split_nodes = object.text.split(delimiter)
            print(f"SPLIT: {object.text} with delimiter '{delimiter}' → {split_nodes}")
            if len(split_nodes) % 2 == 0:
                raise Exception("Error: invalid markdown")
            elif len(split_nodes) == 1:
                new_nodes.append(object)
            else:
                for i in range(len(split_nodes)):
                    text_content = split_nodes[i]
                    if i % 2 == 0:
                        node_type = TextType.TEXT
                    else:
                        node_type = text_type

                    if text_content:
                        new_nodes.append(TextNode(text_content, node_type))
        else:
            new_nodes.append(object)
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
    images_list = []
    for object in old_nodes:
        if object.text_type == TextType.TEXT:
            images = extract_markdown_images(object.text)
            if len(images) == 0:
                images_list.append(object)
            else:
                new_text_nodes = object.text.split(f"![{images[0][0]}]({images[0][1]})", 1)
                if new_text_nodes[0]:
                    images_list.append(TextNode(new_text_nodes[0], TextType.TEXT))
                if images[0][0]:  
                    images_list.append(TextNode(images[0][0], TextType.IMAGE, images[0][1]))
                if new_text_nodes[1]:  
                    remaining_node = TextNode(new_text_nodes[1], TextType.TEXT)
                    remaining_nodes = split_nodes_image([remaining_node])
                    images_list.extend(remaining_nodes)
        else:
            images_list.append(object)
    return images_list

def split_nodes_link(old_nodes):
    links_list = []
    for object in old_nodes:
        if object.text_type == TextType.TEXT:
            links = extract_markdown_links(object.text)
            if len(links) == 0:
                links_list.append(object)
            else:
                new_text_nodes = object.text.split(f"[{links[0][0]}]({links[0][1]})", 1)
                if new_text_nodes[0]:
                    links_list.append(TextNode(new_text_nodes[0], TextType.TEXT))
                if links[0][0]: 
                    links_list.append(TextNode(links[0][0], TextType.LINK, links[0][1]))
                if new_text_nodes[1]:  
                    remaining_node = TextNode(new_text_nodes[1], TextType.TEXT)
                    remaining_nodes = split_nodes_link([remaining_node])
                    links_list.extend(remaining_nodes)
        else:
            links_list.append(object)
    return links_list

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    result = []
    for node in nodes:
        result.append(node)
    return result

def markdown_to_blocks(markdown):
    split_strings = markdown.split(sep="\n\n")
    stripped_strings = []
    for i in split_strings:
            stripped = i.strip()
            if stripped != "":
                stripped_strings.append(stripped)
    return stripped_strings


def text_to_children(markdown):
    converted_HTML = []
    inline_list = text_to_textnodes(markdown)
    for i in inline_list:
        converted_HTML.append(text_node_to_html_node(i))
    return converted_HTML


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    list_of_blocks = []
    for b in blocks:
        type = block_to_block_type(b)
        if type == BlockType.PARAGRAPH:
            list_of_blocks.append(ParentNode("p", text_to_children(b)))
        elif type == BlockType.HEADING:
            split_string = b.split()
            joined_string = " ".join(split_string[1:])
            if len(split_string[0]) == 1:
                list_of_blocks.append(ParentNode("h1", text_to_children(joined_string)))
            if len(split_string[0]) == 2:
                list_of_blocks.append(ParentNode("h2", text_to_children(joined_string)))
            if len(split_string[0]) == 3:
                list_of_blocks.append(ParentNode("h3", text_to_children(joined_string)))
            if len(split_string[0]) == 4:
                list_of_blocks.append(ParentNode("h4", text_to_children(joined_string)))
            if len(split_string[0]) == 5:
                list_of_blocks.append(ParentNode("h5", text_to_children(joined_string)))
            if len(split_string[0]) == 6:
                list_of_blocks.append(ParentNode("h6", text_to_children(joined_string)))

        elif type == BlockType.ORDERED_LIST:
            split_lines = b.split("\n")
            li_nodes_list =[]
            for line in split_lines:
                remove_spaces = line.split()
                remove_numbers = remove_spaces[1:]
                joined_string = " ".join(remove_numbers)
                li_nodes_list.append(ParentNode("li", text_to_children(joined_string)))
            ol_node = ParentNode("ol", li_nodes_list)
            list_of_blocks.append(ol_node)
           
        elif type == BlockType.UNORDERED_LIST:
            split_lines = b.split("\n")
            li_nodes_list = []
            for line in split_lines:
                joined_string = " ".join(line.split()[1:])
                li_nodes_list.append(ParentNode("li", text_to_children(joined_string)))
            ul_node = ParentNode("ul", li_nodes_list)
            list_of_blocks.append(ul_node)

        elif type == BlockType.QUOTE:
            split_lines = b.split("\n")
            cleaned_lines = []
            for line in split_lines:
                joined_string = " ".join(line.split()[1:])
                cleaned_lines.append(joined_string)
            combined_text = "\n".join(cleaned_lines)
            blockquote_node = ParentNode("blockquote", text_to_children(combined_text))
            list_of_blocks.append(blockquote_node)

        elif type == BlockType.CODE:
            split_lines = b.split("\n")
            removed_markers = "\n".join(split_lines[1:-1])
            text_node = TextNode(removed_markers, TextType.CODE)
            converted_html = text_node_to_html_node(text_node)
            pre_node = ParentNode("pre", [converted_html])
            list_of_blocks.append(pre_node)
        
    parent_node = ParentNode("div", list_of_blocks)
    return parent_node


def extract_title(markdown):
    split_lines = markdown.split("\n")
    for line in split_lines:
        starts_hash = line.strip().startswith("# ")
        if starts_hash:
           return line.strip()[2:].strip()
    raise Exception("No header found")





class TestSplitNodes(unittest.TestCase):
    def test_basic_function(self):
        node = TextNode("This is a `coded` test", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        assert len(result) == 3
        assert result[0].text_type == TextType.TEXT
        assert result[0].text == "This is a "
        assert result[1].text == "coded"
        assert result[1].text_type == TextType.CODE
    
        assert result[2].text == " test"
        assert result[2].text_type == TextType.TEXT

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
            ),
        ],
        new_nodes,
    )

    def test_markdown_to_blocks(self):
        md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )



    def test_paragraphs(self):
        md = """
        This is **bolded** paragraph
        text in a p
        tag here

        This is another paragraph with _italic_ text and `code` here

        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
        ```
        This is text that _should_ remain
        the **same** even with inline stuff
        ```
        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()