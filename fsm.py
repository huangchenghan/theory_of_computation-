from transitions.extensions import GraphMachine

from utils import send_text_message
from re import S
import requests
from lxml import etree

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        
        response = requests.get("https://pokemon.wingzero.tw/pokedex/pokemongo/tw")
        content = response.content.decode()
        self.html = etree.HTML(content)
        
        self.start = 0
        self.end = 0
        self.ID = "0"
        self.attribute = "無"
        self.section_name_list = []
        self.section_attribute_list = []
        self.final_name_list = []
        self.final_attribute_list = []
                
    #======================condition===========================
    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "開始"
    
    def is_going_to_illustrated_book(self, event):
        text = event.message.text
        return text.lower() == "圖鑑"
    
    def is_going_to_section(self, event):
        section_list = ["關都","城都","豐緣","神奧","合眾","卡洛斯","阿羅拉","伽勒爾"]
        section_id_list = [(1,151), (152,251), (252,386), (387,493), (494,649), (650,721), (722,809), (810,898)]
        text = event.message.text
        for i,item in enumerate(section_list):
            if text.lower() == item:
                self.start = section_id_list[i][0]
                self.end = section_id_list[i][1]
                return True
        return False
    
    def is_going_to_attribute(self, event):
        attribute_list = ["一般","火","水","草","格鬥","飛行","毒","電","地面","超能力","岩石","冰","蟲","龍","幽靈","惡","鋼","妖精"]
        text = event.message.text
        for item in attribute_list:
            if text.lower() == item:
                self.attribute = item
                return True
        return False
    
    def is_going_to_ID(self, event):
        text = event.message.text
        for item in self.final_name_list:
            if text.lower() == item[0]:
                self.ID = item[0]
                return True
        return False
        
    def go_back_to_illustrated_book(self, event):
        text = event.message.text
        return text.lower() == "重新查詢"
    
    def is_going_to_introduction(self, event):
        text = event.message.text
        return text.lower() == "簡介"
    
    def is_going_to_generation1(self, event):
        text = event.message.text
        return text.lower() == "一"

    def is_going_to_generation2(self, event):
        text = event.message.text
        return text.lower() == "二"
    
    def is_going_to_generation3(self, event):
        text = event.message.text
        return text.lower() == "三"
    
    def is_going_to_generation4(self, event):
        text = event.message.text
        return text.lower() == "四"
    
    def is_going_to_generation5(self, event):
        text = event.message.text
        return text.lower() == "五"
    
    def is_going_to_generation6(self, event):
        text = event.message.text
        return text.lower() == "六"
    
    def is_going_to_generation7(self, event):
        text = event.message.text
        return text.lower() == "七"
    
    def is_going_to_generation8(self, event):
        text = event.message.text
        return text.lower() == "八"
    
    def go_back_to_introduction(self, event):
        text = event.message.text
        return text.lower() == "回到簡介"
    
    def go_back_to_menu(self, event):
        text = event.message.text
        return text.lower() == "回到目錄"
    
    #======================enter===========================
    def on_enter_menu(self, event):
        print("I'm entering menu")
        
        reply_message = "選擇功能\n圖鑑、簡介"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_illustrated_book(self, event):
        print("I'm entering illustrated_book")
        
        reply_message = "選擇地區\n關都、城都、豐緣、神奧、合眾、卡洛斯、阿羅拉、伽勒爾"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_section(self, event):
        print("I'm entering section")
        
        self.section_name_list.clear()
        self.section_attribute_list.clear()
        for i in range(self.start, self.end+1):
            id_name_list = self.html.xpath(f'//*[@id="pokemon"]/div[2]/table/tbody/tr[{i}]/td[1]/a/span[2]/text()')
            attribute1_list = self.html.xpath(f'//*[@id="pokemon"]/div[2]/table/tbody/tr[{i}]/td[3]/span[1]/a/text()')
            attribute2_list = self.html.xpath(f'//*[@id="pokemon"]/div[2]/table/tbody/tr[{i}]/td[3]/span[2]/a/text()')
            if len(id_name_list)==0:
                continue
            else:
                #id and name
                name = id_name_list[0]
                name = str(name)        
                id = str(i)                
                self.section_name_list.append((id,name))
                
                #attribute  
                self_attribute = []      
                attribute1 = attribute1_list[0]
                attribute1 = str(attribute1)
                self_attribute.append(attribute1)
                if len(attribute2_list) != 0:
                    attribute2 = attribute2_list[0]
                    attribute2 = str(attribute2)
                    self_attribute.append(attribute2)
                self.section_attribute_list.append(self_attribute)
        
        reply_message = "選擇屬性\n一般、火、水、草、冰、電、毒、鋼、惡、蟲、龍、格鬥、飛行、地面、岩石、幽靈、妖精、超能力"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_attribute(self, event):
        print("I'm entering attribute")
        self.final_name_list.clear()
        self.final_attribute_list.clear()
        for i in range(len(self.section_attribute_list)):
            for j in range(len(self.section_attribute_list[i])):
                if self.section_attribute_list[i][j] == self.attribute:
                    self.final_name_list.append(self.section_name_list[i])
                    self.final_attribute_list.append(self.section_attribute_list[i])
                    break
        
        reply_message = "選擇ID\n"
        for i in range(len(self.final_name_list)):
            if i != 0:
                reply_message += "、"  
            reply_message += self.final_name_list[i][0]
            reply_message += self.final_name_list[i][1]
                
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)      
        #self.go_back()
    
    def on_enter_ID(self, event):
        print("I'm entering ID")
        for i in range(len(self.final_name_list)):
            if self.final_name_list[i][0] == self.ID:        
                choose_name = self.final_name_list[i]
                choose_attribute = self.final_attribute_list[i]
        choose_xpath = self.html.xpath(f'//*[@id="pokemon"]/div[2]/table/tbody/tr[{self.ID}]/td[1]/a/@href') 
        choose_path = 'https://pokemon.wingzero.tw/'
        choose_path = choose_path + str(choose_xpath[0])
        
        pokemon_info = "ID:" + choose_name[0] + " " + "名稱:" + choose_name[1] + " " + "屬性:"
        for i in range(len(choose_attribute)):
            if i != 0:
                pokemon_info += "、"
            pokemon_info += choose_attribute[i]
        pokemon_info += "\n"
        pokemon_info += choose_path
          
        reply_token = event.reply_token
        send_text_message(reply_token, pokemon_info)    
    
    def on_enter_introduction(self, event):
        print("I'm entering introduction")
        
        reply_message = "選擇世代\n一、二、三、四、五、六、七、八"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)  
        
    def on_enter_generation1(self, event):
        print("I'm entering generation1")
        
        reply_message = "年代: 1996-1999\n遊戲主系列: 紅、綠、藍\n平台: Game Boy、任天堂3DS"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)

    def on_enter_generation2(self, event):
        print("I'm entering generation2")

        reply_message = "年代: 1999-2002\n遊戲主系列: 金、銀\n平台: Game Boy Color、任天堂3DS"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation3(self, event):
        print("I'm entering generation3")
        
        reply_message = "年代: 2002-2006\n遊戲主系列: 紅寶石、藍寶石\n平台: Game Boy Advance"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation4(self, event):
        print("I'm entering generation4")
        
        reply_message = "年代: 2006-2010\n遊戲主系列: 鑽石、珍珠\n平台: 任天堂DS"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation5(self, event):
        print("I'm entering generation5")
        
        reply_message = "年代: 2010-2013\n遊戲主系列: 黑、白\n平台: 任天堂DS"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation6(self, event):
        print("I'm entering generation6")
        
        reply_message = "年代: 2013-2016\n遊戲主系列: X、Y\n平台: 任天堂3DS"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation7(self, event):
        print("I'm entering generation7")
        
        reply_message = "年代: 2016-2019\n遊戲主系列: 太陽、月亮\n平台: 任天堂Switch"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
        
    def on_enter_generation8(self, event):
        print("I'm entering generation8")
        
        reply_message = "年代: 2019-目前\n遊戲主系列: 劍、盾\n平台: 任天堂Switch"
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply_message)
          
    #======================exit===========================    
    def on_exit_section(self, event):
        print("Leaving section")

        
