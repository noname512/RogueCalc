import random
import math
import wx
import wx.lib.agw.ultimatelistctrl as ULC
import wx.adv as ADV
import json
import sys, os
import ctypes
import webbrowser
from PIL import Image, ImageEnhance

WIDTH = 1200
HEIGHT = 800
version_text = "v1.0.1"
title_text = "通天联赛计算器 by 巴别塔攻略组"
foreground_color = "#CDCAFF"
lang_name = ["中文（简体）", "English"]
lang_id = ["zh", 'en']
lang_chosen = 0
lang_choose = ""
loc_dict = {}
squad_dict = {}
emergency_dict = {}
special_lst = []
stage_score = {}
battle_levels = []
battle_text = []
battle_types = []
extra_lst = []
squad_lst = ["MadOverMatter", "PeopleOriented", "Tactical", "Others"]
chosen_squad = 0
special_chosen = [False] * 3
special_score = []

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if os.name == 'nt':
    GDI32 = ctypes.WinDLL('gdi32')
    GDI32.AddFontResourceExW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]

    # GDI32.AddFontResourceExW(resource_path('font/Novecento WideMedium.otf'), 0x10, None)
    # GDI32.AddFontResourceExW(resource_path('font/标小智无界黑.TTF'), 0x10, None)
    GDI32.AddFontResourceExW(resource_path('font/HARMONYOS_SANS_SC_REGULAR.TTF'), 0x10, None)

def init_file(data, pref):
    global loc_dict
    for k, v in data.items():
        if isinstance(v, dict):
            init_file(v, pref + k + "_")
        else:
            loc_dict[pref + k] = v

def init_settings():
    global loc_dict, squad_dict, emergency_dict, special_lst, battle_levels, battle_text, battle_types, extra_lst, special_score, lang_choose
    with open(resource_path(f"localization/{lang_id[lang_chosen]}.json"), 'r', encoding='utf-8') as loc_file:
        data = json.load(loc_file)
        loc_dict.clear()
        init_file(data, "")
        battle_levels = []
        battle_text = []
        battle_types = []
        extra_lst = []
        for lv in ['f3', 'f4', 'f5', 'f6']:
            battle_levels.append(loc_dict.get(f'stage_floor_{lv}', ''))
        for text in ['Type', 'Floor', 'Stage', 'Extra']:
            battle_text.append(loc_dict.get(f'stage_title_{text}', ''))
        for ty in ['Emergency', 'Special']:
            battle_types.append(loc_dict.get(f'stage_type_{ty}', ''))
        for ex in ['NoLeak', 'None']:
            extra_lst.append(loc_dict.get(f'stage_title_{ex}', ''))
        lang_choose = loc_dict.get('title_LanguageChoose', '')

    with open(resource_path("score.json"), "r", encoding='utf-8') as file:
        data = json.load(file)
        squad_dict = data.get('squad', {})
        stage_data = data.get('stage', {})
        emerge_data = stage_data.get('Emergency', {})
        for k, v in emerge_data.items():
            lv = loc_dict.get(f'stage_floor_{k}', '')
            lst = []
            for stage, score in v.items():
                id = loc_dict.get(f'stage_stage_{stage}', '')
                stage_score[id] = score
                lst.append(id)
            emergency_dict[lv] = lst
        if 'Special' in stage_data.keys():
            v = stage_data['Special']
            special_lst = []
            for stage, score in v.items():
                id = loc_dict.get(f'stage_stage_{stage}', '')
                stage_score[id] = score
                special_lst.append(id)
        special_score = data.get('special', [0, 0, 0])


