FULL_WIDTH = 1920
FULL_HEIGHT = 1080
WIDTH = 1280
HEIGHT = 720
CENTER_X = (FULL_WIDTH - WIDTH)/2
CENTER_Y = (FULL_HEIGHT - HEIGHT)/2

import dearpygui.dearpygui as dpg

dpg.create_context()

def button_callback():
    dpg.set_value(inp3, dpg.get_values((inp, inp1, inp2)))

with dpg.window(label="Tutorial",width=WIDTH, height=HEIGHT, pos=(CENTER_X, CENTER_Y)):
    # user data and callback set when button is created
    inp = dpg.add_input_text(label='Text', default_value='value')
    inp1 = dpg.add_input_text(label='Text', default_value='value1')
    inp2 = dpg.add_input_text(label='Text', default_value='value2')
    btn1 = dpg.add_button(label="Apply", callback=button_callback, user_data=inp)
    inp3 = dpg.add_text(label='Result')

# dpg.show_documentation()
# dpg.show_item_registry()
dpg.create_viewport(title='Custom Title', width=FULL_WIDTH, height=FULL_HEIGHT, x_pos=0, y_pos=0)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()