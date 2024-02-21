import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpinBox,QMessageBox, QSystemTrayIcon, QApplication, QTextEdit, QDateTimeEdit, QListWidget, QMenu, QAction, QCheckBox, QListWidgetItem, QLabel, QFrame, QMessageBox, QComboBox
from PyQt5.QtCore import QPoint, QTimer, QDateTime, Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont,QPainter, QColor, QBrush, QIcon

class CouponManagementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.coupon_list = []
        self.reminder_threshold = 1  # 默认提醒阈值为24小时
        self.checkbox_states = {}
        self.alerted_coupons = set()  # 记录已经提醒过的优惠券 
        self.initUI()

    def initUI(self):
        self.setWindowTitle('优惠券管理软件')
        self.setGeometry(100, 100, 600, 400)

        # 添加主题选择下拉框
        self.theme_combo_box = QComboBox(self)
        self.theme_combo_box.addItem("默认主题")
        self.theme_combo_box.addItem("黑色主题")
        self.theme_combo_box.currentIndexChanged.connect(self.changeTheme)

        # 添加提醒阈值选择框
        self.reminder_threshold_input = QSpinBox(self)
        self.reminder_threshold_input.setRange(1, 72)  # 设置阈值范围为1到72小时
        self.reminder_threshold_input.setValue(self.reminder_threshold)  # 设置默认值
        self.reminder_threshold_input.valueChanged.connect(self.updateReminderThreshold)

        # 创建顶级布局
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.border_frame = QFrame(self)
        self.border_frame.setObjectName("borderFrame")
        self.border_frame.setFrameShape(QFrame.StyledPanel)
        self.border_frame.setFrameShadow(QFrame.Raised)

        self.border_layout = QVBoxLayout(self.border_frame)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('输入优惠券名称')
        self.date_input = QDateTimeEdit(self)
        self.name_input.setMinimumWidth(400)
        self.name_input.setMinimumHeight(40)
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_input.setDateTime(QDateTime.currentDateTime())
        self.date_input.setMinimumWidth(400)
        self.date_input.setMinimumHeight(40)
        self.add_button = QPushButton('添加优惠券', self)
        self.add_button.clicked.connect(self.addCoupon)

        font = QFont()
        font.setPointSize(12)
        self.name_input.setFont(font)
        self.date_input.setFont(font)
        self.add_button.setStyleSheet("color: white; background-color: #4CAF50; border: none; padding: 10px; border-radius: 5px;")

        self.select_all_checkbox = QCheckBox('全选', self)
        self.select_all_checkbox.stateChanged.connect(self.selectAllCoupons)

        self.coupon_layout = QVBoxLayout()
        self.coupon_list_widget = QListWidget(self)
        self.coupon_layout.addWidget(self.coupon_list_widget)

        self.delete_button = QPushButton('删除选中优惠券', self)
        self.delete_button.setStyleSheet("color: white; background-color: #cc7391; border: none; padding: 10px; border-radius: 5px;")
        self.delete_button.clicked.connect(self.deleteSelectedCoupon)
        self.coupon_layout.addWidget(self.delete_button)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.name_input)
        hbox1.addWidget(self.date_input)
        hbox1.addWidget(self.add_button)
        hbox1.addWidget(self.select_all_checkbox)
        hbox1.addWidget(self.theme_combo_box)  # 将主题选择下拉框添加到布局中

        hbox2 = QHBoxLayout()  # 添加这一行来定义 hbox2
        hbox2.addWidget(self.reminder_threshold_input)
        hbox2.addWidget(QLabel("小时"))
        hbox1.addLayout(hbox2)  # 将 hbox2 添加到 hbox1 中

        self.border_layout.addLayout(hbox1)
        self.border_layout.addLayout(self.coupon_layout)

        self.layout.addWidget(self.border_frame)

        self.setStyleSheet("""
            #borderFrame {
                background-color: #ffffff;
                border: 2px solid #2C3E50;
                border-radius: 10px;
            }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCouponTime)
        self.timer.start(1000)

        self.loadCoupons()

    def notifyExpiration(self, coupon_name):
        # 创建消息框并设置标题和内容
        msg = QMessageBox()
        msg.setWindowTitle("优惠券即将过期")
        msg.setText("您的优惠券 '{}' 即将过期，请尽快使用！".format(coupon_name))
        msg.setIcon(QMessageBox.Warning)  # 设置消息框图标为警告图标
        msg.exec_()

    def changeTheme(self, index):
        if index == 0:
            # 默认白色主题的样式设置
            self.setStyleSheet("""
                #borderFrame {
                    background-color: #ffffff;
                    border: 2px solid #2C3E50;
                    border-radius: 10px;
                }
                QLineEdit, QDateTimeEdit, QPushButton, QCheckBox, QLabel, QListWidget {
                    color: black; /* 设置文本颜色为黑色 */
                    background-color: transparent; /* 设置背景为透明 */
                }
            """)

        elif index == 1:
            # 黑色主题的样式设置
            self.setStyleSheet("""
                #borderFrame {
                    background-color: #303030;
                    border: 2px solid #ffffff;
                    border-radius: 10px;
                }
                QLineEdit, QDateTimeEdit { /* 明确指定 QDateTimeEdit 的背景色 */
                    color: #ffffff; /* 设置文本颜色为白色 */
                    background-color: #303030; /* 设置背景颜色为黑色 */
                }
                QPushButton, QCheckBox, QLabel, QListWidget {
                    color: #ffffff;
                    background-color: transparent;
                }

                QMessageBox { 
                    color: #ffffff;
                    background-color: #303030;
                }
                QMessageBox::information, QMessageBox::warning, QMessageBox::critical, QMessageBox::question {
                    background-color: #303030;
                    color: #ffffff;
                }
                QMessageBox QPushButton { 
                    color: white;
                    background-color: #4CAF50;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)


    def addCoupon(self):
        name = self.name_input.text()
        date = self.date_input.dateTime()
        self.coupon_list.append((name, date))
        self.updateCouponList()
        self.saveCoupons()
        self.name_input.clear()

        # 添加动画效果
        animation = QPropertyAnimation(self.coupon_list_widget, b"geometry")
        animation.setDuration(500)
        animation.setStartValue(self.coupon_list_widget.geometry())
        animation.setEndValue(self.coupon_list_widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.start()

        self.resize(self.width(), self.height() + 1)

        # 显示消息框，告知用户操作已成功完成
        QMessageBox.information(self, "成功", "优惠券添加成功！")

    def selectAllCoupons(self, state):
        for i in range(self.coupon_list_widget.count()):
            item_widget = self.coupon_list_widget.itemWidget(self.coupon_list_widget.item(i))
            checkbox = item_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(state == Qt.Checked)

    def updateCouponList(self):
        self.coupon_list_widget.clear()
        for i, (name, end_time) in enumerate(self.coupon_list):
            remaining_time = QDateTime.currentDateTime().secsTo(end_time)
            if remaining_time <= 0:
                item_text = f"{name} - 该优惠券已过期"
                # 过期优惠券的动画效果
                item_widget = self.coupon_list_widget.itemWidget(self.coupon_list_widget.item(i))
                if item_widget is not None:
                    self.applyExpiredCouponAnimation(item_widget)
            else:
                days = remaining_time // (60 * 60 * 24)
                hours = (remaining_time % (60 * 60 * 24)) // (60 * 60)
                minutes = (remaining_time % (60 * 60)) // 60
                seconds = remaining_time % 60
                item_text = f"{name} - 剩余时间：{days}天 {hours}小时 {minutes}分钟 {seconds}秒"
                if remaining_time <= self.reminder_threshold * 3600 and name not in self.alerted_coupons:
                    self.notifyExpiration(name)
                    self.alerted_coupons.add(name)
                
            item_widget = QWidget()
            hbox = QHBoxLayout(item_widget)
            checkBox = QCheckBox()
            checkBox.setChecked(self.checkbox_states.get(i, False))
            checkBox.stateChanged.connect(lambda state, i=i: self.checkboxStateChanged(state, i))
            hbox.addWidget(checkBox)
            label = QLabel(item_text)
            hbox.addWidget(label)
            listWidgetItem = QListWidgetItem()
            listWidgetItem.setSizeHint(item_widget.sizeHint())
            self.coupon_list_widget.addItem(listWidgetItem)
            self.coupon_list_widget.setItemWidget(listWidgetItem, item_widget)


    def notifyExpiration(self, coupon_name):
        # 发送桌面通知
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(QIcon('icon.png'))  # 替换 'icon.png' 为你的图标路径
        tray_icon.setToolTip('优惠券管理软件')
        
        menu = QMenu()
        action = QAction("您的优惠券'{}'即将过期，请尽快使用！".format(coupon_name), self)
        menu.addAction(action)
        tray_icon.setContextMenu(menu)
        
        tray_icon.show()

        # 闪烁背景色
        self.blinkBackground()

        QMessageBox.information(self, "提醒", f"您的优惠券'{coupon_name}'即将过期，请尽快使用！")

    def blinkBackground(self):
        # 创建动画以闪烁背景色
        animation = QPropertyAnimation(self.border_frame, b"styleSheet")
        animation.setDuration(500)
        animation.setLoopCount(3)  # 闪烁三次
        animation.setStartValue(self.border_frame.styleSheet())
        animation.setEndValue("background-color: red;")
        animation.start()            

    def applyExpiredCouponAnimation(self, item_widget):
        animation = QPropertyAnimation(item_widget, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(item_widget.geometry())
        # 移动到一侧并渐隐
        end_point = QPoint(item_widget.geometry().x() - 100, item_widget.geometry().y())
        animation.setEndValue(QRect(end_point, item_widget.sizeHint()))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()


    def updateCouponTime(self):
        self.updateCouponList()

    def saveCoupons(self):
        with open('coupons.json', 'w') as f:
            json.dump(self.coupon_list, f, default=self.jsonDefault)

    def loadCoupons(self):
        try:
            with open('coupons.json', 'r') as f:
                coupons = json.load(f)
                for coupon in coupons:
                    name = coupon[0]
                    expiration_date_str = coupon[1]
                    expiration_date = QDateTime.fromString(expiration_date_str, Qt.ISODateWithMs)
                    self.coupon_list.append((name, expiration_date))
                print("Loaded coupons:", self.coupon_list)
        except FileNotFoundError:
            pass

    def updateReminderThreshold(self):
        try:
            # 获取用户输入的提醒阈值，转换为整数
            threshold = int(self.reminder_threshold_input.text())
            self.reminder_threshold = threshold
            self.updateCouponList()  # 更新优惠券列表，以便根据新的阈值进行提醒
        except ValueError:
            pass    

    def jsonDefault(self, obj):
        if isinstance(obj, QDateTime):
            return obj.toString(Qt.ISODateWithMs)
        return obj

    def checkboxStateChanged(self, state, index):
        self.checkbox_states[index] = (state == Qt.Checked)

    def deleteSelectedCoupon(self):
        # Modified code for deleting selected coupons
        if not any(self.checkbox_states.values()):
            QMessageBox.warning(self, "警告", "请选择需要删除的优惠券")
            return

        coupons_to_delete = [index for index, checked in self.checkbox_states.items() if checked]
        
        for index in sorted(coupons_to_delete, reverse=True):
            del self.coupon_list[index]
            del self.checkbox_states[index]

        self.updateCouponList()
        self.saveCoupons()

        self.select_all_checkbox.setChecked(False)

        QMessageBox.information(self, "成功", "选中优惠券已删除！")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CouponManagementApp()
    ex.show()
    sys.exit(app.exec_())