class SettingsPanel(wx.Panel):
    def __init__(self, parent):
        super(SettingsPanel, self).__init__(parent, style=wx.BORDER_NONE)

        self.back_image = wx.Bitmap(resource_path(f"images/back.png"), wx.BITMAP_TYPE_ANY)
        self.back_rect = wx.Rect(70, 170, 40, 40)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

        self.text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        self.title_font = wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "标小智无界黑")

        self.settings_config_choice = wx.Choice(self, choices=lang_name, pos=(400, 275), size=(120, 30))
        self.settings_config_choice.SetSelection(lang_chosen)
        self.settings_config_choice.SetFont(self.text_font)
        self.settings_config_choice.Bind(wx.EVT_CHOICE, self.on_config_choice)
        self.last_lang = lang_chosen

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawBitmap(background_image, 0, 0)
        dc.SetTextForeground(foreground_color)
        dc.SetFont(self.title_font)
        dc.DrawText(lang_choose, 200, 220)
        dc.DrawBitmap(self.back_image, self.back_rect.x, self.back_rect.y)
        
        # dc.SetTextForeground("#808080")
        # dc.SetFont(self.text_font)
        # dc.DrawText(version_text, 1160, 840)

    def on_config_choice(self, event):
        global lang_chosen
        lang_chosen = self.settings_config_choice.GetSelection()

    def on_left_up(self, event):
        pos = event.GetPosition()
        if self.back_rect.Contains(pos):
            self.on_back_clicked()

    def on_back_clicked(self):
        if self.last_lang != lang_chosen:
            self.last_lang = lang_chosen
            self.Parent.close_settings(True)
        else:
            self.Parent.close_settings(False)

class BattlePanel():
    def __init__(self, parent : wx.Panel, rect):
        self.parent = parent
        self.rect = rect

        self.list = []
        self.extra_list = []
        self.text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        self.highlight = -1
        self.true_highlight = -1

    def add_item(self, name, extra_name, score):
        self.list.append((name, score))
        self.extra_list.append(extra_name)
        self.refresh()

    def remove_all_items(self):
        self.list.clear()
        self.extra_list.clear()
        self.refresh()

    def delete_item(self):
        if self.true_highlight != -1 and self.true_highlight < len(self.list):
            self.list.pop(self.true_highlight)
            self.extra_list.pop(self.true_highlight)
            self.true_highlight = -1
            self.refresh()

    def update_highlight(self, index):
        if index != self.highlight:
            self.highlight = index
            # self.refresh()

    def refresh(self):
        self.parent.RefreshRect(self.rect)

    def get_total_score(self):
        ret = 0
        for battle in self.list:
            ret += int(battle[1])
        return ret

