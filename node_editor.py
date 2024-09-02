import dearpygui.dearpygui as dpg
import json

dpg.create_context()

dict_for_json_export = {
    "nodes": {},
    "links": {}
}

def get_node_data(node_editor_id):
    # Get all nodes in the node editor
    nodes = dpg.get_item_children(node_editor_id, 1)  # 1 corresponds to children of type 'mvAppItemType::mvNode'
    
    for node_id in nodes:
        # Get node label
        node_label = dpg.get_item_label(node_id)
        
        # Get all attributes associated with this node
        attributes = dpg.get_item_children(node_id, 1)  # 1 corresponds to children of type 'mvAppItemType::mvNodeAttribute'
        
        attributes_data = {}
        for attr_id in attributes:
            # Get attribute label
            attr_label = dpg.get_item_label(attr_id)
            
            # Collect all children of the attribute (input fields)
            input_fields = dpg.get_item_children(attr_id, 1)  # 1 corresponds to children of type 'mvAppItemType'
            
            input_data = {}
            for input_id in input_fields:
                # Collect the input field's value and label
                input_label = dpg.get_item_label(input_id)
                input_value = dpg.get_value(input_id)
                
                # Store input label and value
                input_data[input_id] = {
                    "label": input_label,
                    "value": input_value
                }
            
            # Store attribute label and its inputs
            attributes_data[attr_id] = {
                "label": attr_label,
                "inputs": input_data
            }

        # Store node label, attributes, and their values in the dictionary
        dict_for_json_export["nodes"][node_id] = {
            "label": node_label,
            "attributes": attributes_data
        }

    return dict_for_json_export

# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
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

def add_node_callback(app_data):
    dpg.add_node(parent="editor")

popup_values = ["add link", "add in pin"]

def add_node_node_callback(sender, app_data):
    dpg.configure_item("node_editor_popup", show=False)
    t = dpg.add_node(parent="editor", label=dpg.get_value("label_node"))
    set_node_background_color(t, (0, 255, 0, 255))  # Green background
    with dpg.popup(t):
        for i in popup_values:
            dpg.add_selectable(label=i, user_data=[t, i], callback=popup_callback)

def popup_callback(sender, app_data, user_data):
    t = user_data[0]
    s = user_data[1]
    if s == "add link":
        att_out_id = add_out_att_no_input(t)
        add_node_link_callback(sender=sender, app_data=app_data, user_data=[att_out_id, t])
    else:
        add_in_att_no_input(t)

def add_node_link_callback(sender, app_data, user_data):
    l = dpg.add_node(parent="editor", label="stuff")
    node_pos = dpg.get_item_pos(user_data[1])
    dpg.set_item_pos(l, [node_pos[0] + 200, node_pos[1]])
    add_static_att(l)
    add_static_att_float(l)
    att_in_id = add_in_att_no_input(l)
    add_out_att_no_input(l)
    set_node_background_color(l, (255, 0, 0, 255))  # Red background
    link_callback(sender="editor", app_data=[att_in_id, user_data[0]])

def add_static_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_text(label="p", width=150)

def add_static_att_float(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_float(label="Kw", width=150)

def add_in_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2"):
        dpg.add_input_text(label="", width=150)

def add_out_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
        dpg.add_input_text(label="F2", width=150)

def add_in_att_no_input(app_data):
    with dpg.node_attribute(parent=app_data) as att_id:
        dpg.add_text("")
    return att_id

def add_out_att_no_input(app_data):
    with dpg.node_attribute(parent=app_data, label="one", attribute_type=dpg.mvNode_Attr_Output) as att_id:
        dpg.add_text("")
    return att_id

def add_out_att_text_input(app_data):
    with dpg.node_attribute(parent=app_data, label="one", attribute_type=dpg.mvNode_Attr_Output) as att_id:
        dpg.add_input_text(width=150, callback=update_node_label)
    return att_id

def update_node_label(sender, app_data):
    # Get the new text value
    new_text = dpg.get_value(sender)
    # dpg.set_item_label(node_id, new_text)

def add_node_in_link_callback(sender, app_data, user_data):
    dpg.configure_item("node_editor_popup", show=False)
    t = dpg.add_node(parent="editor", label=dpg.get_value("label_node"))
    add_in_att(t)

def add_node_out_link_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_out_att(t)

def add_node_in_out_links_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_in_att(t)
    add_out_att(t)

def add_node_in_out_static_links_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_in_att(t)
    add_out_att(t)
    add_static_att(t)

def add_node_out_static_link_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_out_att(t)
    add_static_att(t)

def add_node_in_static_link_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_in_att(t)
    add_static_att(t)

def print_me(sender):
    print(f"Menu Item: {sender}")

def del_node_callback(sender, app_data):
    for id in dpg.get_selected_nodes("editor"):
        dpg.delete_item(id)

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
    mouse_pos = dpg.get_mouse_pos(local=False)
    node_editor_pos = dpg.get_item_rect_min("editor")
    node_editor_size = dpg.get_item_rect_size("editor")
    
    # Check if the mouse is within the node editor bounds
    if (node_editor_pos[0] <= mouse_pos[0] <= node_editor_pos[0] + node_editor_size[0]) and \
       (node_editor_pos[1] <= mouse_pos[1] <= node_editor_pos[1] + node_editor_size[1]):
        print("in")

    dpg.show_item("node_editor_popup")

# Function to open the file dialog
def json_export():
    # Open a file dialog to select the save location
    dpg.show_item("file_dialog_save")

with dpg.file_dialog(directory_selector=False, show=False, callback=save_json_file, id="file_dialog_save", width=500, height=300):
    dpg.add_file_extension(".json", color=(150, 255, 150, 255)) 

with dpg.window(id="node_editor_window", label="Node Editor", no_title_bar=True, no_move=True, no_resize=True, no_scrollbar=True):
    with dpg.group(horizontal=True, width=0):
        with dpg.child_window(width=300, autosize_y=True):
            dpg.add_text("Ctrl+Click to remove a link.", bullet=True)
            dpg.add_button(tag="node_in", label="Add Node In Att")
            dpg.add_button(label="Generate API Stub")
            dpg.add_button(label="Export", callback=json_export)
            dpg.add_button(label="Delete Selected Nodes", callback=del_node_callback)
        with dpg.child_window(autosize_x=True, autosize_y=True):
            with dpg.node_editor(tag="editor", minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, callback=link_callback, delink_callback=delink_callback):
                pass

with dpg.handler_registry():
    dpg.add_mouse_click_handler(callback=show_popup, button=dpg.mvMouseButton_Middle)

# Create the popup (initially hidden)
with dpg.window(modal=True, show=False, tag="node_editor_popup"):
    dpg.add_text("Add label to node")
    dpg.add_separator()
    dpg.add_input_text(tag="label_node", label="label")
    with dpg.group(horizontal=True):
        dpg.add_button(label="OK", width=75, callback=add_node_node_callback)
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("node_editor_popup", show=False))

dpg.create_viewport(title='FSM editor', width=1400, height=700)
dpg.setup_dearpygui()
resize_to_viewport(None, None)

# Set up the viewport and window
dpg.set_viewport_resize_callback(resize_to_viewport)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()