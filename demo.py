from enum import Enum
import wx
import wx.lib.agw.ultimatelistctrl as ULC
import wx.adv as ADV
import json
import sys, os
import ctypes

yes_no_choice = ["是", "否"]
challenge_text = []
challenge_score = []
unique_challenge_text = []
unique_challenge_score = []
boss_score = []
sentinel_base_score = 0
boss_selected = [0] * 12
boss_image_names = [
    "boss_4",
    "boss_3",
    "boss_2",
    "boss_1",
    "boss_4",
    "boss_3",
    "boss_2",
    "collection_1",
    "collection_2",
    "collection_3",
    "collection_4",
    "collection_5"
]
boss_images = []
boss_text = [
    "迈入永恒",
    "　哨兵　",
    "虚无之偶",
    "深寒造像",
    "时光之沙",
    "　园丁　",
    "萨米之熵",
    "无垠赠礼",
    "维度流质",
    "坍缩之种",
    "空间碎片",
    "深度灼痕"
]
boss_extra_text = "　通关\n"
boss_base_text = "　进入\n"
collection_extra_text = "　持有\n"
two_ending = 0
three_ending = 0
both_three_four_ending = 0
battle_text = [
    "关卡类型",
    "关卡层数",
    "关卡名称",
    "是否无漏",
    "是否持有路网",
    "是否有捕猎惩罚",
    "特殊加分"
]
battle_isbanned = [False, True, True, False, False, False, True]
battle_types = ["紧急作战", "特殊作战"]
battle_levels = ["一层", "二层", "三层", "四层", "五层", "六层"]
battle_names = [
    ["死囚之夜", "度假村冤魂", "苔手", "待宰的兽群", "事不过四"],
    ["没有尽头的路", "低空机动", "违和", "幽影与鬼魅", "虫虫别回头", "还之彼身"],
    ["冰海疑影", "狡兽九窟", "弄假成真", "饥渴祭坛", "咫尺天涯", "思维折断", "恃强凌弱"],
    ["坍缩体的午后", "公司纠葛", "以守代攻", "大迁徙", "禁区", "应用测试", "杂音干扰", "冰凝之所"],
    ["人造物狂欢节", "乐理之灾", "亡者行军", "本能污染", "求敌得敌", "混乱的表象", "何处无山海", "生人勿近"],
    ["霜与沙", "生灵的终点"]
]
battle_special_names = ["呼吸", "大地醒转", "夺树者", "黄沙幻境", "天途半道", "惩罚", "豪华车队", "英雄无名", "正义使者", "亘古仇敌"]
battle_score = dict()
battle_special_score = dict() # [无漏，非无漏]
special_extra_title = dict()
special_extra_score = dict()
friend_link = [
    ("DPS计算器", "https://viktorlab.cn/akdata/dps/"),
    ("PRTS MAP", "https://mapcn.ark-nights.com/")
]
relative_link = [
    ("UP主应援计划", "https://www.bilibili.com/blackboard/activity-oc3CbeDPRR.html")
]
credits_link = {
    "程序：" : [
        ("_noname", "https://space.bilibili.com/22275485")
    ],
    "美术：" : [
        ("里雪りあ", "https://space.bilibili.com/1684845011")
    ],
    "规则：" : [

    ]
}

class Unit(Enum):
    BASE = 0
    ZONG = 1

unit = Unit.BASE
config = 0
config_path = [
    "settings/demo.json",
    "settings/demo2.json"
]

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if os.name == 'nt':
    GDI32 = ctypes.WinDLL('gdi32')
    GDI32.AddFontResourceExW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]

    font_path = resource_path('font/Novecento WideMedium.otf')
    GDI32.AddFontResourceExW(font_path, 0x10, None)

