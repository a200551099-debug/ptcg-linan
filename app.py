import streamlit as st
import pandas as pd
import itertools
import io

# ==========================================
# 1. 核心配置与样式
# ==========================================
st.set_page_config(page_title="PTCG 战队 BP 助手 (博弈版)", page_icon="🧠", layout="wide")

def get_color_style(val):
    if not isinstance(val, (int, float)): return ""
    if val <= 1.5: return "background-color: #22c55e; color: white"
    if val <= 2.5: return "background-color: #86efac; color: #14532d"
    if val <= 3.5: return "background-color: #dbeafe; color: #1e3a8a"
    if val <= 4.5: return "background-color: #fef08a; color: #713f12"
    if val <= 5.5: return "background-color: #fca5a5; color: #7f1d1d"
    return "background-color: #ef4444; color: white; font-weight: bold"

# ==========================================
# 2. 内置默认数据
# ==========================================
DEFAULT_DATA = [
    { "player": "三毛九鬼龙", "deck": "鬼龙", "matchups": { "比雕恶喷": 2, "尾狸恶喷": 4, "沙奈朵": 3, "鬼龙": 5, "轰鬼": 5, "密勒顿": 4, "勾喷": 6, "LTB": 5, "纯恶轰明月": 6, "水轰明月": 6, "汇流梦幻": 5, "双无梦幻": 6, "水熊": 3, "炎帝铁武者": 2, "古剑豹": 6, "赛富豪": 3, "宙斯系列": 2, "洛奇亚": 6, "卡比兽": 2, "索罗": 2, "毛崖蟹": 2 } },
    { "player": "土豆", "deck": "鬼龙", "matchups": { "比雕恶喷": 1, "尾狸恶喷": 3, "沙奈朵": 2, "鬼龙": 4, "轰鬼": 3, "密勒顿": 3, "勾喷": 5, "LTB": 4, "纯恶轰明月": 4, "水轰明月": 4, "汇流梦幻": 2, "双无梦幻": 4, "水熊": 2, "炎帝铁武者": 1, "古剑豹": 4, "赛富豪": 1, "宙斯系列": 1, "洛奇亚": 5, "卡比兽": 1, "索罗": 1, "毛崖蟹": 1 } },
    { "player": "语申", "deck": "尾狸恶喷", "matchups": { "比雕恶喷": 5, "尾狸恶喷": 5, "沙奈朵": 4, "鬼龙": 6, "轰鬼": 6, "密勒顿": 1, "勾喷": 4, "LTB": 6, "纯恶轰明月": 1, "水轰明月": 1, "汇流梦幻": 1, "双无梦幻": 1, "水熊": 5, "炎帝铁武者": 4, "古剑豹": 3, "赛富豪": 5, "宙斯系列": 5, "洛奇亚": 1, "卡比兽": 6, "索罗": 6, "毛崖蟹": 6 } },
    { "player": "ZZ", "deck": "沙奈朵", "matchups": { "比雕恶喷": 4, "尾狸恶喷": 2, "沙奈朵": 1, "鬼龙": 3, "轰鬼": 2, "密勒顿": 5, "勾喷": 1, "LTB": 3, "纯恶轰明月": 3, "水轰明月": 3, "汇流梦幻": 3, "双无梦幻": 2, "水熊": 4, "炎帝铁武者": 5, "古剑豹": 5, "赛富豪": 2, "宙斯系列": 4, "洛奇亚": 2, "卡比兽": 3, "索罗": 4, "毛崖蟹": 4 } },
    { "player": "乐子人", "deck": "lostK喷", "matchups": { "比雕恶喷": 3, "尾狸恶喷": 1, "沙奈朵": 6, "鬼龙": 2, "轰鬼": 1, "密勒顿": 6, "勾喷": 3, "LTB": 2, "纯恶轰明月": 2, "水轰明月": 2, "汇流梦幻": 6, "双无梦幻": 5, "水熊": 6, "炎帝铁武者": 6, "古剑豹": 2, "赛富豪": 4, "宙斯系列": 6, "洛奇亚": 4, "卡比兽": 5, "索罗": 3, "毛崖蟹": 3 } },
    { "player": "龟龟", "deck": "涡轮梦幻", "matchups": { "比雕恶喷": 6, "尾狸恶喷": 6, "沙奈朵": 5, "鬼龙": 1, "轰鬼": 4, "密勒顿": 2, "勾喷": 2, "LTB": 1, "纯恶轰明月": 5, "水轰明月": 5, "汇流梦幻": 4, "双无梦幻": 3, "水熊": 1, "炎帝铁武者": 3, "古剑豹": 1, "赛富豪": 6, "宙斯系列": 3, "洛奇亚": 3, "卡比兽": 4, "索罗": 5, "毛崖蟹": 5 } }
]

