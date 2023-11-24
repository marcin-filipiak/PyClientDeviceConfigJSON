import sys
import json

#pip install pybluez==0.22
import bluetooth

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QCheckBox, QRadioButton, QPushButton, QComboBox, QLabel


target_device_address = '30:AE:A4:25:09:E2'


def create_label(member):
    label = QLabel(member["value"])
    return label

def create_text(member):
    text = QLineEdit(member["value"])
    text.setObjectName(member["name"])
    return text

def create_password(member):
    password = QLineEdit(member["value"])
    password.setEchoMode(QLineEdit.Password)
    password.setObjectName(member["name"])
    return password

def create_state(member):
    state = QCheckBox(member["label"])
    state.setChecked(member["value"])
    state.setObjectName(member["name"])
    return state

def create_binswitch(member):
    binswitch = QRadioButton(member["label"])
    binswitch.setChecked(member["set"])
    binswitch.setObjectName(member["name"])
    return binswitch

def create_select(member):
    select = QComboBox()
    for value in member["value"]:
        select.addItem(value["label"], value["value"])
    select.setCurrentIndex(member["set"])
    select.setObjectName(member["name"])
    return select

def create_button(button, form):
    if button["type"] == "save":
        save_button = QPushButton(button["label"])
        save_button.clicked.connect(lambda: save(form))
        return save_button
    elif button["type"] == "reset":
        reset_button = QPushButton(button["label"])
        reset_button.clicked.connect(lambda: reset(form))
        return reset_button

def save(form):
    data = {"forms": [{"name": "test_form","title": "Example Form","members": []}]}
    types_to_search = [QLineEdit, QCheckBox, QRadioButton, QComboBox]
    for widget_type in types_to_search:
        for member in form.findChildren(widget_type):
            name = member.objectName()
            if name:
                member_data = {
                    "name": name,
                }
                if isinstance(member, QLineEdit):
                    member_data["type"] = "text"
                    member_data["value"] = member.text()
                elif isinstance(member, QCheckBox):
                    member_data["type"] = "state"
                    member_data["value"] = member.isChecked()
                elif isinstance(member, QRadioButton):
                    member_data["type"] = "binswitch"
                    member_data["set"] = member.isChecked()
                elif isinstance(member, QComboBox):
                    member_data["type"] = "select"
                    member_data["set"] = member.currentIndex()
                data["forms"][0]["members"].append(member_data)
    sendbt(json.dumps(data))
    pass

def reset(form):
    # Implement reset logic here
    pass

def create_form(form_data):
    form = QWidget()
    layout = QVBoxLayout()

    for member in form_data["members"]:
        if member["type"] == "label":
            layout.addWidget(create_label(member))
        elif member["type"] == "text":
            layout.addWidget(create_label({"value": member["label"]+":"}))
            layout.addWidget(create_text(member))
        elif member["type"] == "password":
            layout.addWidget(create_label({"value": member["label"]+":"}))
            layout.addWidget(create_password(member))
        elif member["type"] == "state":
            layout.addWidget(create_state(member))
        elif member["type"] == "binswitch":
            layout.addWidget(create_binswitch(member))
        elif member["type"] == "select":
            layout.addWidget(create_label({"value": member["label"]+":"}))
            layout.addWidget(create_select(member))

    for button in form_data["button"]:
        layout.addWidget(create_button(button, form))

    form.setLayout(layout)
    return form

def get_available_devices():
  devices = bluetooth.discover_devices(duration=4, lookup_names=True, device_id=-1)
  print(devices)
  return devices

def sendbt(message):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((target_device_address, 1))  # port RFCOMM (default is 1)
        sock.send(message)
        print("Sending data:")
        print(message)
        sock.close()
    except Exception as e:
        print(f'Something gone wrong: {e}')
    pass


def receivebt():
    received_data = ""
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((target_device_address, 1))  # Port RFCOMM (default is 1)
        print(f"Connected to device: {target_device_address}")
        while True:
            data = sock.recv(1024)
            if not data:
                break
            received_data += data.decode('utf-8')
            if '\r\n' in received_data:
                break
        sock.close()
        print("Received data:")
        print(received_data)
        return received_data
    except Exception as e:
        print(f'Something gone wrong: {e}')
        return None

def main():
    app = QApplication(sys.argv)
    data = json.loads(receivebt())
    form_data = data["forms"][0]
    window = QMainWindow()
    window.setWindowTitle("PyClientDeviceConfigJSON")    
    window.setCentralWidget(create_form(form_data))
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
