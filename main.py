import sys
import os
import winsound
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QMenuBar, QMenu, QAction, QFileDialog, QGridLayout, QMessageBox, QSystemTrayIcon, QMenu
from PyQt5.QtCore import QTimer, QTime, Qt, QSettings, QSize, QCoreApplication
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QIcon

class CountdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("循环计时器")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化设置
        self.settings = QSettings("CountdownApp", "Settings")
        
        # 语言字典
        self.language_dict = {
            "zh": {
                "window_title": "循环计时器",
                "hours": "小时:",
                "minutes": "分钟:",
                "seconds": "秒:",
                "start": "开始",
                "pause": "暂停",
                "stop": "停止",
                "reset": "复位",
                "enable_sound": "启用声音",
                "browse": "浏览",
                "enable_notification": "启用通知",
                "settings": "设置",
                "language": "语言",
                "chinese": "中文",
                "english": "English",
                "help": "帮助",
                "about": "关于",
                "notification": "通知",
                "system_default": "系统默认"
            },
            "en": {
                "window_title": "Countdown Timer",
                "hours": "Hours:",
                "minutes": "Minutes:",
                "seconds": "Seconds:",
                "start": "Start",
                "pause": "Pause",
                "stop": "Stop",
                "reset": "Reset",
                "enable_sound": "Enable Sound",
                "browse": "Browse",
                "enable_notification": "Enable Notification",
                "settings": "Settings",
                "language": "Language",
                "chinese": "中文",
                "english": "English",
                "help": "Help",
                "about": "About",
                "notification": "Notification",
                "system_default": "System Default"
            }
        }
        
        # 默认语言
        self.current_language = "zh"
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局 - 使用垂直布局作为基础
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # 创建倒计时显示
        self.time_display = QLabel("00:00:00")
        font = QFont("Arial", 48, QFont.Bold)
        self.time_display.setFont(font)
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("background-color: #f8f8f8; border-radius: 10px; padding: 20px;")
        main_layout.addWidget(self.time_display)
        
        # 添加伸缩因子，使倒计时显示部分能够自动拉伸
        main_layout.addStretch(1)
        
        # 底部区域容器
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # 时间设置区域
        time_group = QWidget()
        time_group.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        time_layout = QHBoxLayout(time_group)
        time_layout.setSpacing(15)
        
        self.hour_input = QLineEdit("0")
        self.hour_input.setFixedWidth(80)
        self.hour_input.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 5px;")
        self.minute_input = QLineEdit("0")
        self.minute_input.setFixedWidth(80)
        self.minute_input.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 5px;")
        self.second_input = QLineEdit("0")
        self.second_input.setFixedWidth(80)
        self.second_input.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 5px;")
        
        self.hours_label = QLabel("小时:")
        time_layout.addWidget(self.hours_label)
        time_layout.addWidget(self.hour_input)
        self.minutes_label = QLabel("分钟:")
        time_layout.addWidget(self.minutes_label)
        time_layout.addWidget(self.minute_input)
        self.seconds_label = QLabel("秒:")
        time_layout.addWidget(self.seconds_label)
        time_layout.addWidget(self.second_input)
        
        bottom_layout.addWidget(time_group)
        
        # 按钮区域
        button_group = QWidget()
        button_group.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("开始")
        self.pause_button = QPushButton("暂停")
        self.stop_button = QPushButton("停止")
        self.reset_button = QPushButton("复位")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)
        
        bottom_layout.addWidget(button_group)
        
        # 将底部区域添加到主布局
        main_layout.addWidget(bottom_widget)
        
        # 保留通知文本变量，确保功能正常工作
        self.notification_text = QLineEdit("倒计时结束！")
        # 保留声音相关变量
        self.sound_combo = QComboBox()
        self.sound_combo.addItem("系统默认")
        self.browse_sound_button = QPushButton("浏览")
        
        # 初始化计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
        # 初始化倒计时时间
        self.time_left = QTime(0, 0, 0)
        self.is_paused = False
        
        # 初始化自定义声音文件路径
        self.custom_sound_path = ""
        
        # 连接按钮信号
        self.start_button.clicked.connect(self.start_countdown)
        self.pause_button.clicked.connect(self.pause_countdown)
        self.stop_button.clicked.connect(self.stop_countdown)
        self.reset_button.clicked.connect(self.reset_countdown)
        
        # 加载设置
        self.load_settings()
        
        # 设置样式
        self.set_style()
        
        # 初始化语言
        self.update_language()
        
        # 初始化系统托盘
        self.init_system_tray()
    
    def init_system_tray(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 创建一个简单的图标（使用红色作为背景）
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(255, 87, 34))  # 使用红色系颜色
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        # 创建托盘菜单
        tray_menu = QMenu(self)
        
        # 显示窗口操作
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show)
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_application)
        
        # 添加菜单项
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 设置托盘图标提示
        self.tray_icon.setToolTip("循环计时器")
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # 连接托盘图标激活信号
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        # 处理托盘图标激活事件
        if reason == QSystemTrayIcon.Trigger:
            # 点击托盘图标时显示/隐藏窗口
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def exit_application(self):
        # 完全退出应用程序
        # 隐藏托盘图标
        self.tray_icon.hide()
        # 保存设置
        self.save_settings()
        # 退出应用程序
        QCoreApplication.quit()
    
    def closeEvent(self, event):
        # 保存设置
        self.save_settings()
        
        # 直接退出应用程序，不再最小化到托盘
        # 隐藏托盘图标
        self.tray_icon.hide()
        # 正常退出
        event.accept()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 设置菜单
        self.settings_menu = menubar.addMenu(self.language_dict[self.current_language]["settings"])
        
        # 声音设置子菜单
        self.sound_menu = QMenu("声音设置", self)
        self.sound_action = QAction("启用声音", self)
        self.sound_action.setCheckable(True)
        self.sound_menu.addAction(self.sound_action)
        # 添加声音文件选择动作
        self.select_sound_action = QAction("选择声音文件", self)
        self.select_sound_action.triggered.connect(self.browse_sound)
        self.sound_menu.addAction(self.select_sound_action)
        self.settings_menu.addMenu(self.sound_menu)
        
        # 通知设置子菜单
        self.notification_menu = QMenu("通知设置", self)
        self.notification_action = QAction("启用通知", self)
        self.notification_action.setCheckable(True)
        self.notification_menu.addAction(self.notification_action)
        # 添加通知文本设置动作
        self.set_notification_action = QAction("设置通知文本", self)
        self.set_notification_action.triggered.connect(self.set_notification_text)
        self.notification_menu.addAction(self.set_notification_action)
        self.settings_menu.addMenu(self.notification_menu)
        
        # 语言子菜单
        self.language_menu = QMenu(self.language_dict[self.current_language]["language"], self)
        self.chinese_action = QAction(self.language_dict[self.current_language]["chinese"], self)
        self.english_action = QAction(self.language_dict[self.current_language]["english"], self)
        
        self.chinese_action.triggered.connect(lambda: self.set_language("zh"))
        self.english_action.triggered.connect(lambda: self.set_language("en"))
        
        self.language_menu.addAction(self.chinese_action)
        self.language_menu.addAction(self.english_action)
        self.settings_menu.addMenu(self.language_menu)
        
        # 帮助菜单
        self.help_menu = menubar.addMenu(self.language_dict[self.current_language]["help"])
        self.about_action = QAction(self.language_dict[self.current_language]["about"], self)
        self.help_menu.addAction(self.about_action)
        
        # 确保菜单栏可见
        menubar.setVisible(True)
    
    def set_language(self, lang):
        # 设置当前语言并更新界面
        self.current_language = lang
        self.update_language()
    
    def update_language(self):
        # 更新所有 UI 元素的文本
        lang_dict = self.language_dict[self.current_language]
        
        # 更新窗口标题
        self.setWindowTitle(lang_dict["window_title"])
        
        # 更新菜单
        self.settings_menu.setTitle(lang_dict["settings"])
        # 更新声音设置和通知设置子菜单
        if hasattr(self, 'sound_menu'):
            self.sound_menu.setTitle("声音设置")
            self.sound_action.setText(lang_dict["enable_sound"])
            if hasattr(self, 'select_sound_action'):
                self.select_sound_action.setText("选择声音文件")
        if hasattr(self, 'notification_menu'):
            self.notification_menu.setTitle("通知设置")
            self.notification_action.setText(lang_dict["enable_notification"])
            if hasattr(self, 'set_notification_action'):
                self.set_notification_action.setText("设置通知文本")
        # 更新语言子菜单
        self.language_menu.setTitle(lang_dict["language"])
        self.chinese_action.setText(lang_dict["chinese"])
        self.english_action.setText(lang_dict["english"])
        # 更新帮助菜单
        self.help_menu.setTitle(lang_dict["help"])
        self.about_action.setText(lang_dict["about"])
        
        # 更新按钮
        self.start_button.setText(lang_dict["start"])
        self.pause_button.setText(lang_dict["pause"])
        self.stop_button.setText(lang_dict["stop"])
        self.reset_button.setText(lang_dict["reset"])
        
        # 更新下拉框
        if self.sound_combo.itemText(0) in ["系统默认", "System Default"]:
            self.sound_combo.setItemText(0, lang_dict["system_default"])
        
        # 更新时间标签
        self.hours_label.setText(lang_dict["hours"])
        self.minutes_label.setText(lang_dict["minutes"])
        self.seconds_label.setText(lang_dict["seconds"])
        
        # 强制刷新界面
        self.repaint()
    
    def set_style(self):
        # 设置红色系配色方案
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(255, 87, 34))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # 设置按钮样式
        button_style = "QPushButton { background-color: #FF5722; color: white; border-radius: 4px; padding: 8px; }"
        button_style += "QPushButton:hover { background-color: #FF7043; }"
        
        self.start_button.setStyleSheet(button_style)
        self.pause_button.setStyleSheet(button_style)
        self.stop_button.setStyleSheet(button_style)
        self.reset_button.setStyleSheet(button_style)
        self.browse_sound_button.setStyleSheet(button_style)
        
        # 设置菜单栏样式
        menubar_style = "QMenuBar { background-color: #f8f8f8; }"
        menubar_style += "QMenuBar::item { color: #333; }"
        menubar_style += "QMenuBar::item:selected { background-color: #FF5722; color: white; }"
        menubar_style += "QMenu { background-color: white; color: #333; }"
        menubar_style += "QMenu::item:selected { background-color: #FF5722; color: white; }"
        self.menuBar().setStyleSheet(menubar_style)
    
    def start_countdown(self):
        # 从输入框获取时间
        try:
            hours = int(self.hour_input.text())
            minutes = int(self.minute_input.text())
            seconds = int(self.second_input.text())
            
            # 设置倒计时时间
            self.time_left = QTime(hours, minutes, seconds)
            self.update_display()
            
            # 启动计时器
            self.timer.start(1000)  # 每秒触发一次
            self.is_paused = False
        except ValueError:
            # 输入无效，使用默认值
            pass
    
    def pause_countdown(self):
        if self.timer.isActive():
            self.timer.stop()
            self.is_paused = True
    
    def stop_countdown(self):
        self.timer.stop()
        self.time_left = QTime(0, 0, 0)
        self.update_display()
        self.is_paused = False
    
    def reset_countdown(self):
        self.timer.stop()
        # 从输入框重新获取时间
        try:
            hours = int(self.hour_input.text())
            minutes = int(self.minute_input.text())
            seconds = int(self.second_input.text())
            self.time_left = QTime(hours, minutes, seconds)
        except ValueError:
            self.time_left = QTime(0, 0, 0)
        self.update_display()
        self.is_paused = False
    
    def update_countdown(self):
        if self.time_left > QTime(0, 0, 0):
            # 减少一秒
            self.time_left = self.time_left.addSecs(-1)
            self.update_display()
        else:
            # 倒计时结束
            self.timer.stop()
            self.update_display()
            # 触发通知和声音
            self.trigger_notification()
    
    def update_display(self):
        # 更新倒计时显示
        self.time_display.setText(self.time_left.toString("HH:mm:ss"))
    

    
    def browse_sound(self):
        # 浏览并选择自定义声音文件
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择声音文件", "", "音频文件 (*.wav *.mp3)")
        
        if file_path:
            self.custom_sound_path = file_path
            # 保存设置
            self.save_settings()
            # 显示成功消息
            QMessageBox.information(self, "成功", f"已选择声音文件: {os.path.basename(file_path)}")
    
    def set_notification_text(self):
        # 设置通知文本
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "设置通知文本", "请输入通知文本:", text=self.notification_text.text())
        if ok and text:
            self.notification_text.setText(text)
            # 保存设置
            self.save_settings()
    
    def load_settings(self):
        # 从 QSettings 加载保存的设置
        
        # 加载语言设置
        language = self.settings.value("language", "zh")
        self.set_language(language)
        
        # 加载声音设置
        enable_sound = self.settings.value("enable_sound", False, type=bool)
        self.sound_action.setChecked(enable_sound)
        
        # 加载自定义声音路径
        custom_sound = self.settings.value("custom_sound", "")
        if custom_sound and os.path.exists(custom_sound):
            self.custom_sound_path = custom_sound
        
        # 加载通知设置
        enable_notification = self.settings.value("enable_notification", True, type=bool)
        self.notification_action.setChecked(enable_notification)
        
        # 加载通知文本
        notification_text = self.settings.value("notification_text", "倒计时结束！")
        self.notification_text.setText(notification_text)
    
    def save_settings(self):
        # 将当前设置保存到 QSettings
        
        # 保存语言设置
        self.settings.setValue("language", self.current_language)
        
        # 保存声音设置
        self.settings.setValue("enable_sound", self.sound_action.isChecked())
        
        # 保存自定义声音路径
        self.settings.setValue("custom_sound", self.custom_sound_path)
        
        # 保存通知设置
        self.settings.setValue("enable_notification", self.notification_action.isChecked())
        
        # 保存通知文本
        self.settings.setValue("notification_text", self.notification_text.text())
    
    def trigger_notification(self):
        # 播放声音
        if self.sound_action.isChecked():
            try:
                if self.custom_sound_path:
                    # 播放自定义声音
                    winsound.PlaySound(self.custom_sound_path, winsound.SND_FILENAME)
                else:
                    # 播放系统默认声音
                    winsound.MessageBeep()
            except Exception as e:
                print(f"播放声音失败: {e}")
        
        # 显示通知
        if self.notification_action.isChecked():
            notification_text = self.notification_text.text() or "倒计时结束！"
            QMessageBox.information(self, "通知", notification_text)
    
    def resizeEvent(self, event):
        # 响应式设计：根据窗口大小调整字体大小
        window_size = self.size()
        
        # 获取倒计时显示部件的几何信息
        time_display_rect = self.time_display.geometry()
        
        # 计算中间区域的大小
        # 考虑到顶部菜单栏和底部控件的高度，使用窗口高度的60%作为可用高度
        available_height = window_size.height() * 0.6
        available_width = window_size.width() * 0.8
        
        # 计算合适的字体大小，确保能够充满中间区域
        # 根据宽度和高度分别计算字体大小，取较小值
        font_size_by_width = available_width // 8  # 8个字符（HH:MM:SS）
        font_size_by_height = available_height
        
        # 取较小值，确保字体能够完全显示
        font_size = int(min(font_size_by_width, font_size_by_height))
        
        # 设置字体大小范围
        font_size = max(24, min(150, font_size))
        
        # 更新倒计时显示字体大小
        font = QFont("Arial", font_size, QFont.Bold)
        self.time_display.setFont(font)
        
        # 调整输入框大小，实现响应式效果
        if window_size.width() < 700:
            # 小屏幕：缩小输入框
            self.hour_input.setFixedWidth(60)
            self.minute_input.setFixedWidth(60)
            self.second_input.setFixedWidth(60)
        else:
            # 大屏幕：正常大小输入框
            self.hour_input.setFixedWidth(80)
            self.minute_input.setFixedWidth(80)
            self.second_input.setFixedWidth(80)
        
        # 强制刷新布局
        self.layout().update()
        self.repaint()

if __name__ == "__main__":
    import signal
    import threading
    
    app = QApplication(sys.argv)
    window = CountdownApp()
    window.show()
    
    # 处理 Ctrl+C 信号
    def signal_handler(signal, frame):
        print("收到终止信号，正在退出...")
        # 在主线程中执行退出操作
        def exit_app():
            # 隐藏托盘图标
            window.tray_icon.hide()
            # 保存设置
            window.save_settings()
            # 退出应用程序
            QCoreApplication.quit()
        
        # 使用 QMetaObject.invokeMethod 在主线程中执行
        from PyQt5.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(app, exit_app, Qt.QueuedConnection)
    
    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行应用程序
    sys.exit(app.exec_())