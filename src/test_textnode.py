import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from textnode import TextNode, TextType, text_node_to_html_node
from markdown_parser import text_to_textnodes

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_equal(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_is_none(self):
        node = TextNode("This is a url", TextType.BOLD)
        self.assertIsNone(node.url)

    def test_not_equal2(self):
        node = TextNode("This is a text string", TextType.BOLD)
        node2 = TextNode("This is also a text string", TextType.BOLD)
        self.assertNotEqual(node, node2)


    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold words!", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold words!")
        self.assertIsNone(html_node.props)

    def test_text_to_textnodes(self):
        test_text = (
            "Wizards are **wise** and _woolly_, "
            "wielding `spells`. "
            "See ![wizard bear](https://boot.dev/bear.png) "
            "and visit [magic library](https://boot.dev/library)."
        )
        nodes = text_to_textnodes(test_text)
        assert nodes[0].text == "Wizards are "
        assert nodes[1].text_type == TextType.BOLD
        assert nodes[1].text == "wise"
        assert nodes[5].text_type == TextType.IMAGE
        assert nodes[5].url == "https://boot.dev/bear.png"
        assert any(
    node.text_type == TextType.LINK and node.text == "magic library" and node.url == "https://boot.dev/library"
    for node in nodes
)


if __name__ == "__main__":
    unittest.main()