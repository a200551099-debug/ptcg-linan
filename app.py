import streamlit as st
import pandas as pd
import itertools
import io

# ==========================================
# 1. 核心配置与样式
# ==========================================
st.set_page_config(page_title="PTCG 战队 BP 沙盘推演 (修复双卡组版)", page_icon="♟️", layout="wide")

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
# 4. 模拟推演算法
# ==========================================
def calculate_simulation(team_data, remaining_opponents):
    results = {}
    
    if not remaining_opponents: return None

    # --- 1. 预测对手 Ban ---
    # 找出剩余对手中，对我方威胁最大（分最低）的人
    player_threats = {} 
    
    for m in team_data:
        p_total = 0
        for opp in remaining_opponents:
            clean_opp = opp.strip()
            score = 3.0
            if clean_opp in m['matchups']: score = m['matchups'][clean_opp]
            else:
                for k in m['matchups']:
                    if clean_opp in k or k in clean_opp:
                        score = m['matchups'][k]; break
            p_total += score
        player_threats[m['player']] = p_total
        
    predicted_enemy_ban = min(player_threats, key=player_threats.get)
    predicted_ban_score = player_threats[predicted_enemy_ban]
    
    results['predicted_ban'] = predicted_enemy_ban
    results['predicted_ban_score'] = predicted_ban_score

    # --- 2. 智能 Pick (献祭流) ---
    all_members = [m['player'] for m in team_data]
    c_size = min(4, len(all_members))
    combos = list(itertools.combinations(all_members, c_size))
    
    best_combo = None
    best_smart_score = float('inf')
    
    for combo in combos:
        # 在这个组合里，谁是对手最想 Ban 的？
        combo_players_scores = {p: player_threats[p] for p in combo}
        combo_ace = min(combo_players_scores, key=combo_players_scores.get)
        
        # 假设这个大哥被 Ban 了 (献祭)
        remaining_3 = [p for p in combo if p != combo_ace]
        
        # 计算剩下 3 个人的总分
        combo_residual_score = sum(player_threats[p] for p in remaining_3)
        
        if combo_residual_score < best_smart_score:
            best_smart_score = combo_residual_score
            best_combo = combo
            
    results['pick_combo'] = best_combo
    results['smart_score'] = best_smart_score
    results['sacrificed_ace'] = predicted_enemy_ban 
    
    return results

# ==========================================
# 5. 界面
# ==========================================
st.title("♟️ PTCG 战队 BP 沙盘推演")

# --- 侧边栏 ---
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
    run_calc = st.button("🚀 确认并进入推演", type="primary", use_container_width=True)

# --- Session State 管理 ---
if "sim_active" not in st.session_state: st.session_state.sim_active = False

if run_calc: st.session_state.sim_active = True

# --- 主界面 ---
if not st.session_state.sim_active:
    st.info("👈 请在左侧选择对手并点击确认")
    with st.expander("👀 数据预览"):
        st.dataframe(pd.DataFrame([{'队员':m['player'], **m['matchups']} for m in current_data]).head(), use_container_width=True)

else:
    if not sel_ops:
        st.warning("⚠️ 未选择对手")
    else:
        # ========================================
        # 沙盘推演区 (修复双卡组问题)
        # ========================================
        st.markdown("### 1. 假如我方 Ban 掉...")
        st.caption("请点击下方按钮，模拟我方 Ban 掉某套卡组后的最优解：")
        
        # 【关键修复】创建带索引的唯一标签
        # 例如：["沙奈朵 (#1)", "沙奈朵 (#2)", "鬼龙 (#3)"]
        ban_options_labels = []
        for idx, op in enumerate(sel_ops):
            ban_options_labels.append(f"{op} (#{idx+1})")
            
        # 让用户选择要Ban的“唯一标签”
        selected_label = st.radio("选择要 Ban 的目标:", ban_options_labels, horizontal=True)
        
        # 解析用户选了第几个
        # 找到被选中的索引
        ban_index = ban_options_labels.index(selected_label)
        
        # 被Ban的卡组名（用于显示）
        banned_deck_name = sel_ops[ban_index]
        
        # 【关键修复】构建剩余对手列表
        # 使用索引移除，确保只移除一个，而不移除所有同名卡组
        remaining_opps = sel_ops.copy()
        remaining_opps.pop(ban_index)
        
        st.markdown("---")
        
        if remaining_opps:
            res = calculate_simulation(current_data, remaining_opps)
            
            c1, c2 = st.columns([1, 1])
            
            with c1:
                st.subheader("🔮 局势预测")
                st.info(f"Ban 掉 **{banned_deck_name}** (第{ban_index+1}位置) 后，剩余对手：\n\n" + " / ".join(remaining_opps))
                st.warning(f"⚠️ 预计敌方会 Ban 我方：**{res['predicted_ban']}**")
                
            with c2:
                st.subheader("🟢 推荐 4 人名单")
                if res['pick_combo']:
                    st.success(f"**{' + '.join(res['pick_combo'])}**")
                    st.write(f"抗压评分: **{res['smart_score']}** (越低越好)")
                    st.caption("策略：假设我们队内针对剩余卡组最强的人被 Ban，这 4 人的剩余战力依然是最高的。")
                else:
                    st.error("无法计算推荐名单")
            
            # 详情表
            st.markdown("---")
            st.subheader(f"📊 针对剩余对手 ({len(remaining_opps)}套) 的优劣势表")
            rows = []
            for m in current_data:
                r = {"队员": f"{m['player']}"}
                total_score = 0
                for i, opp in enumerate(remaining_opps):
                    clean = opp.strip()
                    score = 3.0
                    if clean in m['matchups']: score = m['matchups'][clean]
                    else:
                        for k in m['matchups']:
                            if clean in k or k in clean: score = m['matchups'][k]; break
                    # 表格列名也加上编号，防止重复列名报错
                    r[f"{opp} (#{i+1})"] = score
                    total_score += score
                r["⬇️总威胁值"] = total_score 
                rows.append(r)
            
            df_display = pd.DataFrame(rows).set_index("队员")
            df_display = df_display.sort_values("⬇️总威胁值")
            
            st.dataframe(df_display.style.map(get_color_style), use_container_width=True)
            
        else:
            st.error("对手卡组数量不足，无法推演")
        
        # 重置
        if st.button("🔄 重选对手"):
            st.session_state.sim_active = False
            st.rerun()


