import os
import sys
import threading
import datetime
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Optimizer Pro v3.0")
        self.root.geometry("1000x800")
        
        # --- Design System (Warm Action Theme) ---
        self.colors = {
            "bg": "#F5F7FA",
            "card": "#FFFFFF",
            "action": "#D93025",       # Google Red
            "action_light": "#FCE8E6", # Light Red Wash
            "text": "#202124",
            "subtext": "#5F6368",
            "border": "#E0E0E0",
            "input_bg": "#F1F3F4"
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
        self.style.configure("TProgressbar", background=self.colors["action"], troughcolor=self.colors["action_light"], bordercolor=self.colors["bg"])

        # Vars
        self.r1_w = IntVar(value=1920); self.r1_mb = DoubleVar(value=0.5); self.r1_tw = IntVar(value=1920); self.r1_q = IntVar(value=80)
        self.r2_min = IntVar(value=800); self.r2_max = IntVar(value=1200); self.r2_mb = DoubleVar(value=0.3); self.r2_tw = IntVar(value=800); self.r2_q = IntVar(value=70)
        self.r3_w = IntVar(value=400); self.r3_kb = IntVar(value=30); self.r3_tkb = IntVar(value=30)

        self._build_ui()
        self.is_processing = False

    def _build_ui(self):
        # 1. Header
        head = self._create_card(self.root, pady=(20, 15))
        Label(head, text="🔧 图片数据标准化车间", font=self.fonts["display"], fg=self.colors["text"], bg=self.colors["card"]).pack(side=LEFT)
        Label(head, text="DESIGN DIRECTOR EDITION", font=self.fonts["small"], fg=self.colors["action"], bg=self.colors["card"]).pack(side=LEFT, padx=15, pady=(8,0))
        
        # 2. Rules Configuration (The Control Panel)
        rules = self._create_card(self.root, pady=10)
        Label(rules, text="标准化规则配置 (Parameters)", font=self.fonts["heading"], fg=self.colors["text"], bg=self.colors["card"]).pack(anchor="w", pady=(0, 15))
        
        # Grid Container
        grid = Frame(rules, bg=self.colors["card"])
        grid.pack(fill=X)
        
        self._row(grid, "🔴 超大图规则", "宽 >", self.r1_w, "且 >", self.r1_mb, "MB", "➜ 缩放至", self.r1_tw, "px, 质", self.r1_q)
        self._row_range(grid, "🔵 普通图规则", "宽", self.r2_min, "-", self.r2_max, "且 >", self.r2_mb, "MB", "➜ 缩放至", self.r2_tw, "px, 质", self.r2_q)
        self._row(grid, "⚪ 小图规则", "宽 <", self.r3_w, "且 >", self.r3_kb, "KB", "➜ 限制至", self.r3_tkb, "KB", None, None, True)

        # 3. Drop Zone Action Area
        drop_area = self._create_card(self.root, pady=10)
        
        self.drop_frame = Frame(drop_area, bg=self.colors["action_light"], bd=2, relief="solid")
        self.drop_frame.config(highlightbackground=self.colors["action"], highlightthickness=1)
        self.drop_frame.pack(fill=X, padx=5, pady=5)
        
        if HAS_DND:
            self.drop_label = Label(
                self.drop_frame,
                text="⚠️ 将文件夹拖拽至此执行处理\n\n( 输出目录: 源文件夹/已标准化_Optimized )",
                font=("SimSun", 14, "bold"),
                fg=self.colors["action"],
                bg=self.colors["action_light"],
                width=60, height=5,
                cursor="hand2"
            )
            self.drop_label.pack(fill=BOTH, expand=True, padx=2, pady=2)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
            self.drop_label.bind("<Button-1>", lambda e: self.select_folder())
        else:
            Button(self.drop_frame, text="选择文件夹开始处理", command=self.select_folder, bg=self.colors["action_light"]).pack(fill=BOTH, pady=30)

        # 4. Status & Logs
        status_card = self._create_card(self.root, pady=10, expand=True)
        
        # Status Bar
        s_bar = Frame(status_card, bg=self.colors["card"])
        s_bar.pack(fill=X, pady=(0, 10))
        self.status_label = Label(s_bar, text="等待任务启动...", font=self.fonts["body"], fg=self.colors["subtext"], bg=self.colors["card"], anchor="w")
        self.status_label.pack(fill=X)
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(s_bar, variable=self.progress_var, length=100)
        self.progress_bar.pack(fill=X, pady=5)
        
        # Logs
        Label(status_card, text="处理日志 (Logs)", font=self.fonts["heading"], bg=self.colors["card"], anchor="w").pack(fill=X)
        self.log_text = ScrolledText(status_card, height=8, font=("SimSun", 9), state='disabled', bg="#FAFAFA", relief="flat")
        self.log_text.config(highlightbackground=self.colors["border"], highlightthickness=1)
        self.log_text.pack(fill=BOTH, expand=True, pady=5)
        
        # Tag Config
        self.log_text.tag_config("CHANGE", foreground=self.colors["action"])
        self.log_text.tag_config("SKIP", foreground="#9AA0A6")

        # Footer
        Label(self.root, text="Antigravity Agent Design System", bg=self.colors["bg"], fg="#B0B8C4", font=self.fonts["small"]).pack(side=BOTTOM, pady=10)

    def _create_card(self, parent, pady=10, expand=False):
        f = Frame(parent, bg=self.colors["card"], padx=25, pady=20)
        f.pack(fill=BOTH if expand else X, expand=expand, padx=30, pady=pady)
        return f

    def _entry(self, parent, var, width=5):
        e = Entry(parent, textvariable=var, width=width, bg=self.colors["input_bg"], font=self.fonts["body"], justify="center", relief="flat")
        # Simulate simple bottom border or just flat modern look
        e.pack(side=LEFT, padx=5)
        return e

    def _row(self, parent, label, l1, v1, l2, v2, l3, l4, v3, l5, v4=None, l6=None, is_kb=False):
        f = Frame(parent, bg=self.colors["card"], pady=6); f.pack(fill=X)
        Label(f, text=label, font=self.fonts["body"], bg=self.colors["card"], width=12, anchor="w").pack(side=LEFT)
        Label(f, text=l1, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v1)
        Label(f, text=l2, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v2)
        Label(f, text=l3, bg=self.colors["card"]).pack(side=LEFT)
        
        Label(f, text=l4, fg=self.colors["action"], bg=self.colors["card"], font=("SimSun", 10, "bold")).pack(side=LEFT, padx=15)
        self._entry(f, v3)
        Label(f, text=l5, bg=self.colors["card"]).pack(side=LEFT)
        if v4:
            self._entry(f, v4)
            if l6: Label(f, text=l6, bg=self.colors["card"]).pack(side=LEFT)

    def _row_range(self, parent, label, l1, v1, l2, v2, l3, v3, l4, l5, v4, l6, v5):
        f = Frame(parent, bg=self.colors["card"], pady=6); f.pack(fill=X)
        Label(f, text=label, font=self.fonts["body"], bg=self.colors["card"], width=12, anchor="w").pack(side=LEFT)
        Label(f, text=l1, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v1)
        Label(f, text=l2, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v2)
        Label(f, text=l3, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v3)
        Label(f, text=l4, bg=self.colors["card"]).pack(side=LEFT)
        
        Label(f, text=l5, fg=self.colors["action"], bg=self.colors["card"], font=("SimSun", 10, "bold")).pack(side=LEFT, padx=15)
        self._entry(f, v4)
        Label(f, text=l6, bg=self.colors["card"]).pack(side=LEFT)
        self._entry(f, v5)
        Label(f, text="%", bg=self.colors["card"]).pack(side=LEFT)

    # --- Logic ---
    def log(self, msg, tag="INFO"):
        self.log_text.config(state='normal')
        self.log_text.insert(END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n", tag)
        self.log_text.see(END)
        self.log_text.config(state='disabled')

    def select_folder(self):
        from tkinter import filedialog
        d = filedialog.askdirectory()
        if d: self.start_thread(d)

    def handle_drop(self, event):
        if self.is_processing: return
        data = event.data.strip()
        if data.startswith('{') and data.endswith('}'): data = data[1:-1]
        if os.path.isdir(data): self.start_thread(data)
        else: self.log("请拖入文件夹。", "SKIP")

    def start_thread(self, folder):
        self.is_processing = True
        self.drop_label.config(text=f"🔥 正在处理 {os.path.basename(folder)}...", bg="#FCE8E6")
        t = threading.Thread(target=self.process_folder, args=(folder,))
        t.daemon = True
        t.start()

    def process_folder(self, folder):
        supported = ('.jpg', '.jpeg', '.png', '.webp')
        files = []
        for root, _, fs in os.walk(folder):
            for f in fs:
                if f.lower().endswith(supported): files.append(os.path.join(root, f))
        
        total = len(files)
        if total == 0: self.log("No images."); self.reset_ui(); return
        self.log(f"Task Started: {total} images", "INFO")
        
        output_base = os.path.join(folder, "已标准化_Optimized")
        if not os.path.exists(output_base): os.makedirs(output_base)

        cnt=0; chg=0
        r1 = (self.r1_w.get(), self.r1_mb.get(), self.r1_tw.get(), self.r1_q.get())
        r2 = (self.r2_min.get(), self.r2_max.get(), self.r2_mb.get(), self.r2_tw.get(), self.r2_q.get())
        r3 = (self.r3_w.get(), self.r3_kb.get(), self.r3_tkb.get())
        
        report_data = [] # Store details for Excel
        total_org_size = 0.0
        total_opt_size = 0.0

        for i, fp in enumerate(files):
            if i%5==0: self.root.after(0, lambda p=(i/total)*100, f=fp: self._prog(p, f))
            
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

                out = os.path.join(output_base, os.path.relpath(fp, folder))
                if not os.path.exists(os.path.dirname(out)): os.makedirs(os.path.dirname(out))
                
                res, act = self._apply(fp, out, r1, r2, r3)
                
                # Optimized Stats
                if os.path.exists(out):
                     opt_sz = os.path.getsize(out)
                     total_opt_size += opt_sz
                     entry['优化后大小(MB)'] = round(opt_sz / (1024*1024), 2)
                     entry['节省空间(MB)'] = round((org_sz - opt_sz) / (1024*1024), 2)
                     with Image.open(out) as tmp_img:
                         entry['优化后尺寸'] = f"{tmp_img.width}x{tmp_img.height}"

                if res=='Opt': 
                    self.log(f"Auto-Fix: {os.path.basename(fp)} -> {act}", "CHANGE")
                    entry['状态'] = 'Modified'
                    entry['操作详情'] = act
                    chg+=1
                else: 
                    import shutil; shutil.copy2(fp, out)
                    
                    # Re-read stats after copy
                    opt_sz = os.path.getsize(out)
                    total_opt_size += opt_sz
                    entry['优化后大小(MB)'] = round(opt_sz / (1024*1024), 2)
                    entry['优化后尺寸'] = entry['原始尺寸'] # Same as original

                    self.log(f"Skip: {os.path.basename(fp)}", "SKIP")
                    entry['状态'] = 'Skipped'
                    entry['操作详情'] = 'Direct Copy'
            except Exception as e: 
                self.log(f"Error: {e}")
                entry['状态'] = 'Error'
                entry['操作详情'] = str(e)
            
            report_data.append(entry)
            cnt+=1
            
        self._save_opt_report(report_data, output_base, total, chg, total_org_size, total_opt_size)
        self.root.after(0, lambda: self._finish(output_base, total, chg))

    def _save_opt_report(self, data, out_folder, total, modified, org_bytes, opt_bytes):
        try:
            import pandas as pd # Ensure pandas is imported local or global
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
                        
            self.log(f"Report Generated: {rpt_path}", "INFO")
        except Exception as e:
            self.log(f"Report Error: {e}", "INFO")

    def _apply(self, inp, out, r1, r2, r3):
        try:
            sz = os.path.getsize(inp)/(1024*1024); sz_kb = sz*1024
            img = Image.open(inp); w,h = img.size
            
            if w > r1[0] and sz > r1[1]: # R1
                r = r1[2]/w; img = img.resize((r1[2], int(h*r)), Image.LANCZOS).convert("RGB")
                img.save(out, "JPEG", quality=r1[3]); return 'Opt', f'Resize {r1[2]} Q{r1[3]}'
            elif r2[0] <= w <= r2[1] and sz > r2[2]: # R2
                r = r2[3]/w; img = img.resize((r2[3], int(h*r)), Image.LANCZOS).convert("RGB")
                img.save(out, "JPEG", quality=r2[4]); return 'Opt', f'Resize {r2[3]} Q{r2[4]}'
            elif w < r3[0] and sz_kb > r3[1]: # R3
                img=img.convert("RGB"); q=90
                while q>10:
                    img.save(out, "JPEG", quality=q)
                    if os.path.getsize(out) < r3[2]*1024: break
                    q-=10
                return 'Opt', f'Limit <{r3[2]}kb'
            return 'Skip', '-'
        except: return 'Err', '-'

    def _prog(self, p, f):
        self.progress_var.set(p); self.status_label.config(text=f"Processing: {os.path.basename(f)}")

    def _finish(self, out, t, c):
        self.is_processing=False; self.progress_var.set(100); self.status_label.config(text="Done.")
        self.drop_label.config(text="⚠️ 将文件夹拖拽至此 (处理完成)")
        messagebox.showinfo("Done", f"已优化: {c}/{t}\n{out}"); os.startfile(out)
        self.progress_var.set(0)

if __name__ == "__main__":
    if HAS_DND: root = TkinterDnD.Tk()
    else: root = Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
