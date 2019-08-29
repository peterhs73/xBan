import sys
from PySide2.QtCore import Qt, QPoint, Signal, QObject, Slot, QRect
from PySide2.QtGui import (
    QCursor,
    QPainter,
    QPalette,
    QColor,
    QFont,
    QTextDocument,
    QFontMetrics,
    QIcon,
    QTextCursor,
)
from PySide2.QtWidgets import (
    QMessageBox,
    QStatusBar,
    QAbstractSlider,
    QFrame,
    QAction,
    QFileDialog,
    QStyleOption,
    QLineEdit,
    QStyleFactory,
    QDesktopWidget,
    QLabel,
    QScrollBar,
    QScrollArea,
    QPushButton,
    QApplication,
    QWidget,
    QTableWidget,
    QMenu,
    QMainWindow,
    QPlainTextEdit,
    QTextEdit,
    QToolButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QGraphicsDropShadowEffect,
)

import textwrap
from functools import partial
import json
import os
import time
import pathlib

# Styling ##############################
########################################

SBASE_PROJ = '{widget}{{background-color: white; color: black; font-family: "Courier New"; font-size: {fontsize}px; border-bottom: 1px solid #DCDCDC; font-weight: bold;}}'

STYLEPROJECT = SBASE_PROJ.format(widget='QLineEdit', fontsize=22)
STYLETIME = SBASE_PROJ.format(widget='QLabel', fontsize=14)

STYLETITLE = 'QTextEdit{background-color: white; color: #494949; font-size: 17px; font-weight: bold; padding: 12px 12px 5px 12px;}'

SBASE_CONT = '''QTextEdit{{background-color: {bgcolor}; color: {color}; font-size: 15px; font-weight: bold; padding: 10px; border: 0.5px solid {bcolor}; border-radius: 4px;}}
                QMenu{{border-radius: 3px;}}
                QMenu::item:selected{{background-color: {bgcolor}; color: {color};}}'''

STYLER = SBASE_CONT.format(
    bgcolor='#ffecee', color='#fe3a51', bcolor='#fec9d0'
)
STYLEY = SBASE_CONT.format(
    bgcolor='#fef8e7', color='#ff9900', bcolor='#f2ce98'
)
STYLEB = SBASE_CONT.format(
    bgcolor='#eaf8fe', color='#29ade8', bcolor='#c6ebfb'
)
STYLEG = SBASE_CONT.format(
    bgcolor='#bafce2', color='#00c678', bcolor='#2ce89e'
)
STYLEP = SBASE_CONT.format(
    bgcolor='#fbdbff', color='#d30bea', bcolor='#fb87ff'
)

COLOR_LIST = [STYLEP, STYLER, STYLEY, STYLEB, STYLEG]  # need to add color
COLOR_DICT = {
    'purple': STYLEP,
    'red': STYLER,
    'yellow': STYLEY,
    'blue': STYLEB,
    'green': STYLEG,
}

OPENED_DICT = {}

# SYSTEM PATH
DIR_PATH = os.path.dirname(sys.argv[0])

try:
    XBANPATH = sys.argv[1]
except:
    XBANPATH = ''

with open(
    os.path.join(DIR_PATH, 'files', 'xBanStyle.css'), 'r'
) as style_sheet:
    XSTYLE = style_sheet.read()


def _href_link_path(path):  # Change forward slash to backward slash
    return pathlib.Path(path).as_posix()


def _text_line_count(text, char):
    # recognize that there if there is \n in the end
    # split text and wrap and split and count
    if text.endswith('\n'):
        line_count = 1
    else:
        line_count = 0
    for splited_text in text.splitlines():
        if splited_text == '':
            line_count += 1
        else:
            line_count += len(textwrap.wrap(splited_text, char))
    return max(line_count, 1)


# Class Set Up


