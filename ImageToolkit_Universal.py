import os
import sys
import threading
import datetime
from tkinter import messagebox, filedialog
import pandas as pd
from PIL import Image

try:
    import customtkinter as ctk
    from customtkinter import CTkImage
except ImportError:
    import tkinter.messagebox
    tkinter.messagebox.showerror("缺少依赖", "请先运行启动脚本安装 customtkinter 库！\npip install customtkinter")
    sys.exit(1)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = False 
except ImportError:
    HAS_DND = False

class UniversalImageTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 全局配置 ---
        self.title("Image Inspector & Optimizer - 图片体检与优化器")
        self.geometry("1100x800")
        ctk.set_appearance_mode("Light") 
        
        # --- 调色板 (Clean & Bright Palette) ---
        self.c_bg_main = "#F3F7FA"    # 极淡的冰蓝灰
        self.c_sidebar = "#FFFFFF"    # 侧边栏纯白
        self.c_card    = "#FFFFFF"    # 卡片纯白
        self.c_text    = "#1F2937"    # 深黑灰
        self.c_accent  = "#2563EB"    # 亮蓝色
        self.c_accent_light = "#EFF6FF" 
        
        # New Orange Theme for Optimizer
        self.c_orange  = "#EA580C"    # 活力橙 (Orange 600)
        self.c_orange_hover = "#C2410C"
        self.c_orange_bg = "#FFF7ED"  # 极淡橙
        self.c_orange_border = "#FFEDD5"
        
        self.c_border  = "#E5E7EB"    # 淡边框

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.is_processing = False
        self._init_variables()
        self.configure(fg_color=self.c_bg_main)
        
        # --- 1. 左侧导航栏 Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.c_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        sep = ctk.CTkFrame(self.sidebar_frame, width=2, fg_color=self.c_border)
        sep.grid(row=0, column=1, rowspan=10, sticky="ns")

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IMAGE\nINSPECTOR\n& OPTIMIZER", 
                                       font=ctk.CTkFont(family="SimSun", size=18, weight="bold"), text_color=self.c_accent)
        self.logo_label.grid(row=0, column=0, padx=25, pady=(30, 20), sticky="w")
        
        # Nav Buttons
        self.btn_inspector = self._create_nav_btn("📊 图片体检 (Inspector)", self.show_inspector)
        self.btn_inspector.grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        self.btn_optimizer = self._create_nav_btn("🏭 标准化车间 (Optimizer)", self.show_optimizer)
        self.btn_optimizer.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        # Version
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v5.1 Orange UI\nDesign By Gemini", 
                                          font=ctk.CTkFont(family="SimSun", size=10), text_color="gray60")
        self.version_label.grid(row=5, column=0, padx=20, pady=20)

        # --- 2. Right Panel ---
        self.right_panel = ctk.CTkFrame(self, corner_radius=0, fg_color=self.c_bg_main)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.frame_inspector = InspectorFrame(self.right_panel, self)
        self.frame_optimizer = OptimizerFrame(self.right_panel, self)

        self.show_inspector()

    def _create_nav_btn(self, text, cmd):
        return ctk.CTkButton(self.sidebar_frame, text=text, height=45, corner_radius=10, 
                             font=ctk.CTkFont(family="SimSun", size=14, weight="bold"),
                             fg_color="transparent", 
                             text_color=self.c_text, 
                             hover_color=self.c_accent_light,
                             anchor="w", command=cmd)

    def _init_variables(self):
        self.ins_subfolder = ctk.BooleanVar(value=True)
        self.ins_integrity = ctk.BooleanVar(value=True)
        self.opt_r1_w = ctk.IntVar(value=1920)
        self.opt_r1_mb = ctk.DoubleVar(value=0.5)
        self.opt_r1_tw = ctk.IntVar(value=1920)
        self.opt_r1_q = ctk.IntVar(value=80)
        self.opt_r2_min = ctk.IntVar(value=800)
        self.opt_r2_max = ctk.IntVar(value=1200)
        self.opt_r2_mb = ctk.DoubleVar(value=0.3)
        self.opt_r2_tw = ctk.IntVar(value=800)
        self.opt_r2_q = ctk.IntVar(value=70)
        self.opt_r3_w = ctk.IntVar(value=400)
        self.opt_r3_kb = ctk.IntVar(value=30)
        self.opt_r3_tkb = ctk.IntVar(value=30)

    def show_inspector(self):
        self._highlight_nav(self.btn_inspector, self.c_accent, self.c_accent_light)
        self.frame_optimizer.grid_forget()
        self.frame_inspector.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

    def show_optimizer(self):
        self._highlight_nav(self.btn_optimizer, self.c_orange, self.c_orange_bg)
        self.frame_inspector.grid_forget()
        self.frame_optimizer.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

    def _highlight_nav(self, active_btn, color, bg):
        for btn in [self.btn_inspector, self.btn_optimizer]:
            btn.configure(fg_color="transparent", text_color=self.c_text)
        active_btn.configure(fg_color=bg, text_color=color)