class CalcPanel(wx.Panel):
    def __init__(self, parent):
        super(CalcPanel, self).__init__(parent, style=wx.BORDER_NONE | wx.BG_STYLE_TRANSPARENT)

        self.is_first_init = True
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.is_mouse_down = False
        text_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        # self.final_font = wx.Font(35, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Novecento Wide Medium")
        # self.final_unit_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        # bigger_text_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        # self.bold_text_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "HarmonyOS Sans SC")
        self.text_font = text_font
        self.title_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")
        # self.small_text_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "HarmonyOS Sans SC")

        self.width = WIDTH
        self.height = HEIGHT
        self.interval = 50
        self.list_width = (self.width - self.interval * 4) / 3

        self.settings_image = wx.Bitmap(resource_path(f"images/settings.png"), wx.BITMAP_TYPE_ANY)
        self.settings_rect = wx.Rect(self.width - 190, 40, 40, 40)

        self.information_image = wx.Bitmap(resource_path(f"images/information.png"), wx.BITMAP_TYPE_ANY)
        self.information_rect = wx.Rect(self.width - 130, 40, 40, 40)

        self.delete_image = wx.Bitmap(resource_path(f"images/delete.png"), wx.BITMAP_TYPE_ANY)
        self.delete_rect = wx.Rect(self.width - 132, 165, 37, 26)

        self.special_image = []
        wi = (self.list_width - 64 * 3) / 4
        for i in range(3):
            img = Image.open(resource_path(f"images/pic{i}.png")).convert("RGBA")
            rc = wx.Rect(int(self.interval * 2 + self.list_width + wi * (i + 1) + 64 * i), 190, 64, 64)
            self.special_image.append((img, rc))

        # 挑战分数
        self.challenge_text_ctrl = []
        self.challenge_choice = []
        self.challenge_label = []
        # self.init_challenge()

        # 结局分数
        self.boss_button = []
        posx = 58
        posy = 589
        # for i in range(len(boss_selected)):
        #     image = wx.Bitmap(resource_path(f"images/{boss_image_names[i]}.png"), wx.BITMAP_TYPE_ANY)
        #     boss_images.append(image)
        #     button = wx.BitmapButton(self, 100 + i, image, pos=(posx, posy), size=(70, 90))
        #     button.Bind(wx.EVT_BUTTON, self.on_button_clicked)
        #     self.boss_button.append(button)
        #     if i % 4 == 3:
        #         posx = 58
        #         posy += 99
        #     else:
        #         posx += 80
        # self.boss_image_show()

        # 关卡额外分数
        self.init_stage()

        self.confirm_button = wx.Button(self, wx.ID_ANY, label="添加", pos=(475, posy + 3), size=(300, 35))
        # self.confirm_button.SetFont(bigger_text_font)
        self.confirm_button.Bind(wx.EVT_BUTTON, self.on_confirm)

        # 结算分数
        self.settlement_ctrl = wx.TextCtrl(self, value="0", pos=(670, 570), size=(90, 26), style=wx.TE_CENTER | wx.NO_BORDER)
        # self.settlement_ctrl.SetFont(bigger_text_font)
        self.settlement_ctrl.SetForegroundColour("#808080")
        self.settlement_ctrl.Bind(wx.EVT_TEXT, self.on_text)
        self.settlement_ctrl.Bind(wx.EVT_CHAR, self.on_char)

        # 关卡额外分数一览
        self.list_ctrl = BattlePanel(self, wx.Rect(int(self.interval * 3 + self.list_width * 2), 220, int(self.list_width), 400))

        self.calc_text = "0"
        self.calc_unit_text = ""
        self.show_hint = False
        self.hint_rect = wx.Rect(450, 640, 350, 145)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Refresh()
        self.is_first_init = False

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        # dc.SetPen(wx.Pen(outline_color, 2))
        dc.DrawBitmap(background_image, 0, 0)
        dc.DrawBitmap(self.settings_image, self.settings_rect.x, self.settings_rect.y)
        dc.DrawBitmap(self.information_image, self.information_rect.x, self.information_rect.y)
        dc.DrawBitmap(self.delete_image, self.delete_rect.x, self.delete_rect.y)
        for i in range(3):
            img = self.special_image[i][0].copy()
            if not special_chosen[i]:
                alpha = img.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
                img.putalpha(alpha)
            image_wx = wx.Image(img.size[0], img.size[1])
            image_wx.SetData(img.convert("RGB").tobytes())
            image_wx.SetAlpha(img.convert("RGBA").tobytes()[3::4])
            dc.DrawBitmap(image_wx.ConvertToBitmap(), self.special_image[i][1].x, self.special_image[i][1].y)

        dc.SetTextForeground(foreground_color)
        dc.SetFont(self.title_font)
        title_lst = []
        for ti in ['Information', 'EndingBonus', 'SpecialBonus', 'StageBonus', 'StageList', 'Match']:
             title_lst.append(loc_dict[f"title_{ti}"])
        pos_lst = [[self.interval + self.list_width * 0.5, 150], \
                   [self.interval + self.list_width * 0.5, 350], \
                   [self.interval * 2 + self.list_width * 1.5, 150], \
                   [self.interval * 2 + self.list_width * 1.5, 350], \
                   [self.interval * 3 + self.list_width * 2.5, 150], \
                   [self.interval * 3 + self.list_width * 2.5, 450]]        
        for i in range(6):
            lines = title_lst[i].split('\n')
            h = dc.GetTextExtent(lines[0]).GetHeight()
            posy = int(pos_lst[i][1] - h * len(lines) / 2)
            for line in lines:
                w = dc.GetTextExtent(line).GetWidth()
                dc.DrawText(line, int(pos_lst[i][0] - w / 2), posy)
                posy += h

        dc.SetFont(self.text_font)
        sq = loc_dict["title_Squad"]
        posx = int(self.interval + self.list_width * 0.3)
        dc.DrawText(sq, posx - dc.GetTextExtent(sq).GetWidth(), 200)
        dc.DrawText(loc_dict[f"squad_{squad_lst[chosen_squad]}"], posx + 40, 200)

        for lb in self.battle_label:
            w, h = dc.GetTextExtent(lb[0])
            dc.DrawText(lb[0], lb[1] - w, lb[2])

        dc.SetBrush(wx.Brush("#DDDDDD"))
        dc.SetPen(wx.TRANSPARENT_PEN)

        x, y, w, h = self.list_ctrl.rect

        if self.list_ctrl.true_highlight != -1:
            liney = y + self.list_ctrl.true_highlight * 50 - 5
            dc.DrawRectangle(x, liney, w, 45)
            dc.SetPen(wx.Pen(foreground_color, 1))
            dc.DrawLine(x, liney + 45, x + w, liney + 45)

        # dc.SetBrush(wx.TRANSPARENT_BRUSH)
        # dc.SetPen(wx.Pen(foreground_color, 1))

        # if self.show_hint:
        #     dc.DrawText("长按重置", 465, 760)

        delty = 0
        for battle in self.list_ctrl.list:
            dc.DrawText(battle[0], x + 10, y + delty)
            dc.DrawText(battle[1], x + w - dc.GetTextExtent(battle[1]).GetWidth() - 10, y + delty)
            delty += 50

        # dc.SetFont(self.small_text_font)
        delty = 22
        for extra in self.list_ctrl.extra_list:
            dc.DrawText(extra, x + 10, y + delty)
            delty += 50

        dc.SetTextForeground(foreground_color)
        dc.SetFont(self.title_font)
        w, h = dc.GetTextExtent(self.calc_text)
        x, y = int(self.interval * 3 + self.list_width * 2.5 - w / 2), 550 - h // 2
        dc.DrawText(self.calc_text, x, y)
        
        # dc.SetFont(self.text_font)
        # dc.SetTextForeground(foreground_color)
        # dc.DrawText(version_text, 1160, 840)
    
    def init_stage(self):
        self.battle_label = []
        if self.is_first_init:
            self.battle_choice = []
        posx = int(self.interval * 2 + self.list_width * 1.35)
        posy = 400
        for i in range(len(battle_text)):
            self.battle_label.append((battle_text[i], posx, posy))

            choices = []
            if i == 0:
                choices = battle_types
            elif i == 3:
                choices = extra_lst
            
            if self.is_first_init:
                choice = wx.Choice(self, i + 20, choices=choices, pos=(posx + 40, posy), size=(130, 26))
            else:
                choice = self.battle_choice[i]
                choice.Clear()
                choice.AppendItems(choices)

            if i != 0 and i != 3:
                choice.Disable()
            else:
                choice.Enable()
            if i == 3:
                choice.SetSelection(1)

            if self.is_first_init:
                # choice.SetFont(text_font)
                choice.Bind(wx.EVT_CHOICE, self.on_choice)
                self.battle_choice.append(choice)
            posy += 32

    # def init_challenge(self):
    #     for text_ctrl in self.challenge_text_ctrl:
    #         text_ctrl.Destroy()
    #     for choice in self.challenge_choice:
    #         choice.Destroy()
    #     self.challenge_text_ctrl.clear()
    #     self.challenge_choice.clear()
    #     self.challenge_label.clear()
    #     posy = 255
    #     for i in range(len(challenge_text)):
    #         self.challenge_label.append((challenge_text[i], 67, posy + 2))

    #         text_ctrl = wx.TextCtrl(self, value="0", pos=(313, posy), size=(50, 26), style=wx.TE_CENTER | wx.NO_BORDER)
    #         text_ctrl.SetFont(self.text_font)
    #         text_ctrl.SetBackgroundColour("#EFEFEF")
    #         text_ctrl.SetForegroundColour("#808080")
    #         text_ctrl.Bind(wx.EVT_TEXT, self.on_text)
    #         text_ctrl.Bind(wx.EVT_CHAR, self.on_char)
    #         self.challenge_text_ctrl.append(text_ctrl)

    #         posy += 32

    #     for i in range(len(unique_challenge_text)):
    #         self.challenge_label.append((unique_challenge_text[i], 67, posy + 2))

    #         choice = wx.Choice(self, wx.ID_ANY, choices=yes_no_choice, pos=(313, posy), size=(50, 26))
    #         choice.SetSelection(1)
    #         choice.SetFont(self.text_font)
    #         choice.Bind(wx.EVT_CHOICE, self.on_choice)
    #         self.challenge_choice.append(choice)

    #         posy += 32

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
            elif len(current_value) < 5:
                event.Skip()
        elif event.GetKeyCode() in [wx.WXK_CONTROL_A, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_TAB]:
            event.Skip()

    def on_choice(self, event):
        id = event.GetId()
        choice = event.GetEventObject()
        if id == 20:
            self.battle_choice[1].Clear()
            self.battle_choice[2].Clear()
            if choice.GetSelection() == 0:
                self.battle_choice[1].Enable()
                self.battle_choice[1].AppendItems(battle_levels)
                self.battle_choice[2].Disable()
            else:
                self.battle_choice[2].Enable()
                self.battle_choice[2].AppendItems(special_lst)
                self.battle_choice[1].Disable()
        elif id == 21:
            self.battle_choice[2].Enable()
            self.battle_choice[2].Clear()
            self.battle_choice[2].AppendItems(emergency_dict.get(self.battle_choice[1].GetStringSelection(), []))

        self.calc()

    # def on_button_clicked(self, event):
    #     button_id = event.GetId() - 100
    #     boss_selected[button_id] = 2 - boss_selected[button_id]
    #     if boss_selected[2] + boss_selected[3] + boss_selected[6] > 2:
    #         boss_selected[2] = 0
    #         boss_selected[3] = 0
    #         boss_selected[6] = 0
    #         boss_selected[button_id] = 2
    #     if button_id == 0 and boss_selected[0] != 0:
    #         boss_selected[4] = 0
    #     if button_id == 4 and boss_selected[4] != 0:
    #         boss_selected[0] = 0
    #     if button_id == 1 and boss_selected[5] != 0:
    #         boss_selected[5] = 0
    #     if button_id == 5 and boss_selected[1] != 0:
    #         boss_selected[1] = 0
    #     if boss_selected[1] + boss_selected[5] > 0 and boss_selected[7] == 0:
    #         if button_id == 7:
    #             boss_selected[1] = 0
    #             boss_selected[5] = 0
    #         else:
    #             boss_selected[7] = 2
    #     self.boss_image_show()
    #     self.calc()
    
    def on_confirm(self, event):
        battle_name = self.battle_choice[2].GetStringSelection()
        show_name = battle_name
        extra_name = ""
        times = 1.0
        if self.battle_choice[0].GetSelection() == 0:
            show_name = loc_dict['stage_type_Emergency'] + show_name
        battle_score = stage_score.get(battle_name, 0)
        if self.battle_choice[3].GetSelection() == 0:
            battle_score *= 1.2
            extra_name = loc_dict['stage_title_NoLeak']

        if battle_score > 0 and battle_name != "":
            print(f"new battle: {battle_name}, score: {battle_score}")
            self.list_ctrl.add_item(show_name, extra_name, str(int(battle_score)))
            self.calc()
    
    def on_delete(self):
        self.list_ctrl.delete_item()
        self.calc()

    # def boss_image_show(self):
    #     width, height = 70, 90
    #     for i in range(len(boss_selected)):
    #         image = wx.Bitmap(width, height)
    #         dc = wx.MemoryDC(image)
    #         dc.DrawBitmap(wx.Bitmap(boss_images[i]), 0, 0)

    #         image = image.ConvertToImage()
    #         alpha = 85 * (boss_selected[i] + 1)
    #         if not image.HasAlpha():
    #             image.InitAlpha()
    #         for x in range(image.GetWidth()):
    #             for y in range(image.GetHeight()):
    #                 image.SetAlpha(x, y, alpha)
    #         image = wx.Bitmap(image)

    #         self.boss_button[i].SetBitmapLabel(image)
    
    def calc(self):
        total = int(self.settlement_ctrl.GetValue())
        # for i in range(len(self.challenge_choice)):
        #     if self.challenge_choice[i].GetSelection():
        #         total += challenge_score[i]

        # for i in range(len(boss_selected)):
        #     if boss_selected[i] == 2:
        #         total += boss_score[i]
        # boss_cnt = 0
        # for i in range(7):
        #     if boss_selected[i] == 2:
        #         boss_cnt += 1
        # if boss_cnt == 3:
        #     total += three_ending
        # if boss_cnt >= 2:
        #     total += two_ending
        # if boss_selected[0] + boss_selected[4] >= 2 and boss_selected[1] + boss_selected[5] >= 2:
        #     total += both_three_four_ending

        total += self.list_ctrl.get_total_score()

        for i in range(3):
            if special_chosen[i]:
                total += special_score[i]

        self.calc_text = str(int(total))
        
        self.RefreshRect(wx.Rect(860, 520, 260, 60))
    
    def on_mouse_move(self, event):
        pos = event.GetPosition()
        x, y = pos

        if self.list_ctrl.rect.Contains(pos):
            delty = y - self.list_ctrl.rect.GetTop()
            if delty < len(self.list_ctrl.list) * 50:
                self.list_ctrl.update_highlight(math.floor(delty / 50))
            else:
                self.list_ctrl.update_highlight(-1)
        else:
                self.list_ctrl.update_highlight(-1)

        if self.hint_rect.Contains(pos):
            if not self.show_hint:
                self.show_hint = True
                self.RefreshRect(wx.Rect(457, 758, 200, 30))
        else:
            if self.show_hint:
                self.show_hint = False
                self.RefreshRect(wx.Rect(457, 758, 200, 30))
            self.mouse_is_down = False
            self.timer.Stop()

        event.Skip()
    
    def on_left_down(self, event):
        pos = event.GetPosition()

        if self.hint_rect.Contains(pos):
            self.mouse_is_down = True
            self.timer.Start(1000)

        event.Skip()

    def on_left_up(self, event):
        pos = event.GetPosition()

        if self.list_ctrl.rect.Contains(pos):
            self.list_ctrl.true_highlight = self.list_ctrl.highlight
            self.list_ctrl.refresh()
        elif self.settings_rect.Contains(pos):
            self.Parent.open_settings()
        elif self.information_rect.Contains(pos):
            self.Parent.open_information()
        elif self.delete_rect.Contains(pos):
            self.on_delete()
        else:
            for i in range(3):
                if self.special_image[i][1].Contains(pos):
                    special_chosen[i] = not special_chosen[i]
                    self.RefreshRect(self.special_image[i][1])
                    self.calc()
                    break

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
        # for i in range(len(boss_selected)):
        #     boss_selected[i] = 0
        self.settlement_ctrl.SetValue("0")
        self.list_ctrl.remove_all_items()
        # self.boss_image_show()
    
    def on_settings_clicked(self, event):
        self.Parent.open_settings()
    
    def on_information_clicked(self, event):
        self.Parent.open_information()

