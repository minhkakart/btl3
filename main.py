import dearpygui.dearpygui as dpg
import pandas
from random import randint
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import LabelEncoder

VIEW_WIDTH = 1920
VIEW_HEIGHT = 1080
WIDTH = 1340
HEIGHT = 1000
CENTER_X = (VIEW_WIDTH - WIDTH)/2
CENTER_Y = (VIEW_HEIGHT - HEIGHT)/2
X_MAX = 10
Y_MAX = 50

data = []
list_field_name = []
example_values = []

dpg.create_context()

## Hàm xử lý khi chọn file
def select_file_callback(_, app_data):
    selection = app_data['selections']                                              # Lấy danh sách file đã chọn (chỉ cho phép chọn 1 file)
    file_name = list(selection.keys())                                              # Lấy tên file đã chọn
    if len(file_name) > 0:                                                          # Nếu chọn được file thì xử lý bên dưới
        try:
            file_path = str(selection[file_name[0]])                                # Lấy ra đường dẫn của file
            global data_raw                                                         # Tạo biến toàn cục data
            data_raw = pandas.read_csv(file_path)                                   # Đọc file csv, nếu không phải file csv thì xuống except
            dpg.set_item_label(btn_select_file, file_name[0])                       # Hiển thị tên file đã chọn lên button
            enable_primary_window()

            # Nếu file hợp lệ thì mở chức năng clustering và predict
            dpg.enable_item(clustering_btn)
            dpg.enable_item(predict_btn)

        except:
            # Nếu file không hợp lệ thì vô hiệu hóa chức năng clustering và predict
            dpg.disable_item(clustering_btn)
            dpg.disable_item(predict_btn)

            dpg.set_item_label(btn_select_file, 'File is not supported!')           # File không hợp lệ thì hiện chữ này
            
    else:
        dpg.set_item_label(btn_select_file, 'No file selected.')                    # Nếu không chọn file nào thì hiện chữ này

## Hàm xử lí khi nhấn mở cửa sổ dự đoán bộ dữ liệu mới
def open_predict_window_callback():
    example_values = test.iloc[randint(0, len(test)-1)]
    disable_primary_window()
    dpg.show_item('predict_window')                                                 # Hiển thị cửa sổ
    dpg.delete_item(item='predict_window', children_only=True,slot=1)
    dpg.add_button(label='Predict', callback=btn_submit_predict_callback,           # Thêm button xác nhận dự đoán thông tin
                    width=240, height=50, parent='predict_window', pos=(720,35))    
    
    # print(example_values)
    for i, field_name in enumerate(list_field_name):                                # Thêm các ô input tương ứng với tập data đã chọn
        dpg.add_input_double(width=250,label=str(field_name), tag=str(field_name),
                            parent='predict_window', default_value=(example_values.iloc[i]))

