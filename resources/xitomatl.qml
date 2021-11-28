import QtQuick 2.0
Item {
  width: icon_size
  height: icon_size
  Rectangle {
    color: icon_color
    width: parent.width - icon_padding * 2
    height: parent.height - icon_padding * 2
    radius: icon_radius
    anchors.centerIn: parent

    Text {
      visible: task_running
      color: text_color
      text: icon_text
      font.family: icon_font
      font.pixelSize: icon_font_size
      anchors.fill: parent
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      anchors.leftMargin: text_x
      anchors.topMargin: text_y
    }

    Rectangle {
      visible: !task_running
      width: parent.width - icon_padding * 3
      height: parent.height - icon_padding * 3
      color: text_color
      anchors.centerIn: parent
    }
  }
}