# ==========================================
# 3. CSV 解析 (核弹清洗版)
# ==========================================
def parse_uploaded_csv(file):
    try:
        bytes_data = file.getvalue()
        try: string_data = bytes_data.decode('utf-8')
        except: string_data = bytes_data.decode('gbk')
        
        lines = string_data.split('\n')
        valid_lines = [line for line in lines if line.replace(',', '').strip()]
        cleaned_csv = '\n'.join(valid_lines)
        
        df_raw = pd.read_csv(io.StringIO(cleaned_csv), header=None)
        header_idx = -1
        for i, row in df_raw.iterrows():
            row_str = ",".join(row.astype(str).values)
            if "比雕" in row_str or "沙奈朵" in row_str or "恶喷" in row_str:
                header_idx = i; break
        if header_idx == -1: return None, "未找到表头"

        df = pd.read_csv(io.StringIO(cleaned_csv), header=header_idx)
        df.columns = [str(col).strip().replace('\ufeff', '') for col in df.columns]
        
        start_idx = -1
        for i, col in enumerate(df.columns):
            if "比雕" in str(col) or "沙奈朵" in str(col) or "恶喷" in str(col):
                start_idx = i; break
        if start_idx == -1: start_idx = 2 
        
        opponent_cols = [c for c in df.columns[start_idx:] if "Unnamed" not in str(c)]
        
        team_data = []
        for index, row in df.iterrows():
            p_val = str(row.iloc[0]).strip()
            d_val = str(row.iloc[1]).strip()
            if not p_val or p_val.lower() == "nan" or "unnamed" in p_val.lower(): continue
            matchups = {}
            for opp in opponent_cols:
                try: score = float(row[opp])
                except: score = 3.0
                matchups[opp] = score
            team_data.append({ "player": p_val, "deck": d_val, "matchups": matchups })
            
        return team_data, f"成功读取 {len(team_data)} 名队员"
    except Exception as e: return None, f"解析错误: {e}"

# ==========================================
# 4. 智能博弈算法
# ==========================================
def calculate_smart_bp(team_data, selected_opponents):
    results = {}
    unique_opps = list(set(selected_opponents))
    
    # --- Step 1: 我们的 Ban (正常逻辑) ---
    # Ban 掉那个全队打起来最费劲的
    opp_scores = {}
    for opp in unique_opps:
        clean_opp = opp.strip()
        total = 0
        for m in team_data:
            score = 3.0
            if clean_opp in m['matchups']: score = m['matchups'][clean_opp]
            else:
                for k in m['matchups']:
                    if clean_opp in k or k in clean_opp:
                        score = m['matchups'][k]; break
            total += score
        opp_scores[opp] = total
            
    if opp_scores:
        our_ban_target = max(opp_scores, key=opp_scores.get)
        our_ban_score = opp_scores[our_ban_target]
    else:
        our_ban_target = None; our_ban_score = 0
        
    results['our_ban'] = our_ban_target
    results['our_ban_score'] = our_ban_score
    
    # 剩余对手
    remaining_opps = selected_opponents.copy()
    if our_ban_target and our_ban_target in remaining_opps: 
        remaining_opps.remove(our_ban_target)
    
    if not remaining_opps: return results

    # --- Step 2: 预测对手 Ban (博弈逻辑) ---
    # 对手会Ban掉那个对他们威胁最大的人 (即：打剩余对手总分最低/最好的人)
    player_threats = {} # 我们的队员 -> 对剩余敌人的总分 (越低越强)
    
    for m in team_data:
        p_total = 0
        for opp in remaining_opps:
            clean_opp = opp.strip()
            score = 3.0
            if clean_opp in m['matchups']: score = m['matchups'][clean_opp]
            else:
                for k in m['matchups']:
                    if clean_opp in k or k in clean_opp:
                        score = m['matchups'][k]; break
            p_total += score
        player_threats[m['player']] = p_total
        
    # 找到分最低的 (威胁最大的)
    predicted_enemy_ban = min(player_threats, key=player_threats.get)
    predicted_ban_score = player_threats[predicted_enemy_ban]
    
    results['predicted_ban'] = predicted_enemy_ban
    results['predicted_ban_score'] = predicted_ban_score
    results['remaining_opps'] = remaining_opps

    # --- Step 3: 智能 Pick (献祭流) ---
    # 我们选 4 个人。
    # 假设对手 Ban 掉了这 4 个人里最强的那个 (如果预测的Ban位在里面的话)。
    # 我们要找一个组合，使得【被 Ban 掉核心后】，剩下的 3 个人依然最强。
    
    all_members = [m['player'] for m in team_data]
    c_size = min(4, len(all_members))
    combos = list(itertools.combinations(all_members, c_size))
    
    best_combo = None
    best_smart_score = float('inf') # 越低越好
    
    for combo in combos:
        # 1. 在这个组合里，谁是对手最想 Ban 的？(威胁最大的)
        # 并不是直接用 predicted_enemy_ban，因为那个可能不在这个组合里
        # 我们要看这个组合内部，谁最强
        
        combo_players_scores = {p: player_threats[p] for p in combo}
        # 这个组合里的“大哥”
        combo_ace = min(combo_players_scores, key=combo_players_scores.get)
        
        # 2. 假设这个大哥被 Ban 了 (献祭)
        remaining_3 = [p for p in combo if p != combo_ace]
        
        # 3. 计算剩下 3 个人的总分
        combo_residual_score = sum(player_threats[p] for p in remaining_3)
        
        if combo_residual_score < best_smart_score:
            best_smart_score = combo_residual_score
            best_combo = combo
            
    results['pick_combo'] = best_combo
    results['smart_score'] = best_smart_score
    
    return results