def init_settings():
    global boss_score, sentinel_base_score, battle_score, battle_special_score, two_ending, three_ending, both_three_four_ending
    with open(resource_path(config_path[config]), 'r', encoding='utf-8') as file:
        data = json.load(file)
        challenge_text.clear()
        challenge_score.clear()
        unique_challenge_text.clear()
        unique_challenge_score.clear()
        special_extra_title.clear()
        special_extra_score.clear()

        mp = data.get("challenge", dict())
        for key, value in mp.items():
            challenge_text.append(key)
            challenge_score.append(value)
        mp = data.get("unique_challenge", dict())
        for key, value in mp.items():
            unique_challenge_text.append(key)
            unique_challenge_score.append(value)
        boss_score = data.get("boss_score", [0] * 12)
        if len(boss_score) != 12:
            return False
        sentinel_base_score = data.get("sentinel_base_score", 0)
        two_ending = data.get("two_ending", 0)
        three_ending = data.get("three_ending", 0)
        both_three_four_ending = data.get("both_three_four_ending", 0)
        battle_score = data.get("battle_score", dict())
        battle_special_score = data.get("battle_special_score", dict())
        mp = data.get("special_extra", dict())
        for key, value in mp.items():
            lst = []
            for key1, value1 in value.items():
                lst.append(key1)
                special_extra_score[key1] = value1
            special_extra_title[key] = lst
    
    return True

class SettingsPanel(wx.Panel):
    def __init__(self, parent):
        super(SettingsPanel, self).__init__(parent, style=wx.BORDER_NONE)

        self.SetBackgroundColour("#F6F6F6")
        self.settings_image = wx.Image(resource_path(f"images/back.png"), wx.BITMAP_TYPE_ANY)
        self.settings_image = self.settings_image.Scale(32, 32)
        self.settings_image = wx.Bitmap(self.settings_image)
        self.settings_icon = wx.StaticBitmap(self, bitmap=self.settings_image, pos=(70, 70))
        self.settings_icon.Bind(wx.EVT_LEFT_UP, self.on_back_clicked)

        text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")
        self.settings_unit_label = wx.StaticText(self, label="分数单位", pos=(100, 150))
        self.settings_unit_label.SetFont(text_font)
        self.settings_unit_choice = wx.Choice(self, choices=["分", "棕"], pos=(200, 150), size=(100, 30))
        self.settings_unit_choice.SetSelection(unit.value)
        self.settings_unit_choice.SetFont(text_font)
        self.settings_unit_choice.Bind(wx.EVT_CHOICE, self.on_unit_choice)

        self.settings_config_label = wx.StaticText(self, label="分数配置", pos=(100, 190))
        self.settings_config_label.SetFont(text_font)
        self.settings_config_choice = wx.Choice(self, choices=["标准配置", "测试配置"], pos=(200, 190), size=(100, 30))
        self.settings_config_choice.SetSelection(config)
        self.settings_config_choice.SetFont(text_font)
        self.settings_config_choice.Bind(wx.EVT_CHOICE, self.on_config_choice)
        self.last_config = config

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush("#F2F2F2"))
        dc.SetPen(wx.Pen("#000000", 0))
        dc.DrawRectangle(0, 0, self.GetSize().GetWidth(), self.GetSize().GetHeight())

    def on_unit_choice(self, event):
        global unit
        unit = Unit(self.settings_unit_choice.GetSelection())

    def on_config_choice(self, event):
        global config
        config = self.settings_config_choice.GetSelection()

    def on_back_clicked(self, event):
        if self.last_config != config:
            self.last_config = config
            self.Parent.close_settings(True)
        else:
            self.Parent.close_settings(False)