class NoteBase(QWidget):

    noteMovedSig = Signal(int)
    noteChangeSig = Signal()

    def __init__(self, text, col, parent=None):
        super().__init__(parent)

        self._note_width = 348  # initial width based on 1120 total width
        self._text = text
        self._col = col

        self.note_init()
        self.text_resize(self._char_conv)

    def note_init(self):
        # self.dotBtn = QPushButton('comments', self) # button designed to add comments.
        # red if there's comments, gray if there is nothing
        # use flat and cicular button

        self.note_doc = QTextDocument(self)
        self.note_doc.setPlainText(self._text)

        self.note_doc.contentsChanged.connect(
            partial(self.text_resize, char_width=self._char_conv)
        )
        self.note_doc.contentsChanged.connect(self.confirm_edit)

        self.note_editor = QTextEdit(self)
        self.note_editor.setDocument(self.note_doc)
        self.note_editor.resize(self.size())
        self.note_editor.setLineWrapMode(QTextEdit.WidgetWidth)
        self.note_editor.setTabChangesFocus(True)
        self.note_editor.moveCursor(QTextCursor.End)
        self.note_editor.setAcceptRichText(
            False
        )  # prevent rich text paste from webs

    def confirm_edit(self):
        self._text = self.note_editor.toPlainText()
        self.text_resize(self._char_conv)
        self.noteChangeSig.emit()

    def text_resize(self, char_width):
        line_num = _text_line_count(
            self._text, int(self._note_width / char_width)
        )
        self.setMinimumHeight(33 + 18 * line_num)

    def resizeEvent(self, event):
        self.note_editor.resize(
            self.size()
        )  # change the size when ported to boxlayout changed
        self._note_width = self.size().width()
        self._text = self.note_editor.toPlainText()
        self.text_resize(self._char_conv)
        super().resizeEvent(event)