class CalcFrame(wx.Frame):
    def __init__(self, parent, title):
        super(CalcFrame, self).__init__(parent, title=title, size=(WIDTH, HEIGHT), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        init_settings()
        self.SetIcon(wx.Icon(resource_path("images/巴别塔.ico")))
        self.calc_panel = CalcPanel(self)
        self.settings_panel = SettingsPanel(self)
        # self.information_panel = InformationPanel(self)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
    
    def open_settings(self):
        self.settings_panel.Show()
        self.calc_panel.Hide()
        self.Sizer.Add(self.settings_panel, 1, wx.EXPAND)
        self.Sizer.Remove(0)
        self.Layout()
    
    def close_settings(self, reset=False):
        self.calc_panel.Show()
        if reset:
            init_settings()
            self.calc_panel.init_stage()
            # self.calc_panel.init_challenge()
        self.calc_panel.calc()
        self.settings_panel.Hide()
        self.Sizer.Remove(0)
        self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
        self.Layout()
    
    # def open_information(self):
    #     self.information_panel.Show()
    #     self.calc_panel.Hide()
    #     self.Sizer.Remove(0)
    #     self.Sizer.Add(self.information_panel, 1, wx.EXPAND)
    #     self.Layout()
    
    # def close_information(self):
    #     self.calc_panel.Show()
    #     self.information_panel.Hide()
    #     self.Sizer.Remove(0)
    #     self.Sizer.Add(self.calc_panel, 1, wx.EXPAND)
    #     self.Layout()

if __name__ == "__main__":
    app = wx.App(False)
    global background_image
    background_image = wx.Bitmap(resource_path("images/background.jpg"), wx.BITMAP_TYPE_ANY)
    window = CalcFrame(None, title_text)
    window.Show()
    app.MainLoop()