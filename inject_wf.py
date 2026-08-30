
# Reads wireframes.html, injects remaining 12 page SVGs before </div><!--/frame-wrap-->

PAGES = {}

W = 1280
BG='#f4f4f4';WHITE='#fff';DARK='#222';MID='#555';LIGHT='#888'
BORDER='#ccc';HDR='#ddd';ROW='#f9f9f9';BTN='#333';BTN2='#eee'
NAV='#222';SID='#2e2e2e';SIDA='#555'
CX=210; CW=W-CX-20

def r(x,y,w,h,fill=WHITE,stroke=BORDER,rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" rx="{rx}"/>\n'
def t(x,y,txt,size=13,fill=DARK,weight='normal',anchor='start'):
    safe = str(txt).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" font-family="Arial" text-anchor="{anchor}">{safe}</text>\n'
def ln(x1,y1,x2,y2): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BORDER}" stroke-width="1"/>\n'
def btn(x,y,w,h,label,fill=BTN,tf=WHITE,size=12,rx=4):
    return r(x,y,w,h,fill,fill,rx)+t(x+w//2,y+h//2+5,label,size,tf,'bold','middle')
def btn2(x,y,w,h,label): return btn(x,y,w,h,label,BTN2,DARK)
def inp(x,y,w,label,ph=''):
    return t(x,y,label,11,LIGHT)+r(x,y+6,w,34,WHITE,BORDER,3)+(t(x+10,y+28,ph,11,'#bbb') if ph else '')
def sbar(x,y,w,label):
    return r(x,y,w,32,HDR,BORDER,0)+t(x+12,y+21,label,12,DARK,'bold')
def card(x,y,w,h,title,val,sub=''):
    return r(x,y,w,h,WHITE,BORDER,6)+r(x,y,w,3,HDR,HDR,0)+t(x+12,y+20,title,11,LIGHT)+t(x+12,y+44,val,20,DARK,'bold')+(t(x+12,y+62,sub,10,LIGHT) if sub else '')
def th(x,y,cols,widths):
    s=r(x,y,sum(widths),32,HDR,BORDER,0); cx=x
    for c,w in zip(cols,widths): s+=t(cx+10,y+21,c,11,DARK,'bold'); cx+=w
    return s
def tr(x,y,vals,widths,alt=False):
    s=r(x,y,sum(widths),34,ROW if alt else WHITE,BORDER,0); cx=x
    for v,w in zip(vals,widths): s+=t(cx+10,y+22,v,11,MID); cx+=w
    return s
def chart(x,y,w,h,label):
    s=r(x,y,w,h,WHITE,BORDER,4)+t(x+12,y+20,label,11,DARK,'bold')
    s+=ln(x+40,y+30,x+40,y+h-20)+ln(x+40,y+h-20,x+w-20,y+h-20)
    bw=(w-80)//6
    for i,bh in enumerate([60,90,50,110,70,95]):
        bx=x+50+i*(bw+8); s+=r(bx,y+h-20-bh,bw,bh,HDR,BORDER,2)
    return s
def navbar(active=''):
    links=['Dashboard','Food','Calorie Burn','Health','Medications','Wellness','Progress','Reports']
    s=r(0,0,W,56,NAV,NAV,0)+t(24,36,'Care Plus',17,WHITE,'bold')
    x2=180
    for l in links:
        s+=t(x2,36,l,12,'#aaa' if l!=active else WHITE); x2+=len(l)*8+24
    s+=r(W-130,12,118,32,SID,SID,4)+t(W-71,33,'John (42)',11,WHITE,'normal','middle')
    return s
def sidebar(items,active=0):
    s=r(0,56,200,3000,SID,SID,0)
    for i,(label,) in enumerate(items):
        bg=SIDA if i==active else SID
        s+=r(8,64+i*44,184,36,bg,bg,4)+t(20,88+i*44,label,12,WHITE if i==active else '#aaa')
    return s

NAV_ITEMS=[('Dashboard',),('Food',),('Calorie Burn',),('Health',),
           ('Medications',),('Wellness',),('Progress',),('Reports',)]

# ── 04 DASHBOARD ──────────────────────────────────────────
def p04():
    H=980; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Dashboard')+sidebar(NAV_ITEMS,0)
    s+=t(CX+16,90,'Dashboard',18,DARK,'bold')+t(CX+16,112,'Good morning, John. Here is your health summary for today.',13,LIGHT)
    s+=ln(CX,120,W-20,120)
    cw=(CW-60)//4
    for i,(ti,v,sub) in enumerate([('Calories Consumed','1,240 kcal','Today'),('Calories Burned','380 kcal','Today'),('Water Intake','1,500 ml','Today'),('Sleep Duration','7.5 hrs','Last night')]):
        s+=card(CX+16+i*(cw+16),132,cw,88,ti,v,sub)
    for i,(ti,v,sub) in enumerate([('Current BMI','22.9','Normal weight'),('Activity Streak','5 days','Consecutive'),('Active Medications','2','Due today'),('Notifications','3 unread','')]):
        s+=card(CX+16+i*(cw+16),236,cw,88,ti,v,sub)
    s+=r(CX+16,340,CW-16,44,HDR,BORDER,4)+t(CX+28,367,'Complete your BMI check to get personalised health insights',12,MID)
    s+=btn(W-190,348,160,28,'Complete BMI Check')
    s+=t(CX+16,412,"Today's Meals",14,DARK,'bold')
    cols=['Food Item','Meal','Serving','Calories','Protein','Carbs','Fat']; widths=[220,110,90,100,90,90,90]
    s+=th(CX+16,424,cols,widths)
    for i,row in enumerate([['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g'],['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g'],['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g']]):
        s+=tr(CX+16,456+i*34,row,widths,i%2==1)
    s+=t(CX+16,582,"Today's Activities",14,DARK,'bold')
    ac=['Activity','Duration','Calories Burned','Date']; aw=[280,160,200,200]
    s+=th(CX+16,594,ac,aw)
    s+=tr(CX+16,626,['Walking','30 mins','120 kcal','Today'],aw)
    s+=tr(CX+16,660,['Yoga','45 mins','150 kcal','Today'],aw,True)
    s+=t(CX+16,716,'Macro Summary — Today',14,DARK,'bold')
    for i,(label,val,pct) in enumerate([('Protein','62 g',0.4),('Carbohydrates','180 g',0.7),('Fat','38 g',0.3)]):
        my=728+i*52; s+=t(CX+16,my+16,label,11,LIGHT)+t(CX+120,my+16,val,11,MID,'bold')
        s+=r(CX+16,my+22,CW-32,12,HDR,BORDER,6)+r(CX+16,my+22,int((CW-32)*pct),12,BTN,BTN,6)
    s+='</svg>'; return s

# ── 05 PROFILE ────────────────────────────────────────────
def p05():
    H=980; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar()+sidebar(NAV_ITEMS,-1)
    s+=t(CX+16,90,'Profile Management',18,DARK,'bold')+t(CX+16,112,'Update your personal information and preferences.',13,LIGHT)+ln(CX,120,W-20,120)
    s+=r(CX+16,132,CW-16,90,WHITE,BORDER,4)+r(CX+32,148,60,60,HDR,BORDER,30)+t(CX+62,184,'J',20,DARK,'bold','middle')
    s+=t(CX+108,172,'John Smith',16,DARK,'bold')+t(CX+108,192,'john40   |   john@example.com',12,LIGHT)+t(CX+108,210,'Age: 42   |   Male   |   Moderate Activity',11,LIGHT)
    s+=r(CX+16,240,CW-16,480,WHITE,BORDER,4)+sbar(CX+16,240,CW-16,'Personal Information')
    fw=(CW-64)//3
    s+=inp(CX+32,284,fw,'Full Name','John Smith')+inp(CX+32+fw+16,284,fw,'Username','john40')+inp(CX+32+fw*2+32,284,fw,'Email Address','john@example.com')
    s+=inp(CX+32,364,fw,'Birth Year','1982')+inp(CX+32+fw+16,364,fw,'Gender','Male')+inp(CX+32+fw*2+32,364,fw,'Activity Level','Moderate')
    s+=inp(CX+32,444,fw,'Height (cm)','175')+inp(CX+32+fw+16,444,fw,'Weight (kg)','70')+inp(CX+32+fw*2+32,444,fw,'Theme Preference','Light')
    s+=sbar(CX+32,530,CW-48,'Change Password')
    s+=inp(CX+32,572,fw,'New Password','Min. 6 characters')+inp(CX+32+fw+16,572,fw,'Confirm Password','Re-enter password')
    s+=btn(CX+32,650,180,40,'Save Changes')+btn2(CX+228,650,110,40,'Cancel')
    s+='</svg>'; return s

# ── 06 SETTINGS ───────────────────────────────────────────
def p06():
    H=760; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar()+sidebar(NAV_ITEMS,-1)
    s+=t(CX+16,90,'Settings',18,DARK,'bold')+t(CX+16,112,'Manage your account security and preferences.',13,LIGHT)+ln(CX,120,W-20,120)
    s+=r(CX+16,132,680,300,WHITE,BORDER,4)+sbar(CX+16,132,680,'Change Password')
    s+=inp(CX+32,176,640,'Current Password','••••••••')+inp(CX+32,250,640,'New Password (minimum 6 characters)','••••••••')+inp(CX+32,324,640,'Confirm New Password','••••••••')
    s+=btn(CX+32,398,180,38,'Update Password')+btn2(CX+228,398,110,38,'Cancel')
    s+=r(CX+16,452,680,180,WHITE,BORDER,4)+sbar(CX+16,452,680,'Theme Preference')
    s+=r(CX+32,496,200,60,HDR,BORDER,4)+t(CX+132,532,'Light Mode',13,DARK,'bold','middle')
    s+=r(CX+248,496,200,60,BTN,BTN,4)+t(CX+348,532,'Dark Mode',13,WHITE,'bold','middle')
    s+=t(CX+32,572,'Selected theme will apply across all pages.',11,LIGHT)+btn(CX+32,584,160,36,'Save Preference')
    s+=r(CX+16,640,680,100,WHITE,BORDER,4)+sbar(CX+16,640,680,'Account')
    s+=t(CX+32,688,'Delete your account permanently. This action cannot be undone.',12,LIGHT)+btn(CX+32,700,160,36,'Delete Account',BTN2,DARK)
    s+='</svg>'; return s

# ── 07 FOOD RECOGNITION ───────────────────────────────────
def p07():
    H=1000; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Food')+sidebar(NAV_ITEMS,1)
    s+=t(CX+16,90,'Food Recognition',18,DARK,'bold')+t(CX+16,112,'Upload a food image for AI-powered recognition and nutrition lookup.',13,LIGHT)+ln(CX,120,W-20,120)
    half=(CW-32)//2
    s+=r(CX+16,132,half,300,WHITE,BORDER,4)+sbar(CX+16,132,half,'Upload Food Image')
    s+=r(CX+32,176,half-32,180,ROW,BORDER,4)+r(CX+32+(half-32)//2-30,210,60,60,HDR,BORDER,4)
    s+=t(CX+32+(half-32)//2,296,'Drag & drop or click to select image',12,LIGHT,'normal','middle')
    s+=t(CX+32+(half-32)//2,314,'Supported: JPG, PNG, WEBP',10,LIGHT,'normal','middle')
    s+=btn(CX+32,368,half-32,38,'Recognise Food')
    rx=CX+16+half+16
    s+=r(rx,132,half,300,WHITE,BORDER,4)+sbar(rx,132,half,'Recognition Result')
    s+=r(rx+16,176,120,120,HDR,BORDER,4)+t(rx+76,242,'Image Preview',10,LIGHT,'normal','middle')
    s+=t(rx+156,196,'Banana',18,DARK,'bold')+r(rx+156,208,120,22,HDR,BORDER,11)+t(rx+216,224,'Confidence: 94%',10,MID,'normal','middle')
    for i,(label,val) in enumerate([('Calories (100g)','89 kcal'),('Protein','1.1 g'),('Carbohydrates','23 g'),('Fat','0.3 g'),('Fibre','2.6 g')]):
        s+=t(rx+156,248+i*18,f'{label}:',10,LIGHT)+t(rx+300,248+i*18,val,10,MID,'bold')
    s+=r(CX+16,448,CW-16,340,WHITE,BORDER,4)+sbar(CX+16,448,CW-16,'Save to Food Log')
    fw=(CW-64)//4
    s+=inp(CX+32,492,fw,'Food Name','Banana')+inp(CX+32+fw+16,492,fw,'Meal Name','Breakfast')
    s+=inp(CX+32+fw*2+32,492,fw,'Serving Amount (g)','150')+inp(CX+32+fw*3+48,492,fw,'Calories (auto-scaled)','133.5 kcal')
    s+=inp(CX+32,572,fw,'Protein (auto)','1.65 g')+inp(CX+32+fw+16,572,fw,'Carbohydrates (auto)','34.5 g')
    s+=inp(CX+32+fw*2+32,572,fw,'Fat (auto)','0.45 g')+inp(CX+32+fw*3+48,572,fw,'Fibre (auto)','3.9 g')
    s+=btn(CX+32,652,180,38,'Save to Log')+btn2(CX+228,652,160,38,'Manual Entry')
    s+=r(CX+16,708,CW-16,60,ROW,BORDER,4)+t(CX+32,732,'Manual Entry: Select a food from the dropdown or enter custom nutrition values.',12,LIGHT)
    s+=r(CX+32,742,300,28,WHITE,BORDER,3)+t(CX+42,761,'Select food from database...',11,LIGHT)
    s+='</svg>'; return s

# ── 08 FOOD HISTORY ───────────────────────────────────────
def p08():
    H=900; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Food')+sidebar(NAV_ITEMS,1)
    s+=t(CX+16,90,'Food History',18,DARK,'bold')+t(CX+16,112,'All your logged meals and nutrition data.',13,LIGHT)+ln(CX,120,W-20,120)
    cw=(CW-64)//3
    s+=card(CX+16,132,cw,80,'Today Consumed','1,240 kcal','Total intake')+card(CX+16+cw+16,132,cw,80,'Today Burned','380 kcal','Activity')+card(CX+16+cw*2+32,132,cw,80,'Net Calories','860 kcal','Consumed - Burned')
    s+=btn(W-200,140,170,36,'+ Log New Food')
    s+=r(CX+16,228,CW-16,600,WHITE,BORDER,4)+sbar(CX+16,228,CW-16,'Food Log')
    cols=['Food Name','Meal','Serving','Calories','Protein','Carbs','Fat','Date & Time','Action']; widths=[180,100,80,90,80,80,80,150,120]
    s+=th(CX+16,260,cols,widths)
    for i,row in enumerate([['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g','Today 08:30'],['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g','Today 13:00'],['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g','Today 16:00'],['Grilled Chicken','Dinner','200 g','330 kcal','62 g','0 g','7.2 g','Yesterday'],['Oatmeal','Breakfast','180 g','166 kcal','6 g','28 g','3.6 g','Yesterday'],['Banana','Breakfast','100 g','52 kcal','0.8 g','13.8 g','0.2 g','2 days ago']]):
        s+=tr(CX+16,292+i*36,row,widths[:-1],i%2==1)+btn2(CX+16+sum(widths[:-1]),296+i*36,100,28,'Delete')
    s+='</svg>'; return s

print('04-08 built')

# ── 09 CALORIE BURN ───────────────────────────────────────
def p09():
    H=960; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Calorie Burn')+sidebar(NAV_ITEMS,2)
    s+=t(CX+16,90,'Calorie Burn Prediction',18,DARK,'bold')+t(CX+16,112,'AI-powered calorie burn estimation using your health profile.',13,LIGHT)+ln(CX,120,W-20,120)
    lw=660; rw=CW-lw-32; rx=CX+16+lw+16; fw=(lw-48)//2
    s+=r(CX+16,132,lw,560,WHITE,BORDER,4)+sbar(CX+16,132,lw,'Prediction Parameters')
    s+=inp(CX+32,176,lw-32,'Activity Type','e.g. Walking, Running, Cycling')
    s+=inp(CX+32,256,fw,'Duration (minutes)','30')+inp(CX+32+fw+16,256,fw,'Heart Rate (bpm)','110')
    s+=inp(CX+32,336,fw,'Body Temperature (C)','38.5')+inp(CX+32+fw+16,336,fw,'Weight (kg)','70')
    s+=inp(CX+32,416,fw,'Height (cm)','175')+inp(CX+32+fw+16,416,fw,'Gender','Male  (from profile)')
    s+=t(CX+32,510,'Age and gender are pre-filled from your profile.',11,LIGHT)
    s+=btn(CX+32,524,lw-32,42,'Predict Calorie Burn')
    s+=r(rx,132,rw,240,WHITE,BORDER,4)+sbar(rx,132,rw,'Prediction Result')
    s+=r(rx+16,176,rw-32,120,HDR,BORDER,4)+t(rx+rw//2,228,'Estimated Calorie Burn',12,LIGHT,'normal','middle')+t(rx+rw//2,260,'247 kcal',26,DARK,'bold','middle')
    s+=t(rx+16,308,'Based on: Walking · 30 min · HR 110 bpm',11,LIGHT)
    s+=r(rx,388,rw,300,WHITE,BORDER,4)+sbar(rx,388,rw,'Save Activity to Log')
    s+=inp(rx+16,432,rw-32,'Activity Type','Walking')+inp(rx+16,506,rw-32,'Duration (minutes)','30')+inp(rx+16,580,rw-32,'Calories Burned','247')
    s+=btn(rx+16,640,rw-32,38,'Save Activity')
    s+=r(CX+16,708,CW-16,220,WHITE,BORDER,4)+sbar(CX+16,708,CW-16,'Recent Activity Log')
    ac=['Activity','Duration','Calories Burned','Date','Action']; aw=[280,160,200,200,160]
    s+=th(CX+16,740,ac,aw)
    s+=tr(CX+16,772,['Walking','30 mins','247 kcal','Today'],aw[:-1])+btn2(CX+16+sum(aw[:-1]),776,130,28,'Delete')
    s+=tr(CX+16,806,['Yoga','45 mins','150 kcal','Yesterday'],aw[:-1],True)+btn2(CX+16+sum(aw[:-1]),810,130,28,'Delete')
    s+='</svg>'; return s

# ── 10 HEALTH ─────────────────────────────────────────────
def p10():
    H=960; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Health')+sidebar(NAV_ITEMS,3)
    s+=t(CX+16,90,'Health Monitoring',18,DARK,'bold')+t(CX+16,112,'Track your BMI, blood pressure, blood sugar and heart rate.',13,LIGHT)+ln(CX,120,W-20,120)
    fw=(CW-64)//4
    s+=r(CX+16,132,CW-16,300,WHITE,BORDER,4)+sbar(CX+16,132,CW-16,'Add Health Record')
    s+=inp(CX+32,176,fw,'Weight (kg)','70')+inp(CX+32+fw+16,176,fw,'Height (cm)','175')+inp(CX+32+fw*2+32,176,fw,'BMI (auto-calculated)','22.9')+inp(CX+32+fw*3+48,176,fw,'Blood Pressure','120/80')
    s+=inp(CX+32,256,fw,'Blood Sugar (mg/dL)','95')+inp(CX+32+fw+16,256,fw,'Cholesterol (mg/dL)','180')+inp(CX+32+fw*2+32,256,fw,'Heart Rate (bpm)','72')+inp(CX+32+fw*3+48,256,fw,'Notes','Optional notes')
    s+=btn(CX+32,340,200,38,'Save Health Record')+btn2(CX+248,340,110,38,'Cancel')
    s+=r(CX+16,448,CW-16,480,WHITE,BORDER,4)+sbar(CX+16,448,CW-16,'Health Records History')
    cols=['Date','Weight','Height','BMI','Blood Pressure','Blood Sugar','Cholesterol','Heart Rate','Action']; widths=[120,80,80,70,120,110,110,100,110]
    s+=th(CX+16,480,cols,widths)
    for i,row in enumerate([['Today','70 kg','175 cm','22.9','120/80','95 mg/dL','180 mg/dL','72 bpm'],['Yesterday','70.5 kg','175 cm','23.1','122/82','98 mg/dL','182 mg/dL','74 bpm'],['3 days ago','71 kg','175 cm','23.2','118/78','92 mg/dL','178 mg/dL','70 bpm'],['1 week ago','71.5 kg','175 cm','23.3','124/84','100 mg/dL','185 mg/dL','76 bpm']]):
        s+=tr(CX+16,512+i*36,row,widths[:-1],i%2==1)+btn2(CX+16+sum(widths[:-1]),516+i*36,90,28,'Delete')
    s+='</svg>'; return s

# ── 11 MEDICATIONS ────────────────────────────────────────
def p11():
    H=980; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Medications')+sidebar(NAV_ITEMS,4)
    s+=t(CX+16,90,'Medications & Reminders',18,DARK,'bold')+t(CX+16,112,'Manage your medication schedule and track doses taken.',13,LIGHT)+ln(CX,120,W-20,120)
    fw=(CW-64)//4
    s+=r(CX+16,132,CW-16,220,WHITE,BORDER,4)+sbar(CX+16,132,CW-16,'Add Medication')
    s+=inp(CX+32,176,fw,'Medication Name *','e.g. Metformin')+inp(CX+32+fw+16,176,fw,'Dosage','e.g. 500mg')+inp(CX+32+fw*2+32,176,fw,'Scheduled Time *','HH:MM  e.g. 08:00')+inp(CX+32+fw*3+48,176,fw,'Frequency','e.g. Daily')
    s+=inp(CX+32,256,fw*2+16,'Notes','Optional notes')+btn(CX+32,316,180,36,'Add Medication')
    lw=700; rw=CW-lw-32; rx=CX+16+lw+16
    s+=r(CX+16,368,lw,560,WHITE,BORDER,4)+sbar(CX+16,368,lw,'Active Medications')
    for i,(name,dose,time,freq) in enumerate([('Metformin','500mg','08:00','Daily'),('Aspirin','100mg','20:00','Daily'),('Vitamin D','1000 IU','09:00','Daily'),('Lisinopril','10mg','07:00','Daily')]):
        my=408+i*112; s+=r(CX+32,my,lw-32,96,ROW,BORDER,4)+t(CX+48,my+24,name,14,DARK,'bold')+t(CX+48,my+44,f'Dosage: {dose}',11,LIGHT)+t(CX+48,my+60,f'Time: {time}   Frequency: {freq}',11,LIGHT)
        s+=btn(CX+32+lw-200,my+16,100,30,'Mark Taken')+btn2(CX+32+lw-90,my+16,70,30,'Delete')
    s+=r(rx,368,rw,560,WHITE,BORDER,4)+sbar(rx,368,rw,'Recent Dose Logs')
    for i,(name,status,time) in enumerate([('Metformin','Taken','Today 08:05'),('Aspirin','Taken','Yesterday 20:02'),('Vitamin D','Taken','Yesterday 09:10'),('Lisinopril','Taken','Today 07:03'),('Metformin','Taken','Yesterday 08:00')]):
        ly=408+i*72; s+=r(rx+16,ly,rw-32,56,ROW,BORDER,4)+t(rx+28,ly+22,name,13,DARK,'bold')+t(rx+28,ly+40,time,10,LIGHT)
        s+=r(rx+rw-100,ly+16,80,24,HDR,BORDER,12)+t(rx+rw-60,ly+32,status,10,MID,'normal','middle')
    s+='</svg>'; return s

# ── 12 WELLNESS ───────────────────────────────────────────
def p12():
    H=1040; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Wellness')+sidebar(NAV_ITEMS,5)
    s+=t(CX+16,90,'Wellness Tracking',18,DARK,'bold')+t(CX+16,112,'Log water intake, exercise sessions and sleep records.',13,LIGHT)+ln(CX,120,W-20,120)
    third=(CW-48)//3
    # water
    s+=r(CX+16,132,third,260,WHITE,BORDER,4)+sbar(CX+16,132,third,'Water Intake')
    s+=t(CX+16+third//2,192,'1,500 ml',22,DARK,'bold','middle')+t(CX+16+third//2,212,'logged today  (goal: 2,500 ml)',11,LIGHT,'normal','middle')
    s+=r(CX+32,224,third-32,10,HDR,BORDER,5)+r(CX+32,224,int((third-32)*0.6),10,BTN,BTN,5)+t(CX+32,250,'1,500 / 2,500 ml',10,LIGHT)
    s+=inp(CX+32,258,third-32,'Amount (ml)','250')+btn(CX+32,316,third-32,36,'Add Water')
    # exercise
    ex=CX+16+third+16; s+=r(ex,132,third,260,WHITE,BORDER,4)+sbar(ex,132,third,'Exercise')
    s+=inp(ex+16,176,third-32,'Activity Name','e.g. Yoga, Walking')+inp(ex+16,250,third-32,'Duration (minutes)','30')+inp(ex+16,324,third-32,'Calories Burned','120')+btn(ex+16,362,third-32,36,'Log Exercise')
    # sleep
    sx=CX+16+third*2+32; s+=r(sx,132,third,260,WHITE,BORDER,4)+sbar(sx,132,third,'Sleep')
    s+=inp(sx+16,176,third-32,'Sleep Time','YYYY-MM-DDTHH:MM')+inp(sx+16,250,third-32,'Wake Time','YYYY-MM-DDTHH:MM')
    s+=t(sx+16,330,'Calculated Duration: 8.0 hours',12,MID,'bold')+btn(sx+16,344,third-32,36,'Log Sleep')
    # reminders
    s+=r(CX+16,408,CW-16,400,WHITE,BORDER,4)+sbar(CX+16,408,CW-16,'Wellness Reminders')
    s+=btn(W-220,414,100,20,'+ Add',BTN,WHITE,10)+btn2(W-110,414,90,20,'Clear All')
    for i,(name,time) in enumerate([('10-minute walk','09:00'),('Light stretching','11:00'),('Drink water','13:00'),('Stand and move','15:00'),('Breathing exercise','20:00')]):
        ry=448+i*56; s+=r(CX+32,ry,CW-48,44,ROW,BORDER,4)+t(CX+48,ry+27,name,13,DARK,'bold')
        s+=r(CX+CW-200,ry+10,70,24,WHITE,BORDER,3)+t(CX+CW-165,ry+27,time,11,MID,'normal','middle')+btn2(CX+CW-120,ry+10,90,24,'Delete')
    s+=r(CX+16,824,CW-16,100,WHITE,BORDER,4)+sbar(CX+16,824,CW-16,'Add Custom Reminder')
    s+=inp(CX+32,856,300,'Activity Name','e.g. Meditation')+inp(CX+348,856,160,'Time (HH:MM)','07:00')+btn(CX+528,862,160,36,'Add Reminder')
    s+='</svg>'; return s

# ── 13 PROGRESS ───────────────────────────────────────────
def p13():
    H=1020; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Progress')+sidebar(NAV_ITEMS,6)
    s+=t(CX+16,90,'Progress & Analytics',18,DARK,'bold')+t(CX+16,112,'Visual trends for your health and fitness data.',13,LIGHT)+ln(CX,120,W-20,120)
    s+=r(CX+16,132,CW-16,44,WHITE,BORDER,4)+t(CX+32,160,'Date Range:',12,MID,'bold')
    for i,(label,active) in enumerate([('7 Days',False),('30 Days',True),('90 Days',False)]):
        s+=btn(CX+130+i*96,140,86,28,label,BTN if active else BTN2,WHITE if active else DARK,11)
    cw=(CW-48)//2
    s+=chart(CX+16,192,cw,200,'Weight Trend (kg)')+chart(CX+16+cw+16,192,cw,200,'BMI Trend')
    s+=chart(CX+16,408,cw,200,'Calories Consumed vs Burned (kcal)')+chart(CX+16+cw+16,408,cw,200,'Daily Water Intake (Litres)')
    cw3=(CW-64)//3
    s+=chart(CX+16,624,cw3,200,'Blood Pressure (mmHg)')+chart(CX+16+cw3+16,624,cw3,200,'Blood Sugar (mg/dL)')+chart(CX+16+cw3*2+32,624,cw3,200,'Heart Rate (bpm)')
    s+='</svg>'; return s

# ── 14 REPORTS ────────────────────────────────────────────
def p14():
    H=880; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=navbar('Reports')+sidebar(NAV_ITEMS,7)
    s+=t(CX+16,90,'Health Reports',18,DARK,'bold')+t(CX+16,112,'Generate, download and securely share your health reports.',13,LIGHT)+ln(CX,120,W-20,120)
    s+=r(CX+16,132,CW-16,180,WHITE,BORDER,4)+sbar(CX+16,132,CW-16,'Generate PDF Report')
    s+=t(CX+32,180,'Select date range:',12,MID)
    for i,(label,) in enumerate([('Last 7 Days',),('Last 30 Days',),('Last 90 Days',)]):
        s+=btn(CX+32+i*160,192,148,34,label,BTN if i==1 else BTN2,WHITE if i==1 else DARK,11)
    s+=btn(CX+32,244,220,38,'Download PDF Report')+btn2(CX+268,244,200,38,'Create Share Link')
    s+=t(CX+32,298,'A secure shareable link will be valid for 7 days and can be revoked at any time.',11,LIGHT)
    s+=r(CX+16,328,CW-16,500,WHITE,BORDER,4)+sbar(CX+16,328,CW-16,'Secure Share Links')
    cols=['Share ID','Report Type','Created','Expires','Status','Actions']; widths=[100,160,160,160,120,220]
    s+=th(CX+16,360,cols,widths)
    for i,(sid,rtype,created,expires,status) in enumerate([('SH-001','Health Summary','01 Jan 2025','08 Jan 2025','Active'),('SH-002','Health Summary','15 Dec 2024','22 Dec 2024','Expired'),('SH-003','Health Summary','20 Dec 2024','27 Dec 2024','Revoked')]):
        s+=tr(CX+16,392+i*48,[sid,rtype,created,expires,status],widths[:-1],i%2==1)
        if status=='Active': s+=btn(CX+16+sum(widths[:-1]),396+i*48,100,32,'Copy Link')+btn2(CX+16+sum(widths[:-1])+108,396+i*48,100,32,'Revoke')
        else: s+=t(CX+16+sum(widths[:-1])+40,416+i*48,'—',13,LIGHT)
    s+='</svg>'; return s

# ── 15 SHARED REPORT ──────────────────────────────────────
def p15():
    H=880; s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="{BG}"/>\n'
    s+=r(0,0,W,56,NAV,NAV,0)+t(32,36,'Care Plus',18,WHITE,'bold')+t(W//2,36,'Shared Health Report',14,WHITE,'normal','middle')
    s+=r(W-160,14,140,28,SID,SID,4)+t(W-90,32,'Secure Link',11,WHITE,'normal','middle')
    s+=r(0,56,W,40,HDR,BORDER,0)+t(W//2,81,'This report is valid and expires on 08 Jan 2025. View only — no login required.',12,MID,'normal','middle')
    s+=r(40,112,W-80,88,WHITE,BORDER,4)+r(56,128,56,56,HDR,BORDER,28)+t(84,162,'J',20,DARK,'bold','middle')
    s+=t(128,148,'John Smith',16,DARK,'bold')+t(128,168,'Shared health summary  ·  Last 30 days',12,LIGHT)+t(128,186,'Age: 42   |   Male',11,LIGHT)
    cw=(W-80-48)//4
    for i,(ti,v,sub) in enumerate([('Latest BMI','22.9','Normal weight'),('Weight','70 kg','Last recorded'),('Blood Pressure','120/80 mmHg','Last recorded'),('Heart Rate','72 bpm','Last recorded')]):
        s+=card(40+i*(cw+16),228,cw,80,ti,v,sub)
    s+=t(40,336,'Recent Food Log (Last 30 Days)',14,DARK,'bold')
    s+=r(40,350,W-80,420,WHITE,BORDER,4)
    cols=['Food Name','Meal','Serving','Calories','Protein','Carbs','Fat','Date']; widths=[190,110,90,100,90,90,90,150]
    s+=th(40,350,cols,widths)
    for i,row in enumerate([['Banana','Breakfast','150 g','78 kcal','1.2 g','20 g','0.3 g','Today'],['Biryani','Lunch','250 g','425 kcal','18.8 g','60 g','13 g','Today'],['Apple','Snack','120 g','62 kcal','0.4 g','16.6 g','0.2 g','Yesterday'],['Grilled Chicken','Dinner','200 g','330 kcal','62 g','0 g','7.2 g','Yesterday']]):
        s+=tr(40,382+i*36,row,widths,i%2==1)
    s+=r(0,800,W,80,HDR,BORDER,0)+t(W//2,846,'Generated by Care Plus  ·  This link will expire automatically  ·  Do not share with untrusted parties.',11,LIGHT,'normal','middle')
    s+='</svg>'; return s

# ── INJECT INTO HTML ──────────────────────────────────────
builders = {
    'dashboard': p04, 'profile': p05, 'settings': p06,
    'food': p07, 'foodhist': p08, 'calorie': p09,
    'health': p10, 'meds': p11, 'wellness': p12,
    'progress': p13, 'reports': p14, 'shared': p15,
}

with open(r'e:\Care_Plus\wireframes.html', 'r', encoding='utf-8') as f:
    html = f.read()

inject = ''
for key, fn in builders.items():
    inject += f'\n<div class="wf-frame" id="wf-{key}">\n{fn()}\n</div>\n'

html = html.replace('</div><!-- /frame-wrap -->', inject + '\n</div><!-- /frame-wrap -->')

with open(r'e:\Care_Plus\wireframes.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done — wireframes.html updated with all 15 pages.')
