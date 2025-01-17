import dearpygui.dearpygui as dpg
import json
import yaml
import os
from utils import *
from swagger_codegen_utils import *

dpg.create_context()

dict_for_json_export = {
    "nodes": {},
    "links": {},
    "short": [],
    "AIDA": {}
}

list_json = []

def get_node_data(node_editor_id):
    dict_for_json_export["nodes"] = {}
    list_json.clear()
    # Get all nodes in the node editor
    nodes = dpg.get_item_children(node_editor_id, 1)  # 1 corresponds to children of type 'mvAppItemType::mvNode'
    
    for node_id in nodes:
        # Get node label
        node_label = dpg.get_item_label(node_id)

        # Get node position
        node_pos = dpg.get_item_pos(node_id)
        
        # Get node type
        node_type = dpg.get_item_configuration(node_id)["user_data"]

        # Get all attributes associated with this node
        attributes = dpg.get_item_children(node_id, 1)  # 1 corresponds to children of type 'mvAppItemType::mvNodeAttribute'
        
        attributes_data = {}
        attributes_short = {}
        for attr_id in attributes:
            # Get attribute label
            attr_label = dpg.get_item_label(attr_id)

            # Get attribute type
            item_info = dpg.get_item_configuration(attr_id)
            #print(item_info)
            if "attribute_type" in item_info:
                if item_info["attribute_type"] == 1:
                    attr_type = "mvNode_Attr_Output"
                elif item_info["attribute_type"] == 2:
                    attr_type = "mvNode_Attr_Static"
                else:
                    attr_type = "mvNode_Attr_Input"
            
            # Collect all children of the attribute (input fields)
            input_fields = dpg.get_item_children(attr_id, 1)  # 1 corresponds to children of type 'mvAppItemType'
            
            input_data = {}

            for input_id in input_fields:
                if dpg.get_item_type(input_id) == "mvAppItemType::mvChildWindow":
                    child_window_fields = dpg.get_item_children(input_id, 1)
                    for nested_input in child_window_fields:
                        if dpg.get_item_type(nested_input) == "mvAppItemType::mvInputText":
                            input_label = dpg.get_item_label(nested_input)
                            input_value = dpg.get_value(nested_input)
                            input_type = dpg.get_item_type(nested_input)
                            input_id = nested_input
                            break
                else:
                    # Collect the input field's value and label
                    input_label = dpg.get_item_label(input_id)
                    input_value = dpg.get_value(input_id)
                    input_type = dpg.get_item_type(input_id)
                
                # Store input label and value
                input_data[input_id] = {
                    "label": input_label,
                    "value": input_value,
                    "type": input_type
                }
            
            # Store attribute label and its inputs
            attributes_data[attr_id] = {
                "label": attr_label,
                "type": attr_type,
                "inputs": input_data
            }

            if attr_label != "node transition in" and attr_label != "node transition out" and attr_label != "":
                attributes_short[attr_label] = input_value

        # Store node label, attributes, and their values in the dictionary
        dict_for_json_export["nodes"][node_id] = {
            "label": node_label,
            "attributes": attributes_data,
            "position": node_pos,
            "type": node_type
        }

        # Short dict version
        if node_type == "node_transition":
            attributes_short["operation id"] = node_label
            list_json.append(attributes_short)

            associated_links = get_links_for_node(node_id)
            for link_id, link_data in associated_links:
                start = link_data["start_attr"]
                end = link_data["end_attr"]
                att_end_label = dpg.get_item_label(end)
                att_st_label = dpg.get_item_label(start)
                if att_end_label == "node transition in":
                    parent_node_st = dpg.get_item_parent(start)
                    attributes_short["start"] = dpg.get_item_label(parent_node_st)
                if att_end_label == "node transition out":
                    parent_node_st = dpg.get_item_parent(start)
                    if "end" in attributes_short:
                        attributes_short["end_b"] = dpg.get_item_label(parent_node_st)
                    else:
                        attributes_short["end"] = dpg.get_item_label(parent_node_st)
                if att_st_label == "node transition in":
                    parent_node_en = dpg.get_item_parent(end)
                    attributes_short["start"] = dpg.get_item_label(parent_node_en)
                if att_st_label == "node transition out":
                    parent_node_en = dpg.get_item_parent(end)
                    if "end" in attributes_short:
                        attributes_short["end_b"] = dpg.get_item_label(parent_node_en)
                    else:
                        attributes_short["end"] = dpg.get_item_label(parent_node_en)
        dict_for_json_export["short"] = list_json
    return dict_for_json_export