# Hàm bắt đầu train mô hình
def btn_cluster_callback():
    global list_field_name                                                          # Tạo biến toàn cục là danh sách tên dữ liệu   
    list_field_name = data_raw.columns.values  
    data = data_raw                                                                 # Lấy giá trị của ô check box
    if(dpg.get_value(is_drop_first_col)):                                           # Nếu tích thì bỏ cột dầu tiên của dữ liệu
        data = data_raw.iloc[:,1:]          
        list_field_name = list_field_name[1:]
    data = data.apply(LabelEncoder().fit_transform)                                 # Encode dữ liệu tránh gặp chữ hoặc không phải số

    if len(data):
        ## Tách và huấn luyện mô hình
        global test
        train,test = train_test_split(data, test_size=0.1,shuffle=False)
        
        global KMeans_clustering              # Dưới này để lấy giá trị từ input số lượng nhóm (clusters) #
        KMeans_clustering = KMeans(n_clusters=dpg.get_value(inp_number_of_group),algorithm='elkan',n_init='auto')
        KMeans_clustering.fit(train)

        labels = KMeans_clustering.labels_.tolist()                                 # Lấy ra nhãn của tập data train
        # print(labels)
        gr = list(set(labels))                                                      # Tạo danh sách các nhóm (clusters)
        gr.sort()                                                                   # Sắp xép từ nhỏ đến lớn
        count_train = list(map(lambda i: labels.count(i),gr))                       # Tạo danh sách số lượng phần tử của nhóm tương ứng

        x_max = len(gr)                                                             # Lấy ra số lượng nhóm (clusters)
        y_max = max(count_train)+20                                                 # Lấy ra giá trị cao nhất của số phần tử mỗi nhóm

        ## Dùng chung cho biểu đồ train và test
        label_pair = tuple(map(lambda item: (str(item), item), gr))                 # Tạo danh sách nhãn cho trục x
        dpg.set_axis_ticks(xAxis, label_pair)                                       # Gán nhãn cho trục x

        # add series to y axis
        dpg.set_axis_limits(xAxis, -1, x_max)                                       # Giới hạn độ dài trục x
        dpg.set_axis_limits(yAxis, 0, y_max)                                        # Giới hạn độ dài trục y
        
        dpg.set_value(item='bar_series_tag',value=(gr,count_train))                 # Gán giá trị cho biểu đồ cột của biểu đồ (kmean_plot_train)
        dpg.delete_item(item=kmean_plot_train, children_only=True, slot=2)          # Xóa text của biểu đồ (kmean_plot_train) đang ở slot 2
        for i in gr:
            dpg.draw_text((i-0.2,count_train[i]+10),str(count_train[i]),            # Viết text lên biểu đồ (kmean_plot_train)
                          size=0.3,parent=kmean_plot_train)

        ## score
        score = [silhouette_score(train, KMeans_clustering.labels_),                # Tính điểm và lưu vào mảng score
                  davies_bouldin_score(train, KMeans_clustering.labels_)]
        dpg.set_value(item='score_bar_series', value=([1, 3],score))                # Gán giá trị cho biểu đồ cột của biểu đồ (score)
        dpg.delete_item(item='score_plot_train', children_only=True, slot=2)
        for i, val in enumerate(score):
            dpg.draw_text((i*2+0.7,val+0.19),str(int(val*10000)/10000),             # Giống mấy dòng trên
                          size=0.2,parent='score_plot_train')
            
            
        ### Xử lí và thêm dữ liệu cho biểu đồ test data ở đây ###
        dpg.set_axis_ticks('xAxis_test', label_pair)
        dpg.set_axis_limits('xAxis_test', -1, x_max)

        labels_test = KMeans_clustering.predict(test).tolist()
        # print('labels_test:',labels_test)
        count_test = list(map(lambda i: labels_test.count(i), gr))

        
        dpg.set_axis_limits('yAxis_test', 0, max(count_test)+10)
        dpg.set_value(item='bar_series_tag_test',value=(gr,count_test))
        dpg.delete_item(item='plot_test', children_only=True, slot=2)
        for i in gr:
            dpg.draw_text((i-0.2,count_test[i]+6),str(count_test[i]),
                          size=0.3,parent='plot_test')
        
        labels_test_group_count = len(set(labels_test))
        if labels_test_group_count > 1:
            ## Tạm không dùng
            test_score = [silhouette_score(test, labels_test),davies_bouldin_score(test, labels_test)]
            dpg.set_value(item='score_bar_series_test', value=([1, 3],test_score))
            dpg.delete_item(item='score_plot_test', children_only=True, slot=2)
            for i, val in enumerate(test_score):
                dpg.draw_text((i*2+0.7,val+0.19),str(int(val*10000)/10000),
                              size=0.2,parent='score_plot_test')
        else:
            dpg.delete_item('score_plot_test', children_only=True, slot=2)
            dpg.set_value(item='score_bar_series_test', value=([],[]))
            dpg.show_item('alert')

## Hàm xử lý khi nhấn dự doán cho mẫu dữ liệu mới
def btn_submit_predict_callback():
    ## Xử lý các dữ liệu mới khi nhập xong ở đây ##
    predict_data = []
    for i in list_field_name:
        predict_data.append(dpg.get_value(str(i)))
    predict_data =[predict_data]
    global predict_group
    predict_group = KMeans_clustering.predict(predict_data)
    dpg.show_item('alert_group_window')
    dpg.draw_text(text=str(predict_group[0]),pos=(230, 70), size=100, parent='alert_group_window', tag='group_predict_sanple')

def disable_primary_window():
    dpg.disable_item(btn_select_file)
    dpg.disable_item(inp_number_of_group)
    dpg.disable_item(is_drop_first_col)
    dpg.disable_item(clustering_btn)
    dpg.disable_item(predict_btn)

def enable_primary_window():
    dpg.enable_item(btn_select_file)
    dpg.enable_item(inp_number_of_group)
    dpg.enable_item(is_drop_first_col)
    dpg.enable_item(clustering_btn)
    dpg.enable_item(predict_btn)

def close_alert_predict_window():
    dpg.delete_item('group_predict_sanple')
    dpg.hide_item('alert_group_window')

## Tạo cửa sổ chọn file (mặc định ẩn show=False)
with dpg.file_dialog(directory_selector=False, show=False, callback=select_file_callback, file_count=1,
                      tag="file_dialog_tag", width=700 ,height=400, modal=True):
    dpg.add_file_extension(".*")

## Tạo cửa sổ dự đoán cho mẫu dữ liệu mới (mặc định ẩn show=False)
dpg.add_window(label='Predict group of customer', show=False, tag='predict_window',
                pos=(200,100), width=980, height=550, on_close=enable_primary_window)

## Hiển thị kết quả dự đoán
with dpg.window(label='Predict group', show=False, width=540, height=300, tag='alert_group_window', pos=(420, 200), modal=True, no_close=True):
    dpg.draw_text(text='Mau duoc phan loai vao nhom so:', pos=(10,10), size=30)
    dpg.add_button(label='OK', width=520, height=60, callback=close_alert_predict_window, pos=(10, 230))
    