# ==========================================
# 5. 界面
# ==========================================
st.title("🧠 PTCG 战队 BP 助手 (博弈版)")

if "analysis_done" not in st.session_state: st.session_state.analysis_done = False

with st.sidebar:
    st.header("1. 数据源")
    uploaded_file = st.file_uploader("上传 CSV", type="csv")
    current_data = DEFAULT_DATA
    if uploaded_file:
        parsed, msg = parse_uploaded_csv(uploaded_file)
        if parsed:
            current_data = parsed
            st.success(f"✅ {msg}")
            if len(current_data) != 6: st.warning(f"⚠️ 识别到 {len(current_data)} 人")
        else: st.error(msg)
    else: st.info("使用内置默认数据")

    st.markdown("---")
    st.header("2. 选择对手")
    sel_ops = []
    all_ops = set()
    for m in current_data: all_ops.update(m['matchups'].keys())
    sorted_ops = sorted([x for x in all_ops if x!="其它"])
    defaults = ["沙奈朵", "鬼龙", "密勒顿", "赛富豪", "(无)", "(无)"]
    for i in range(6):
        opts = ["(无)"] + sorted_ops
        idx = opts.index(defaults[i]) if defaults[i] in opts else 0
        d = st.selectbox(f"对手 {i+1}", opts, index=idx, key=f"s_{i}")
        if d != "(无)": sel_ops.append(d)
        
    st.markdown("---")
    run_calc = st.button("🚀 确认并分析", type="primary", use_container_width=True)

if run_calc: st.session_state.analysis_done = True

if not st.session_state.analysis_done:
    st.info("👈 请选择对手并点击分析")
    with st.expander("👀 数据预览"):
        st.dataframe(pd.DataFrame([{'队员':m['player'], **m['matchups']} for m in current_data]).head(), use_container_width=True)
else:
    if not sel_ops:
        st.warning("⚠️ 未选择对手")
    else:
        st.success(f"✅ 战术分析完成")
        res = calculate_smart_bp(current_data, sel_ops)
        
        # 第一行：Ban 和 预测
        c1, c2 = st.columns(2)
        with c1:
            st.error(f"🔴 建议我方 Ban: **{res['our_ban']}**")
            st.caption(f"如果不Ban它，我方全队总劣势最大 (威胁分 {res['our_ban_score']})")
            
        with c2:
            st.warning(f"🔮 预测敌方 Ban: **{res['predicted_ban']}**")
            st.caption(f"他是我们队对阵【剩余对手】时的头号杀手 (威胁分 {res['predicted_ban_score']})，大概率会被针对。")
            
        st.markdown("---")
        
        # 第二行：Pick
        st.subheader("🟢 推荐 4 人大名单 (献祭流策略)")
        if res['pick_combo']:
            st.success(f"**{' + '.join(res['pick_combo'])}**")
            
            st.info(f"""
            **💡 推荐理由：**
            我们把 **{res['predicted_ban']}** (或其他强力核心) 放进去作为“诱饵”。
            即使对手真的Ban掉了这个组合里最强的大哥，**剩下的 3 个人依然是所有备选方案里最能打的**。
            (抗压评分: {res['smart_score']})
            """)
        else:
            st.info("数据不足")
            
        st.markdown("---")
        # 详情表
        st.subheader("📊 实时优劣势数据")
        st.caption("以下分数基于当前选择的对手：")
        rows = []
        for m in current_data:
            r = {"队员": f"{m['player']}"}
            for i, opp in enumerate(sel_ops):
                clean = opp.strip()
                score = 3.0
                if clean in m['matchups']: score = m['matchups'][clean]
                else:
                    for k in m['matchups']:
                        if clean in k or k in clean: score = m['matchups'][k]; break
                r[f"{opp} #{i+1}"] = score
            rows.append(r)
        st.dataframe(pd.DataFrame(rows).set_index("队员").style.map(get_color_style), use_container_width=True)
        
        if st.button("🔄 重置"):
            st.session_state.analysis_done = False
            st.rerun()