class InformationPanel(wx.Panel):
    def __init__(self, parent):
        super(InformationPanel, self).__init__(parent, style=wx.BORDER_NONE)

        self.SetBackgroundColour("#F6F6F6")
        self.settings_image = wx.Image(resource_path(f"images/back.png"), wx.BITMAP_TYPE_ANY)
        self.settings_image = self.settings_image.Scale(32, 32)
        self.settings_image = wx.Bitmap(self.settings_image)
        self.settings_icon = wx.StaticBitmap(self, bitmap=self.settings_image, pos=(70, 70))
        self.settings_icon.Bind(wx.EVT_LEFT_UP, self.on_back_clicked)

        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Microsoft YaHei UI")
        text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")
        self.friend_title_label = wx.StaticText(self, label="友情链接", pos=(200, 170))
        self.friend_title_label.SetFont(title_font)
        self.links = []
        posx, posy = 200, 220
        for i in range(len(friend_link)):
            link = ADV.HyperlinkCtrl(self, id=wx.ID_ANY, label=friend_link[i][0], url=friend_link[i][1], pos=(posx, posy))
            link.SetFont(text_font)
            link.SetBackgroundColour("#F2F2F2")
            link.SetSize(wx.Size(link.GetTextExtent(friend_link[i][0])))
            self.links.append(link)
            posy += 30

        self.relative_title_label = wx.StaticText(self, label="相关链接", pos=(500, 170))
        self.relative_title_label.SetFont(title_font)
        posx, posy = 500, 220
        for i in range(len(relative_link)):
            link = ADV.HyperlinkCtrl(self, id=wx.ID_ANY, label=relative_link[i][0], url=relative_link[i][1], pos=(posx, posy))
            link.SetFont(text_font)
            link.SetBackgroundColour("#F2F2F2")
            link.SetSize(wx.Size(link.GetTextExtent(relative_link[i][0])))
            self.links.append(link)
            posy += 30

        self.credit_title_label = wx.StaticText(self, label="制作人员", pos=(800, 170))
        self.credit_title_label.SetFont(title_font)
        posy = 220
        self.credit_label = []
        for key, value in credits_link.items():
            posx = 800
            label = wx.StaticText(self, label=key, pos=(posx, posy))
            label.SetFont(text_font)
            posx += label.GetSize().GetWidth() + 5
            self.credit_label.append(label)

            for val in value:
                link = ADV.HyperlinkCtrl(self, id=wx.ID_ANY, label=val[0], url=val[1], pos=(posx, posy))
                link.SetFont(text_font)
                link.SetBackgroundColour("#F2F2F2")
                link.SetSize(wx.Size(link.GetTextExtent(val[0])))
                posy += 30
                self.links.append(link)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush("#F2F2F2"))
        dc.SetPen(wx.Pen("#000000", 0))
        dc.DrawRectangle(0, 0, self.GetSize().GetWidth(), self.GetSize().GetHeight())

    def on_back_clicked(self, event):
        self.Parent.close_information()

