import os
import sys
import threading
import datetime
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from PIL import Image, UnidentifiedImageError
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class ImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Inspector v3.0")
        self.root.geometry("960x720")
        
        # --- Design System (Design Director Edition) ---
        self.colors = {
            "bg": "#F5F7FA",           # Cool Light Grey
            "card": "#FFFFFF",         # Pure White
            "primary": "#1A73E8",      # Google Blue
            "primary_light": "#E8F0FE",# Light Blue Wash
            "text": "#202124",         # Ink
            "subtext": "#5F6368",      # Graphite
            "border": "#E0E0E0",       # Subtle Border
            "success": "#34A853",
            "warning": "#F9AB00"
        }
        self.fonts = {
            "display": ("SimSun", 20, "bold"),
            "heading": ("SimSun", 11, "bold"),
            "body": ("SimSun", 10),
            "small": ("SimSun", 9)
        }
        self.root.configure(bg=self.colors["bg"])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", background=self.colors["primary"], troughcolor=self.colors["primary_light"], bordercolor=self.colors["bg"])
        
        self.check_subfolders = BooleanVar(value=True)
        self.check_integrity = BooleanVar(value=True)

        self._build_ui()
        self.is_processing = False

    def _build_ui(self):
        # 1. Header Card
        header = self._create_card(self.root, pady=(20, 15))
        Label(header, text="✨ 图片数据体检中心", font=self.fonts["display"], fg=self.colors["text"], bg=self.colors["card"]).pack(side=LEFT)
        Label(header, text="DESIGN DIRECTOR EDITION", font=self.fonts["small"], fg=self.colors["primary"], bg=self.colors["card"]).pack(side=LEFT, padx=15, pady=(8,0))
        
        # 2. Hero Drop Zone (The Centerpiece)
        drop_area = self._create_card(self.root, pady=0)
        
        # Dashed Border Simulation
        self.drop_frame = Frame(drop_area, bg=self.colors["primary_light"], bd=2, relief="solid") # Solid border, colored
        self.drop_frame.config(highlightbackground=self.colors["primary"], highlightthickness=1)
        self.drop_frame.pack(fill=X, padx=5, pady=5)
        
        if HAS_DND:
            self.drop_label = Label(
                self.drop_frame,
                text="📂 拖入文件夹 或 Excel清单\n\n( 智能识别 · 读取只读 · 自动导出 )",
                font=("SimSun", 14),
                fg=self.colors["primary"],
                bg=self.colors["primary_light"],
                width=60, height=6,
                cursor="hand2"
            )
            self.drop_label.pack(fill=BOTH, expand=True, padx=2, pady=2)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
            self.drop_label.bind("<Button-1>", lambda e: self.select_folder_fallback())
        else:
            Button(self.drop_frame, text="选择数据源", command=self.select_folder_fallback, bg=self.colors["primary_light"]).pack(fill=BOTH, pady=40)

        # 3. Settings & Status Grid
        settings_area = self._create_card(self.root, pady=15)
        
        # Left: Settings
        opts = Frame(settings_area, bg=self.colors["card"])
        opts.pack(side=LEFT, fill=Y)
        Label(opts, text="扫描配置", font=self.fonts["heading"], fg=self.colors["text"], bg=self.colors["card"]).pack(anchor="w", pady=(0,5))
        Checkbutton(opts, text="深度遍历 (含子文件夹)", variable=self.check_subfolders, bg=self.colors["card"], font=self.fonts["body"], activebackground=self.colors["card"]).pack(anchor="w")
        Checkbutton(opts, text="健康度检查 (坏图扫描)", variable=self.check_integrity, bg=self.colors["card"], font=self.fonts["body"], activebackground=self.colors["card"]).pack(anchor="w")

        # Right: Progress Info
        prog = Frame(settings_area, bg=self.colors["card"])
        prog.pack(side=RIGHT, fill=BOTH, expand=True, padx=(40, 0))
        Label(prog, text="当前任务状态", font=self.fonts["heading"], fg=self.colors["text"], bg=self.colors["card"]).pack(anchor="w", pady=(0,5))
        
        self.status_label = Label(prog, text="系统待机中...", font=self.fonts["body"], fg=self.colors["subtext"], bg=self.colors["card"], anchor="w")
        self.status_label.pack(fill=X)
        
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(prog, variable=self.progress_var, length=100)
        self.progress_bar.pack(fill=X, pady=5)

        # 4. Logs Console (Refined)
        log_card = self._create_card(self.root, pady=0, expand=True)
        lbl_bar = Frame(log_card, bg=self.colors["card"])
        lbl_bar.pack(fill=X, pady=(0,5))
        Label(lbl_bar, text="运行日志", font=self.fonts["heading"], fg=self.colors["text"], bg=self.colors["card"]).pack(side=LEFT)
        Label(lbl_bar, text="Real-time Logs", font=self.fonts["small"], fg=self.colors["subtext"], bg=self.colors["card"]).pack(side=LEFT, padx=10)

        self.log_text = ScrolledText(log_card, height=6, font=("SimSun", 9), state='disabled', bg="#FAFAFA", relief="flat")
        self.log_text.config(highlightbackground=self.colors["border"], highlightthickness=1)
        self.log_text.pack(fill=BOTH, expand=True)

        # Footer
        Label(self.root, text="Antigravity Agent Design System", bg=self.colors["bg"], fg="#B0B8C4", font=self.fonts["small"]).pack(side=BOTTOM, pady=10)

    def _create_card(self, parent, pady=10, expand=False):
        f = Frame(parent, bg=self.colors["card"], padx=25, pady=20)
        # Shadow simulation (Bottom Border)
        f.pack(fill=BOTH if expand else X, expand=expand, padx=30, pady=pady)
        return f

    # --- Logic (Same as before) ---
    def log(self, message, level="INFO"):
        self.log_text.config(state='normal')
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(END)
        self.log_text.config(state='disabled')

    def handle_drop(self, event):
        if self.is_processing: return
        data = event.data.strip()
        if data.startswith('{') and data.endswith('}'): data = data[1:-1]
        
        if os.path.isdir(data): self.start_analysis_thread(data)
        elif data.lower().endswith(('.xlsx', '.xls')): self.start_excel_analysis_thread(data)
        else: self.log(f"无效文件: {data}")

    def select_folder_fallback(self):
        from tkinter import filedialog
        choice_win = Toplevel(self.root)
        choice_win.title("数据源")
        choice_win.geometry("300x120")
        choice_win.config(bg="white")
        Label(choice_win, text="请选择:", bg="white", font=self.fonts["body"]).pack(pady=10)
        f = Frame(choice_win, bg="white")
        f.pack()
        def pick(t):
            choice_win.destroy()
            if t=='d': 
                d = filedialog.askdirectory()
                if d: self.start_analysis_thread(d)
            else:
                f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
                if f: self.start_excel_analysis_thread(f)
        Button(f, text="文件夹", command=lambda:pick('d'), font=self.fonts["body"]).pack(side=LEFT, padx=10)
        Button(f, text="Excel", command=lambda:pick('e'), font=self.fonts["body"]).pack(side=LEFT, padx=10)

    def start_analysis_thread(self, folder_path):
        self.is_processing = True
        self.drop_label.config(text=f"⏳ 正在分析...\n{os.path.basename(folder_path)}", bg="#E6F4EA", fg="#137333")
        thread = threading.Thread(target=self.process_folder, args=(folder_path,))
        thread.daemon = True
        thread.start()

    def start_excel_analysis_thread(self, excel_path):
        self.is_processing = True
        self.drop_label.config(text=f"⏳ 正在读取...\n{os.path.basename(excel_path)}", bg="#E6F4EA", fg="#137333")
        thread = threading.Thread(target=self.process_from_excel, args=(excel_path,))
        thread.daemon = True
        thread.start()

    def process_from_excel(self, excel_path):
        self.log(f"Loading: {excel_path}")
        try:
            df = pd.read_excel(excel_path)
            path_col = None
            possible = ['path', 'file', 'filepath', 'filename', '文件路径', '路径', '地址']
            for c in df.columns:
                if any(p in str(c).lower() for p in possible): path_col=c; break
            
            if not path_col: path_col = df.columns[0]; self.log(f"路径列不明确，使用: {path_col}")
            
            base_dir = os.path.dirname(excel_path)
            paths = []
            for p in df[path_col].dropna().astype(str).tolist():
                paths.append(p if os.path.isabs(p) else os.path.join(base_dir, p))
            
            self.analyze_files(paths, base_dir)
        except Exception as e:
            self.log(f"Error: {e}")
            self.reset_ui()

    def process_folder(self, folder):
        exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.psd'}
        files = []
        if self.check_subfolders.get():
            for r,_,fs in os.walk(folder):
                for f in fs:
                    if os.path.splitext(f)[1].lower() in exts: files.append(os.path.join(r,f))
        else:
            for f in os.listdir(folder):
                if os.path.isfile(os.path.join(folder,f)) and os.path.splitext(f)[1].lower() in exts:
                    files.append(os.path.join(folder,f))
        self.analyze_files(files, folder)

    def analyze_files(self, files, out_dir):
        total = len(files)
        if total == 0: self.log("No images found."); self.reset_ui(); return
        
        data = []
        errs = 0
        size_sum = 0
        fmt_count = {}
        
        for i, fp in enumerate(files):
            if i%5==0: self.root.after(0, lambda p=(i/total)*100, f=fp: self.update_prog(p, f))
            
            # Initial info with defaults
            info = {
                '文件名': os.path.basename(fp), 
                '相对路径': os.path.relpath(fp, out_dir), 
                '完整路径': fp,
                '状态': 'Pending',
                # Pre-fill columns
                '格式': '', 
                '色彩模式': '', 
                '图片尺寸': '',
                '宽 (px)': '', 
                '高 (px)': '', 
                '分辨率 (DPI)': '', 
                '文件大小 (MB)': ''
            }
            
            if not os.path.exists(fp): info['状态']='Missing'; errs+=1; data.append(info); continue
            
            try:
                sz = os.path.getsize(fp)/(1024*1024)
                size_sum += sz
                info['文件大小 (MB)'] = round(sz, 2)
                
                with Image.open(fp) as img:
                    if self.check_integrity.get(): img.verify(); 
                    with Image.open(fp) as img2: self._enrich(img2, info)
                    info['状态']='OK'; 
                    fmt=info['格式']; fmt_count[fmt]=fmt_count.get(fmt,0)+1
            except Exception as e:
                info['状态']='Error'; info['备注']=str(e); errs+=1
            data.append(info)
            
        self.save_report(data, out_dir, total, errs, size_sum, fmt_count)
        self.reset_ui()

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

    def save_report(self, data, folder, total, errs, sz_sum, fmts):
        # Format the format counts string
        fmt_str = ", ".join([f"{k}:{v}" for k,v in fmts.items()])
        
        # ordered columns
        cols = [
            '文件名', '完整路径', 
            '格式', '图片尺寸', '宽 (px)', '高 (px)', 
            '分辨率 (DPI)', '文件大小 (MB)'
        ]
        
        df = pd.DataFrame(data)
        # Reorder if columns exist
        df = df[cols] if set(cols).issubset(df.columns) else df
        
        summ = pd.DataFrame({
            "项目": ["时间", "路径", "文件总数", "有效", "无效", "总大小(MB)", "格式"],
            "内容": [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                folder, 
                total, 
                total-errs, 
                errs, 
                round(sz_sum,2), 
                fmt_str
            ]
        })
        
        path = os.path.join(folder, f"Image_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        try:
            with pd.ExcelWriter(path, engine='openpyxl') as w:
                summ.to_excel(w, sheet_name='概览', index=False)
                df.to_excel(w, sheet_name='详细数据', index=False)
                
                # Auto-adjust column widths (Basic attempt)
                for sheet in w.sheets.values():
                    for column in sheet.columns:
                        try:
                            max_len = max(len(str(cell.value)) for cell in column)
                            adj_width = (max_len + 2)
                            sheet.column_dimensions[column[0].column_letter].width = adj_width
                        except: pass
                        
            messagebox.showinfo("完成", f"分析报告生成完毕！\n{path}")
            os.startfile(folder)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_prog(self, p, f):
        self.progress_var.set(p)
        self.status_label.config(text=f"Processing: {os.path.basename(f)}")

    def reset_ui(self):
        self.progress_var.set(0)
        self.is_processing = False
        self.root.after(0, lambda: self.drop_label.config(text="📂 拖入文件夹 或 Excel清单\n\n( 智能识别 · 读取只读 · 自动导出 )", bg=self.colors["primary_light"], fg=self.colors["primary"]))
        self.root.after(0, lambda: self.status_label.config(text="系统待机中..."))

if __name__ == "__main__":
    if HAS_DND: root = TkinterDnD.Tk()
    else: root = Tk()
    app = ImageAnalyzerApp(root)
    root.mainloop()