## Popup thông báo
with dpg.window(label="Alert", show=False, popup=True, tag='alert'):
    dpg.add_text(default_value='Tat ca du lieu test deu thuoc cung 1 nhom \n nen khong the tinh diem!',pos=(10, 40))
    dpg.add_button(label='OK', width=450, height=90, pos=(6,120), callback=lambda:dpg.hide_item('alert'))

## Tạo cửa sổ giao diện chính
with dpg.window(label="Tutorial", width=WIDTH, height=HEIGHT,pos=(CENTER_X, CENTER_Y), no_scrollbar=True, tag="Primary Window"):

    ## Thêm các button, check box cần thiết
    btn_select_file = dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog_tag"), pos=(10, 20), height=40)
    inp_number_of_group = dpg.add_input_int(label='Number of group', min_value=2, max_value=100, default_value=5, 
                                            pos=(400, 20), min_clamped=True, max_clamped=True, width=100)
    is_drop_first_col = dpg.add_checkbox(label='Drop first column',default_value=True, pos=(400, 50))
    clustering_btn = dpg.add_button(label='Clustering data', pos=(700, 20), callback=btn_cluster_callback, height=40)
    predict_btn = dpg.add_button(label='Predict a customer', pos=(1000, 20), callback=open_predict_window_callback, height=40)

    # Chưa chọn file dữ liệu sẽ vô hiệu hóa chức năng clustering và predict
    dpg.disable_item(clustering_btn)
    dpg.disable_item(predict_btn)
    
    #######################
    ### Tạo các biểu đồ ###

    ## Train data ##
    dpg.add_text('Train data', pos=(20, 85))
    # Plot group
    kmean_plot_train = dpg.add_plot(label='K-means clustering', height=360, width=640,pos=(10,110))
    # create x axis
    xAxis = dpg.add_plot_axis(dpg.mvXAxis, label='Group', parent=kmean_plot_train)
    dpg.set_axis_limits(xAxis, -1, X_MAX+1)
    # create y axis
    yAxis = dpg.add_plot_axis(dpg.mvYAxis, label="Number of member", parent=kmean_plot_train)
    dpg.add_bar_series([],[],weight=1,parent=yAxis,label='sdfsf',tag='bar_series_tag')
    dpg.set_axis_limits(yAxis, 0, Y_MAX+20)

    # Plot score
    with dpg.plot(label='Score', height=360, width=640, pos=(670,110), tag='score_plot_train'):
        dpg.add_plot_axis(dpg.mvXAxis)
        dpg.set_axis_ticks(dpg.last_item(), (('Silhouette score', 1),('Davies-Bouldin score', 3)))
        dpg.set_axis_limits(dpg.last_item(), 0, 4)

        dpg.add_plot_axis(dpg.mvYAxis, label='Score',tag='score_y_axis_train')
        dpg.set_axis_limits(dpg.last_item(), 0, 2)
        dpg.add_bar_series([],[],parent='score_y_axis_train', tag='score_bar_series')

    
    ## Test data ##
    dpg.add_text('Test data', pos=(20, 485))
    # Plot group
    with dpg.plot(label='K-means clustering', height=360, width=640,pos=(10,510), tag='plot_test'):
        # create x axis
        dpg.add_plot_axis(dpg.mvXAxis, label='Group', tag='xAxis_test')
        dpg.set_axis_limits(dpg.last_item(), -1, X_MAX+1)
        # create y axis
        dpg.add_plot_axis(dpg.mvYAxis, label="Number of member", tag='yAxis_test')
        dpg.set_axis_limits(dpg.last_item(), 0, Y_MAX+20)
        dpg.add_bar_series([],[],weight=1,parent='yAxis_test',label='sdfsf',tag='bar_series_tag_test')

    ## Plot score
    with dpg.plot(label='Score', height=360, width=640, pos=(670,510), tag='score_plot_test'):
        dpg.add_plot_axis(dpg.mvXAxis)
        dpg.set_axis_ticks(dpg.last_item(), (('Silhouette score', 1),('Davies-Bouldin score', 3)))
        dpg.set_axis_limits(dpg.last_item(), 0, 4)

        dpg.add_plot_axis(dpg.mvYAxis, label='Score',tag='score_y_axis_test')
        dpg.set_axis_limits(dpg.last_item(), 0, 2)
        dpg.add_bar_series([],[],parent='score_y_axis_test', tag='score_bar_series_test')

    #######################

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
dpg.bind_theme(global_theme)
dpg.set_global_font_scale(1.5)
dpg.create_viewport(title='Credit Card Dataset for Clustering', width=WIDTH, height=HEIGHT, x_pos=int(CENTER_X), y_pos=int(CENTER_Y), clear_color=(106, 176, 222, 255))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()