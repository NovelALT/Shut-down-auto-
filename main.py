import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QInputDialog
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFontDatabase, QFont

# โหลดไฟล์สไตล์ Dracula
def load_stylesheet():
    with open("dracula.qss", "r") as file:
        return file.read()

class ShutdownApp(QWidget):
    def __init__(self):
        super().__init__()

        # ตั้งค่าหน้าต่าง UI
        self.setWindowTitle('ปิดเครื่องอัตโนมัติ By.Kanjanat Soywo')
        self.setGeometry(100, 100, 400, 100)

        # โหลดฟอนต์ Prompt
        font_id = QFontDatabase.addApplicationFont("Prompt-ExtraBold.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.setFont(QFont("Prompt", 10))  # ตั้งค่า default font

        # สร้าง Label สำหรับแสดงข้อความ
        self.label = QLabel('กรอกระยะเวลาในการปิดเครื่อง (ชั่วโมง:นาที:วินาที):', self)
        
        # สร้างกล่องกรอกข้อมูลสำหรับชั่วโมง นาที และวินาที
        self.hour_input = QLineEdit(self)
        self.hour_input.setPlaceholderText("ชั่วโมง")
        self.hour_input.setMaxLength(2)

        self.minute_input = QLineEdit(self)
        self.minute_input.setPlaceholderText("นาที")
        self.minute_input.setMaxLength(2)

        self.second_input = QLineEdit(self)
        self.second_input.setPlaceholderText("วินาที")
        self.second_input.setMaxLength(2)

        # จัด layout สำหรับกรอกชั่วโมง นาที วินาที
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hour_input)
        time_layout.addWidget(self.minute_input)
        time_layout.addWidget(self.second_input)

        # สร้างปุ่มสำหรับปิดเครื่อง
        self.button = QPushButton('ปิดเครื่อง', self)
        self.button.clicked.connect(self.initiate_shutdown)

        # สร้างปุ่มยกเลิก
        self.cancel_button = QPushButton('ยกเลิกการปิดเครื่อง', self)
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        self.cancel_button.setEnabled(False)  # ปิดการใช้งานก่อนเริ่มการนับถอยหลัง

        # สร้าง Label สำหรับแสดงการนับถอยหลัง
        self.countdown_label = QLabel('', self)

        # จัด layout หลัก
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(time_layout)
        layout.addWidget(self.button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)

        # Timer สำหรับการนับถอยหลัง
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)

        # ตัวแปรสำหรับเก็บเวลาที่เหลือ
        self.remaining_time = 0

    def initiate_shutdown(self):
        try:
            # ดึงค่าชั่วโมง นาที วินาที
            hours = int(self.hour_input.text()) if self.hour_input.text() else 0
            minutes = int(self.minute_input.text()) if self.minute_input.text() else 0
            seconds = int(self.second_input.text()) if self.second_input.text() else 0

            # แปลงชั่วโมงและนาทีเป็นวินาที
            delay = (hours * 3600) + (minutes * 60) + seconds
            
            if delay <= 0:
                QMessageBox.warning(self, 'ข้อผิดพลาด', 'กรุณากรอกเวลาที่ถูกต้อง!')
                return
            
            reply = QMessageBox.question(self, 'ยืนยัน', 
                f"คุณแน่ใจหรือไม่ว่าต้องการปิดเครื่องใน {hours:02}:{minutes:02}:{seconds:02}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                # ตั้งค่าเวลาที่เหลือ
                self.remaining_time = delay

                # เปิดการใช้งานปุ่มยกเลิก
                self.cancel_button.setEnabled(True)

                # เริ่มนับถอยหลัง
                self.timer.start(1000)  # อัปเดตทุก 1 วินาที
                self.update_countdown()

        except ValueError:
            QMessageBox.warning(self, 'ข้อผิดพลาด', 'กรุณากรอกตัวเลขที่ถูกต้อง!')

    def update_countdown(self):
        if self.remaining_time > 0:
            # แสดงเวลาที่เหลือในรูปแบบ "ชั่วโมง:นาที:วินาที"
            hours, remainder = divmod(self.remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.countdown_label.setText(f"ปิดเครื่องในอีก {hours:02}:{minutes:02}:{seconds:02}")

            # ลดเวลาที่เหลือทุกวินาที
            self.remaining_time -= 1
        else:
            self.timer.stop()  # หยุดการนับถอยหลัง
            self.perform_shutdown()

    def perform_shutdown(self):
        # สำหรับ Windows
        if os.name == 'nt':
            os.system('shutdown /s /t 0')
        # สำหรับ Linux หรือ MacOS
        else:
            os.system('sudo shutdown -h now')

    def cancel_shutdown(self):
        # หยุดการนับถอยหลัง
        self.timer.stop()
        self.countdown_label.setText("การปิดเครื่องถูกยกเลิก")
        self.cancel_button.setEnabled(False)  # ปิดการใช้งานปุ่มยกเลิก

    def closeEvent(self, event):
        # แสดงข้อความยืนยันเมื่อผู้ใช้ต้องการปิดโปรแกรม
        reply, ok = QInputDialog.getText(self, 'ยืนยันการปิดโปรแกรม', 'กรุณากรอกรหัส:')
        
        if ok and reply == '1234':
            event.accept()  # ปิดโปรแกรม
        else:
            QMessageBox.warning(self, 'รหัสผิด', 'รหัสที่คุณกรอกไม่ถูกต้อง!')
            event.ignore()  # ยกเลิกการปิดโปรแกรม

# ฟังก์ชันเริ่มต้นโปรแกรม
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # โหลดธีม Dracula
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)

    window = ShutdownApp()
    window.show()
    sys.exit(app.exec())
