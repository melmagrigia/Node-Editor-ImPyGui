import dearpygui.dearpygui as dpg

dpg.create_context()

# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

def add_node_callback():
    t = dpg.add_node(parent="editor")
    # print(t)
    # dpg.bind_item_handler_registry(t, "widget handler")

def print_me(sender):
    print(f"Menu Item: {sender}")

def del_node_callback(sender, app_data):
    # print(dpg.get_selected_nodes("editor"))
    for id in dpg.get_selected_nodes("editor"):
        dpg.delete_item(id)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)

with dpg.window(label="Tutorial", width=800, height=600):
    with dpg.child_window(autosize_x=True, height=600):
        with dpg.group(horizontal=True, width=0):
            with dpg.child_window(width=150, height=150):
                dpg.add_button(label="Add Node", callback=add_node_callback)
                dpg.add_button(label="Delete Selected Nodes", callback=del_node_callback)
            with dpg.child_window(width=700, height=500):
                with dpg.node_editor(tag="editor", callback=link_callback, delink_callback=delink_callback):
                    with dpg.node(label="Node 1"):
                        with dpg.node_attribute(label="Node A1"):
                            dpg.add_input_float(label="F1", width=150)

                        with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                            dpg.add_input_float(label="F2", width=150)
            with dpg.child_window(width=50, height=150):
                dpg.add_button(label="B1", width=25, height=25)
                dpg.add_button(label="B2", width=25, height=25)
                dpg.add_button(label="B3", width=25, height=25)
                
    # with dpg.menu_bar():
    #     with dpg.menu(label="File"):
    #         dpg.add_menu_item(label="Save", callback=print_me)
    #         dpg.add_menu_item(label="Save As", callback=add_node_callback)

    #         with dpg.menu(label="Settings"):
    #             dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
    #             dpg.add_menu_item(label="Setting 2", callback=print_me)

    #     dpg.add_menu_item(label="Help", callback=print_me)
    
    # with dpg.item_handler_registry(tag="widget handler") as handler:
    #     dpg.add_item_clicked_handler(button=1, callback=del_node_callback)


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()