def transform_json(input_json):
    """
    Transform the input JSON into the specified format.

    Args:
        input_json (list): A list of dictionaries in the input format.

    Returns:
        dict: A dictionary in the desired output format.
    """
    output = {}

    for item in input_json:
        # Extract data
        start_state = item.get("start")
        end_state = item.get("end")
        end_b_state = item.get("end_b")
        operation_id = item.get("operation id")
        probability = item.get("Probability", 0.0)
        reward = item.get("Reward", 0.0)
        unemployable_prob = 1 - probability

        con_key = start_state
        con_action_key = operation_id
        if end_b_state:
            con_value = (
                {
                    end_state: probability,
                    end_b_state: unemployable_prob
                } if unemployable_prob > 0.0 else {end_state: probability},
                reward
            )
        else:
            con_value = (
                {
                    end_state: probability
                },
                reward
            )
        output.setdefault(con_key, {})
        output[con_key][con_action_key] = con_value

    return output


# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    get_node_data("editor")
    if dict_for_json_export["nodes"][dpg.get_item_parent(app_data[0])]["type"] == "node_transition" or dict_for_json_export["nodes"][dpg.get_item_parent(app_data[1])]["type"] == "node_transition":  
        l = dpg.add_node_link(app_data[0], app_data[1], parent=sender, label="label")
        dict_for_json_export["links"][l] = {
            "start_attr": app_data[0], 
            "end_attr": app_data[1]
            }

def resize_to_viewport(sender, app_data):
    # Get the viewport's width and height
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    
    # Resize the window to match the viewport's size
    dpg.set_item_width("node_editor_window", viewport_width)
    dpg.set_item_height("node_editor_window", viewport_height)

# Function to create a custom theme with the desired background color
def create_node_background_theme(color):
    with dpg.theme() as node_theme:
        with dpg.theme_component(dpg.mvNode):
            dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, color, category=dpg.mvThemeCat_Nodes)
    return node_theme

# Function to apply the theme to a specific node
def set_node_background_color(node_id, color):
    node_theme = create_node_background_theme(color)
    dpg.bind_item_theme(node_id, node_theme)

popup_values = ["Add Action Right", "Add Action Left", "Add left pin", "Add right pin", "Mark as Init state", "Change node label"]

popup_node_transition = ["Change node label"]

def add_node_node_callback(sender, app_data):
    dpg.configure_item("node_editor_popup", show=False)
    wind_pos = dpg.get_item_pos("node_editor_popup")
    pos_offset = wind_pos[0] - 400
    node_id = dpg.add_node(parent="editor", label=dpg.get_value("label_node"), user_data="node_state", pos=[pos_offset, wind_pos[1]])
    set_node_background_color(node_id, (0, 146, 204))  # Green background
    with dpg.popup(node_id):
        for i in popup_values:
            dpg.add_selectable(label=i, user_data=[node_id, i], callback=popup_callback)

