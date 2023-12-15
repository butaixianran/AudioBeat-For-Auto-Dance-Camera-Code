# -*- coding: UTF-8 -*-
# Import the wxPython package.
import wx
import beat_helper as bh


lang = "en"

class UiUtil:


    def Msg(msg):
        wx.MessageBox(msg, "Confirm", wx.OK|wx.ICON_INFORMATION)

class MainFrame(wx.Frame):
    """
    Main Frame
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # UI
        # 音频类型标签
        self.audio_type_lbl = wx.StaticText(pnl, label="Audio Type:")
        # 音频类型选项
        self.audio_type = wx.ComboBox(pnl, id=wx.ID_ANY, value="Song", choices =bh.audio_types, style=wx.CB_READONLY)


        # 读取音频按钮
        self.load_audio_btn = wx.Button(pnl, id=wx.ID_ANY, label="Select Audio")
        # 显示音频路径
        self.audio_path_lbl = wx.StaticText(pnl, label="No Audio")

        # 读取人声按钮
        self.load_vocal_btn = wx.Button(pnl, id=wx.ID_ANY, label="Select Vocal")
        # 显示人声路径
        self.vocal_path_lbl = wx.StaticText(pnl, label="No Vocal")

        # 读取音乐按钮
        self.load_music_btn = wx.Button(pnl, id=wx.ID_ANY, label="Select Music")
        # 显示音乐路径
        self.music_path_lbl = wx.StaticText(pnl, label="No Music")

        # 生成节拍按钮
        gen_beat_btn = wx.Button(pnl, id=wx.ID_ANY, label="Generate Beats")

        # 选项checkbox
        # self.export_click_chk = wx.CheckBox(pnl, id=wx.ID_ANY, label="Export Beat Audio")
        # self.use_ffmpeg_chk = wx.CheckBox(pnl, id=wx.ID_ANY, label="Installed ffmpeg")

        # 用于写入log的多行文本框，用户只读
        self.log_txt = wx.TextCtrl(pnl, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # --Bind 绑定--
        # 读取音频按钮
        self.load_audio_btn.Bind(wx.EVT_BUTTON, self.OnSelectAudio)
        self.load_vocal_btn.Bind(wx.EVT_BUTTON, self.OnSelectVocal)
        self.load_music_btn.Bind(wx.EVT_BUTTON, self.OnSelectMusic)
        # 生成按钮
        gen_beat_btn.Bind(wx.EVT_BUTTON, self.GenBeat)
        
        # checkbox
        # self.export_click_chk.Bind(wx.EVT_CHECKBOX,self.OnExportClickChecked)

        # 音频类型
        self.audio_type.Bind(wx.EVT_COMBOBOX, self.OnAudioTypeSelect)


        # checkbox行布局
        # chk_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # chk_sizer.Add(self.export_click_chk,flag=wx.LEFT | wx.LEFT | wx.RIGHT, border=5)
        # chk_sizer.Add(self.use_ffmpeg_chk,flag=wx.LEFT | wx.LEFT | wx.RIGHT, border=5)

        # 音乐类型布局
        combo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        combo_sizer.Add(self.audio_type_lbl, flag=wx.ALL, border=5)
        combo_sizer.Add(self.audio_type, flag=wx.ALL, border=5)


        # 主布局
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # 音频类型
        self.sizer.Add(combo_sizer,flag=wx.CENTER | wx.ALL, border=5)

        # 添加音频按钮
        self.sizer.Add(self.load_audio_btn,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(self.audio_path_lbl,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)
        
        # 添加人声按钮
        self.sizer.Add(self.load_vocal_btn,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(self.vocal_path_lbl,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)

        # 添加音乐按钮
        self.sizer.Add(self.load_music_btn,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(self.music_path_lbl,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)

        # 添加checkbox行
        # sizer.Add(chk_sizer,flag=wx.LEFT | wx.ALL, border=5)

        # 添加生成按钮
        self.sizer.Add(gen_beat_btn,flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)
        # 添加log窗口
        self.sizer.Add(self.log_txt, proportion=1, flag=wx.CENTER | wx.EXPAND | wx.ALL, border=5)


        pnl.SetSizer(self.sizer)

        # 提供控件，用于写log
        bh.log_ctrl = self.log_txt



    # 打开音频文件
    def OnSelectAudio(self, event):

        wildcard = "Audio (*.wav,*.mp3)|*.wav;*.mp3"

        with wx.FileDialog(self, "Choose Audio", wildcard=wildcard,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                # 清空log
                self.log_txt.Clear()
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            bh.audio_path = fileDialog.GetPath()
            self.audio_path_lbl.SetLabel(bh.audio_path)

            # 清空log
            self.log_txt.Clear()

    # 打开人声文件
    def OnSelectVocal(self, event):

        wildcard = "Vocal (*.wav,*.mp3)|*.wav;*.mp3"

        with wx.FileDialog(self, "Choose Vocal", wildcard=wildcard,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                # 清空log
                self.log_txt.Clear()
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            bh.vocal_path = fileDialog.GetPath()
            self.vocal_path_lbl.SetLabel(bh.vocal_path)

            # 清空log
            self.log_txt.Clear()


    # 打开音乐文件
    def OnSelectMusic(self, event):

        wildcard = "Music (*.wav,*.mp3)|*.wav;*.mp3"

        with wx.FileDialog(self, "Choose Music", wildcard=wildcard,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                # 清空log
                self.log_txt.Clear()
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            bh.music_path = fileDialog.GetPath()
            self.music_path_lbl.SetLabel(bh.music_path)

            # 清空log
            self.log_txt.Clear()



    # 勾选是否输出节拍音频
    # def OnExportClickChecked(self, event):
    #     bh.is_export_click_audio = self.export_click_chk.GetValue()


    # 选择音频类型
    def OnAudioTypeSelect(self, event):
        bh.audio_type = self.audio_type.GetStringSelection()

        # 根据类型，判断显示隐藏哪些按钮
        if bh.audio_type == bh.audio_types[-1]:
            # 同时使用 vocal 和 music
            # 隐藏audio按钮
            self.load_audio_btn.Hide()
            self.audio_path_lbl.Hide()
            # 显示其他两个按钮
            self.load_vocal_btn.Show()
            self.vocal_path_lbl.Show()

            self.load_music_btn.Show()
            self.music_path_lbl.Show()
        else:
            # 只显示audio按钮
            self.load_audio_btn.Show()
            self.audio_path_lbl.Show()
            # 隐藏其他两个按钮
            self.load_vocal_btn.Hide()
            self.vocal_path_lbl.Hide()

            self.load_music_btn.Hide()
            self.music_path_lbl.Hide()


        self.sizer.Layout()
        # self.Fit()



    # 初始化控件状态
    def StatusInit(self):
        # 只显示audio按钮
        self.load_audio_btn.Show()
        self.audio_path_lbl.Show()
        # 隐藏其他两个按钮
        self.load_vocal_btn.Hide()
        self.vocal_path_lbl.Hide()

        self.load_music_btn.Hide()
        self.music_path_lbl.Hide()

        self.sizer.Layout()
        # self.Fit()


    # 生成节拍
    def GenBeat(self, event):

        bh.gen_beat()
        if bh.error != "":
            UiUtil.Msg(bh.error)



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MainFrame(None, title='Audio Beat', size=wx.Size(480,480))
    frm.SetIcon(wx.Icon("audio_beat.ico"))
    frm.Centre()
    frm.Show()
    frm.StatusInit()
    app.MainLoop()