class CalcPanel(wx.Panel):
    def __init__(self, parent):
        super(CalcPanel, self).__init__(parent, style=wx.BORDER_NONE)

        self.SetBackgroundColour("#F6F6F6")
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.is_mouse_down = False
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Microsoft YaHei UI")
        text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")
        final_font = wx.Font(35, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Novecento Wide Medium")
        final_unit_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")
        bigger_text_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")
        bold_text_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Microsoft YaHei UI")
        self.text_font = text_font
        self.button_text_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft YaHei UI")

        self.settings_image = wx.Image(resource_path(f"images/settings.png"), wx.BITMAP_TYPE_ANY)
        self.settings_image = self.settings_image.Scale(32, 32)
        self.settings_image = wx.Bitmap(self.settings_image)
        self.settings_icon = wx.StaticBitmap(self, bitmap=self.settings_image, pos=(1080, 100))
        self.settings_icon.Bind(wx.EVT_LEFT_UP, self.on_settings_clicked)

        self.information_image = wx.Image(resource_path(f"images/information.png"), wx.BITMAP_TYPE_ANY)
        self.information_image = self.information_image.Scale(32, 32)
        self.information_image = wx.Bitmap(self.information_image)
        self.information_icon = wx.StaticBitmap(self, bitmap=self.information_image, pos=(1140, 100))
        self.information_icon.Bind(wx.EVT_LEFT_UP, self.on_information_clicked)

        self.challenge_title_label = wx.StaticText(self, label="挑战分数", pos=(63, 203))
        self.challenge_title_label.SetFont(title_font)
        self.challenge_text_ctrl = []
        self.challenge_choice = []
        self.challenge_label = []
        self.init_challenge()

        self.boss_title_label = wx.StaticText(self, label="结局分数", pos=(63, 513))
        self.boss_title_label.SetFont(title_font)
        self.boss_button = []
        posx = 69
        posy = 559
        for i in range(len(boss_selected)):
            image = wx.Bitmap(resource_path(f"images/{boss_image_names[i]}.png"), wx.BITMAP_TYPE_ANY)
            boss_images.append(image)
            button = wx.BitmapButton(self, 100 + i, image, pos=(posx, posy), size=(64, 64))
            button.Bind(wx.EVT_BUTTON, self.on_button_clicked)
            self.boss_button.append(button)
            if i % 4 == 3:
                posx = 69
                posy += 67
            else:
                posx += 72
        self.boss_image_show()

        self.battle_title_label = wx.StaticText(self, label="关卡分数", pos=(473, 203))
        self.battle_title_label.SetFont(title_font)
        self.battle_label = []
        self.battle_choice = []
        posy = 245
        for i in range(len(battle_text)):
            label = wx.StaticText(self, label=battle_text[i], pos=(477, posy + 2))
            label.SetFont(text_font)
            self.battle_label.append(label)

            choices = []
            if i == 0:
                choices = battle_types
            elif 3 <= i <= 5:
                choices = yes_no_choice
            choice = wx.Choice(self, i + 20, choices=choices, pos=(633, posy), size=(130, 26))
            if 3 <= i <= 5:
                choice.SetSelection(1)
            else:
                choice.SetSelection(-1)
            choice.SetFont(text_font)
            choice.Bind(wx.EVT_CHOICE, self.on_choice)
            self.battle_choice.append(choice)
            posy += 32
        self.confirm_button = wx.Button(self, wx.ID_ANY, label="添加", pos=(475, posy + 3), size=(290, 35))
        self.confirm_button.SetFont(bigger_text_font)
        self.confirm_button.Bind(wx.EVT_BUTTON, self.on_confirm)

        self.settlement_title_label = wx.StaticText(self, label="结算分数", pos=(473, 543))
        self.settlement_title_label.SetFont(title_font)
        self.settlement_ctrl = wx.TextCtrl(self, value="0", pos=(643, 543), size=(120, 30), style=wx.TE_CENTER)
        self.settlement_ctrl.SetFont(bigger_text_font)
        self.settlement_ctrl.SetBackgroundColour("#EFEFEF")
        self.settlement_ctrl.SetForegroundColour("#808080")
        self.settlement_ctrl.Bind(wx.EVT_TEXT, self.on_text)
        self.settlement_ctrl.Bind(wx.EVT_CHAR, self.on_char)

        self.battle_total_title_label = wx.StaticText(self, label="关卡分数一览", pos=(883, 203))
        self.battle_total_title_label.SetFont(title_font)
        self.battle_total_delete_button = wx.Button(self, label="删除", pos=(1100, 203), size=(80, 35))
        self.battle_total_delete_button.SetFont(bigger_text_font)
        self.battle_total_delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        self.list_ctrl = ULC.UltimateListCtrl(self, pos=(880, 240), size=(300, 525), agwStyle=ULC.ULC_REPORT | ULC.ULC_NO_HEADER)
        self.list_ctrl.SetBackgroundColour("#F2F2F2")
        self.list_ctrl.InsertColumn(0, "", width=175)
        self.list_ctrl.InsertColumn(1, "", wx.LIST_FORMAT_RIGHT, width=120)
        self.list_ctrl.SetFont(text_font)

        self.calc_text = wx.StaticText(self, label="0", style=wx.ALIGN_CENTER, pos=(600, 700))
        self.calc_text.SetFont(final_font)
        self.calc_text.SetForegroundColour("#B7D5F7")
        self.calc_text.SetBackgroundColour("#F2F2F2")
        self.calc_text.SetPosition((620 - self.calc_text.GetSize().GetWidth() // 2, 700 - self.calc_text.GetSize().GetHeight() // 2))
        self.calc_unit_text = wx.StaticText(self, label="", style=wx.ALIGN_CENTER, pos=(600, 700))
        self.calc_unit_text.SetFont(final_unit_font)
        self.calc_unit_text.SetForegroundColour("#B7D5F7")
        self.calc_unit_text.SetBackgroundColour("#F2F2F2")
        self.calc_title_text = wx.StaticText(self, label="总分！", style=wx.ALIGN_CENTER, pos=(600, 650))
        self.calc_title_text.SetFont(bold_text_font)
        self.calc_title_text.SetBackgroundColour("#F2F2F2")
        self.calc_title_text.SetPosition((620 - self.calc_title_text.GetSize().GetWidth() // 3, 690 - self.calc_text.GetSize().GetHeight() // 2 - self.calc_title_text.GetSize().GetHeight() // 2))
        self.calc_hint_text = wx.StaticText(self, label="", pos=(477, 738))
        self.calc_hint_text.SetFont(text_font)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush("#F2F2F2"))
        dc.SetPen(wx.Pen("#000000", 1))
        dc.DrawRoundedRectangle(60, 240, 300, 235, 7) # 挑战分数
        dc.DrawRoundedRectangle(60, 550, 300, 215, 7) # 结局分数
        dc.DrawRoundedRectangle(470, 240, 300, 275, 7) # 关卡分数
        dc.DrawRoundedRectangle(470, 620, 300, 145, 7) # 总得分
        dc.DrawRoundedRectangle(880, 240, 300, 525, 7) # 关卡分数一览

    def init_challenge(self):
        for text_ctrl in self.challenge_text_ctrl:
            text_ctrl.Destroy()
        for choice in self.challenge_choice:
            choice.Destroy()
        for label in self.challenge_label:
            label.Destroy()
        self.challenge_text_ctrl.clear()
        self.challenge_choice.clear()
        self.challenge_label.clear()
        posy = 245
        for i in range(len(challenge_text)):
            label = wx.StaticText(self, label=challenge_text[i], pos=(67, posy + 2))
            label.SetFont(self.text_font)
            self.challenge_label.append(label)

            text_ctrl = wx.TextCtrl(self, value="0", pos=(303, posy), size=(50, 26), style=wx.TE_CENTER)
            text_ctrl.SetFont(self.text_font)
            text_ctrl.SetBackgroundColour("#EFEFEF")
            text_ctrl.SetForegroundColour("#808080")
            text_ctrl.Bind(wx.EVT_TEXT, self.on_text)
            text_ctrl.Bind(wx.EVT_CHAR, self.on_char)
            self.challenge_text_ctrl.append(text_ctrl)

            posy += 32

        for i in range(len(unique_challenge_text)):
            label = wx.StaticText(self, label=unique_challenge_text[i], pos=(67, posy + 2))
            label.SetFont(self.text_font)
            self.challenge_label.append(label)

            choice = wx.Choice(self, wx.ID_ANY, choices=yes_no_choice, pos=(303, posy), size=(50, 26))
            choice.SetSelection(1)
            choice.SetFont(self.text_font)
            choice.Bind(wx.EVT_CHOICE, self.on_choice)
            self.challenge_choice.append(choice)

            posy += 32

    def on_text(self, event):
        text_ctrl = event.GetEventObject()
        value = text_ctrl.GetValue()
        if not value:
            text_ctrl.SetValue("0")
            text_ctrl.SetForegroundColour("#808080")
        else:
            if value == "0":
                text_ctrl.SetForegroundColour("#808080")
            else:
                text_ctrl.SetForegroundColour("#000000")
        self.calc()

    def on_char(self, event):
        text_ctrl = event.GetEventObject()
        current_value = text_ctrl.GetValue()
        new_char = chr(event.GetKeyCode())
        if new_char.isdigit():
            if current_value == "0":
                text_ctrl.SetValue(new_char)
                text_ctrl.SetInsertionPointEnd()
            else:
                event.Skip()
        elif event.GetKeyCode() in [wx.WXK_CONTROL_A, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_TAB]:
            event.Skip()

    def on_choice(self, event):
        id = event.GetId()
        choice = event.GetEventObject()
        if id == 20:
            self.battle_choice[1].SetSelection(-1)
            self.battle_choice[2].SetSelection(-1)
            self.battle_choice[5].SetSelection(-1)
            self.battle_choice[1].Clear()
            self.battle_choice[2].Clear()
            self.battle_choice[5].Clear()
            if choice.GetSelection() == 0:
                self.battle_choice[1].AppendItems(battle_levels)
                self.battle_choice[5].AppendItems(yes_no_choice)
                self.battle_choice[5].SetSelection(1)
            else:
                self.battle_choice[2].AppendItems(battle_special_names)
        elif id == 21:
            self.battle_choice[2].SetSelection(-1)
            self.battle_choice[2].Clear()
            self.battle_choice[2].AppendItems(battle_names[self.battle_choice[1].GetSelection()])
        elif id == 22:
            self.battle_choice[6].SetSelection(-1)
            self.battle_choice[6].Clear()
            name = self.battle_choice[2].GetStringSelection()
            if name in special_extra_title.keys():
                self.battle_choice[6].AppendItems(special_extra_title[name])

        self.calc()

    def on_button_clicked(self, event):
        button_id = event.GetId() - 100
        if button_id == 1:
            boss_selected[1] = (boss_selected[1] + 1) % 3
        else:
            boss_selected[button_id] = 2 - boss_selected[button_id]
        if boss_selected[2] + boss_selected[3] + boss_selected[6] > 2:
            boss_selected[2] = 0
            boss_selected[3] = 0
            boss_selected[6] = 0
            boss_selected[button_id] = 2
        if button_id == 0 and boss_selected[0] != 0:
            boss_selected[4] = 0
        if button_id == 4 and boss_selected[4] != 0:
            boss_selected[0] = 0
        if button_id == 1 and boss_selected[5] != 0:
            boss_selected[5] = 0
        if button_id == 5 and boss_selected[1] != 0:
            boss_selected[1] = 0
        if boss_selected[0] + boss_selected[4] > 0 and boss_selected[8] == 0:
            if button_id == 8:
                boss_selected[0] = 0
                boss_selected[4] = 0
            else:
                boss_selected[8] = 2
        if boss_selected[1] + boss_selected[5] > 0 and boss_selected[7] == 0:
            if button_id == 7:
                boss_selected[1] = 0
                boss_selected[5] = 0
            else:
                boss_selected[7] = 2
        self.boss_image_show()
        self.calc()
    
    def on_confirm(self, event):
        battle_total = 0
        battle_name = self.battle_choice[2].GetStringSelection()
        if self.battle_choice[0].GetSelection() == 0:
            if battle_name in battle_score.keys():
                battle_total += battle_score[battle_name]
            if self.battle_choice[4].GetSelection() == 0:
                battle_total += 20
            times = 1.0
            if self.battle_choice[3].GetSelection() == 0:
                times += 0.2
            if self.battle_choice[5].GetSelection() == 0:
                times -= 0.7
            battle_total *= times
        elif self.battle_choice[0].GetSelection() == 1:
            battle_total = battle_special_score[battle_name][self.battle_choice[3].GetSelection()]
        else:
            return
        extra_item = self.battle_choice[6].GetStringSelection()
        if extra_item in special_extra_score.keys():
            battle_total += special_extra_score[extra_item]

        if battle_total > 0 and battle_name != "":
            print(f"新增战斗：{battle_name}，得分为{battle_total}")
            index = self.list_ctrl.InsertStringItem(self.list_ctrl.GetItemCount(), " " + battle_name)
            self.list_ctrl.SetStringItem(index, 1, str(int(battle_total)))
            self.calc()
    
    def on_delete(self, event):
        selection = self.list_ctrl.GetFirstSelected()
        if selection != -1:
            self.list_ctrl.DeleteItem(selection)
        self.calc()

    def boss_image_show(self):
        width, height = 64, 64
        for i in range(len(boss_selected)):
            image = wx.Bitmap(width, height)
            dc = wx.MemoryDC(image)
            dc.DrawBitmap(wx.Bitmap(boss_images[i]), 0, 0)
            dc.SetTextForeground("#FFFFFF")
            dc.SetFont(self.button_text_font)
            text = boss_text[i]
            tw, th = dc.GetTextExtent(text)
            if boss_selected[i] == 1:
                text = boss_base_text + text
                th *= 2
            elif boss_selected[i] == 2:
                if i < 7:
                    text = boss_extra_text + text
                else:
                    text = collection_extra_text + text
                th *= 2
            dc.DrawText(text, (width - tw) // 2, height - th - 2)
            del dc

            image = image.ConvertToImage()
            alpha = 85 * (boss_selected[i] + 1)
            if not image.HasAlpha():
                image.InitAlpha()
            for x in range(image.GetWidth()):
                for y in range(image.GetHeight()):
                    image.SetAlpha(x, y, alpha)
            image = wx.Bitmap(image)

            self.boss_button[i].SetBitmapLabel(image)
    
    def calc(self):
        total = int(self.settlement_ctrl.GetValue())
        for i in range(len(self.challenge_text_ctrl)):
            total += int(self.challenge_text_ctrl[i].GetValue()) * challenge_score[i]
        for i in range(len(self.challenge_choice)):
            if self.challenge_choice[i].GetSelection() == 0:
                total += unique_challenge_score[i]

        for i in range(len(boss_selected)):
            if boss_selected[i] == 2:
                total += boss_score[i]
            elif i == 1 and boss_selected[i] == 1:
                total += sentinel_base_score
        boss_cnt = 0
        for i in range(7):
            if boss_selected[i] == 2:
                boss_cnt += 1
        if boss_cnt == 3:
            total += 100
        if boss_cnt >= 2:
            total += 200
        if boss_selected[0] + boss_selected[4] >= 2 and boss_selected[1] + boss_selected[5] >= 2:
            total += 100

        for i in range(self.list_ctrl.GetItemCount()):
            item = self.list_ctrl.GetItem(i, 1)
            total += int(item.GetText())

        if unit == Unit.BASE:
            self.calc_text.SetLabelText(str(total))
            self.calc_text.SetPosition((620 - self.calc_text.GetSize().GetWidth() // 2, 700 - self.calc_text.GetSize().GetHeight() // 2))
            self.calc_unit_text.SetLabelText("")
        else:
            self.calc_text.SetLabelText(f"{total / 21.0:.2f}")
            self.calc_unit_text.SetLabelText("粽")
            self.calc_text.SetPosition((620 - self.calc_text.GetSize().GetWidth() // 2, 700 - self.calc_text.GetSize().GetHeight() // 2))
            self.calc_unit_text.SetPosition((self.calc_text.GetPosition().x + self.calc_text.GetSize().GetWidth() + 5, (self.calc_text.GetPosition().y + self.calc_text.GetSize().GetHeight() - self.calc_unit_text.GetSize().GetHeight() - 10)))
    
    def on_mouse_move(self, event):
        x, y = event.GetPosition()
        if 470 <= x <= 770 and 620 <= y <= 765:
            self.calc_hint_text.SetLabelText("长按重置")
        else:
            self.calc_hint_text.SetLabelText("")
            self.mouse_is_down = False
            self.timer.Stop()
        event.Skip()
    
    def on_left_down(self, event):
        x, y = event.GetPosition()
        if 470 <= x <= 770 and 620 <= y <= 765:
            self.mouse_is_down = True
            self.timer.Start(1000)
        event.Skip()

    def on_left_up(self, event):
        self.mouse_is_down = False
        self.timer.Stop()
        event.Skip()
    
    def on_timer(self, event):
        if self.mouse_is_down:
            self.reset()
            self.calc()
        self.timer.Stop()
    
    def reset(self):
        for i in self.challenge_text_ctrl:
            i.SetValue("0")
        for i in self.challenge_choice:
            i.SetSelection(1)
        for i in range(len(boss_selected)):
            boss_selected[i] = 0
        self.settlement_ctrl.SetValue("0")
        self.list_ctrl.DeleteAllItems()
        self.boss_image_show()
    
    def on_settings_clicked(self, event):
        self.Parent.open_settings()
    
    def on_information_clicked(self, event):
        self.Parent.open_information()

class CalcFrame(wx.Frame):
    def __init__(self, parent, title):
        super(CalcFrame, self).__init__(parent, title=title, size=(1275, 900), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        init_settings()
        self.calc_panel = CalcPanel(self)
        self.settings_panel = SettingsPanel(self)
        self.information_panel = InformationPanel(self)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
    
    def open_settings(self):
        self.settings_panel.Show()
        self.calc_panel.Hide()
        self.Sizer.Remove(0)
        self.Sizer.Add(self.settings_panel, 1, wx.EXPAND)
        self.Layout()
    
    def close_settings(self, reset=False):
        self.calc_panel.Show()
        if reset:
            init_settings()
            self.calc_panel.init_challenge()
            self.calc_panel.reset()
        self.calc_panel.calc()
        self.settings_panel.Hide()
        self.Sizer.Remove(0)
        self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
        self.Layout()
    
    def open_information(self):
        self.information_panel.Show()
        self.calc_panel.Hide()
        self.Sizer.Remove(0)
        self.Sizer.Add(self.information_panel, 1, wx.EXPAND)
        self.Layout()
    
    def close_information(self):
        self.calc_panel.Show()
        self.information_panel.Hide()
        self.Sizer.Remove(0)
        self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
        self.Layout()

if __name__ == "__main__":
    app = wx.App(False)
    window = CalcFrame(None, "通天联赛计算器 demo by 巴别塔攻略组")
    window.Show()
    app.MainLoop()