def popup_callback(sender, app_data, user_data):
    node_id = user_data[0]
    command = user_data[1]
    if command == "Add Action Right":
        att_out_id = add_out_att_text_input(node_id)
        add_node_link_callback(sender=sender, app_data=app_data, user_data=[att_out_id, node_id, "right"])
    elif command == "Add Action Left":
        att_out_id = add_in_att_text_input(node_id)
        add_node_link_callback(sender=sender, app_data=app_data, user_data=[att_out_id, node_id, "left"])
    elif command == "Add right pin":
        add_out_att_no_input(sender=node_id, app_data=app_data, user_data="node state in")
    elif command == "Add left pin":
        add_in_att_no_input(sender=node_id, app_data=app_data, user_data="node state in")
    elif command == "Change node label":
        dpg.configure_item("node_change_label_popup", show=True, user_data=node_id)
    elif command == "Mark as Init state":
        set_node_background_color(node_id, (183, 179, 39))

def add_node_link_callback(sender, app_data, user_data):
    node_id = dpg.add_node(parent="editor", user_data="node_transition")
    node_pos = dpg.get_item_pos(user_data[1])
    if user_data[2] == "right":
        pos_offset = node_pos[0] + 200
        att_in_id = add_in_att_no_input_transition(sender=node_id, app_data=app_data, user_data="node transition in")
        add_out_att_no_input_transition(sender=node_id, app_data=app_data, user_data="node transition out")
    else:
        pos_offset = node_pos[0] - 300
        att_in_id = add_out_att_no_input_transition(sender=node_id, app_data=app_data, user_data="node transition in")
        add_in_att_no_input_transition(sender=node_id, app_data=app_data, user_data="node transition out")
    dpg.set_item_pos(node_id, [pos_offset, node_pos[1]])
    add_static_att(sender=node_id, app_data=app_data)
    add_static_att_float(sender=node_id, app_data=app_data)
    add_static_att_silent(sender=node_id, app_data=app_data)
    add_preconditions_group(sender=node_id, app_data=app_data)
    set_node_background_color(node_id, (255, 51, 51))  # Red background
    link_callback(sender="editor", app_data=[user_data[0], att_in_id])
    with dpg.popup(node_id):
        for i in popup_node_transition:
            dpg.add_selectable(label=i, user_data=[node_id, i], callback=popup_callback)
    return node_id

def add_preconditions_group(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Preconditions", attribute_type=dpg.mvNode_Attr_Static):
        with dpg.child_window(width=200, height=90, border=True, show=False):
            dpg.add_text(default_value="PRE", indent=5)
            dpg.add_input_text(multiline=True, tracked=True, width=200, height=63, label="Pre", callback=check_pre_post)
            dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))
    with dpg.node_attribute(parent=sender, label="Effects", attribute_type=dpg.mvNode_Attr_Static):
        with dpg.child_window(width=200, height=90, border=True, show=False):
            dpg.add_text(default_value="POST", indent=5)
            dpg.add_input_text(multiline=True, tracked=True, width=200, height=63, label="Post", callback=check_pre_post)
            dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))

def check_pre_post(sender, app_data, user_data):
    if not is_boolean_expression(app_data):
        #print(f"'{app_data}' is a valid boolean expression")
        set_error_style(sender)
    else:
        reset_style(sender)

def set_error_style(item):
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0))  # Red text
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 200, 200))  # Light red background

    dpg.bind_item_theme(item, theme)

def reset_style(item):
    dpg.bind_item_theme(item, None)  # Reset theme to default

def create_background_theme(color):
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, color, category=dpg.mvThemeCat_Core)
    return theme

