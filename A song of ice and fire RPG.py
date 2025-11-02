# asoiaf_game.py - 完全优化版
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import requests
import json
import os
from datetime import datetime
from threading import Thread
import re

class ASOIAFGame:
    def __init__(self, root):
        self.root = root
        self.root.title("冰与火之歌 - AI角色扮演游戏")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1612')
        
        # 游戏状态
        self.game_state = {
            'character': {
                'name': '',
                'identity': '',
                'age': 0,
                'location': '',
                'health': '健康',
                'mental': '平静',
                'hunger': '饱足',
                'fatigue': '精力充沛',
                'gold_dragons': 0,
                'silver_stags': 0,
                'copper_stars': 0
            },
            'story_log': [],
            'current_model': '',
            'game_started': False
        }
        
        self.ollama_url = 'http://localhost:11434'
        self.save_dir = 'saves'
        self.is_processing = False
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        self.setup_ui()
        self.scan_models()
    
    def setup_ui(self):
        """设置UI界面"""
        # 配置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#1a1612')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧边栏
        sidebar = tk.Frame(main_frame, bg='#2a2318', relief=tk.RIDGE, bd=3)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar.configure(width=320)
        
        # 标题
        title_label = tk.Label(sidebar, text="⚔ 角色信息 ⚔", bg='#2a2318', 
                               fg='#d4af37', font=('Georgia', 16, 'bold'))
        title_label.pack(pady=15)
        
        # 角色信息框
        char_frame = tk.Frame(sidebar, bg='#1a1612', relief=tk.SUNKEN, bd=2)
        char_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.labels = {}
        char_info = [
            ('姓名', 'name', '未创建'),
            ('身份', 'identity', '-'),
            ('年龄', 'age', '0岁'),
            ('地点', 'location', '-')
        ]
        
        for label, key, default in char_info:
            row = tk.Frame(char_frame, bg='#1a1612')
            row.pack(fill=tk.X, padx=10, pady=6)
            tk.Label(row, text=f"{label}：", bg='#1a1612', fg='#d4af37', 
                    font=('Microsoft YaHei', 11, 'bold')).pack(side=tk.LEFT)
            self.labels[key] = tk.Label(row, text=default, bg='#1a1612', 
                                       fg='#e8dcc8', font=('Microsoft YaHei', 10),
                                       wraplength=180, justify=tk.LEFT)
            self.labels[key].pack(side=tk.RIGHT)
        
        # 状态标题
        tk.Label(sidebar, text="⚔ 状态 ⚔", bg='#2a2318', 
                fg='#d4af37', font=('Georgia', 14, 'bold')).pack(pady=(20, 10))
        
        # 状态网格
        status_container = tk.Frame(sidebar, bg='#2a2318')
        status_container.pack(fill=tk.X, padx=15)
        
        self.status_labels = {}
        statuses = [
            ('health', '身体', '健康', '#4a7c59'),
            ('mental', '精神', '平静', '#5a7c9a'),
            ('hunger', '饥饿', '饱足', '#9a7c4a'),
            ('fatigue', '疲劳', '精力充沛', '#7c5a9a')
        ]
        
        for i, (key, label, default, color) in enumerate(statuses):
            frame = tk.Frame(status_container, bg='#1a1612', relief=tk.RAISED, bd=2)
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            
            tk.Label(frame, text=label, bg='#1a1612', fg=color,
                    font=('Microsoft YaHei', 10, 'bold')).pack(pady=(5, 2))
            self.status_labels[key] = tk.Label(frame, text=default, bg='#1a1612',
                                              fg='#e8dcc8', font=('Microsoft YaHei', 9))
            self.status_labels[key].pack(pady=(0, 5))
        
        status_container.grid_columnconfigure(0, weight=1)
        status_container.grid_columnconfigure(1, weight=1)
        
        # 资产标题
        tk.Label(sidebar, text="⚔ 资产 ⚔", bg='#2a2318', 
                fg='#d4af37', font=('Georgia', 14, 'bold')).pack(pady=(20, 10))
        
        # 资产信息
        money_frame = tk.Frame(sidebar, bg='#1a1612', relief=tk.SUNKEN, bd=2)
        money_frame.pack(fill=tk.X, padx=15, pady=10)
        
        money_info = [
            ('金龙 🐉', 'gold_dragons', '#d4af37'),
            ('银鹿 🦌', 'silver_stags', '#c0c0c0'),
            ('铜星 ⭐', 'copper_stars', '#cd7f32')
        ]
        
        for label, key, color in money_info:
            row = tk.Frame(money_frame, bg='#1a1612')
            row.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(row, text=f"{label}：", bg='#1a1612', fg=color,
                    font=('Microsoft YaHei', 10, 'bold')).pack(side=tk.LEFT)
            self.labels[key] = tk.Label(row, text='0', bg='#1a1612',
                                       fg='#e8dcc8', font=('Microsoft YaHei', 10))
            self.labels[key].pack(side=tk.RIGHT)
        
        # AI模型
        tk.Label(sidebar, text="⚔ AI模型 ⚔", bg='#2a2318', 
                fg='#d4af37', font=('Georgia', 14, 'bold')).pack(pady=(20, 10))
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(sidebar, textvariable=self.model_var,
                                       state='readonly', font=('Microsoft YaHei', 10))
        self.model_combo.pack(fill=tk.X, padx=15, pady=5)
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # 控制按钮
        tk.Label(sidebar, text="⚔ 控制 ⚔", bg='#2a2318', 
                fg='#d4af37', font=('Georgia', 14, 'bold')).pack(pady=(20, 10))
        
        btn_frame = tk.Frame(sidebar, bg='#2a2318')
        btn_frame.pack(fill=tk.X, padx=15, pady=5)
        
        buttons = [
            ('🎮 新游戏', self.new_game, '#4a7c59'),
            ('💾 保存', self.save_game, '#5a7c9a'),
            ('📂 读取', self.load_game, '#9a7c4a'),
            ('🔄 刷新模型', self.scan_models, '#7c5a9a')
        ]
        
        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command, bg=color,
                     fg='#ffffff', font=('Microsoft YaHei', 10, 'bold'), 
                     relief=tk.RAISED, bd=2, cursor='hand2',
                     activebackground=color).pack(fill=tk.X, pady=4)
        
        # 右侧主内容区
        content_frame = tk.Frame(main_frame, bg='#1a1612')
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 游戏标题
        game_title = tk.Label(content_frame, text="冰与火之歌 - AI角色扮演游戏", 
                             bg='#1a1612', fg='#d4af37', 
                             font=('Georgia', 20, 'bold'))
        game_title.pack(pady=(0, 10))
        
        # 游戏显示区
        display_frame = tk.Frame(content_frame, bg='#2a2318', relief=tk.RIDGE, bd=3)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.game_display = scrolledtext.ScrolledText(
            display_frame, wrap=tk.WORD, bg='#0d0d0a', fg='#e8dcc8',
            font=('Microsoft YaHei', 11), relief=tk.FLAT, padx=20, pady=20,
            insertbackground='#d4af37', spacing1=5, spacing3=5
        )
        self.game_display.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.game_display.insert('1.0', '🏰 欢迎来到维斯特洛大陆 🏰\n\n请选择AI模型并开始新游戏。')
        self.game_display.config(state=tk.DISABLED)
        
        # 配置文本标签
        self.game_display.tag_config('player', foreground='#4a7c59', 
                                     font=('Microsoft YaHei', 11, 'bold'))
        self.game_display.tag_config('ai', foreground='#e8dcc8',
                                     font=('Microsoft YaHei', 11))
        self.game_display.tag_config('timestamp', foreground='#8b7355', 
                                     font=('Microsoft YaHei', 9))
        self.game_display.tag_config('system', foreground='#d4af37', 
                                     font=('Microsoft YaHei', 10, 'italic'))
        self.game_display.tag_config('title', foreground='#d4af37',
                                     font=('Georgia', 13, 'bold'))
        
        # 输入区
        input_frame = tk.Frame(content_frame, bg='#2a2318', relief=tk.RIDGE, bd=3)
        input_frame.pack(fill=tk.X)
        
        input_container = tk.Frame(input_frame, bg='#2a2318')
        input_container.pack(fill=tk.BOTH, padx=15, pady=15)
        
        self.player_input = tk.Text(input_container, height=3, wrap=tk.WORD,
                                    bg='#0d0d0a', fg='#e8dcc8',
                                    font=('Microsoft YaHei', 11), relief=tk.SUNKEN, bd=2,
                                    insertbackground='#d4af37')
        self.player_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.player_input.bind('<Return>', self.on_enter_key)
        
        self.send_btn = tk.Button(input_container, text='行动\n(Enter)',
                                  command=self.send_action, bg='#4a7c59',
                                  fg='#ffffff', font=('Microsoft YaHei', 12, 'bold'),
                                  relief=tk.RAISED, bd=3, cursor='hand2',
                                  width=10, activebackground='#5a8c69')
        self.send_btn.pack(side=tk.RIGHT, fill=tk.Y)
    
    def scan_models(self):
        """扫描Ollama模型"""
        print("[调试] 扫描模型中...")
        try:
            response = requests.get(f'{self.ollama_url}/api/tags', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('models'):
                    models = [model['name'] for model in data['models']]
                    self.model_combo['values'] = models
                    if models:
                        self.model_combo.current(0)
                        self.game_state['current_model'] = models[0]
                        self.add_system_message(f'✓ 找到 {len(models)} 个模型')
                        print(f"[调试] 成功: {models}")
                else:
                    self.model_combo['values'] = ['未找到模型']
                    
        except Exception as e:
            print(f"[调试] 扫描失败: {e}")
            self.model_combo['values'] = ['连接失败']
    
    def on_model_change(self, event):
        """模型选择变化"""
        self.game_state['current_model'] = self.model_var.get()
        self.add_system_message(f'已选择: {self.game_state["current_model"]}')
    
    def new_game(self):
        """开始新游戏"""
        if not self.game_state['current_model']:
            messagebox.showerror('错误', '请先选择AI模型！')
            return
        
        if self.is_processing:
            return
        
        # 重置
        self.game_state['character'] = {
            'name': '', 'identity': '', 'age': 0, 'location': '',
            'health': '健康', 'mental': '平静', 'hunger': '饱足',
            'fatigue': '精力充沛', 'gold_dragons': 0,
            'silver_stags': 0, 'copper_stars': 0
        }
        self.game_state['story_log'] = []
        self.game_state['game_started'] = False
        
        self.clear_display()
        self.add_system_message('⏳ AI正在创建角色...')
        self.send_btn.config(state=tk.DISABLED)
        
        # 优化后的简短提示词
        create_prompt = """你是《冰与火之歌》游戏主持人。时间：劳勃国王赦免巴利斯坦当日。

创建一个新生儿角色，随机选择身份（史塔克家族/私生子/自由城邦/骑士家族/平民）。

必须按此格式回复：
姓名: [维斯特洛风格姓名]
身份: [简短描述，20字内]
地点: [出生地]
金龙: [0-10]
银鹿: [0-100]
铜星: [0-1000]

[开场故事]
用2-3句话描述出生场景。

状态更新:
身体: 健康
精神: 平静
饥饿: 饱足
疲劳: 精力充沛"""
        
        Thread(target=self.call_ai_thread, args=(create_prompt, True), daemon=True).start()
    
    def send_action(self):
        """发送玩家行动"""
        if not self.game_state['game_started']:
            messagebox.showwarning('提示', '请先开始新游戏！')
            return
        
        if self.is_processing:
            return
        
        action = self.player_input.get('1.0', tk.END).strip()
        if not action:
            return
        
        self.add_story_entry(action, is_player=True)
        self.player_input.delete('1.0', tk.END)
        
        self.send_btn.config(state=tk.DISABLED)
        self.player_input.config(state=tk.DISABLED)
        
        # 简短的游戏提示词
        context = '\n'.join([e['text'][:100] for e in self.game_state['story_log'][-3:]])
        
        prompt = f"""《冰与火之歌》世界，劳勃国王时代。

角色: {self.game_state['character']['name']} - {self.game_state['character']['identity']}
地点: {self.game_state['character']['location']}
最近情况: {context}

玩家行动: {action}

要求:
1. 用2-3句话描述结果
2. 真实后果（可能受伤/死亡）
3. 更新状态（身体/精神/饥饿/疲劳/财产/地点）

格式:
[故事]
简短描述...

状态更新:
身体: [状态]
精神: [状态]
饥饿: [状态]
疲劳: [状态]
金龙: [数量]
银鹿: [数量]
铜星: [数量]
地点: [位置]"""
        
        Thread(target=self.call_ai_thread, args=(prompt, False), daemon=True).start()
    
    def call_ai_thread(self, prompt, is_creation):
        """调用AI（非流式）"""
        self.is_processing = True
        print(f"[调试] 调用AI: {self.game_state['current_model']}")
        
        try:
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.game_state['current_model'],
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'num_predict': 500  # 限制长度加快速度
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                ai_response = response.json()['response']
                print(f"[调试] 响应长度: {len(ai_response)}")
                self.root.after(0, self.parse_ai_response, ai_response, is_creation)
            else:
                self.root.after(0, self.add_system_message, f'✗ 失败: HTTP {response.status_code}')
                
        except Exception as e:
            print(f"[调试] 错误: {e}")
            self.root.after(0, self.add_system_message, f'✗ 错误: {str(e)}')
        finally:
            self.is_processing = False
            self.root.after(0, self._enable_input)
    
    def _enable_input(self):
        """重新启用输入"""
        self.send_btn.config(state=tk.NORMAL)
        self.player_input.config(state=tk.NORMAL)
        self.player_input.focus()
    
    def parse_ai_response(self, response, is_creation):
        """解析AI回应"""
        story_text = response
        
        # 提取状态
        status_match = re.search(r'状态更新[：:](.*?)(?:\n\n|$)', response, re.DOTALL | re.IGNORECASE)
        if status_match:
            self.update_game_state(status_match.group(1))
            story_text = re.sub(r'状态更新[：:].*$', '', response, flags=re.DOTALL | re.IGNORECASE).strip()
        
        # 角色创建
        if is_creation:
            name_match = re.search(r'姓名[：:]\s*(.+)', response)
            identity_match = re.search(r'身份[：:]\s*(.+)', response)
            location_match = re.search(r'地点[：:]\s*(.+)', response)
            
            if name_match:
                self.game_state['character']['name'] = name_match.group(1).strip()
            if identity_match:
                self.game_state['character']['identity'] = identity_match.group(1).strip()
            if location_match:
                self.game_state['character']['location'] = location_match.group(1).strip()
            
            self.game_state['character']['age'] = 0
            self.game_state['game_started'] = True
            self.update_ui()
            self.add_system_message('✓ 角色创建成功！')
        
        self.add_story_entry(story_text, is_player=False)
    
    def update_game_state(self, status_text):
        """更新游戏状态"""
        updates = {
            '身体': 'health', '精神': 'mental', '饥饿': 'hunger', 
            '疲劳': 'fatigue', '金龙': 'gold_dragons', '银鹿': 'silver_stags',
            '铜星': 'copper_stars', '地点': 'location'
        }
        
        for key, prop in updates.items():
            match = re.search(rf'{key}[：:]\s*(.+)', status_text)
            if match:
                value = match.group(1).strip()
                try:
                    self.game_state['character'][prop] = int(value)
                except:
                    self.game_state['character'][prop] = value
        
        self.update_ui()
    
    def update_ui(self):
        """更新UI显示"""
        char = self.game_state['character']
        
        self.labels['name'].config(text=char['name'] or '未知')
        self.labels['identity'].config(text=char['identity'] or '-')
        self.labels['age'].config(text=f"{char['age']}岁")
        self.labels['location'].config(text=char['location'] or '-')
        
        self.status_labels['health'].config(text=char['health'])
        self.status_labels['mental'].config(text=char['mental'])
        self.status_labels['hunger'].config(text=char['hunger'])
        self.status_labels['fatigue'].config(text=char['fatigue'])
        
        self.labels['gold_dragons'].config(text=str(char['gold_dragons']))
        self.labels['silver_stags'].config(text=str(char['silver_stags']))
        self.labels['copper_stars'].config(text=str(char['copper_stars']))
    
    def add_story_entry(self, text, is_player):
        """添加故事条目"""
        entry = {
            'text': text,
            'is_player': is_player,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.game_state['story_log'].append(entry)
        
        self.game_display.config(state=tk.NORMAL)
        
        prefix = '⚔️ 你的行动' if is_player else '🏰 世界回应'
        self.game_display.insert(tk.END, f'\n[{entry["timestamp"]}] {prefix}\n', 'timestamp')
        
        tag = 'player' if is_player else 'ai'
        self.game_display.insert(tk.END, f'{text}\n', tag)
        
        self.game_display.config(state=tk.DISABLED)
        self.game_display.see(tk.END)
    
    def add_system_message(self, message):
        """添加系统消息"""
        self.game_display.config(state=tk.NORMAL)
        self.game_display.insert(tk.END, f'\n[系统] {message}\n', 'system')
        self.game_display.config(state=tk.DISABLED)
        self.game_display.see(tk.END)
    
    def clear_display(self):
        """清空显示区"""
        self.game_display.config(state=tk.NORMAL)
        self.game_display.delete('1.0', tk.END)
        self.game_display.config(state=tk.DISABLED)
    
    def save_game(self):
        """保存游戏"""
        if not self.game_state['game_started']:
            messagebox.showwarning('提示', '还没有开始游戏！')
            return
        
        save_name = simpledialog.askstring(
            '保存游戏',
            '请输入存档名称：',
            initialvalue=f"{self.game_state['character']['name']}_{datetime.now().strftime('%m%d')}"
        )
        
        if not save_name:
            return
        
        save_data = {
            'name': save_name,
            'date': datetime.now().isoformat(),
            'state': self.game_state
        }
        
        filename = os.path.join(self.save_dir, f"{save_name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        self.add_system_message(f'💾 已保存: {save_name}')
    
    def load_game(self):
        """读取存档"""
        saves = []
        if os.path.exists(self.save_dir):
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            saves.append((filename, json.load(f)))
                    except:
                        continue
        
        if not saves:
            messagebox.showinfo('提示', '没有找到存档！')
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title('读取存档')
        dialog.geometry('500x400')
        dialog.configure(bg='#2a2318')
        
        tk.Label(dialog, text='选择存档', bg='#2a2318', fg='#d4af37',
                font=('Georgia', 16, 'bold')).pack(pady=15)
        
        listbox = tk.Listbox(dialog, bg='#0d0d0a', fg='#e8dcc8',
                            font=('Microsoft YaHei', 11), selectmode=tk.SINGLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for filename, save_data in saves:
            date_str = datetime.fromisoformat(save_data['date']).strftime('%m-%d %H:%M')
            listbox.insert(tk.END, f"{save_data['name']} - {date_str}")
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                _, save_data = saves[selection[0]]
                self.game_state = save_data['state']
                self.update_ui()
                
                self.clear_display()
                for entry in self.game_state['story_log']:
                    self.game_display.config(state=tk.NORMAL)
                    prefix = '⚔️ 你的行动' if entry['is_player'] else '🏰 世界回应'
                    self.game_display.insert(tk.END, f'\n[{entry["timestamp"]}] {prefix}\n', 'timestamp')
                    tag = 'player' if entry['is_player'] else 'ai'
                    self.game_display.insert(tk.END, f'{entry["text"]}\n', tag)
                    self.game_display.config(state=tk.DISABLED)
                
                dialog.destroy()
                self.add_system_message('📂 存档已读取')
        
        tk.Button(dialog, text='读取', command=load_selected, bg='#4a7c59',
                 fg='#ffffff', font=('Microsoft YaHei', 12, 'bold')).pack(pady=10)
    
    def on_enter_key(self, event):
        """Enter键处理"""
        if not event.state & 1:
            self.send_action()
            return 'break'

def main():
    root = tk.Tk()
    app = ASOIAFGame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
