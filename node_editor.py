import dearpygui.dearpygui as dpg
import json

dpg.create_context()

dict_for_json_export = {
    "nodes": {},
    "links": {}
}

def get_node_data(node_editor_id):
    dict_for_json_export["nodes"] = {}
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

        # Store node label, attributes, and their values in the dictionary
        dict_for_json_export["nodes"][node_id] = {
            "label": node_label,
            "attributes": attributes_data,
            "position": node_pos,
            "type": node_type
        }

    return dict_for_json_export

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

popup_values = ["Add Action Right", "Add Action Left", "Add left pin", "Add right pin", "Mark as Init state"]

def add_node_node_callback(sender, app_data):
    dpg.configure_item("node_editor_popup", show=False)
    wind_pos = dpg.get_item_pos("node_editor_popup")
    pos_offset = wind_pos[0] - 400
    node_id = dpg.add_node(parent="editor", label=dpg.get_value("label_node"), user_data="node_state", pos=[pos_offset, wind_pos[1]])
    set_node_background_color(node_id, (183, 179, 39))  # Green background
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
    elif command == "Mark as Init state":
        set_node_background_color(node_id, (0, 146, 204))

def add_node_link_callback(sender, app_data, user_data):
    node_id = dpg.add_node(parent="editor", user_data="node_transition")
    node_pos = dpg.get_item_pos(user_data[1])
    if user_data[2] == "right":
        pos_offset = node_pos[0] + 200
        att_in_id = add_in_att_no_input(sender=node_id, app_data=app_data, user_data="")
        add_out_att_no_input(sender=node_id, app_data=app_data, user_data="node transition out")
    else:
        pos_offset = node_pos[0] - 300
        att_in_id = add_out_att_no_input(sender=node_id, app_data=app_data, user_data="")
        add_in_att_no_input(sender=node_id, app_data=app_data, user_data="node transition out")
    dpg.set_item_pos(node_id, [pos_offset, node_pos[1]])
    add_static_att(sender=node_id, app_data=app_data)
    add_static_att_float(sender=node_id, app_data=app_data)
    set_node_background_color(node_id, (255, 51, 51))  # Red background
    link_callback(sender="editor", app_data=[user_data[0], att_in_id])
    return node_id

def add_static_att(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Probability", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_text(label="p", width=150)

def add_static_att_float(sender, app_data):
    with dpg.node_attribute(parent=sender, label="Cost", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_float(label="Cost", width=150)

def add_in_att_no_input(sender, app_data, user_data):
    shape = dpg.mvNode_PinShape_CircleFilled
    if user_data == "node state in":
        shape = dpg.mvNode_PinShape_Triangle
    with dpg.node_attribute(parent=sender, label=user_data, shape=shape) as att_id:
        dpg.add_text("")
    return att_id

def add_out_att_no_input(sender, app_data, user_data):
    shape = dpg.mvNode_PinShape_CircleFilled
    if user_data == "node state in":
        shape = dpg.mvNode_PinShape_Triangle
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
        # Export the node data to the selected file
        with open(selected_file, "w") as outfile:
            json.dump(dict_for_json_export, outfile, indent=4, sort_keys=False)
        print(f"File saved to: {selected_file}")

popup_values_editor = ["Add Node"]

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
                set_node_background_color(node_id, (183, 179, 39))  # Green background
                with dpg.popup(node_id):
                    for i in popup_values:
                        dpg.add_selectable(label=i, user_data=[node_id, i], callback=popup_callback)
            else:
                set_node_background_color(node_id, (255, 51, 51))  # Red background
            for attr_id, attr_data in node_data["attributes"].items():
                shape = dpg.mvNode_PinShape_CircleFilled
                if attr_data["type"] == "mvNode_Attr_Output":
                    attribute_type=dpg.mvNode_Attr_Output
                    if attr_data["label"] == "node state in":
                        shape = dpg.mvNode_PinShape_Triangle   
                elif attr_data["type"] == "mvNode_Attr_Input":
                    if attr_data["label"] == "node state in":
                        shape = dpg.mvNode_PinShape_Triangle   
                    attribute_type=dpg.mvNode_Attr_Input
                else:
                    attribute_type=dpg.mvNode_Attr_Static      
                with dpg.node_attribute(tag=attr_id, attribute_type=attribute_type, label=attr_data["label"], shape=shape) as att_id:
                    # Create input fields with stored values
                    for input_id, input_data in attr_data["inputs"].items():
                        if input_data["type"] == "mvAppItemType::mvInputText" and attribute_type == dpg.mvNode_Attr_Static:
                            dpg.add_input_text(tag=input_id, width=150, label=input_data["label"], default_value=input_data["value"])
                        elif input_data["type"] == "mvAppItemType::mvInputFloat":
                            dpg.add_input_float(tag=input_id, width=150, label=input_data["label"], default_value=input_data["value"])
                        elif input_data["type"] == "mvAppItemType::mvText":
                            dpg.add_text(tag=input_id, label=input_data["label"], default_value=input_data["value"])

    # Create links
    for link in data["links"].values():
        attr_1 = dpg.get_alias_id(str(link["start_attr"]))
        attr_2 = dpg.get_alias_id(str(link["end_attr"]))
        link_callback(sender="editor", app_data=[attr_1, attr_2])

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
            dpg.add_button(label="Export", callback=json_export)
            dpg.add_button(label="Import", callback=json_import)
            dpg.add_button(label="Generate API Stub")
            dpg.add_button(label="Delete Selected Nodes", callback=del_node_callback)
        with dpg.child_window(autosize_x=True, autosize_y=True):
            with dpg.node_editor(tag="editor", minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, 
                                 callback=link_callback, delink_callback=delink_callback):
                pass

with dpg.handler_registry():
    dpg.add_mouse_click_handler(callback=show_popup, button=dpg.mvMouseButton_Right)

# Create the popup (initially hidden)
with dpg.window(modal=True, show=False, tag="node_editor_popup"):
    dpg.add_text("Add label to node")
    dpg.add_separator()
    dpg.add_input_text(tag="label_node", label="label")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=add_node_node_callback)
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("node_editor_popup", show=False))

# Load a custom font that supports a wide range of Unicode characters
with dpg.font_registry():
    with dpg.font("/home/pablo/Thesis/Mecella/imPyGUI/arial-unicode-ms.ttf", 20) as default_font:
        # Add font range to include basic Latin and mathematical symbols
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range(0x2200, 0x22FF)  # Range for mathematical symbols

dpg.bind_font(default_font)

# For debug need to deactivate the thread management
dpg.configure_app(manual_callback_management=True)

dpg.create_viewport(title='FSM editor', width=1400, height=700)
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