def add_static_att_silent(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Silent", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_checkbox(label="Silent", show=False)

def add_static_att(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Probability", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_float(label="p", width=150, show=False)

def add_static_att_float(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Reward", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_float(label="Reward", width=150, show=False)

def add_in_att_no_input_transition(sender, app_data, user_data):
    with dpg.node_attribute(parent=sender, label=user_data) as att_id:
        pass
    return att_id

def add_out_att_no_input_transition(sender, app_data, user_data):
    with dpg.node_attribute(parent=sender, label=user_data, attribute_type=dpg.mvNode_Attr_Output) as att_id:
        pass
    return att_id

def add_in_att_no_input(sender, app_data, user_data):
    shape = dpg.mvNode_PinShape_TriangleFilled
    with dpg.node_attribute(parent=sender, label=user_data, shape=shape) as att_id:
        dpg.add_text("")
    return att_id

def add_out_att_no_input(sender, app_data, user_data):
    shape = dpg.mvNode_PinShape_TriangleFilled
    with dpg.node_attribute(parent=sender, label=user_data, attribute_type=dpg.mvNode_Attr_Output, shape=shape) as att_id:
        dpg.add_text("")
    return att_id

def add_out_att_text_input(sender):
    with dpg.node_attribute(parent=sender, attribute_type=dpg.mvNode_Attr_Output) as att_id:
        pass
    return att_id

def add_in_att_text_input(sender):
    with dpg.node_attribute(parent=sender, attribute_type=dpg.mvNode_Attr_Input) as att_id:
        pass
    return att_id

# Function to get all links associated with a node (both input and output)
def get_links_for_node(node_id):
    node_attrs = dpg.get_item_children(node_id, 1)
    associated_links = []
    
    # Loop through the link dictionary to find any links involving the node's attributes
    for link_id, link_data in dict_for_json_export["links"].items():
        if link_data["start_attr"] in node_attrs or link_data["end_attr"] in node_attrs:
            associated_links.append((link_id, link_data))
    
    return associated_links

def del_node_callback(sender, app_data):
    get_node_data("editor")
    for node_id in dpg.get_selected_nodes("editor"):
        # Get all links associated with this node
        associated_links = get_links_for_node(node_id)
        for link_id, link_data in associated_links:
            del dict_for_json_export["links"][link_id]
        if dict_for_json_export["nodes"][node_id]["type"] == "node_transition":
            node_attrs = dpg.get_item_children(node_id, 1)
            for link_id, link_data in associated_links:
                for att in node_attrs:
                    if link_data["end_attr"] == att:
                        dpg.delete_item(link_data["start_attr"])
        dpg.delete_item(node_id)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # Remove the link from the list if it exists
    del dict_for_json_export["links"][app_data]
    # app_data -> link_id
    dpg.delete_item(app_data)

def save_json_file(sender, app_data, user_data):
    # Get the directory and file name from the file dialog
    selected_file = app_data["file_path_name"]
    
    if selected_file:
        get_node_data("editor")
        ff = transform_json(dict_for_json_export["short"])
        dict_for_json_export["AIDA"] = ff
        # Export the node data to the selected file
        with open(selected_file, "w") as outfile:
            json.dump(dict_for_json_export, outfile, indent=4, sort_keys=False)
        print(f"File saved to: {selected_file}")

popup_values_editor = ["Add Node"]

# Callback for handling double-click events
def handle_node_double_click(sender, app_data, user_data):
    if dpg.is_item_hovered("editor"):
        for node in dpg.get_item_children("editor", 1):
            if dpg.is_item_hovered(node):
                # Retrieve node details from dictionary
                get_node_data("editor")
                node_data = dict_for_json_export["nodes"].get(node, None)
                node_id_id = node
                if not node_data or node_data["type"] != "node_transition":
                    return
                # Get attributes from the node
                attributes = node_data["attributes"]

                # Create a side window if not already created
                if dpg.does_item_exist("side_window"):
                    dpg.delete_item("side_window", children_only=True)
                    dpg.delete_item("side_window")
                with dpg.window(modal=True, label="Node Transition Details", tag="side_window", width=400, pos=(700, 100)):
                    dpg.add_text(f"Editing Node ID: {node_data["label"]}")
                    for attr_name, attr_value in attributes.items():
                        for input_id, input_data in attr_value["inputs"].items():
                            if input_data["label"] == "p":
                                dpg.add_input_float(tag=str(input_id)+'_'+str(node), width=150, label=input_data["label"], default_value=input_data["value"])
                            elif input_data["label"] == "Reward":
                                dpg.add_input_float(tag=str(input_id)+'_'+str(node), width=150, label=input_data["label"], default_value=input_data["value"])
                            elif input_data["label"] == "Silent":
                                dpg.add_checkbox(tag=str(input_id)+'_'+str(node), label=input_data["label"], default_value=input_data["value"])
                            elif input_data["label"] == "Pre":
                                # with dpg.child_window(width=200, height=90, border=True):
                                dpg.add_text(default_value="PRE", indent=5)
                                dpg.add_input_text(tag=str(input_id)+'_'+str(node), multiline=True, tracked=False, width=200, height=63, 
                                                    default_value=input_data["value"], callback=check_pre_post)
                                    # dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))
                            elif input_data["label"] == "Post":
                                # with dpg.child_window(width=200, height=90, border=True):
                                dpg.add_text(default_value="POST", indent=5)
                                dpg.add_input_text(tag=str(input_id)+'_'+str(node), multiline=True, tracked=False, width=200, height=63, 
                                                    default_value=input_data["value"], callback=check_pre_post)
                                    # dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))
                            else:
                                dpg.add_text(tag=str(input_id)+'_'+str(node), label=input_data["label"], default_value=input_data["value"])
                    dpg.add_button(label="Done", callback=lambda: (save_changes(node_id_id), dpg.configure_item("side_window", show=False)))
    else:
        return

# Callback to save changes back to the dictionary
def save_changes(node):
    node_data = dict_for_json_export["nodes"].get(node, None)
    attributes = node_data["attributes"]
    for attr_name, attr_value in attributes.items():
        for input_id, input_data in attr_value["inputs"].items():
            field_value = dpg.get_value(str(input_id)+'_'+str(node))
            #print(input_id, str(input_id)+'_'+str(node))
            #print(dpg.get_value(input_id), field_value)
            if dpg.does_item_exist(input_id):
                dpg.set_value(input_id, field_value)
            else:
                print(f"Item with ID {input_id} does not exist.")

def show_popup(sender, app_data):
    if dpg.is_item_hovered("editor"):
        for node in dpg.get_item_children("editor", 1):
            if dpg.is_item_hovered(node):
                return
        dpg.focus_item("node_editor_popup")
        dpg.show_item("node_editor_popup")
        dpg.set_item_pos("node_editor_popup", dpg.get_mouse_pos(local=False))
    else:
        pass

# Function to open the file dialog
def json_export():
    # Open a file dialog to select the save location
    dpg.show_item("file_dialog_save")

def open_file_dialog(sender, app_data, user_data):
    file_path = app_data['file_path_name']
    import_json(sender, app_data, file_path)

def import_json(sender, app_data, user_data):
    with open(user_data, "r") as in_file:
        data = json.load(in_file)

    # Create nodes
    for node_id, node_data in data["nodes"].items():
        with dpg.node(tag=node_id, label=node_data["label"], pos=node_data["position"], parent="editor", user_data=node_data["type"]):
            if node_data["type"] == "node_state":
                set_node_background_color(node_id, (0, 146, 204))  # Green background
                with dpg.popup(node_id):
                    for i in popup_values:
                        dpg.add_selectable(label=i, user_data=[node_id, i], callback=popup_callback)
            else:
                set_node_background_color(node_id, (255, 51, 51))  # Red background
                with dpg.popup(node_id):
                    for i in popup_node_transition:
                        dpg.add_selectable(label=i, user_data=[node_id, i], callback=popup_callback)
            for attr_id, attr_data in node_data["attributes"].items():
                shape = dpg.mvNode_PinShape_CircleFilled
                if attr_data["type"] == "mvNode_Attr_Output":
                    attribute_type=dpg.mvNode_Attr_Output
                    if attr_data["label"] == "node state in":
                        shape = dpg.mvNode_PinShape_QuadFilled
                elif attr_data["type"] == "mvNode_Attr_Input":
                    if attr_data["label"] == "node state in":
                        shape = dpg.mvNode_PinShape_TriangleFilled   
                    attribute_type=dpg.mvNode_Attr_Input
                else:
                    attribute_type=dpg.mvNode_Attr_Static      
                with dpg.node_attribute(tag=attr_id, attribute_type=attribute_type, label=attr_data["label"], shape=shape):
                    # Create input fields with stored values
                    for input_id, input_data in attr_data["inputs"].items():
                        if input_data["label"] == "p":
                            dpg.add_input_float(tag=input_id, width=150, label=input_data["label"], default_value=input_data["value"], show=False)
                        elif input_data["label"] == "Reward":
                            dpg.add_input_float(tag=input_id, width=150, label=input_data["label"], default_value=input_data["value"], show=False)
                        elif input_data["label"] == "Silent":
                            dpg.add_checkbox(tag=input_id, label=input_data["label"], default_value=input_data["value"], show=False)
                        elif input_data["label"] == "Pre":
                            with dpg.child_window(width=200, height=90, border=True, show=False):
                                dpg.add_text(default_value="PRE", indent=5)
                                dpg.add_input_text(tag=input_id, multiline=True, tracked=False, width=200, height=63, label=input_data["label"], 
                                                   default_value=input_data["value"])
                                dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))
                        elif input_data["label"] == "Post":
                            with dpg.child_window(width=200, height=90, border=True, show=False):
                                dpg.add_text(default_value="POST", indent=5)
                                dpg.add_input_text(tag=input_id, multiline=True, tracked=False, width=200, height=63, label=input_data["label"], 
                                                   default_value=input_data["value"])

                                dpg.bind_item_theme(dpg.last_container(), create_background_theme((119, 153, 51)))
                        else:
                            dpg.add_text(tag=input_id, label=input_data["label"], default_value=input_data["value"])

    # Create links
    for link in data["links"].values():
        attr_1 = dpg.get_alias_id(str(link["start_attr"]))
        attr_2 = dpg.get_alias_id(str(link["end_attr"]))
        link_callback(sender="editor", app_data=[attr_1, attr_2])

def yaml_export():
    get_node_data("editor")

    selected_file = "modeling_short.json"
    # Export the node data to the selected file
    with open(selected_file, "w") as outfile:
        json.dump(list_json, outfile, indent=2,sort_keys=False)
    print(f"File saved to: {selected_file}")

def json_import():
    dpg.show_item("file_dialog_load")

with dpg.file_dialog(directory_selector=False, show=False, callback=open_file_dialog, tag="file_dialog_load", width=700, height=400):
    dpg.add_file_extension(".json", color=(0, 255, 0, 255))
    dpg.add_file_extension(".*")

with dpg.file_dialog(directory_selector=False, show=False, callback=save_json_file, id="file_dialog_save", width=500, height=300):
    dpg.add_file_extension(".json", color=(150, 255, 150, 255)) 

with dpg.window(id="node_editor_window", label="Node Editor", no_title_bar=True, no_move=True, no_resize=True, no_scrollbar=True):
    with dpg.group(horizontal=True, width=0):
        with dpg.child_window(width=400, autosize_y=True):
            dpg.add_text("Right Click to Add a State Node", bullet=True)
            dpg.add_text("Right Click on a State Node to Open Actions Dialog", bullet=True)
            dpg.add_text("Ctrl+Click to remove a link", bullet=True)
            dpg.add_text("Double Click on Transition Nodes to open \n the Attributes window", bullet=True)
            dpg.add_button(label="Export", callback=json_export)
            dpg.add_button(label="Import", callback=json_import)
            dpg.add_button(label="Generate API Stub", callback=lambda: dpg.show_item("generate_stub_popup"))
            dpg.add_button(label="Delete Selected Nodes", callback=del_node_callback)
        with dpg.child_window(autosize_x=True, autosize_y=True):
            with dpg.node_editor(tag="editor", minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, 
                                 callback=link_callback, delink_callback=delink_callback):
                pass

with dpg.handler_registry():
    dpg.add_mouse_click_handler(callback=show_popup, button=dpg.mvMouseButton_Right)
    dpg.add_mouse_double_click_handler(callback=handle_node_double_click, button=dpg.mvMouseButton_Left)

# Create the popup (initially hidden)
with dpg.window(modal=True, show=False, tag="node_editor_popup"):
    dpg.add_text("Add label to node")
    dpg.add_separator()
    dpg.add_input_text(tag="label_node")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=add_node_node_callback)
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("node_editor_popup", show=False))

