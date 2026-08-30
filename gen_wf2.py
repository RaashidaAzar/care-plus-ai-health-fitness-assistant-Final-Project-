import os

OUT = r'e:\Care_Plus\wireframes_clean'
os.makedirs(OUT, exist_ok=True)

W = 1440

# ── GRAYSCALE PALETTE ──────────────────────────────────────
BG       = '#F4F4F4'   # page background
WHITE    = '#FFFFFF'
DARK     = '#222222'   # headings
MID      = '#555555'   # body text
LIGHT    = '#888888'   # placeholder / label
BORDER   = '#CCCCCC'
FILL_HDR = '#DDDDDD'   # table header / section bar
FILL_ROW = '#F9F9F9'   # alt table row
FILL_BTN = '#333333'   # primary button
FILL_BTN2= '#EEEEEE'   # secondary button
FILL_NAV = '#222222'   # navbar
FILL_SID = '#2E2E2E'   # sidebar
FILL_SID_ACT = '#555555'
FILL_CARD= '#FFFFFF'
STROKE_CARD = '#CCCCCC'

def svg(h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="Arial,sans-serif">\n<rect width="{W}" height="{h}" fill="{BG}"/>\n'

def end():
    return '</svg>'

def r(x,y,w,h,fill=WHITE,stroke=BORDER,rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" rx="{rx}"/>\n'

def t(x,y,txt,size=13,fill=DARK,weight='normal',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{txt}</text>\n'

def line(x1,y1,x2,y2,stroke=BORDER):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="1"/>\n'

def btn(x,y,w,h,label,fill=FILL_BTN,tf=WHITE,size=12,rx=4):
    s  = r(x,y,w,h,fill,fill,rx)
    s += t(x+w//2, y+h//2+5, label, size, tf, 'bold', 'middle')
    return s

def btn2(x,y,w,h,label):
    return btn(x,y,w,h,label,FILL_BTN2,DARK)

def input_field(x,y,w,label,placeholder=''):
    s  = t(x, y, label, 11, LIGHT)
    s += r(x, y+6, w, 34, WHITE, BORDER, 3)
    if placeholder:
        s += t(x+10, y+28, placeholder, 11, LIGHT)
    return s

def section_bar(x,y,w,label):
    s  = r(x,y,w,32,FILL_HDR,BORDER,0)
    s += t(x+12, y+21, label, 12, DARK, 'bold')
    return s

def card(x,y,w,h,title,value,sub=''):
    s  = r(x,y,w,h,FILL_CARD,STROKE_CARD,6)
    s += r(x,y,w,3,FILL_HDR,FILL_HDR,0)
    s += t(x+12, y+20, title, 11, LIGHT)
    s += t(x+12, y+44, value, 20, DARK, 'bold')
    if sub:
        s += t(x+12, y+62, sub, 10, LIGHT)
    return s

def tbl_header(x,y,cols,widths):
    s = r(x,y,sum(widths),32,FILL_HDR,BORDER,0)
    cx = x
    for col,w2 in zip(cols,widths):
        s += t(cx+10, y+21, col, 11, DARK, 'bold')
        cx += w2
    return s

def tbl_row(x,y,vals,widths,alt=False):
    fill = FILL_ROW if alt else WHITE
    s = r(x,y,sum(widths),34,fill,BORDER,0)
    cx = x
    for v,w2 in zip(vals,widths):
        s += t(cx+10, y+22, v, 11, MID)
        cx += w2
    return s

def chart_box(x,y,w,h,label):
    s  = r(x,y,w,h,WHITE,BORDER,4)
    s += t(x+12, y+20, label, 11, DARK, 'bold')
    # fake axis lines
    s += line(x+40, y+30, x+40, y+h-20)
    s += line(x+40, y+h-20, x+w-20, y+h-20)
    # fake bars / line
    bw = (w-80)//6
    for i in range(6):
        bh2 = [60,90,50,110,70,95][i]
        bx2 = x+50+i*(bw+8)
        s += r(bx2, y+h-20-bh2, bw, bh2, FILL_HDR, BORDER, 2)
    return s

def navbar(active_link=''):
    links = ['Dashboard','Food','Calorie Burn','Health','Medications','Wellness','Progress','Reports']
    s  = r(0,0,W,56,FILL_NAV,FILL_NAV,0)
    s += t(24, 36, 'Care Plus', 17, WHITE, 'bold')
    x2 = 180
    for l in links:
        fill = '#AAAAAA' if l == active_link else '#777777'
        s += t(x2, 36, l, 12, fill)
        x2 += len(l)*8 + 24
    s += r(W-130,12,118,32,FILL_SID,FILL_SID,4)
    s += t(W-71, 33, 'John (42)', 11, WHITE, 'normal', 'middle')
    return s

def sidebar(items, active=0):
    s = r(0,56,200,2000,FILL_SID,FILL_SID,0)
    for i,(label,) in enumerate(items):
        bg = FILL_SID_ACT if i==active else FILL_SID
        s += r(8, 64+i*44, 184, 36, bg, bg, 4)
        c = WHITE if i==active else '#AAAAAA'
        s += t(20, 88+i*44, label, 12, c)
    return s

def page_wrap(content_fn, active_nav='', active_side=0):
    """Wrap a page with navbar + sidebar, return (svg_string, height)"""
    return content_fn

NAV_ITEMS = [('Dashboard',),('Food',),('Calorie Burn',),('Health',),
             ('Medications',),('Wellness',),('Progress',),('Reports',)]
CX = 210   # content x start (after sidebar)
CW = W - CX - 20  # content width

print('Helpers ready.')

# ═══════════════════════════════════════════════
# 01 LANDING
# ═══════════════════════════════════════════════
def p01_landing():
    H = 860
    s = svg(H)
    # nav
    s += r(0,0,W,56,FILL_NAV,FILL_NAV,0)
    s += t(32,36,'Care Plus',18,WHITE,'bold')
    s += t(W-320,36,'Features',13,'#AAAAAA')
    s += t(W-240,36,'About',13,'#AAAAAA')
    s += t(W-180,36,'How it works',13,'#AAAAAA')
    s += btn(W-100,12,88,32,'Sign In')
    # hero
    s += r(0,56,W,340,FILL_HDR,FILL_HDR,0)
    s += t(W//2,140,'Care Plus',32,DARK,'bold','middle')
    s += t(W//2,178,'AI-Based Personal Health & Fitness Assistant',18,MID,'normal','middle')
    s += t(W//2,204,'Built for Adults 40+',14,LIGHT,'normal','middle')
    s += t(W//2,232,'Track nutrition · Monitor health · Predict calorie burn · Share reports',13,LIGHT,'normal','middle')
    s += btn(W//2-160,264,150,40,'Get Started')
    s += btn2(W//2+20,264,130,40,'Learn More')
    # feature strip
    s += line(0,396,W,396)
    s += t(W//2,430,'Key Features',16,DARK,'bold','middle')
    features = ['Food Recognition\n& Nutrition Analysis',
                'Health Monitoring\nBMI · BP · Sugar',
                'Medication\nReminders',
                'Calorie Burn\nPrediction (AI)',
                'Progress\nAnalytics',
                'Secure Report\nSharing']
    fw2 = (W-80)//6
    for i,f in enumerate(features):
        fx = 40+i*(fw2+8)
        s += r(fx,450,fw2,160,WHITE,BORDER,6)
        s += r(fx+fw2//2-20,468,40,40,FILL_HDR,BORDER,4)
        for j,line2 in enumerate(f.split('\n')):
            s += t(fx+fw2//2,530+j*18,line2,12,MID,'normal','middle')
    # cta bottom
    s += r(0,640,W,80,FILL_HDR,FILL_HDR,0)
    s += t(W//2,672,'Ready to take control of your health?',16,DARK,'bold','middle')
    s += t(W//2,696,'Join thousands of adults managing their wellness with Care Plus.',13,LIGHT,'normal','middle')
    s += btn(W//2-80,710,160,36,'Register Free')
    # footer
    s += r(0,740,W,120,FILL_NAV,FILL_NAV,0)
    s += t(W//2,790,'Care Plus  —  AI Health & Fitness Assistant',13,'#777777','normal','middle')
    s += t(W//2,812,'Privacy Policy  ·  Terms of Service  ·  Contact',11,'#555555','normal','middle')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 02 REGISTER
# ═══════════════════════════════════════════════
def p02_register():
    H = 900
    s = svg(H)
    s += r(0,0,W,56,FILL_NAV,FILL_NAV,0)
    s += t(32,36,'Care Plus',18,WHITE,'bold')
    s += t(W-100,36,'Sign In',13,'#AAAAAA')
    # card
    cx2 = W//2-240
    s += r(cx2,76,480,800,WHITE,BORDER,6)
    s += t(W//2,120,'Create Account',20,DARK,'bold','middle')
    s += t(W//2,144,'Fill in your details to get started',12,LIGHT,'normal','middle')
    s += line(cx2,156,cx2+480,156)
    bx = cx2+24
    fw2 = 432
    s += input_field(bx,166,fw2,'Full Name *','e.g. John Smith')
    s += input_field(bx,240,fw2,'Username *','e.g. john40')
    s += input_field(bx,314,fw2,'Email Address *','e.g. john@example.com')
    s += input_field(bx,388,fw2,'Password *','Min. 6 characters')
    s += input_field(bx,462,fw2,'Confirm Password *','Re-enter password')
    # gender
    s += t(bx,542,'Gender *',11,LIGHT)
    for gi,gl in enumerate(['Male','Female','Other']):
        gx = bx+gi*148
        s += r(gx,550,138,34,WHITE,BORDER,3)
        s += t(gx+69,572,gl,12,MID,'normal','middle')
    # birth year
    s += input_field(bx,600,fw2,'Birth Year *','e.g. 1982')
    s += btn(bx,672,fw2,42,'Create Account')
    s += line(cx2,728,cx2+480,728)
    s += t(W//2,750,'Already have an account?',12,LIGHT,'normal','middle')
    s += t(W//2,772,'Sign In here',12,MID,'bold','middle')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 03 LOGIN
# ═══════════════════════════════════════════════
def p03_login():
    H = 760
    s = svg(H)
    s += r(0,0,W,56,FILL_NAV,FILL_NAV,0)
    s += t(32,36,'Care Plus',18,WHITE,'bold')
    s += t(W-120,36,'Register',13,'#AAAAAA')
    cx2 = W//2-220
    s += r(cx2,96,440,560,WHITE,BORDER,6)
    s += t(W//2,144,'Sign In',22,DARK,'bold','middle')
    s += t(W//2,168,'Welcome back to Care Plus',13,LIGHT,'normal','middle')
    s += line(cx2,180,cx2+440,180)
    bx = cx2+24
    fw2 = 392
    s += input_field(bx,196,fw2,'Username or Email','john40  or  john@example.com')
    s += input_field(bx,276,fw2,'Password','••••••••')
    # remember + forgot
    s += r(bx,330,14,14,WHITE,BORDER,2)
    s += t(bx+22,342,'Remember me',11,MID)
    s += t(bx+280,342,'Forgot password?',11,LIGHT)
    s += btn(bx,360,fw2,42,'Sign In')
    # error state
    s += r(bx,416,fw2,36,FILL_ROW,BORDER,3)
    s += t(bx+fw2//2,439,'Invalid username or password. Please try again.',11,LIGHT,'normal','middle')
    s += line(cx2,464,cx2+440,464)
    s += t(W//2,488,'Don\'t have an account?',12,LIGHT,'normal','middle')
    s += t(W//2,508,'Register here',12,MID,'bold','middle')
    s += end()
    return s

print('01-03 done')

# ═══════════════════════════════════════════════
# 04 DASHBOARD
# ═══════════════════════════════════════════════
def p04_dashboard():
    H = 980
    s = svg(H)
    s += navbar('Dashboard')
    s += sidebar(NAV_ITEMS, 0)
    # welcome
    s += t(CX+16,90,'Dashboard',18,DARK,'bold')
    s += t(CX+16,112,'Good morning, John. Here is your health summary for today.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # stat cards row 1
    card_w = (CW-60)//4
    labels1 = [('Calories Consumed','1,240 kcal','Today'),
               ('Calories Burned','380 kcal','Today'),
               ('Water Intake','1,500 ml','Today'),
               ('Sleep Duration','7.5 hrs','Last night')]
    for i,(ti,v,sub) in enumerate(labels1):
        s += card(CX+16+i*(card_w+16),132,card_w,88,ti,v,sub)
    # stat cards row 2
    labels2 = [('Current BMI','22.9','Normal weight'),
               ('Activity Streak','5 days','Consecutive'),
               ('Active Medications','2','Due today'),
               ('Notifications','3 unread','')]
    for i,(ti,v,sub) in enumerate(labels2):
        s += card(CX+16+i*(card_w+16),236,card_w,88,ti,v,sub)
    # BMI onboarding banner
    s += r(CX+16,340,CW-16,44,FILL_HDR,BORDER,4)
    s += t(CX+28,367,'Complete your BMI check to get personalised health insights',12,MID)
    s += btn(W-180,348,150,28,'Complete BMI Check')
    # today meals
    s += t(CX+16,412,'Today\'s Meals',14,DARK,'bold')
    cols = ['Food Item','Meal','Serving','Calories','Protein','Carbs','Fat']
    widths = [220,110,90,100,90,90,90]
    s += tbl_header(CX+16,424,cols,widths)
    rows2 = [['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g'],
             ['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g'],
             ['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g']]
    for i,row in enumerate(rows2):
        s += tbl_row(CX+16,456+i*34,row,widths,i%2==1)
    # today activities
    s += t(CX+16,582,'Today\'s Activities',14,DARK,'bold')
    acols = ['Activity','Duration','Calories Burned','Date']
    awidths = [280,160,200,200]
    s += tbl_header(CX+16,594,acols,awidths)
    s += tbl_row(CX+16,626,['Walking','30 mins','120 kcal','Today'],awidths)
    s += tbl_row(CX+16,660,['Yoga','45 mins','150 kcal','Today'],awidths,True)
    # macro summary
    s += t(CX+16,716,'Macro Summary — Today',14,DARK,'bold')
    for i,(label,val,pct) in enumerate([('Protein','62 g',0.4),('Carbohydrates','180 g',0.7),('Fat','38 g',0.3)]):
        my = 728+i*52
        s += t(CX+16,my+16,label,11,LIGHT)
        s += t(CX+120,my+16,val,11,MID,'bold')
        s += r(CX+16,my+22,CW-32,12,FILL_HDR,BORDER,6)
        s += r(CX+16,my+22,int((CW-32)*pct),12,FILL_BTN,FILL_BTN,6)
    s += end()
    return s

# ═══════════════════════════════════════════════
# 05 PROFILE
# ═══════════════════════════════════════════════
def p05_profile():
    H = 1000
    s = svg(H)
    s += navbar('Profile')
    s += sidebar(NAV_ITEMS, -1)
    s += t(CX+16,90,'Profile Management',18,DARK,'bold')
    s += t(CX+16,112,'Update your personal information and preferences.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # avatar strip
    s += r(CX+16,132,CW-16,90,WHITE,BORDER,4)
    s += r(CX+32,148,60,60,FILL_HDR,BORDER,30)
    s += t(CX+62,184,'J',20,DARK,'bold','middle')
    s += t(CX+108,172,'John Smith',16,DARK,'bold')
    s += t(CX+108,192,'john40   |   john@example.com',12,LIGHT)
    s += t(CX+108,210,'Age: 42   |   Male   |   Moderate Activity',11,LIGHT)
    # personal info section
    s += r(CX+16,240,CW-16,480,WHITE,BORDER,4)
    s += section_bar(CX+16,240,CW-16,'Personal Information')
    fw2 = (CW-64)//3
    s += input_field(CX+32,284,fw2,'Full Name','John Smith')
    s += input_field(CX+32+fw2+16,284,fw2,'Username','john40')
    s += input_field(CX+32+fw2*2+32,284,fw2,'Email Address','john@example.com')
    s += input_field(CX+32,364,fw2,'Birth Year','1982')
    s += input_field(CX+32+fw2+16,364,fw2,'Gender','Male')
    s += input_field(CX+32+fw2*2+32,364,fw2,'Activity Level','Moderate')
    s += input_field(CX+32,444,fw2,'Height (cm)','175')
    s += input_field(CX+32+fw2+16,444,fw2,'Weight (kg)','70')
    s += input_field(CX+32+fw2*2+32,444,fw2,'Theme Preference','Light')
    # password section
    s += section_bar(CX+32,530,CW-48,'Change Password')
    s += input_field(CX+32,572,fw2,'New Password','Min. 6 characters')
    s += input_field(CX+32+fw2+16,572,fw2,'Confirm Password','Re-enter password')
    # buttons
    s += btn(CX+32,650,180,40,'Save Changes')
    s += btn2(CX+228,650,110,40,'Cancel')
    s += end()
    return s

print('04-05 done')

# ═══════════════════════════════════════════════
# 06 SETTINGS
# ═══════════════════════════════════════════════
def p06_settings():
    H = 760
    s = svg(H)
    s += navbar('Settings')
    s += sidebar(NAV_ITEMS, -1)
    s += t(CX+16,90,'Settings',18,DARK,'bold')
    s += t(CX+16,112,'Manage your account security and preferences.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # password card
    s += r(CX+16,132,680,280,WHITE,BORDER,4)
    s += section_bar(CX+16,132,680,'Change Password')
    s += input_field(CX+32,176,640,'Current Password','••••••••')
    s += input_field(CX+32,250,'New Password (minimum 6 characters)','••••••••')
    s += input_field(CX+32,324,640,'Confirm New Password','••••••••')
    s += btn(CX+32,398,180,38,'Update Password')
    s += btn2(CX+228,398,110,38,'Cancel')
    # theme card
    s += r(CX+16,432,680,180,WHITE,BORDER,4)
    s += section_bar(CX+16,432,680,'Theme Preference')
    s += r(CX+32,476,200,60,FILL_HDR,BORDER,4)
    s += t(CX+132,512,'Light Mode',13,DARK,'bold','middle')
    s += r(CX+248,476,200,60,FILL_BTN,FILL_BTN,4)
    s += t(CX+348,512,'Dark Mode',13,WHITE,'bold','middle')
    s += t(CX+32,556,'Selected theme will apply across all pages.',11,LIGHT)
    s += btn(CX+32,568,160,36,'Save Preference')
    # danger zone
    s += r(CX+16,632,680,100,WHITE,BORDER,4)
    s += section_bar(CX+16,632,680,'Account')
    s += t(CX+32,680,'Delete your account permanently. This action cannot be undone.',12,LIGHT)
    s += btn(CX+32,692,160,36,'Delete Account',FILL_HDR,DARK)
    s += end()
    return s

# ═══════════════════════════════════════════════
# 07 FOOD RECOGNITION
# ═══════════════════════════════════════════════
def p07_food():
    H = 1000
    s = svg(H)
    s += navbar('Food')
    s += sidebar(NAV_ITEMS, 1)
    s += t(CX+16,90,'Food Recognition',18,DARK,'bold')
    s += t(CX+16,112,'Upload a food image for AI-powered recognition and nutrition lookup.',13,LIGHT)
    s += line(CX,120,W-20,120)
    half = (CW-32)//2
    # upload card
    s += r(CX+16,132,half,300,WHITE,BORDER,4)
    s += section_bar(CX+16,132,half,'Upload Food Image')
    # drop zone
    s += r(CX+32,176,half-32,180,FILL_ROW,BORDER,4)
    s += r(CX+32+(half-32)//2-30,210,60,60,FILL_HDR,BORDER,4)
    s += t(CX+32+(half-32)//2,296,'Drag & drop or click to select image',12,LIGHT,'normal','middle')
    s += t(CX+32+(half-32)//2,314,'Supported: JPG, PNG, WEBP',10,LIGHT,'normal','middle')
    s += btn(CX+32,368,half-32,38,'Recognise Food')
    # result card
    rx2 = CX+16+half+16
    s += r(rx2,132,half,300,WHITE,BORDER,4)
    s += section_bar(rx2,132,half,'Recognition Result')
    s += r(rx2+16,176,120,120,FILL_HDR,BORDER,4)
    s += t(rx2+76,242,'Image Preview',10,LIGHT,'normal','middle')
    s += t(rx2+156,196,'Banana',18,DARK,'bold')
    s += r(rx2+156,208,120,22,FILL_HDR,BORDER,11)
    s += t(rx2+216,224,'Confidence: 94%',10,MID,'normal','middle')
    for i,(label,val) in enumerate([('Calories (100g)','89 kcal'),('Protein','1.1 g'),
                                     ('Carbohydrates','23 g'),('Fat','0.3 g'),('Fibre','2.6 g')]):
        s += t(rx2+156,248+i*18,f'{label}:',10,LIGHT)
        s += t(rx2+300,248+i*18,val,10,MID,'bold')
    # save form
    s += r(CX+16,448,CW-16,340,WHITE,BORDER,4)
    s += section_bar(CX+16,448,CW-16,'Save to Food Log')
    fw2 = (CW-64)//4
    s += input_field(CX+32,492,fw2,'Food Name','Banana')
    s += input_field(CX+32+fw2+16,492,fw2,'Meal Name','Breakfast')
    s += input_field(CX+32+fw2*2+32,492,fw2,'Serving Amount (g)','150')
    s += input_field(CX+32+fw2*3+48,492,fw2,'Calories (auto-scaled)','133.5 kcal')
    s += input_field(CX+32,572,fw2,'Protein (auto)','1.65 g')
    s += input_field(CX+32+fw2+16,572,fw2,'Carbohydrates (auto)','34.5 g')
    s += input_field(CX+32+fw2*2+32,572,fw2,'Fat (auto)','0.45 g')
    s += input_field(CX+32+fw2*3+48,572,fw2,'Fibre (auto)','3.9 g')
    s += btn(CX+32,652,180,38,'Save to Log')
    s += btn2(CX+228,652,160,38,'Manual Entry')
    # manual entry note
    s += r(CX+16,708,CW-16,60,FILL_ROW,BORDER,4)
    s += t(CX+32,732,'Manual Entry: Select a food from the dropdown below or enter custom nutrition values.',12,LIGHT)
    s += r(CX+32,742,300,28,WHITE,BORDER,3)
    s += t(CX+42,761,'Select food from database...',11,LIGHT)
    s += end()
    return s

# ═══════════════════════════════════════════════
# 08 FOOD HISTORY
# ═══════════════════════════════════════════════
def p08_food_history():
    H = 900
    s = svg(H)
    s += navbar('Food')
    s += sidebar(NAV_ITEMS, 1)
    s += t(CX+16,90,'Food History',18,DARK,'bold')
    s += t(CX+16,112,'All your logged meals and nutrition data.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # summary cards
    cw2 = (CW-64)//3
    s += card(CX+16,132,cw2,80,'Today Consumed','1,240 kcal','Total intake')
    s += card(CX+16+cw2+16,132,cw2,80,'Today Burned','380 kcal','Activity')
    s += card(CX+16+cw2*2+32,132,cw2,80,'Net Calories','860 kcal','Consumed - Burned')
    s += btn(W-200,140,170,36,'+ Log New Food')
    # table
    s += r(CX+16,228,CW-16,600,WHITE,BORDER,4)
    s += section_bar(CX+16,228,CW-16,'Food Log')
    cols = ['Food Name','Meal','Serving','Calories','Protein','Carbs','Fat','Date & Time','Action']
    widths = [180,100,80,90,80,80,80,150,120]
    s += tbl_header(CX+16,260,cols,widths)
    rows2 = [['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g','Today 08:30'],
             ['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g','Today 13:00'],
             ['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g','Today 16:00'],
             ['Grilled Chicken','Dinner','200 g','330 kcal','62 g','0 g','7.2 g','Yesterday'],
             ['Oatmeal','Breakfast','180 g','166 kcal','6 g','28 g','3.6 g','Yesterday'],
             ['Banana','Breakfast','100 g','52 kcal','0.8 g','13.8 g','0.2 g','2 days ago']]
    for i,row in enumerate(rows2):
        s += tbl_row(CX+16,292+i*36,row,widths[:-1],i%2==1)
        s += btn2(CX+16+sum(widths[:-1]),296+i*36,100,28,'Delete')
    s += end()
    return s

print('06-08 done')

# ═══════════════════════════════════════════════
# 09 CALORIE BURN
# ═══════════════════════════════════════════════
def p09_calorie():
    H = 960
    s = svg(H)
    s += navbar('Calorie Burn')
    s += sidebar(NAV_ITEMS, 2)
    s += t(CX+16,90,'Calorie Burn Prediction',18,DARK,'bold')
    s += t(CX+16,112,'AI-powered calorie burn estimation using your health profile.',13,LIGHT)
    s += line(CX,120,W-20,120)
    left_w = 660
    right_w = CW - left_w - 32
    # prediction form
    s += r(CX+16,132,left_w,560,WHITE,BORDER,4)
    s += section_bar(CX+16,132,left_w,'Prediction Parameters')
    fw2 = (left_w-48)//2
    s += input_field(CX+32,176,left_w-32,'Activity Type','e.g. Walking, Running, Cycling')
    s += input_field(CX+32,256,fw2,'Duration (minutes)','30')
    s += input_field(CX+32+fw2+16,256,fw2,'Heart Rate (bpm)','110')
    s += input_field(CX+32,336,fw2,'Body Temperature (C)','38.5')
    s += input_field(CX+32+fw2+16,336,fw2,'Weight (kg)','70')
    s += input_field(CX+32,416,fw2,'Height (cm)','175')
    s += input_field(CX+32+fw2+16,416,fw2,'Gender','Male  (from profile)')
    s += t(CX+32,510,'Age and gender are pre-filled from your profile.',11,LIGHT)
    s += btn(CX+32,524,left_w-32,42,'Predict Calorie Burn')
    # result panel
    rx2 = CX+16+left_w+16
    s += r(rx2,132,right_w,240,WHITE,BORDER,4)
    s += section_bar(rx2,132,right_w,'Prediction Result')
    s += r(rx2+16,176,right_w-32,120,FILL_HDR,BORDER,4)
    s += t(rx2+right_w//2,228,'Estimated Calorie Burn',12,LIGHT,'normal','middle')
    s += t(rx2+right_w//2,260,'247 kcal',26,DARK,'bold','middle')
    s += t(rx2+16,308,'Based on: Walking · 30 min · HR 110 bpm',11,LIGHT)
    # save activity
    s += r(rx2,388,right_w,300,WHITE,BORDER,4)
    s += section_bar(rx2,388,right_w,'Save Activity to Log')
    s += input_field(rx2+16,432,right_w-32,'Activity Type','Walking')
    s += input_field(rx2+16,506,right_w-32,'Duration (minutes)','30')
    s += input_field(rx2+16,580,right_w-32,'Calories Burned','247')
    s += btn(rx2+16,640,right_w-32,38,'Save Activity')
    # activity log table
    s += r(CX+16,708,CW-16,220,WHITE,BORDER,4)
    s += section_bar(CX+16,708,CW-16,'Recent Activity Log')
    acols = ['Activity','Duration','Calories Burned','Date','Action']
    awidths = [280,160,200,200,160]
    s += tbl_header(CX+16,740,acols,awidths)
    s += tbl_row(CX+16,772,['Walking','30 mins','247 kcal','Today'],awidths[:-1])
    s += btn2(CX+16+sum(awidths[:-1]),776,130,28,'Delete')
    s += tbl_row(CX+16,806,['Yoga','45 mins','150 kcal','Yesterday'],awidths[:-1],True)
    s += btn2(CX+16+sum(awidths[:-1]),810,130,28,'Delete')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 10 HEALTH RECORDS
# ═══════════════════════════════════════════════
def p10_health():
    H = 960
    s = svg(H)
    s += navbar('Health')
    s += sidebar(NAV_ITEMS, 3)
    s += t(CX+16,90,'Health Monitoring',18,DARK,'bold')
    s += t(CX+16,112,'Track your BMI, blood pressure, blood sugar and heart rate.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # add form
    s += r(CX+16,132,CW-16,300,WHITE,BORDER,4)
    s += section_bar(CX+16,132,CW-16,'Add Health Record')
    fw2 = (CW-64)//4
    s += input_field(CX+32,176,fw2,'Weight (kg)','70')
    s += input_field(CX+32+fw2+16,176,fw2,'Height (cm)','175')
    s += input_field(CX+32+fw2*2+32,176,fw2,'BMI (auto-calculated)','22.9')
    s += input_field(CX+32+fw2*3+48,176,fw2,'Blood Pressure','120/80')
    s += input_field(CX+32,256,fw2,'Blood Sugar (mg/dL)','95')
    s += input_field(CX+32+fw2+16,256,fw2,'Cholesterol (mg/dL)','180')
    s += input_field(CX+32+fw2*2+32,256,fw2,'Heart Rate (bpm)','72')
    s += input_field(CX+32+fw2*3+48,256,fw2,'Notes','Optional notes')
    s += btn(CX+32,340,200,38,'Save Health Record')
    s += btn2(CX+248,340,110,38,'Cancel')
    # records table
    s += r(CX+16,448,CW-16,480,WHITE,BORDER,4)
    s += section_bar(CX+16,448,CW-16,'Health Records History')
    cols = ['Date','Weight','Height','BMI','Blood Pressure','Blood Sugar','Cholesterol','Heart Rate','Action']
    widths = [120,80,80,70,120,110,110,100,110]
    s += tbl_header(CX+16,480,cols,widths)
    rows2 = [['Today','70 kg','175 cm','22.9','120/80','95 mg/dL','180 mg/dL','72 bpm'],
             ['Yesterday','70.5 kg','175 cm','23.1','122/82','98 mg/dL','182 mg/dL','74 bpm'],
             ['3 days ago','71 kg','175 cm','23.2','118/78','92 mg/dL','178 mg/dL','70 bpm'],
             ['1 week ago','71.5 kg','175 cm','23.3','124/84','100 mg/dL','185 mg/dL','76 bpm']]
    for i,row in enumerate(rows2):
        s += tbl_row(CX+16,512+i*36,row,widths[:-1],i%2==1)
        s += btn2(CX+16+sum(widths[:-1]),516+i*36,90,28,'Delete')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 11 MEDICATIONS
# ═══════════════════════════════════════════════
def p11_medications():
    H = 980
    s = svg(H)
    s += navbar('Medications')
    s += sidebar(NAV_ITEMS, 4)
    s += t(CX+16,90,'Medications & Reminders',18,DARK,'bold')
    s += t(CX+16,112,'Manage your medication schedule and track doses taken.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # add form
    s += r(CX+16,132,CW-16,220,WHITE,BORDER,4)
    s += section_bar(CX+16,132,CW-16,'Add Medication')
    fw2 = (CW-64)//4
    s += input_field(CX+32,176,fw2,'Medication Name *','e.g. Metformin')
    s += input_field(CX+32+fw2+16,176,fw2,'Dosage','e.g. 500mg')
    s += input_field(CX+32+fw2*2+32,176,fw2,'Scheduled Time *','HH:MM  e.g. 08:00')
    s += input_field(CX+32+fw2*3+48,176,fw2,'Frequency','e.g. Daily')
    s += input_field(CX+32,256,fw2*2+16,'Notes','Optional notes')
    s += btn(CX+32,316,180,36,'Add Medication')
    # two columns
    left_w = 700
    right_w = CW - left_w - 32
    # medications list
    s += r(CX+16,368,left_w,560,WHITE,BORDER,4)
    s += section_bar(CX+16,368,left_w,'Active Medications')
    meds = [('Metformin','500mg','08:00','Daily'),
            ('Aspirin','100mg','20:00','Daily'),
            ('Vitamin D','1000 IU','09:00','Daily'),
            ('Lisinopril','10mg','07:00','Daily')]
    for i,(name,dose,time,freq) in enumerate(meds):
        my = 408+i*112
        s += r(CX+32,my,left_w-32,96,FILL_ROW,BORDER,4)
        s += t(CX+48,my+24,name,14,DARK,'bold')
        s += t(CX+48,my+44,f'Dosage: {dose}',11,LIGHT)
        s += t(CX+48,my+60,f'Time: {time}   Frequency: {freq}',11,LIGHT)
        s += btn(CX+32+left_w-200,my+16,100,30,'Mark Taken')
        s += btn2(CX+32+left_w-90,my+16,70,30,'Delete')
    # logs
    rx2 = CX+16+left_w+16
    s += r(rx2,368,right_w,560,WHITE,BORDER,4)
    s += section_bar(rx2,368,right_w,'Recent Dose Logs')
    logs = [('Metformin','Taken','Today 08:05'),
            ('Aspirin','Taken','Yesterday 20:02'),
            ('Vitamin D','Taken','Yesterday 09:10'),
            ('Lisinopril','Taken','Today 07:03'),
            ('Metformin','Taken','Yesterday 08:00')]
    for i,(name,status,time) in enumerate(logs):
        ly = 408+i*72
        s += r(rx2+16,ly,right_w-32,56,FILL_ROW,BORDER,4)
        s += t(rx2+28,ly+22,name,13,DARK,'bold')
        s += t(rx2+28,ly+40,time,10,LIGHT)
        s += r(rx2+right_w-100,ly+16,80,24,FILL_HDR,BORDER,12)
        s += t(rx2+right_w-60,ly+32,status,10,MID,'normal','middle')
    s += end()
    return s

print('09-11 done')

# ═══════════════════════════════════════════════
# 12 WELLNESS
# ═══════════════════════════════════════════════
def p12_wellness():
    H = 1040
    s = svg(H)
    s += navbar('Wellness')
    s += sidebar(NAV_ITEMS, 5)
    s += t(CX+16,90,'Wellness Tracking',18,DARK,'bold')
    s += t(CX+16,112,'Log water intake, exercise sessions and sleep records.',13,LIGHT)
    s += line(CX,120,W-20,120)
    third = (CW-48)//3
    # water card
    s += r(CX+16,132,third,260,WHITE,BORDER,4)
    s += section_bar(CX+16,132,third,'Water Intake')
    s += t(CX+16+third//2,192,'1,500 ml',22,DARK,'bold','middle')
    s += t(CX+16+third//2,212,'logged today  (goal: 2,500 ml)',11,LIGHT,'normal','middle')
    s += r(CX+32,224,third-32,10,FILL_HDR,BORDER,5)
    s += r(CX+32,224,int((third-32)*0.6),10,FILL_BTN,FILL_BTN,5)
    s += t(CX+32,250,'1,500 / 2,500 ml',10,LIGHT)
    s += input_field(CX+32,258,third-32,'Amount (ml)','250')
    s += btn(CX+32,316,third-32,36,'Add Water')
    # exercise card
    ex = CX+16+third+16
    s += r(ex,132,third,260,WHITE,BORDER,4)
    s += section_bar(ex,132,third,'Exercise')
    s += input_field(ex+16,176,third-32,'Activity Name','e.g. Yoga, Walking')
    s += input_field(ex+16,250,third-32,'Duration (minutes)','30')
    s += input_field(ex+16,324,'Calories Burned','120')
    s += btn(ex+16,362,third-32,36,'Log Exercise')
    # sleep card
    sx = CX+16+third*2+32
    s += r(sx,132,third,260,WHITE,BORDER,4)
    s += section_bar(sx,132,third,'Sleep')
    s += input_field(sx+16,176,third-32,'Sleep Time','YYYY-MM-DDTHH:MM')
    s += input_field(sx+16,250,third-32,'Wake Time','YYYY-MM-DDTHH:MM')
    s += t(sx+16,330,'Calculated Duration: 8.0 hours',12,MID,'bold')
    s += btn(sx+16,344,third-32,36,'Log Sleep')
    # reminders section
    s += r(CX+16,408,CW-16,400,WHITE,BORDER,4)
    s += section_bar(CX+16,408,CW-16,'Wellness Reminders')
    s += btn(W-220,414,100,20,'+ Add',FILL_BTN,WHITE,10)
    s += btn2(W-110,414,90,20,'Clear All')
    reminders = [('10-minute walk','09:00'),('Light stretching','11:00'),
                 ('Drink water','13:00'),('Stand and move','15:00'),('Breathing exercise','20:00')]
    for i,(name,time) in enumerate(reminders):
        ry = 448+i*56
        s += r(CX+32,ry,CW-48,44,FILL_ROW,BORDER,4)
        s += t(CX+48,ry+27,name,13,DARK,'bold')
        s += r(CX+CW-200,ry+10,70,24,WHITE,BORDER,3)
        s += t(CX+CW-165,ry+27,time,11,MID,'normal','middle')
        s += btn2(CX+CW-120,ry+10,90,24,'Delete')
    # add custom reminder form
    s += r(CX+16,824,CW-16,100,WHITE,BORDER,4)
    s += section_bar(CX+16,824,CW-16,'Add Custom Reminder')
    s += input_field(CX+32,856,300,'Activity Name','e.g. Meditation')
    s += input_field(CX+348,856,160,'Time (HH:MM)','07:00')
    s += btn(CX+528,862,160,36,'Add Reminder')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 13 PROGRESS
# ═══════════════════════════════════════════════
def p13_progress():
    H = 1020
    s = svg(H)
    s += navbar('Progress')
    s += sidebar(NAV_ITEMS, 6)
    s += t(CX+16,90,'Progress & Analytics',18,DARK,'bold')
    s += t(CX+16,112,'Visual trends for your health and fitness data.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # filter bar
    s += r(CX+16,132,CW-16,44,WHITE,BORDER,4)
    s += t(CX+32,160,'Date Range:',12,MID,'bold')
    for i,(label,active) in enumerate([('7 Days',False),('30 Days',True),('90 Days',False)]):
        bx2 = CX+130+i*96
        s += btn(bx2,140,86,28,label,FILL_BTN if active else FILL_BTN2,WHITE if active else DARK,11)
    # row 1 charts
    cw2 = (CW-48)//2
    s += chart_box(CX+16,192,cw2,200,'Weight Trend (kg)')
    s += chart_box(CX+16+cw2+16,192,cw2,200,'BMI Trend')
    # row 2 charts
    s += chart_box(CX+16,408,cw2,200,'Calories Consumed vs Burned (kcal)')
    s += chart_box(CX+16+cw2+16,408,cw2,200,'Daily Water Intake (Litres)')
    # row 3 charts
    cw3 = (CW-64)//3
    s += chart_box(CX+16,624,cw3,200,'Blood Pressure (mmHg)')
    s += chart_box(CX+16+cw3+16,624,cw3,200,'Blood Sugar (mg/dL)')
    s += chart_box(CX+16+cw3*2+32,624,cw3,200,'Heart Rate (bpm)')
    s += end()
    return s

# ═══════════════════════════════════════════════
# 14 REPORTS
# ═══════════════════════════════════════════════
def p14_reports():
    H = 880
    s = svg(H)
    s += navbar('Reports')
    s += sidebar(NAV_ITEMS, 7)
    s += t(CX+16,90,'Health Reports',18,DARK,'bold')
    s += t(CX+16,112,'Generate, download and securely share your health reports.',13,LIGHT)
    s += line(CX,120,W-20,120)
    # generate card
    s += r(CX+16,132,CW-16,180,WHITE,BORDER,4)
    s += section_bar(CX+16,132,CW-16,'Generate PDF Report')
    s += t(CX+32,180,'Select date range:',12,MID)
    for i,(label,) in enumerate([('Last 7 Days',),('Last 30 Days',),('Last 90 Days',)]):
        s += btn(CX+32+i*160,192,148,34,label,FILL_BTN if i==1 else FILL_BTN2,WHITE if i==1 else DARK,11)
    s += btn(CX+32,244,220,38,'Download PDF Report')
    s += btn2(CX+268,244,200,38,'Create Share Link')
    s += t(CX+32,298,'A secure shareable link will be valid for 7 days and can be revoked at any time.',11,LIGHT)
    # share links table
    s += r(CX+16,328,CW-16,500,WHITE,BORDER,4)
    s += section_bar(CX+16,328,CW-16,'Secure Share Links')
    cols = ['Share ID','Report Type','Created','Expires','Status','Actions']
    widths = [100,160,160,160,120,220]
    s += tbl_header(CX+16,360,cols,widths)
    shares = [('SH-001','Health Summary','01 Jan 2025','08 Jan 2025','Active'),
              ('SH-002','Health Summary','15 Dec 2024','22 Dec 2024','Expired'),
              ('SH-003','Health Summary','20 Dec 2024','27 Dec 2024','Revoked')]
    for i,(sid,rtype,created,expires,status) in enumerate(shares):
        s += tbl_row(CX+16,392+i*48,[sid,rtype,created,expires,status],widths[:-1],i%2==1)
        if status == 'Active':
            s += btn(CX+16+sum(widths[:-1]),396+i*48,100,32,'Copy Link')
            s += btn2(CX+16+sum(widths[:-1])+108,396+i*48,100,32,'Revoke')
        else:
            s += t(CX+16+sum(widths[:-1])+40,416+i*48,'—',13,LIGHT)
    s += end()
    return s

# ═══════════════════════════════════════════════
# 15 SHARED REPORT (public)
# ═══════════════════════════════════════════════
def p15_shared():
    H = 880
    s = svg(H)
    # minimal public nav
    s += r(0,0,W,56,FILL_NAV,FILL_NAV,0)
    s += t(32,36,'Care Plus',18,WHITE,'bold')
    s += t(W//2,36,'Shared Health Report',14,WHITE,'normal','middle')
    s += r(W-160,14,140,28,FILL_SID,FILL_SID,4)
    s += t(W-90,32,'Secure Link',11,WHITE,'normal','middle')
    # expiry banner
    s += r(0,56,W,40,FILL_HDR,BORDER,0)
    s += t(W//2,81,'This report is valid and expires on 08 Jan 2025. View only — no login required.',12,MID,'normal','middle')
    # user info
    s += r(40,112,W-80,88,WHITE,BORDER,4)
    s += r(56,128,56,56,FILL_HDR,BORDER,28)
    s += t(84,162,'J',20,DARK,'bold','middle')
    s += t(128,148,'John Smith',16,DARK,'bold')
    s += t(128,168,'Shared health summary  ·  Last 30 days',12,LIGHT)
    s += t(128,186,'Age: 42   |   Male',11,LIGHT)
    # health summary cards
    s += t(40,228,'Health Summary',14,DARK,'bold')
    cw2 = (W-80-48)//4
    for i,(ti,v,sub) in enumerate([('Latest BMI','22.9','Normal weight'),
                                    ('Weight','70 kg','Last recorded'),
                                    ('Blood Pressure','120/80 mmHg','Last recorded'),
                                    ('Heart Rate','72 bpm','Last recorded')]):
        s += card(40+i*(cw2+16),244,cw2,80,ti,v,sub)
    # food log table
    s += t(40,356,'Recent Food Log (Last 30 Days)',14,DARK,'bold')
    s += r(40,370,W-80,420,WHITE,BORDER,4)
    cols = ['Food Name','Meal','Serving','Calories','Protein','Carbs','Fat','Date']
    widths = [200,120,100,110,100,100,100,160]
    s += tbl_header(40,370,cols,widths)
    rows2 = [['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g','Today'],
             ['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g','Today'],
             ['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g','Yesterday'],
             ['Grilled Chicken','Dinner','200 g','330 kcal','62 g','0 g','7.2 g','Yesterday']]
    for i,row in enumerate(rows2):
        s += tbl_row(40,402+i*36,row,widths,i%2==1)
    # footer
    s += r(0,820,W,60,FILL_HDR,BORDER,0)
    s += t(W//2,856,'Generated by Care Plus  ·  This link will expire automatically  ·  Do not share with untrusted parties.',11,LIGHT,'normal','middle')
    s += end()
    return s

# ═══════════════════════════════════════════════
# SAVE ALL
# ═══════════════════════════════════════════════
pages = {
    '01_landing':           p01_landing(),
    '02_register':          p02_register(),
    '03_login':             p03_login(),
    '04_dashboard':         p04_dashboard(),
    '05_profile':           p05_profile(),
    '06_settings':          p06_settings(),
    '07_food_recognition':  p07_food(),
    '08_food_history':      p08_food_history(),
    '09_calorie_burn':      p09_calorie(),
    '10_health':            p10_health(),
    '11_medications':       p11_medications(),
    '12_wellness':          p12_wellness(),
    '13_progress':          p13_progress(),
    '14_reports':           p14_reports(),
    '15_shared_report':     p15_shared(),
}

for name, content in pages.items():
    path = os.path.join(OUT, f'{name}.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  Saved: {name}.svg')

print(f'\nDone — {len(pages)} wireframes saved to:\n{OUT}')
