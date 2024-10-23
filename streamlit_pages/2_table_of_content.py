import os
import importlib.util
import inspect


import streamlit as st

import streamlit_antd_components as sac
from anytree import Node, PreOrderIter
from regulations_rag.regulation_table_of_content import StandardTableOfContent


# If there is page reload, switch to a page where init_session was called.
if 'chat' not in st.session_state:
    st.switch_page('question_answering.py')

st.title('Table of Content')

st.markdown('**A few quirks to note when navigating this page:**\n\
- Click on the triangle to the left of the word "Corpus" below to expand the source documents.\n\
- If the triangle rotates (as if it\'s expanding) but nothing happens, try selecting the word "Corpus" (it should change to red) and then press the triangle again to expand the list. \n\
- The Table of Content generally functions as expected after the first level of the tree has been expanded.')
st.markdown('Want more documents included? Reach out to me on <a href="https://www.linkedin.com/in/steven-davey-12295415" target="_blank">linkedin</a>', unsafe_allow_html=True)
st.markdown("---")
    

def load_class_from_file(filepath):
    spec = importlib.util.spec_from_file_location("module.name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find the class that is not abstract
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__ and not inspect.isabstract(obj):
            return obj
    raise ValueError(f"No suitable class found in {filepath}")


# Function to add a property to every node in the tree
def add_property_to_all_nodes(root, property_name, property_value):
    for node in PreOrderIter(root):
        setattr(node, property_name, property_value)


def anytree_to_treeitem(node):
    if not hasattr(node, 'full_node_name') or node.full_node_name == '':
        if node.name == '':
            name = 'Corpus'
        else:
            name = node.name

        return sac.TreeItem(
        label= name,
        children=[anytree_to_treeitem(child) for child in node.children] if node.children else None
        )
    else: 
        return sac.TreeItem(
            label= f'{node.full_node_name} {node.heading_text}',
            children=[anytree_to_treeitem(child) for child in node.children] if node.children else None
        )



@st.cache_resource
def load_tree_data():
    date_ordered_list_of_documents = ['gdpr.py', 'article_30_5.py', 'article_47_bcr.py', 'decision_making.py', 'dpia.py', 'dpo.py', 'article_49_intl_transfer.py',
                                    'lead_sa.py', 'data_breach.py', 'data_portability.py', 'transparency.py', 'codes.py', 'online_services.py', 'territorial_scope.py',
                                    'video.py', 'covid_health.py', 'covid_location.py', 'consent.py', 'forgotten.py', 'protection.py']


    input_folder = './gdpr_rag/documents/'

    combined_toc = Node("Corpus")

    for filename in date_ordered_list_of_documents:
        filepath = os.path.join(input_folder, filename)
        Class = load_class_from_file(filepath)
        instance = Class()
        toc = instance.get_toc()
        class_name = Class.__name__
        add_property_to_all_nodes(toc.root, 'document', class_name)
        toc.root.parent = combined_toc

    sac_tree = anytree_to_treeitem(combined_toc.root)
    # Display the tree using sac.tree
    return combined_toc, sac_tree


def find_nth_item(tree_item, n):
    def traverse_tree(item, count):
        if count[0] == n:
            return item
        count[0] += 1
        for child in item.children:
            result = traverse_tree(child, count)
            if result:
                return result
        return None
    return traverse_tree(tree_item, [0])

def get_text_for_node(node_number):
    combined_toc = st.session_state['tree_data']
    anytree_node = find_nth_item(combined_toc, node_number)
    
    if hasattr(find_nth_item(combined_toc, node_number), "full_node_name"):
        node = find_nth_item(combined_toc, node_number)
        return st.session_state['chat'].corpus.get_document(node.document).get_text(node.full_node_name, add_markdown_decorators = True, add_headings = True, section_only = False)
    else:
        return "No selection to display yet"



if 'tree' not in st.session_state:    
    anytree_toc, sac_tree_data = load_tree_data()
    st.session_state['tree'] = sac_tree_data
    st.session_state['tree_data'] = anytree_toc

selected = sac.tree(items=[st.session_state['tree']], label='Included Documents', size='md', return_index=True)

st.write(get_text_for_node(selected), unsafe_allow_html=True)

