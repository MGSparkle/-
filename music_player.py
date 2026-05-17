import sys
import os
import random

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QSlider,
    QListWidget
)

from PyQt5.QtCore import Qt, QUrl

from PyQt5.QtMultimedia import (
    QMediaPlayer,
    QMediaContent
)

# =========================================================
# 全局样式
# =========================================================

STYLE_SHEET = """
QMainWindow {
    background-color: #0B0B0F;
}

/* 标题 */
QLabel {
    color: white;
    font-size: 16px;
    font-family: "Microsoft YaHei";
}

/* 歌曲标题 */
#TitleLabel {
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 15px;
}

/* 歌曲列表 */
QListWidget {
    background-color: #151518;
    border: none;
    border-radius: 20px;
    color: #BBBBBB;
    padding: 10px;
    outline: none;
}

QListWidget::item {
    padding: 14px;
    border-radius: 12px;
}

QListWidget::item:selected {
    background-color: #232329;
    color: #1ED760;
}

/* 滑块 */
QSlider::groove:horizontal {
    background: #3A3A3A;
    height: 6px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #1ED760;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #1ED760;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

/* 通用按钮 */
QPushButton {
    color: white;
    border: none;
    font-family: "Segoe UI Symbol";
}

/* 主播放按钮 */
#MainBtn {

    background-color: #1ED760;

    font-size: 42px;
    font-weight: bold;

    min-width: 110px;
    max-width: 110px;

    min-height: 110px;
    max-height: 110px;

    border-radius: 55px;
}

#MainBtn:hover {
    background-color: #24FF77;
}

/* 圆形按钮 */
#CircleBtn {

    background-color: #1A1A1F;

    font-size: 38px;

    min-width: 82px;
    max-width: 82px;

    min-height: 82px;
    max-height: 82px;

    border-radius: 41px;

    border: 2px solid #2B2B31;
}

#CircleBtn:hover {
    border: 2px solid #1ED760;
    background-color: #232329;
}

/* 底部按钮 */
#BottomBtn {

    background-color: #1A1A1F;

    font-size: 20px;
    font-weight: bold;

    min-height: 60px;

    border-radius: 20px;

    padding-left: 20px;
    padding-right: 20px;

    border: 2px solid #2B2B31;
}

#BottomBtn:hover {
    border: 2px solid #1ED760;
    background-color: #232329;
}
"""


# =========================================================
# 主窗口
# =========================================================

