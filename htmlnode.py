


class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if self.props == None:
            return 
        result = ""
        for key in self.props:
            value = self.props[key]
            result += f' {key}="{value}"' 
        return result
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        props_str = self.props_to_html() or ""
        if self.tag == "img":
            return f"<img{props_str}/>"
        if self.value == None:
            raise ValueError("No value")
        if self.tag == None:
            return f"{self.value}"
        else:
           return f"<{self.tag}{props_str}>{self.value}</{self.tag}>"
        

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        props_string = self.props_to_html() or ""
        if self.tag == None:
            raise ValueError("No tag")
        if self.children == None:
            raise ValueError("No children")
        else:
            child_types = ""
            for child in self.children:
                child_types += child.to_html()
            return f"<{self.tag}{props_string}>{child_types}</{self.tag}>"