# Create the popup (initially hidden)
with dpg.window(modal=True, show=False, tag="node_change_label_popup", user_data=""):
    dpg.add_text("Change node label")
    dpg.add_separator()
    dpg.add_input_text(tag="change_label_input")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: (dpg.set_item_label(dpg.get_item_user_data("node_change_label_popup"), 
                                                                                 dpg.get_value("change_label_input")), 
                                                                                 dpg.configure_item("node_change_label_popup", show=False)))
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("node_change_label_popup", show=False))

languages_options = ['python']

frameworks_options = ['python-flask', 'spring']

swagger_file = "swagger_active_asset.json"
swagger_url = "https://generator.swagger.io/api/gen/servers"
swagger_path = os.path.join(os.path.dirname(__file__), "swagger/", swagger_file)

open_api_file = "openapi3_0_active_asset.json"
openapigen_url = "http://api.openapi-generator.tech/api/gen/servers"
openapi_path = os.path.join(os.path.dirname(__file__), "openapi3_0/", open_api_file)

# popup modal for generate stub functionality
with dpg.window(modal=True, show=False, tag="generate_stub_popup", width=500):
    dpg.add_text("Generate API Stub from Diagram")
    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_combo(items=frameworks_options, tag="framework_combo", width=100, label="Select Framework")
        # dpg.add_combo(items=languages_options, tag="language_combo", width=100, label="Select Language")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=lambda: (dpg.configure_item("generate_stub_popup", show=False), 
                                                               POST_SERVER(openapi_path, dpg.get_value("framework_combo"), openapigen_url)))
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("generate_stub_popup", show=False))