class SimplePlayer(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("本地音爆")

        self.setFixedSize(560, 700)

        # 播放器
        self.mediaPlayer = QMediaPlayer(self)

        # 数据
        self.playlist_data = []

        self.current_song_index = -1

        # 播放模式
        # 0 = 顺序播放
        # 1 = 随机播放
        self.play_mode = 0

        # 初始化UI
        self.init_ui()

        # 应用样式
        self.setStyleSheet(STYLE_SHEET)

        # =================================================
        # 信号绑定
        # =================================================

        self.mediaPlayer.positionChanged.connect(
            self.position_changed
        )

        self.mediaPlayer.durationChanged.connect(
            self.duration_changed
        )

        self.mediaPlayer.stateChanged.connect(
            self.update_ui_state
        )

        self.mediaPlayer.mediaStatusChanged.connect(
            self.auto_next_song
        )

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        self.main_widget = QWidget()

        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout(self.main_widget)

        layout.setContentsMargins(30, 25, 30, 30)

        layout.setSpacing(22)

        # =================================================
        # 歌曲标题
        # =================================================

        self.title_label = QLabel("暂无播放歌曲")

        self.title_label.setObjectName("TitleLabel")

        self.title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title_label)

        # =================================================
        # 歌曲列表
        # =================================================

        self.list_widget = QListWidget()

        self.list_widget.itemDoubleClicked.connect(
            self.play_selected
        )

        layout.addWidget(self.list_widget)

        # =================================================
        # 倍速控制
        # =================================================

        speed_layout = QHBoxLayout()

        speed_layout.setSpacing(15)

        speed_text = QLabel("变速")

        self.speed_slider = QSlider(Qt.Horizontal)

        self.speed_slider.setRange(20, 400)

        self.speed_slider.setValue(100)

        self.speed_slider.sliderReleased.connect(
            self.update_playback_rate
        )

        self.speed_label = QLabel("1.0x")

        self.speed_label.setFixedWidth(55)

        speed_layout.addWidget(speed_text)

        speed_layout.addWidget(self.speed_slider)

        speed_layout.addWidget(self.speed_label)

        layout.addLayout(speed_layout)

        # =================================================
        # 进度条
        # =================================================

        self.progress_slider = QSlider(Qt.Horizontal)

        self.progress_slider.sliderMoved.connect(
            self.set_position
        )

        layout.addWidget(self.progress_slider)

        # =================================================
        # 播放控制按钮
        # =================================================

        control_layout = QHBoxLayout()

        control_layout.setSpacing(35)

        # 上一首
        self.prev_btn = QPushButton("⏮️")

        self.prev_btn.setObjectName("CircleBtn")

        self.prev_btn.clicked.connect(
            self.previous_song
        )

        # 播放暂停
        self.play_pause_btn = QPushButton("▶")

        self.play_pause_btn.setObjectName("MainBtn")

        self.play_pause_btn.clicked.connect(
            self.toggle_play
        )

        # 下一首
        self.next_btn = QPushButton("⏭️")

        self.next_btn.setObjectName("CircleBtn")

        self.next_btn.clicked.connect(
            self.next_song
        )

        control_layout.addStretch()

        control_layout.addWidget(self.prev_btn)

        control_layout.addWidget(self.play_pause_btn)

        control_layout.addWidget(self.next_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        # =================================================
        # 底部按钮
        # =================================================

        bottom_layout = QHBoxLayout()

        bottom_layout.setSpacing(20)

        # 添加歌曲
        self.add_btn = QPushButton("+ 添加歌曲")

        self.add_btn.setObjectName("BottomBtn")

        self.add_btn.clicked.connect(
            self.add_files
        )

        # 播放模式
        self.mode_btn = QPushButton("↻ 顺序播放")

        self.mode_btn.setObjectName("BottomBtn")

        self.mode_btn.clicked.connect(
            self.toggle_play_mode
        )

        bottom_layout.addWidget(self.add_btn)

        bottom_layout.addWidget(self.mode_btn)

        layout.addLayout(bottom_layout)

    # =====================================================
    # 添加文件
    # =====================================================

    def add_files(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音乐",
            "",
            "Audio Files (*.mp3 *.wav)"
        )

        if files:

            for file in files:

                self.playlist_data.append(file)

                self.list_widget.addItem(
                    os.path.basename(file)
                )

    # =====================================================
    # 播放选中歌曲
    # =====================================================

    def play_selected(self):

        row = self.list_widget.currentRow()

        if row == -1:
            return

        self.current_song_index = row

        path = self.playlist_data[row]

        self.mediaPlayer.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(path)
            )
        )

        self.title_label.setText(
            os.path.basename(path)
        )

        # 应用倍速
        self.update_playback_rate()

        self.mediaPlayer.play()

    # =====================================================
    # 播放/暂停
    # =====================================================

    def toggle_play(self):

        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:

            self.mediaPlayer.pause()

        else:

            # 如果没媒体
            if self.mediaPlayer.mediaStatus() == QMediaPlayer.NoMedia:

                if self.list_widget.count() > 0:

                    self.list_widget.setCurrentRow(0)

                    self.play_selected()

            else:

                self.mediaPlayer.play()

    # =====================================================
    # 更新播放按钮
    # =====================================================

    def update_ui_state(self, state):

        if state == QMediaPlayer.PlayingState:

            self.play_pause_btn.setText("❚❚")

        else:

            self.play_pause_btn.setText("▶")

    # =====================================================
    # 更新倍速
    # =====================================================

    def update_playback_rate(self):

        rate = self.speed_slider.value() / 100.0

        self.speed_label.setText(
            f"{rate:.1f}x"
        )

        self.mediaPlayer.setPlaybackRate(rate)

    # =====================================================
    # 更新进度
    # =====================================================

    def position_changed(self, pos):

        if not self.progress_slider.isSliderDown():

            self.progress_slider.setValue(pos)

    # =====================================================
    # 更新时长
    # =====================================================

    def duration_changed(self, dur):

        self.progress_slider.setRange(0, dur)

    # =====================================================
    # 设置位置
    # =====================================================

    def set_position(self, pos):

        self.mediaPlayer.setPosition(pos)

    # =====================================================
    # 上一首
    # =====================================================

    def previous_song(self):

        if not self.playlist_data:
            return

        if self.current_song_index <= 0:

            self.current_song_index = len(
                self.playlist_data
            ) - 1

        else:

            self.current_song_index -= 1

        self.list_widget.setCurrentRow(
            self.current_song_index
        )

        self.play_selected()

    # =====================================================
    # 下一首
    # =====================================================

    def next_song(self):

        if not self.playlist_data:
            return

        # 顺序播放
        if self.play_mode == 0:

            if self.current_song_index >= len(self.playlist_data) - 1:

                self.current_song_index = 0

            else:

                self.current_song_index += 1

        # 随机播放
        else:

            self.current_song_index = random.randint(
                0,
                len(self.playlist_data) - 1
            )

        self.list_widget.setCurrentRow(
            self.current_song_index
        )

        self.play_selected()

    # =====================================================
    # 自动下一首
    # =====================================================

    def auto_next_song(self, status):

        if status == QMediaPlayer.EndOfMedia:

            self.next_song()

    # =====================================================
    # 切换播放模式
    # =====================================================

    def toggle_play_mode(self):

        # 随机
        if self.play_mode == 0:

            self.play_mode = 1

            self.mode_btn.setText(
                "⇄ 随机播放"
            )

        # 顺序
        else:

            self.play_mode = 0

            self.mode_btn.setText(
                "↻ 顺序播放"
            )


# =========================================================
# 主程序
# =========================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    player = SimplePlayer()

    player.show()

    sys.exit(app.exec_())