class NoteTitle(NoteBase):
    colorChangeSig = Signal(dict)
    delListSig = Signal()

    def __init__(self, text, col, parent=None):

        self._char_conv = 9
        super().__init__(text, col, parent)
        self.setStyleSheet(STYLETITLE)

        self.btnn_init()

    def btnn_init(self):

        self.cbtn = QPushButton('', self)
        self.cbtn.setFlat(True)
        self.cbtn.setStyleSheet('color: black; border: none;')
        self.cbtn.resize(10, 10)

        menu = QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | Qt.NoDropShadowWindowHint)
        colorMenu = menu.addMenu('Color Scheme')
        colorMenu.setWindowFlags(
            colorMenu.windowFlags() | Qt.NoDropShadowWindowHint
        )
        for color in COLOR_DICT.keys():
            colorAction = colorMenu.addAction(color)
            colorAction.triggered.connect(
                partial(self.change_colcolor, color=color)
            )

        delAction = menu.addAction('Delete Column')
        delAction.triggered.connect(self.delete_list)

        self.cbtn.setMenu(menu)

    def change_colcolor(self, color):
        print("this is col for color", self._col)
        self.colorChangeSig.emit({'col': self._col, 'color': color})

    def delete_list(self):
        reply = QMessageBox.question(
            self,
            'Delete Column',
            "Are you sure to delete column, this cannot be reversed?",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if reply == QMessageBox.Yes:
            self.delListSig.emit()
        else:
            pass

    def resizeEvent(self, event):
        self.cbtn.move(self.size().width() - 20, 10)
        super().resizeEvent(event)


class NoteBlock(NoteBase):
    def __init__(self, text, col, color_list, parent=None):

        self._char_conv = 7.8
        super().__init__(text, col, parent)

        self._color_list = color_list
        self._tncol = len(self._color_list)  # total number of columns
        self.setStyleSheet(COLOR_DICT[color_list[col]])
        self.design_init()

    def design_init(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(2)
        self.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(False)

        self.setCursor(
            Qt.ClosedHandCursor
        )  # open hand cursor seems very big and annoying

    def para_changed(self, color_list):
        self._color_list = color_list
        self._tncol = len(color_list)

    def mousePressEvent(self, event):
        self.__ori_pos = self.pos()
        self.__mousePressPos = None
        self.__mouseMovePos = None

        if event.button() == Qt.LeftButton:
            # self.setCursor(Qt.ClosedHandCursor)
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

            self.shadow.setEnabled(True)
            self.raise_()
            self.note_editor.clearFocus()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            self.__newPos = self.mapFromGlobal(currPos + diff)
            self.move(self.__newPos)

            self.__mouseMovePos = globalPos

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # self.setCursor(Qt.OpenHandCursor)
        if self.__mousePressPos is not None:
            # moved = event.globalPos() - self.__mousePressPos

            if not hasattr(self, '__newPos'):
                self.__newPos = self.pos()

            total_width = (self._note_width + 6) * (
                self._tncol + 1
            ) + 54  # 6 for spacing, 30 for each sides add additonal to cover the whole board
            bound = list(range(30, total_width, self._note_width + 6))

            for col_n in range(self._tncol + 1):
                if (
                    self.__newPos.x() < bound[col_n] - self._note_width / 3.3
                ):  # pass approximately 30% of the tile
                    new_col = col_n - 1
                    break

            if self._col != new_col:
                self.noteMovedSig.emit(new_col)
                self._col = new_col
                self.setStyleSheet(COLOR_DICT[self._color_list[new_col]])
                self.noteChangeSig.emit()
            else:
                self.move(self.__ori_pos)

            self.shadow.setEnabled(False)

        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):

        menu = QMenu(self)
        delAction = menu.addAction('Delete')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is not None and action == delAction:
            self.deleteLater()

        super().contextMenuEvent(event)


class ProjectInfo(QWidget):
    def __init__(self, _title='xBan Project', _time='04/11/2018', parent=None):
        super().__init__(parent)
        self._title = _title
        self._time = _time

        layout = QHBoxLayout()

        self.project_editor = QLineEdit(_title, self)
        # # self.project_editor.setDocument(self.project_doc)
        self.project_editor.setFixedHeight(35)
        self.project_editor.setStyleSheet(STYLEPROJECT)

        self.project_editor.textChanged.connect(self.title_changed)
        self.project_editor.textChanged.connect(self.time_changed)

        self.project_time = QLabel(f'Last Updated: {_time}', self)
        self.project_time.setStyleSheet(STYLETIME)

        layout.addWidget(self.project_editor)
        layout.addWidget(self.project_time)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.show()

    def time_changed(self):
        self._time = time.strftime('%X %x %Z')
        self.project_time.setText(f'Last Updated: {self._time}')

    def title_changed(self):
        self._title = self.project_editor.text()


class NewTileBtn(QPushButton):
    def __init__(self, text, col, parent=None):
        super().__init__(text, parent)

        self._col = col


class BanBoard(QWidget):

    mousePressedSig = Signal()
    projEditedSig = Signal()
    scrollSig = Signal(list)
    paraChangedSig = Signal(list)
    colChangedSig = Signal(int)

    def __init__(self, proj_path, parent=None):
        super().__init__(parent)

        self._proj_path = proj_path
        self.initBasicLayout()
        self._framewidth = 1120

        if os.stat(proj_path).st_size == 0:
            print('Empty, skip board GUI')
            pass
        else:
            with open(proj_path, 'r') as project_file:
                xban_proj = json.load(project_file)
            self.initProj(xban_proj)

    def initBasicLayout(self):
        self.VL_Board = QVBoxLayout()
        self.VL_Board.setContentsMargins(0, 0, 0, 0)

        self.HL_info = QHBoxLayout()  # Project Name, Last update
        self.HL_info.setContentsMargins(0, 0, 0, 0)

        self.HL_title = QHBoxLayout()  # Project titles
        self.HL_title.setContentsMargins(30, 0, 30, 12)

        self.HL_content = QHBoxLayout()  # Project note tiles
        self.HL_content.setContentsMargins(30, 0, 30, 12)

        self.VL_Board.addLayout(self.HL_info, 1)
        self.VL_Board.addLayout(self.HL_title, 1)
        self.VL_Board.addLayout(self.HL_content, 100)
        self.setLayout(self.VL_Board)

    # Initate Project ------------------------------------------
    def initProj(self, proj_data):
        """Ability to completely restart the GUI
            proj_file is the json file for initiation
        """
        self._proj_info = proj_data[
            'project_info'
        ]  # this info is stored class-wide
        proj_title = proj_data['project_title']
        proj_content = proj_data['project_content']

        # Header Info Layout ----------------------------------------
        self.projinfo = ProjectInfo(
            self._proj_info['project_name'],
            self._proj_info['last_update'],
            self,
        )
        self.projEditedSig.connect(self.projinfo.time_changed)
        self.HL_info.addWidget(self.projinfo)
        self._colcolor = self._proj_info['colcolor']

        # Title Layout -------------------------------------------------------
        for note_title in proj_title:
            titleObj = NoteTitle(note_title['content'], note_title['col'])
            self.HL_title.addWidget(titleObj)
            titleObj.noteChangeSig.connect(self.proj_edited)
            titleObj.colorChangeSig.connect(self.col_color_change)
            titleObj.delListSig.connect(self.del_col)

        # Content Layout ------------------------------------------------------
        self._tnum_col = len(proj_title)
        for ncol in range(
            self._tnum_col
        ):  # set up the vertical layouts based on the length of the title
            VL = QVBoxLayout()
            VL.setAlignment(Qt.AlignTop)
            VL.setSpacing(6)
            self.HL_content.addLayout(VL)

        self.noteVL_list = []
        for nlayout in range(self.HL_content.count()):
            self.noteVL_list.append(self.HL_content.itemAt(nlayout).layout())

        # Content Tiles ------------------------------------------------------
        for note in proj_content:
            _ncol = note['col']

            noteObj = NoteBlock(note['content'], _ncol, self._colcolor)
            noteObj.noteChangeSig.connect(self.proj_edited)
            noteObj.noteMovedSig.connect(self.note_moved_signal)
            noteObj.setStyleSheet(COLOR_DICT[self._colcolor[_ncol]])
            self.noteVL_list[_ncol].insertWidget(note['col_index'], noteObj)
            self.paraChangedSig.connect(noteObj.para_changed)

        for ncol in range(len(self.noteVL_list)):
            plusbtn = NewTileBtn('+', ncol, self)
            plusbtn.setFixedHeight(30)
            plusbtn.clicked.connect(self.add_notes)
            self.noteVL_list[ncol].addWidget(plusbtn)

    def note_moved_signal(self, ncol):
        note_sender = self.sender()
        num_widget = self.noteVL_list[ncol].count()
        self.noteVL_list[ncol].insertWidget(num_widget - 1, note_sender)
        self.tab_reorder(note_sender, ncol, num_widget)

        self.scroll_action(note_sender, ncol, num_widget)

    def scroll_action(self, note_obj, ncol, num_widget):

        top = self.noteVL_list[ncol].itemAt(num_widget).widget().pos().y()
        height = note_obj.size().height()
        maxh = self.size().height()
        print('height', [top, height, maxh])
        self.scrollSig.emit([top, height, maxh])

    def add_notes(self):
        ncol = self.sender()._col
        noteObj = NoteBlock('', ncol, self._colcolor, self)
        noteObj.setStyleSheet(COLOR_DICT[self._colcolor[ncol]])
        noteObj.noteMovedSig.connect(self.note_moved_signal)
        noteObj.noteChangeSig.connect(self.proj_edited)
        noteObj.note_editor.setFocus()

        num_widget = self.noteVL_list[ncol].count()
        self.noteVL_list[ncol].insertWidget(num_widget - 1, noteObj)
        self.paraChangedSig.connect(noteObj.para_changed)

        self.tab_reorder(noteObj, ncol, num_widget)
        self.proj_edited()

        self.scroll_action(noteObj, ncol, num_widget)

    def tab_reorder(self, widgetObj, n_col, n_widget):

        while n_col >= 0:
            if n_widget >= 2:
                self.setTabOrder(
                    self.noteVL_list[n_col]
                    .itemAt(n_widget - 2)
                    .widget()
                    .note_editor,
                    widgetObj.note_editor,
                )
                break
            else:
                n_col -= 1
                n_widget = self.noteVL_list[n_col].count()
        if n_col == -1:  # if not link the last one of the title
            self.setTabOrder(
                self.HL_title.itemAt(self.HL_title.count() - 1)
                .widget()
                .note_editor,
                widgetObj.note_editor,
            )

    def proj_edited(self):
        self.projEditedSig.emit()

    def col_color_change(self, change_dict):

        for block in self.col_map(change_dict['col'])[
            :-1
        ]:  # get rid of the btn at the end
            block.setStyleSheet(COLOR_DICT[change_dict['color']])
        self._colcolor[change_dict['col']] = change_dict['color']
        self.paraChangedSig.emit(self._colcolor)
        self.projEditedSig.emit()

    def col_map(self, col):

        content_list = []
        for col_index in range(self.noteVL_list[col].count()):
            content_list.append(
                self.noteVL_list[col].itemAt(col_index).widget()
            )
        return content_list

    def del_col(self):

        delwidget = self.sender()
        ncol = delwidget._col

        for n_col in range(ncol + 1, self._tnum_col):
            self.HL_title.itemAt(n_col).widget()._col -= 1
            for tiles in self.col_map(n_col):
                print(tiles._col)
                tiles._col -= 1

        self.HL_title.removeWidget(delwidget)

        if ncol + 1 < self._tnum_col and ncol > 0:
            self.setTabOrder(
                self.HL_title.itemAt(ncol - 1).widget().note_editor,
                self.HL_title.itemAt(ncol).widget().note_editor,
            )

        for tile in self.col_map(ncol):
            tile.deleteLater()

        self.HL_content.removeItem(self.noteVL_list[ncol])
        delwidget.deleteLater()
        del self.noteVL_list[ncol]
        del self._colcolor[ncol]

        self._tnum_col -= 1

        # Reset the value of col for each widget
        self.paraChangedSig.emit(self._colcolor)
        self.colChangedSig.emit(-1)

    def add_col(self):

        # Add title line -------------------------------------------------
        ncol = self._tnum_col
        titleObj = NoteTitle('New List', ncol)
        self.HL_title.addWidget(titleObj)
        titleObj.noteChangeSig.connect(self.proj_edited)
        titleObj.colorChangeSig.connect(self.col_color_change)
        titleObj.delListSig.connect(self.del_col)
        self.setTabOrder(
            self.HL_title.itemAt(ncol - 1).widget().note_editor,
            titleObj.note_editor,
        )

        # Add content layout ------------------------------------------------
        VL = QVBoxLayout()
        VL.setAlignment(Qt.AlignTop)
        VL.setSpacing(6)
        self.HL_content.addLayout(VL)

        # Add content (btn) -------------------------------------------------
        plusbtn = NewTileBtn('+', ncol, self)
        plusbtn.setMinimumHeight(25)
        plusbtn.clicked.connect(self.add_notes)
        VL.addWidget(plusbtn)

        # Update Properties ------------------------------------------------
        self.noteVL_list.append(VL)
        self._colcolor.append('blue')
        self._tnum_col += 1

        # Signal to change the total column count
        self.paraChangedSig.emit(self._colcolor)
        self.colChangedSig.emit(1)

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()

        if focused_widget is not None:  # or is an instance of QTextEdit
            focused_widget.clearFocus()
            self.mousePressedSig.emit()

        super().mousePressEvent(event)


class XBan(QMainWindow):
    def __init__(self, proj_path):
        super().__init__()
        if proj_path and proj_path not in OPENED_DICT:
            OPENED_DICT[proj_path] = self  # add a dict of the object
        print('Opened Projects', OPENED_DICT.keys())

        self._proj_path = proj_path

        self.stbar = QStatusBar()
        self.stbar.setSizeGripEnabled(False)
        self.stbar.setMaximumHeight(25)

        self.initMenu()
        self.initproject(proj_path)

        self.setWindowTitle('xBan')
        self.setStyleSheet(XSTYLE)
        self.move_center()
        self.show()

    def initproject(self, file_path):

        if not file_path:
            print('No start Project')
            self.bg_image()
        else:
            self.board = BanBoard(file_path, self)
            self.board.mousePressedSig.connect(self.clear_msg)
            self.board.projEditedSig.connect(self.note_changed)
            self.board.scrollSig.connect(self.scroll)
            self.board.colChangedSig.connect(self.change_size)

            self.boardArea = QScrollArea(self)
            self.boardArea.setWidget(self.board)
            self.boardArea.setWidgetResizable(True)
            self.resize(
                360 * self.board._tnum_col + 40, 640
            )  # expand the size based on the board num
            self.setCentralWidget(self.boardArea)

            # add status bar btn -------------------------------------
            addcol_btn = QPushButton('Add New Column', self)
            addcol_btn.setFlat(True)
            addcol_btn.setStyleSheet(
                "font-size:10px; color: #494949; margin-right: 10px;"
            )
            addcol_btn.setMinimumHeight(20)
            addcol_btn.pressed.connect(self.board.add_col)

            self.stbar.addPermanentWidget(addcol_btn)
            self.setStatusBar(self.stbar)

    def scroll(self, sig_pos):
        # There seems to be a bug regarding this issue, it does not go all the
        # way down
        bar = self.boardArea.verticalScrollBar()
        pre_move = bar.value()
        win_size = self.centralWidget().size().height()

        if sig_pos[0] < pre_move:
            bar.setValue(sig_pos[0] - 20)
        elif sig_pos[0] + sig_pos[1] - pre_move > win_size:
            bar.setValue(sig_pos[0] + sig_pos[1] + 40 - win_size)

    def initMenu(self):
        self.setMinimumWidth(800)
        self.resize(1120, 640)
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu('File')

        new_proj = QAction('New Project', self)
        new_proj.setShortcut('Ctrl+N')
        new_proj.triggered.connect(self.start_project)

        open_proj = QAction('Open Project', self)
        open_proj.setShortcut('Ctrl+O')
        open_proj.triggered.connect(self.open_project)

        save_proj = QAction('Save Project', self)
        save_proj.setShortcut('Ctrl+S')
        save_proj.triggered.connect(self.save_proj)

        filemenu.addAction(new_proj)
        filemenu.addAction(open_proj)
        filemenu.addAction(save_proj)

    def move_center(self):  # show window in the middle
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def bg_image(self):
        image_style = '''
            background-image: url('{}') 100px 100px stretch stretch; 
            background-repeat: no-repeat; 
            background-position: center center;
            '''.format(
            _href_link_path(os.path.join(DIR_PATH, 'files', 'xBanBG.png'))
        )

        background_image = QFrame(self)
        background_image.setStyleSheet(image_style)
        self.setCentralWidget(background_image)

    def note_changed(self):
        self.stbar.showMessage('Note Changed')

    def clear_msg(self):
        self.stbar.clearMessage()

    def save_proj(self):
        title_list = []
        for ncol in range(self.board.HL_title.count()):
            tile = self.board.HL_title.itemAt(ncol).widget()
            title_list.append(
                {'content': tile._text, 'col': tile._col, 'comments': ''}
            )

        note_list = []
        for noteVL in self.board.noteVL_list:
            for col_index in range(noteVL.count() - 1):
                tile = noteVL.itemAt(col_index).widget()
                note_list.append(
                    {
                        'content': tile._text,
                        'col': tile._col,
                        'col_index': col_index,
                        'comments': '',
                    }
                )

        xban_proj_dict = {
            'project_info': {
                'project_name': self.board.projinfo._title,
                'last_update': self.board.projinfo._time,
                'colcolor': self.board._colcolor,
            },
            'project_title': title_list,
            'project_content': note_list,
        }

        with open(self._proj_path, 'w+') as project_file:
            json.dump(xban_proj_dict, project_file)

        self.stbar.showMessage('Project Saved')

    def closeEvent(self, event):
        if hasattr(self, 'board'):
            self.save_proj()

        if self._proj_path and self._proj_path in OPENED_DICT:
            OPENED_DICT.pop(self._proj_path)
            print('Opened Projects', OPENED_DICT.keys())

        super().closeEvent(event)

    def start_project(self):
        projpath = QFileDialog.getSaveFileName(
            self,
            'Start Project',
            os.path.expanduser('~/Desktop'),
            ('xBan Projects (*.xban)'),
        )[0]
        projname = os.path.splitext(os.path.basename(projpath))[0]
        xban_default = {
            'project_info': {
                'project_name': projname,
                'last_update': time.strftime('%X %x %Z'),
                'colcolor': ['red', 'yellow', 'green'],
            },
            'project_title': [
                {'content': 'To-Do', 'col': 0, 'comments': ''},
                {'content': 'In Process', 'col': 1, 'comments': ''},
                {'content': 'Done', 'col': 2, 'comments': ''},
            ],
            'project_content': [
                {'content': '', 'col': 0, 'col_index': 1, 'comments': ''}
            ],
        }
        if not projpath:
            pass
        else:
            if not projpath.endswith('.xban'):
                projpath = f'{projpath}.xban'
            with open(projpath, 'w+') as new_xban:
                json.dump(xban_default, new_xban)
            self.new_ban_win(projpath)

    def open_project(
        self
    ):  # need to limit the file options avoid open the same board, bring it up to focus instead
        projpath = QFileDialog.getOpenFileName(
            self,
            'Open Project',
            os.path.expanduser('~/Desktop'),
            ('xBan Projects (*.xban)'),
        )[0]
        # self.open_new_ban.emit()
        if not projpath:
            pass
        elif not projpath.endswith('.xban'):
            print('not a correct file')
        elif projpath in OPENED_DICT:
            OPENED_DICT[projpath].show()
        else:
            self.new_ban_win(projpath)

    def new_ban_win(self, file_path):

        if self.centralWidget() is None or not isinstance(
            self.centralWidget(), QScrollArea
        ):
            self._proj_path = (
                file_path
            )  # update the path to the current window
            self.initproject(file_path)
        else:
            print('start new window')
            self.newWIN = XBan(file_path)
            self.newWIN.show()

    def change_size(self, change_msg):
        self.resize(
            self.size().width() + change_msg * (350), self.size().height()
        )


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setWindowIcon(QIcon(os.path.join(DIR_PATH, 'files', 'xBanUI.png')))
    xban_gui = XBan(XBANPATH)
    app.setStyle('Fusion')
    sys.exit(app.exec_())