# --- Inspector (Blue Theme) ---
class InspectorFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.c_card, corner_radius=20)
        self.app = app
        
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(fill="x", padx=40, pady=(40, 0))
        ctk.CTkLabel(title_box, text="图片数据体检中心", font=ctk.CTkFont(family="SimSun", size=26, weight="bold"), text_color=app.c_text).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Dashboard / 安全无损 · 深度扫描 · 自动报表", font=ctk.CTkFont(family="SimSun", size=13), text_color="gray50").pack(anchor="w", pady=(5,0))

        self.hero_btn = ctk.CTkButton(self, text="  📁  点击选择文件夹开始分析  ", 
                                      font=ctk.CTkFont(family="SimSun", size=18, weight="bold"),
                                      height=90, 
                                      fg_color=app.c_accent_light, text_color=app.c_accent, hover_color="#DBEAFE",
                                      corner_radius=15, border_width=2, border_color="#BFDBFE",
                                      command=self.select_folder)
        self.hero_btn.pack(fill="x", padx=40, pady=30)

        opt_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=10)
        opt_frame.pack(fill="x", padx=40, pady=0)
        ctk.CTkCheckBox(opt_frame, text="深度遍历 (包含子目录)", font=ctk.CTkFont(family="SimSun", size=13), fg_color=app.c_accent, text_color=app.c_text, variable=app.ins_subfolder).pack(side="left", padx=20, pady=15)
        ctk.CTkCheckBox(opt_frame, text="文件完整性校验 (Detect Corruption)", font=ctk.CTkFont(family="SimSun", size=13), fg_color=app.c_accent, text_color=app.c_text, variable=app.ins_integrity).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(self, text="运行日志", font=ctk.CTkFont(family="SimSun", size=14, weight="bold"), text_color=app.c_text).pack(anchor="w", padx=40, pady=(30,10))
        self.log_box = ctk.CTkTextbox(self, corner_radius=12, fg_color="#F8FAFC", text_color="#374151", font=ctk.CTkFont(family="SimSun", size=12), border_width=1, border_color=app.c_border)
        self.log_box.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
    def log(self, msg):
        self.log_box.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    # --- Inspector Logic (Ported from app.py) ---
    def select_folder(self):
        f = filedialog.askdirectory()
        if f: self.run_analysis(f)

    def run_analysis(self, folder):
        self.hero_btn.configure(text=f"⏳ 分析中... {os.path.basename(folder)}", state="disabled")
        t = threading.Thread(target=self._process, args=(folder,))
        t.daemon = True
        t.start()

    def _process(self, folder):
        self.log(f"Start Analyzing: {folder}")
        
        # 1. Collect Files
        exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.psd'}
        files = []
        if self.app.ins_subfolder.get():
            for r,_,fs in os.walk(folder):
                for f in fs:
                    if os.path.splitext(f)[1].lower() in exts: files.append(os.path.join(r,f))
        else:
            for f in os.listdir(folder):
                if os.path.isfile(os.path.join(folder,f)) and os.path.splitext(f)[1].lower() in exts:
                    files.append(os.path.join(folder,f))
        
        total = len(files)
        if total == 0: 
            self.log("No images found.")
            self.app.after(0, lambda: self._finish(None))
            return

        # 2. Analyze
        data = []
        errs = 0
        size_sum = 0
        fmt_count = {}

        for i, fp in enumerate(files):
            # Simple progress log every 10%
            if total > 0 and i % max(1, total // 10) == 0:
                 self.app.after(0, lambda p=int((i/total)*100): self.hero_btn.configure(text=f"⏳ 分析中... {p}%"))

            info = {
                '文件名': os.path.basename(fp), 
                '相对路径': os.path.relpath(fp, folder), 
                '完整路径': fp,
                '状态': 'Pending',
                '格式': '', '色彩模式': '', '图片尺寸': '',
                '宽 (px)': '', '高 (px)': '', 
                '分辨率 (DPI)': '', '文件大小 (MB)': ''
            }
            
            if not os.path.exists(fp): 
                info['状态']='Missing'; errs+=1; data.append(info); continue
            
            try:
                sz = os.path.getsize(fp)/(1024*1024)
                size_sum += sz
                info['文件大小 (MB)'] = round(sz, 2)
                
                with Image.open(fp) as img:
                    if self.app.ins_integrity.get(): img.verify()
                    with Image.open(fp) as img2: self._enrich(img2, info)
                    info['状态']='OK'
                    fmt = info['格式']
                    fmt_count[fmt] = fmt_count.get(fmt,0) + 1
            except Exception as e:
                info['状态']='Error'; info['备注'] = str(e); errs+=1
            data.append(info)

        # 3. Save Report
        self._save_report(data, folder, total, errs, size_sum, fmt_count)

    def _enrich(self, img, info):
        w,h = img.size
        dpi = img.info.get('dpi')
        dpi_val = int(dpi[0]) if dpi else 72
        
        info.update({
            '格式': img.format, 
            '色彩模式': img.mode, 
            '图片尺寸': f"{w}x{h}",
            '宽 (px)': w, 
            '高 (px)': h, 
            '分辨率 (DPI)': dpi_val
        })

    def _save_report(self, data, folder, total, errs, sz_sum, fmts):
        fmt_str = ", ".join([f"{k}:{v}" for k,v in fmts.items()])
        cols = [
            '文件名', '完整路径', 
            '格式', '图片尺寸', '宽 (px)', '高 (px)', 
            '分辨率 (DPI)', '文件大小 (MB)'
        ]
        
        df = pd.DataFrame(data)
        df = df[cols] if set(cols).issubset(df.columns) else df
        
        summ = pd.DataFrame({
            "项目": ["时间", "路径", "文件总数", "有效", "无效", "总大小(MB)", "格式"],
            "内容": [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                folder, total, total-errs, errs, round(sz_sum,2), fmt_str
            ]
        })
        
        path = os.path.join(folder, f"Image_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        try:
            with pd.ExcelWriter(path, engine='openpyxl') as w:
                summ.to_excel(w, sheet_name='概览', index=False)
                df.to_excel(w, sheet_name='详细数据', index=False)
                # Auto width adjustment
                for sheet in w.sheets.values():
                    for column in sheet.columns:
                        try:
                            max_len = max(len(str(cell.value)) for cell in column)
                            sheet.column_dimensions[column[0].column_letter].width = max_len + 2
                        except: pass

            self.log(f"Report Generated: {path}")
            self.app.after(0, lambda: self._finish(path))
        except Exception as e: 
            self.log(f"Save Error: {e}")
            self.app.after(0, lambda: self._finish(None))

    def _finish(self, out_path):
        self.hero_btn.configure(text="  📁  点击选择文件夹开始分析  ", state="normal")
        if out_path:
            messagebox.showinfo("完成", f"分析报告生成完毕！\n{out_path}")
            os.startfile(os.path.dirname(out_path))
        else:
             messagebox.showinfo("提示", "分析过程结束（未生成报告或出错）")

# --- Optimizer (Orange Theme) ---
class OptimizerFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.c_card, corner_radius=20)
        self.app = app
        
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(fill="x", padx=40, pady=(40, 0))
        # Orange Title
        ctk.CTkLabel(title_box, text="标准化处理车间", font=ctk.CTkFont(family="SimSun", size=26, weight="bold"), text_color=app.c_orange).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Workshop / 三级分层逻辑 · 自动压图 · 物理隔离", font=ctk.CTkFont(family="SimSun", size=13), text_color="gray50").pack(anchor="w", pady=(5,0))

        # Rules Card (Orange bg)
        r_frame = ctk.CTkFrame(self, fg_color=app.c_orange_bg, corner_radius=15, border_width=1, border_color=app.c_orange_border)
        r_frame.pack(fill="x", padx=40, pady=30)
        
        self._add_rule_row(r_frame, "🔴 超大图", app.opt_r1_w, app.opt_r1_mb, app.opt_r1_tw, app.opt_r1_q)
        ctk.CTkFrame(r_frame, height=1, fg_color="white").pack(fill="x", padx=20) 
        self._add_rule_row(r_frame, "🔵 普通图 (宽800~1200)", None, app.opt_r2_mb, app.opt_r2_tw, app.opt_r2_q) 
        ctk.CTkFrame(r_frame, height=1, fg_color="white").pack(fill="x", padx=20)
        self._add_rule_row(r_frame, "⚪ 小图", app.opt_r3_w, app.opt_r3_kb, app.opt_r3_tkb, None, is_small=True)

        # Action Button (Orange)
        self.action_btn = ctk.CTkButton(self, text="  🚀  选择文件夹开始处理 (Output: _Optimized)  ", 
                                        font=ctk.CTkFont(family="SimSun", size=18, weight="bold"),
                                        height=70, 
                                        fg_color=app.c_orange, hover_color=app.c_orange_hover,
                                        corner_radius=15,
                                        command=self.select_folder)
        self.action_btn.pack(fill="x", padx=40, pady=10)

        # Logs
        ctk.CTkLabel(self, text="处理日志", font=ctk.CTkFont(family="SimSun", size=14, weight="bold"), text_color=app.c_text).pack(anchor="w", padx=40, pady=(30,10))
        self.log_box = ctk.CTkTextbox(self, corner_radius=12, fg_color="#F8FAFC", text_color="#374151", font=ctk.CTkFont(family="SimSun", size=12), border_width=1, border_color=app.c_border)
        self.log_box.pack(fill="both", expand=True, padx=40, pady=(0, 40))

    def _add_rule_row(self, p, label, v1, v2, v3, v4, is_small=False):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", pady=12, padx=15)
        ctk.CTkLabel(f, text=label, width=130, anchor="w", font=ctk.CTkFont(family="SimSun", size=14, weight="bold"), text_color=self.app.c_orange).pack(side="left")
        
        if not is_small and v1: 
            ctk.CTkLabel(f, text="宽 >", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
            self._entry(f, v1)
        
        unit = "KB" if is_small else "MB"
        ctk.CTkLabel(f, text=f"大小 >", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
        self._entry(f, v2)
        ctk.CTkLabel(f, text=unit, font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left", padx=(0,10))
        
        ctk.CTkLabel(f, text="➜", text_color=self.app.c_orange, font=ctk.CTkFont(family="SimSun", weight="bold", size=16)).pack(side="left", padx=15)
        
        if is_small:
            ctk.CTkLabel(f, text="限制至", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
            self._entry(f, v3)
            ctk.CTkLabel(f, text="KB", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
        else:
            ctk.CTkLabel(f, text="宽:", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
            self._entry(f, v3)
            ctk.CTkLabel(f, text="PX  质:", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")
            self._entry(f, v4)
            ctk.CTkLabel(f, text="%", font=ctk.CTkFont(family="SimSun"), text_color="gray40").pack(side="left")

    def _entry(self, p, v):
        ctk.CTkEntry(p, textvariable=v, width=65, height=30, corner_radius=6, 
                     fg_color="white", border_width=1, border_color="#E5E7EB", text_color="black",
                     font=ctk.CTkFont(family="SimSun")).pack(side="left", padx=5)

    def log(self, msg):
        self.log_box.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    def select_folder(self):
        f = filedialog.askdirectory()
        if f: self.run_prop(f)
    
    def run_prop(self, folder):
        self.action_btn.configure(text="🔥 处理中...", state="disabled")
        t = threading.Thread(target=self._process, args=(folder,))
        t.daemon=True
        t.start()
        
    def _process(self, folder):
        self.log(f"Start Processing: {folder}")
        out_base = os.path.join(folder, "已标准化_Optimized")
        if not os.path.exists(out_base): os.makedirs(out_base)
        
        files = []
        for r,_,fs in os.walk(folder):
            for f in fs:
                if f.lower().endswith(('.jpg','.png','.jpeg','.webp')): files.append(os.path.join(r,f))

        r1 = (self.app.opt_r1_w.get(), self.app.opt_r1_mb.get(), self.app.opt_r1_tw.get(), self.app.opt_r1_q.get())
        r2 = (self.app.opt_r2_min.get(), self.app.opt_r2_max.get(), self.app.opt_r2_mb.get(), self.app.opt_r2_tw.get(), self.app.opt_r2_q.get())
        r3 = (self.app.opt_r3_w.get(), self.app.opt_r3_kb.get(), self.app.opt_r3_tkb.get())

        total = len(files)
        chg = 0
        report_data = [] # Store details for Excel
        total_org_size = 0.0
        total_opt_size = 0.0
        
        for i, fp in enumerate(files):
             # Progress update
            if total > 0 and i % max(1, total//20) == 0:
                 self.app.after(0, lambda p=int((i/total)*100): self.action_btn.configure(text=f"🔥 处理中... {p}%"))
            
            # Common info
            fname = os.path.basename(fp)
            entry = {
                '文件名': fname,
                '状态': 'Unknown',
                '操作详情': '',
                '原始尺寸': '', '原始大小(MB)': 0.0,
                '优化后尺寸': '', '优化后大小(MB)': 0.0,
                '节省空间(MB)': 0.0
            }

            try:
                 # Original Stats
                 org_sz = os.path.getsize(fp)
                 total_org_size += org_sz
                 entry['原始大小(MB)'] = round(org_sz / (1024*1024), 2)
                 with Image.open(fp) as tmp_img:
                     entry['原始尺寸'] = f"{tmp_img.width}x{tmp_img.height}"
                 
                 out = os.path.join(out_base, os.path.relpath(fp, folder))
                 d = os.path.dirname(out)
                 if not os.path.exists(d): os.makedirs(d)
                 
                 res, act = self._apply(fp, out, r1, r2, r3)
                 
                 # Optimized Stats
                 if os.path.exists(out):
                     opt_sz = os.path.getsize(out)
                     total_opt_size += opt_sz
                     entry['优化后大小(MB)'] = round(opt_sz / (1024*1024), 2)
                     entry['节省空间(MB)'] = round((org_sz - opt_sz) / (1024*1024), 2)
                     with Image.open(out) as tmp_img:
                         entry['优化后尺寸'] = f"{tmp_img.width}x{tmp_img.height}"
                 
                 if res == 'Opt': 
                     self.log(f"Synced: {fname} -> {act}")
                     entry['状态'] = 'Modified'
                     entry['操作详情'] = act
                     chg += 1
                 elif res == 'Skip':
                     import shutil
                     shutil.copy2(fp, out)
                     
                     # Re-read stats after copy
                     opt_sz = os.path.getsize(out)
                     total_opt_size += opt_sz
                     entry['优化后大小(MB)'] = round(opt_sz / (1024*1024), 2)
                     entry['优化后尺寸'] = entry['原始尺寸'] # Same as original
                     
                     self.log(f"Copy: {fname}")
                     entry['状态'] = 'Skipped'
                     entry['操作详情'] = 'Direct Copy (No Rule Triggered)'
                 else:
                     entry['状态'] = 'Error'
                     entry['操作详情'] = 'Processing Failed'

            except Exception as e: 
                self.log(f"Error {fname}: {e}")
                entry['状态'] = 'Error'
                entry['操作详情'] = str(e)
            
            report_data.append(entry)
        
        self._save_opt_report(report_data, out_base, total, chg, total_org_size, total_opt_size)
        self.app.after(0, lambda: self._finish(out_base, total, chg))

    def _save_opt_report(self, data, out_folder, total, modified, org_bytes, opt_bytes):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            saved_bytes = org_bytes - opt_bytes
            saved_mb = saved_bytes / (1024*1024)
            ratio = (saved_bytes / org_bytes * 100) if org_bytes > 0 else 0
            
            summ = pd.DataFrame({
                "项目": ["处理时间", "输出目录", "文件总数", "修改数量", "未修改/复制", 
                         "原始总大小(MB)", "处理后总大小(MB)", "总节省空间(MB)", "压缩率"],
                "数值": [
                    timestamp, out_folder, total, modified, total - modified,
                    round(org_bytes/(1024*1024), 2), 
                    round(opt_bytes/(1024*1024), 2),
                    round(saved_mb, 2),
                    f"{ratio:.1f}%"
                ]
            })
            
            df = pd.DataFrame(data)
            col_order = ['文件名', '状态', '操作详情', '原始尺寸', '原始大小(MB)', '优化后尺寸', '优化后大小(MB)', '节省空间(MB)']
            df = df[col_order] if set(col_order).issubset(df.columns) else df
            
            rpt_path = os.path.join(out_folder, f"Optimization_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            
            with pd.ExcelWriter(rpt_path, engine='openpyxl') as w:
                summ.to_excel(w, sheet_name='概览', index=False)
                df.to_excel(w, sheet_name='详细记录', index=False)
                
                # Auto width
                for sheet in w.sheets.values():
                    for column in sheet.columns:
                        try:
                            max_len = max(len(str(cell.value)) for cell in column)
                            sheet.column_dimensions[column[0].column_letter].width = max_len + 2
                        except: pass
                        
            self.log(f"Report Saved: {rpt_path}")
        except Exception as e:
            self.log(f"Report Error: {e}")

    def _apply(self, inp, out, r1, r2, r3):
        # Implementation from processor.py matched logic
        try:
            sz = os.path.getsize(inp)/(1024*1024); sz_kb = sz*1024
            img = Image.open(inp); w,h = img.size
            if w > r1[0] and sz > r1[1]: # R1
                r = r1[2]/w; img = img.resize((r1[2], int(h*r)), Image.LANCZOS).convert("RGB")
                img.save(out, "JPEG", quality=r1[3]); return 'Opt', f'R1 Resize {r1[2]} Q{r1[3]}'
            elif r2[0] <= w <= r2[1] and sz > r2[2]: # R2
                r = r2[3]/w; img = img.resize((r2[3], int(h*r)), Image.LANCZOS).convert("RGB")
                img.save(out, "JPEG", quality=r2[4]); return 'Opt', f'R2 Resize {r2[3]} Q{r2[4]}'
            elif w < r3[0] and sz_kb > r3[1]: # R3
                img=img.convert("RGB"); q=90
                while q>10:
                    img.save(out, "JPEG", quality=q)
                    if os.path.getsize(out) < r3[2]*1024: break
                    q-=10
                return 'Opt', f'R3 Limit <{r3[2]}kb'
            return 'Skip', '-'
        except: return 'Err', '-'

    def _finish(self, out, total=0, chg=0):
        self.action_btn.configure(text="  🚀  选择文件夹开始处理 (Output: _Optimized)  ", state="normal")
        messagebox.showinfo("完成", f"处理完成! (优化: {chg}/{total})\n位置: {out}")
        if out and os.path.exists(out): os.startfile(out)

if __name__ == "__main__":
    app = UniversalImageTool()
    app.mainloop()
