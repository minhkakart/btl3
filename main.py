import dearpygui.dearpygui as dpg
import pandas
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import LabelEncoder

VIEW_WIDTH = 1920
VIEW_HEIGHT = 1080
WIDTH = 1340
HEIGHT = 720
CENTER_X = (VIEW_WIDTH - WIDTH)/2
CENTER_Y = (VIEW_HEIGHT - HEIGHT)/2
x_max = 15
y_max = 50

# KMeans_clustering = KMeans()

dpg.create_context()

def callback_selected_file(_, app_data):
    # print("Sender: ", sender)
    # print("App Data: ", app_data)
    selection = app_data['selections']
    file_name = list(selection.keys())
    if len(file_name) > 0:
        try:
            file_path = str(selection[file_name[0]])
            data = pandas.read_csv(file_path)
            if(dpg.get_value(is_drop_first_col)):
                data = data.iloc[:,1:]
            data = data.apply(LabelEncoder().fit_transform)
            print('read ok')
            train,test = train_test_split(data, test_size=0.1,shuffle=False)
            print('Split ok')
            KMeans_clustering = KMeans(n_clusters=dpg.get_value(inp_number_of_group),algorithm='elkan',n_init='auto')
            print('Clustering ok')
            KMeans_clustering.fit(train)
            print('fit ok')

            # print('Centers:',KMeans_clustering.cluster_centers_)
            # print(type(KMeans_clustering.cluster_centers_))

            dpg.set_item_label(btn_select_file, file_name[0])

            labels = KMeans_clustering.labels_.tolist()
            # print(labels)
            gr = list(set(labels))
            gr.sort()
            count = list(map(lambda i: labels.count(i),gr))

            x_max = len(gr)
            y_max = max(count)+20

            label_pair = tuple(map(lambda item: ('Group ' + str(item), item), gr))
            dpg.set_axis_ticks(xAxis, label_pair)

            # add series to y axis
            dpg.set_axis_limits(xAxis, -1, x_max)
            dpg.set_axis_limits(yAxis, 0, y_max)
            
            dpg.set_value(item='bar_series_tag',value=(gr,count))
            # for i in gr:
            #     dpg.draw_text((i-0.2,count[i]+10),str(count[i]),size=0.3,parent=kmean_plot)

            ## score
            dpg.set_value(item='score_bar_series',value=([1, 3],[silhouette_score(train, KMeans_clustering.labels_),davies_bouldin_score(train, KMeans_clustering.labels_)]))

        except:
            dpg.set_item_label(btn_select_file, 'File is not supported!')
    else:
        dpg.set_item_label(btn_select_file, 'No file selected.')


with dpg.file_dialog(directory_selector=False, show=False, callback=callback_selected_file, file_count=1,
                      tag="file_dialog_tag", width=700 ,height=400):
    dpg.add_file_extension(".*")

with dpg.window(label="Tutorial", width=WIDTH, height=HEIGHT,pos=(CENTER_X, CENTER_Y), no_scrollbar=True, tag="Primary Window"):
    btn_select_file = dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog_tag"), pos=(10, 5))
    inp_number_of_group = dpg.add_input_int(label='Number of group', min_value=2, max_value=100, default_value=6, 
                                            pos=(400, 5), min_clamped=True, max_clamped=True, width=100)
    is_drop_first_col = dpg.add_checkbox(label='Drop first column',default_value=True, pos=(700, 5))


    # Plot group
    kmean_plot = dpg.add_plot(label='K-means clustering', height=360, width=640,pos=(10,40))
    # create x axis
    xAxis = dpg.add_plot_axis(dpg.mvXAxis, label='Group', parent=kmean_plot)
    dpg.set_axis_limits(xAxis, -1, x_max+1)
    # create y axis
    yAxis = dpg.add_plot_axis(dpg.mvYAxis, label="Number of member", parent=kmean_plot)
    dpg.add_bar_series([],[],weight=1,parent=yAxis,label='sdfsf',tag='bar_series_tag')
    dpg.set_axis_limits(yAxis, 0, y_max+20)

    # Plot score
    with dpg.plot(label='Score', height=360, width=640, pos=(680,40), tag='score_plot'):
        dpg.add_plot_axis(dpg.mvXAxis)
        dpg.set_axis_ticks(dpg.last_item(), (('Silhouette score', 1),('Davies-Bouldin score', 3)))
        # dpg.set_axis_limits(dpg.last_item(), 0, 4)

        dpg.add_plot_axis(dpg.mvYAxis, label='Score (minium is good)',tag='score_y_axis')
        # dpg.set_axis_limits(dpg.last_item(), 0, 1.1)
        dpg.add_bar_series([],[],parent='score_y_axis', tag='score_bar_series')

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 140, 23))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)

    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (140, 255, 0))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)

    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)

dpg.bind_theme(global_theme)
dpg.create_viewport(title='Custom Title', width=WIDTH, height=HEIGHT, x_pos=int(CENTER_X), y_pos=int(CENTER_Y), clear_color=(106, 176, 222, 255))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()