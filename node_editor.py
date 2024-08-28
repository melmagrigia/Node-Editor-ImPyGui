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

def add_node_callback(app_data):
    dpg.add_node(parent="editor")

def add_node_static_link_callback(app_data):
    t = dpg.add_node(parent="editor", label="stuff")
    add_static_att(t)

def add_static_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2", attribute_type=dpg.mvNode_Attr_Static):
        dpg.add_input_text(label="F2", width=150)

def add_in_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2"):
        dpg.add_input_text(label="F2", width=150)

def add_out_att(app_data):
    with dpg.node_attribute(parent=app_data, label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
        dpg.add_input_text(label="F2", width=150)

def add_node_in_link_callback(sender, app_data, user_data):
    dpg.configure_item("__demo_popup3", show=False)
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

def json_export():
    print(get_node_data("editor"))
    with open("test_nested.json", "w") as outfile:
        json.dump(dict_for_json_export, outfile, indent=4, sort_keys=False)


with dpg.window(label="Node Editor", width=1300, height=600):
    with dpg.child_window(autosize_x=True, height=600):
        with dpg.group(horizontal=True, width=0):
            with dpg.child_window(width=300, height=250):
                dpg.add_text("Ctrl+Click to remove a link.", bullet=True)
                dpg.add_button(label="Add Node", callback=add_node_callback)
                dpg.add_button(label="Add Node Static Att", callback=add_node_static_link_callback)
                dpg.add_button(label="Add Node In Out Att", callback=add_node_in_out_links_callback)
                dpg.add_button(tag="node_in", label="Add Node In Att")
                with dpg.popup(parent="node_in", modal=True, mousebutton=dpg.mvMouseButton_Left, tag="__demo_popup3"):
                    dpg.add_text("Add label to node")
                    dpg.add_separator()
                    dpg.add_input_text(tag="label_node", label="label")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="OK", width=75, callback=add_node_in_link_callback)
                        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("__demo_popup3", show=False))
                dpg.add_button(label="Add Node In Out Static Att", callback=add_node_in_out_static_links_callback)
                dpg.add_button(label="Add Node Out Att", callback=add_node_out_link_callback)
                dpg.add_button(label="Add Node Out static Att", callback=add_node_out_static_link_callback)
                dpg.add_button(label="Add Node In Static Att", callback=add_node_in_static_link_callback)
                dpg.add_button(label="Delete Selected Nodes", callback=del_node_callback)
            with dpg.child_window(width=700, height=500):
                with dpg.node_editor(tag="editor", minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, callback=link_callback, 
                                     delink_callback=delink_callback):
                    with dpg.node(label="Node 1"):
                        with dpg.node_attribute(label="Node A1"):
                            dpg.add_input_text(label="F1", width=150)

                        with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                            dpg.add_input_float(label="F2", width=150)
            with dpg.child_window(width=150, height=150):
                dpg.add_button(label="Generate API Stub")
                dpg.add_button(label="Export", callback=json_export)

dpg.create_viewport(title='FSM editor', width=1400, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()