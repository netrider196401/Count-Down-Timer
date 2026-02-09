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
                "system_default": "系统默认",
                "sound_settings": "声音设置",
                "select_sound_file": "选择声音文件",
                "notification_settings": "通知设置",
                "set_notification_text": "设置通知文本",
                "select_sound_type": "选择提示音类型"
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
                "system_default": "System Default",
                "sound_settings": "Sound Settings",
                "select_sound_file": "Select Sound File",
                "notification_settings": "Notification Settings",
                "set_notification_text": "Set Notification Text",
                "select_sound_type": "Select Sound Type"
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
    
    def show_manual(self):
        # 根据当前语言选择使用说明书内容
        if self.current_language == "zh":
            manual_content = """循环计时器使用说明书

1. 应用程序简介
循环计时器是一款功能强大的倒计时工具，支持多种设置选项，适合各种需要计时的场景。

2. 功能特性
- 倒计时核心功能（开始、暂停、停止、复位）
- 响应式布局，底部控件固定，中间显示自动放大
- 字体大小随窗口变化自动调整
- 声音和通知设置
- 系统托盘后台运行
- 中英文语言切换
- 本地配置存储

3. 使用方法
3.1 时间设置
在窗口底部的时间设置区域，分别输入小时、分钟和秒的数值，设置倒计时的时间长度。

3.2 控制按钮
- 开始：启动倒计时
- 暂停：暂停当前倒计时
- 停止：停止当前倒计时
- 复位：将倒计时重置为初始设置

3.3 声音设置
在设置菜单 -> 声音设置中：
- 启用声音：勾选后，倒计时结束时会播放声音
- 选择声音文件：点击后可选择自定义声音文件

3.4 通知设置
在设置菜单 -> 通知设置中：
- 启用通知：勾选后，倒计时结束时会显示通知
- 设置通知文本：点击后可设置自定义通知文本

3.5 语言切换
在设置菜单 -> 语言中选择中文或 English，切换应用程序语言。

3.6 后台运行
当窗口关闭时，应用程序会最小化到系统托盘，继续后台运行。
在系统托盘图标上右键，可选择显示窗口或退出应用程序。

4. 技术支持
如有任何问题或建议，请联系开发者。

5. 版本信息
当前版本：v1.01
发布日期：2026-02-08
"""
            window_title = "使用说明书"
        else:
            manual_content = """Countdown Timer User Manual

1. Application Introduction
Countdown Timer is a powerful countdown tool with multiple setting options, suitable for various timing scenarios.

2. Features
- Core countdown functions (Start, Pause, Stop, Reset)
- Responsive layout, fixed bottom controls, auto-scaling middle display
- Font size automatically adjusts with window changes
- Sound and notification settings
- System tray background running
- Chinese and English language switching
- Local configuration storage

3. Usage Instructions
3.1 Time Setting
In the time setting area at the bottom of the window, enter the values for hours, minutes, and seconds respectively to set the countdown duration.

3.2 Control Buttons
- Start: Start the countdown
- Pause: Pause the current countdown
- Stop: Stop the current countdown
- Reset: Reset the countdown to the initial setting

3.3 Sound Settings
In Settings menu -> Sound Settings:
- Enable Sound: When checked, sound will play at the end of countdown
- Select Sound File: Click to select a custom sound file

3.4 Notification Settings
In Settings menu -> Notification Settings:
- Enable Notification: When checked, notification will be displayed at the end of countdown
- Set Notification Text: Click to set custom notification text

3.5 Language Switching
In Settings menu -> Language, select Chinese or English to switch the application language.

3.6 Background Running
When the window is closed, the application will minimize to the system tray and continue running in the background.
Right-click on the system tray icon to select Show Window or Exit Application.

4. Technical Support
For any questions or suggestions, please contact the developer.

5. Version Information
Current Version: v1.01
Release Date: 2026-02-08
"""
            window_title = "User Manual"
        
        # 创建一个消息框显示使用说明书
        msg_box = QMessageBox()
        msg_box.setWindowTitle(window_title)
        msg_box.setText(manual_content)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_about(self):
        # 根据当前语言选择关于对话框内容
        if self.current_language == "zh":
            about_content = """循环计时器 v1.01

一款由菜鸟开发的倒计时工具，该应用主要由Trae SOLO帮助编写。

开发者：骑鹅勇士
版权所有 © 2026

保留所有权利。

联系方式：
- 邮箱：hct003@outlook.com
- 网站： https://github.com/netrider196401
"""
            window_title = "关于"
        else:
            about_content = """Countdown Timer v1.01

A countdown tool developed by a novice, mainly written with the help of Trae SOLO.

Developer: NETRIDER
Copyright © 2026

All rights reserved.

Contact:
- Email: hct003@outlook.com
- Website: https://github.com/netrider196401
"""
            window_title = "About"
        
        # 创建一个消息框显示关于信息
        msg_box = QMessageBox()
        msg_box.setWindowTitle(window_title)
        msg_box.setText(about_content)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
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
        self.sound_menu = QMenu(self.language_dict[self.current_language]["sound_settings"], self)
        self.sound_action = QAction(self.language_dict[self.current_language]["enable_sound"], self)
        self.sound_action.setCheckable(True)
        self.sound_menu.addAction(self.sound_action)
        
        # 添加声音文件选择动作
        self.select_sound_action = QAction(self.language_dict[self.current_language]["select_sound_file"], self)
        self.select_sound_action.triggered.connect(self.browse_sound)
        self.sound_menu.addAction(self.select_sound_action)
        self.settings_menu.addMenu(self.sound_menu)
        
        # 通知设置子菜单
        self.notification_menu = QMenu(self.language_dict[self.current_language]["notification_settings"], self)
        self.notification_action = QAction(self.language_dict[self.current_language]["enable_notification"], self)
        self.notification_action.setCheckable(True)
        self.notification_menu.addAction(self.notification_action)
        # 添加通知文本设置动作
        self.set_notification_action = QAction(self.language_dict[self.current_language]["set_notification_text"], self)
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
        # 添加使用说明书选项
        self.manual_action = QAction("使用说明书", self)
        self.manual_action.triggered.connect(self.show_manual)
        self.help_menu.addAction(self.manual_action)
        # 添加关于选项
        self.about_action = QAction(self.language_dict[self.current_language]["about"], self)
        self.about_action.triggered.connect(self.show_about)
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
            self.sound_menu.setTitle(lang_dict["sound_settings"])
            self.sound_action.setText(lang_dict["enable_sound"])
            if hasattr(self, 'select_sound_action'):
                self.select_sound_action.setText(lang_dict["select_sound_file"])
        if hasattr(self, 'notification_menu'):
            self.notification_menu.setTitle(lang_dict["notification_settings"])
            self.notification_action.setText(lang_dict["enable_notification"])
            if hasattr(self, 'set_notification_action'):
                self.set_notification_action.setText(lang_dict["set_notification_text"])
        # 更新语言子菜单
        self.language_menu.setTitle(lang_dict["language"])
        self.chinese_action.setText(lang_dict["chinese"])
        self.english_action.setText(lang_dict["english"])
        # 更新帮助菜单
        self.help_menu.setTitle(lang_dict["help"])
        # 更新使用说明书选项
        if hasattr(self, 'manual_action'):
            self.manual_action.setText("使用说明书" if self.current_language == "zh" else "User Manual")
        # 更新关于选项
        self.about_action.setText(lang_dict["about"])
        
        # 更新按钮
        self.start_button.setText(lang_dict["start"])
        self.pause_button.setText(lang_dict["pause"])
        self.stop_button.setText(lang_dict["stop"])
        self.reset_button.setText(lang_dict["reset"])
        

        
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
            self.update_display()
            # 触发通知和声音
            self.trigger_notification()
            # 重新开始倒计时（循环）
            self.restart_countdown()
    
    def restart_countdown(self):
        # 重新开始倒计时
        # 从输入框获取初始设置的时间
        try:
            hours = int(self.hour_input.text())
            minutes = int(self.minute_input.text())
            seconds = int(self.second_input.text())
            self.time_left = QTime(hours, minutes, seconds)
        except ValueError:
            self.time_left = QTime(0, 0, 0)
        
        # 重新启动计时器
        self.timer.start(1000)
    
    def update_display(self):
        # 更新倒计时显示
        self.time_display.setText(self.time_left.toString("HH:mm:ss"))



    def browse_sound(self):
        # 浏览并选择自定义声音文件
        file_dialog = QFileDialog()
        # 只允许选择WAV格式的声音文件，因为winsound模块只支持WAV格式
        file_path, _ = file_dialog.getOpenFileName(self, "选择声音文件", "", "WAV音频文件 (*.wav)")
        
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
        enable_sound = self.settings.value("enable_sound", True, type=bool)
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
                    # 使用当前目录下的Sound.wav作为默认提示音
                    sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sound.wav")
                    if os.path.exists(sound_path):
                        winsound.PlaySound(
                            sound_path,
                            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                        )
                    else:
                        # 如果Sound.wav不存在，使用系统默认声音
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