# Compute the path to the font file dynamically based on the script's location
font_file = "arial-unicode-ms.ttf"
font_path = os.path.join(os.path.dirname(__file__), "", font_file)

# Load a custom font that supports a wide range of Unicode characters
with dpg.font_registry():
    with dpg.font(font_path, 20) as default_font:
        # Add font range to include basic Latin and mathematical symbols
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range(0x2200, 0x22FF)  # Range for mathematical symbols

dpg.bind_font(default_font)


# Create a light theme
with dpg.theme() as light_theme:
    with dpg.theme_component(dpg.mvAll):
        # dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_Border, (200, 200, 200), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (240, 240, 240), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_Button, (200, 200, 200), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (170, 170, 170), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (150, 150, 150), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (240, 240, 240), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (230, 230, 230), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (210, 210, 210), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvNodeStyleVar_PinTriangleSideLength, 15, category=dpg.mvThemeCat_Nodes)

# Bind the theme globally
dpg.bind_theme(light_theme)

# For debug need to deactivate the thread management
dpg.configure_app(manual_callback_management=True)

dpg.create_viewport(title='Industrial API Editor', width=1400, height=700)
dpg.setup_dearpygui()
resize_to_viewport(None, None)

# Set up the viewport and window
dpg.set_viewport_resize_callback(resize_to_viewport)
dpg.show_viewport()
# For debug purpose
while dpg.is_dearpygui_running():
    jobs = dpg.get_callback_queue() # retrieves and clears queue
    dpg.run_callbacks(jobs)
    dpg.render_dearpygui_frame()
# dpg.start_dearpygui()
dpg.destroy_context()
