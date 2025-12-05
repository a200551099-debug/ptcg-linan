import streamlit as st
import pandas as pd
import itertools
import io

# ==========================================
# 1. 核心配置与样式
# ==========================================

st.set_page_config(page_title="PTCG 战队 BP 助手 (Pro 4人版)", page_icon="🛡️", layout="wide")

# 颜色样式：根据 1-6 的数值上色
def get_color_style(val):
    if not isinstance(val, (int, float)): return ""
    if val <= 1.5: return "background-color: #22c55e; color: white" # 1: 深绿
    if val <= 2.5: return "background-color: #86efac; color: #14532d" # 2: 浅绿
    if val <= 3.5: return "background-color: #dbeafe; color: #1e3a8a" # 3: 蓝
    if val <= 4.5: return "background-color: #fef08a; color: #713f12" # 4: 黄
    if val <= 5.5: return "background-color: #fca5a5; color: #7f1d1d" # 5: 橙红
    return "background-color: #ef4444; color: white; font-weight: bold" # 6: 深红

# ==========================================
# 2. 默认数据 (这是你刚才提供的最新数据)
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
# 3. CSV 解析函数 (强力清洗修复版)
# ==========================================
def parse_uploaded_csv(file):
    try:
        # 1. 尝试解码 (UTF-8 或 GBK)
        bytes_data = file.getvalue()
        try:
            string_data = bytes_data.decode('utf-8')
        except:
            string_data = bytes_data.decode('gbk')
        
        # 2. 预处理：按行分割，暴力过滤掉全是逗号或空白的行
        # 这能解决文件末尾几百行逗号导致的“幽灵队员”问题
        lines = string_data.split('\n')
        valid_lines = []
        for line in lines:
            if line.replace(',', '').strip():
                valid_lines.append(line)
        
        cleaned_csv = '\n'.join(valid_lines)
        
        # 3. 初步读取，寻找真正的表头
        df_raw = pd.read_csv(io.StringIO(cleaned_csv), header=None)
        
        header_idx = -1
        for i, row in df_raw.iterrows():
            row_str = ",".join(row.astype(str).values)
            # 只要包含这几个关键词之一，就认为是表头行
            if "比雕" in row_str or "沙奈朵" in row_str or "恶喷" in row_str:
                header_idx = i
                break
        
        if header_idx == -1: return None, "未找到包含卡组名的表头行"

        # 4. 正式读取
        df = pd.read_csv(io.StringIO(cleaned_csv), header=header_idx)
        
        # 5. 列名清洗 (去除空格，防止匹配失败)
        df.columns = [str(col).strip() for col in df.columns]
        
        team_data = []
        
        # 锁定对手列：排除 "Unnamed"、"队员"、"卡组" 等列
        opponent_cols = [c for c in df.columns if "Unnamed" not in c and "队员" not in c and "卡组" not in c]
        
        for index, row in df.iterrows():
            # 假设第0列是队员，第1列是卡组
            # 如果某一行没有队员名字，直接跳过
            p_val = str(row.iloc[0]).strip()
            d_val = str(row.iloc[1]).strip()
            
            if p_val.lower() == 'nan' or p_val == "": 
                continue
                
            matchups = {}
            for opp in opponent_cols:
                try:
                    raw_score = row[opp]
                    score = float(raw_score)
                except:
                    score = 3.0 # 读不到数字就默认为3
                matchups[opp] = score
            
            team_data.append({
                "player": p_val,
                "deck": d_val,
                "matchups": matchups
            })
            
        return team_data, f"成功！识别到 {len(team_data)} 名队员"

    except Exception as e:
        return None, f"解析出错: {str(e)}"

# ==========================================
# 4. 核心算法 (推荐 4 人)
# ==========================================
def calculate_ban_pick(team_data, selected_opponents):
    results = {}
    
    # --- 1. Ban 计算 ---
    unique_opponents = list(set(selected_opponents))
    opponent_scores = {} 
    
    for opp_deck in unique_opponents:
        total_score = 0
        for member in team_data:
            # 增加去空格匹配和模糊匹配逻辑
            clean_opp = opp_deck.strip()
            score = member['matchups'].get(clean_opp, 3.0)
            
            # 如果直接匹配不到，尝试模糊匹配
            if clean_opp not in member['matchups']:
                for k in member['matchups'].keys():
                    if clean_opp in k or k in clean_opp:
                        score = member['matchups'][k]
                        break
            
            total_score += score
        opponent_scores[opp_deck] = total_score
    
    if opponent_scores:
        ban_target = max(opponent_scores, key=opponent_scores.get)
        ban_reason_score = opponent_scores[ban_target]
    else:
        ban_target = None
        ban_reason_score = 0

    results['ban_target'] = ban_target
    results['ban_score'] = ban_reason_score

    # --- 2. Pick 计算 (选4个) ---
    remaining_opponents = selected_opponents.copy()
    if ban_target and ban_target in remaining_opponents:
        remaining_opponents.remove(ban_target)

    if not remaining_opponents:
        return results

    all_members = [m['player'] for m in team_data]
    # 组合数改为 4 (如果总人数不足4人，则取最大人数)
    combo_size = min(4, len(all_members))
    combos_4 = list(itertools.combinations(all_members, combo_size))
    
    best_combo_4 = None
    best_score_4 = float('inf')

    # 寻找总分最低的组合
    for combo in combos_4:
        current_combo_score = 0
        for player_name in combo:
            player_data = next(p for p in team_data if p['player'] == player_name)
            for opp_deck in remaining_opponents:
                # 同样的匹配逻辑
                clean_opp = opp_deck.strip()
                score = player_data['matchups'].get(clean_opp, 3.0)
                if clean_opp not in player_data['matchups']:
                    for k in player_data['matchups'].keys():
                        if clean_opp in k or k in clean_opp:
                            score = player_data['matchups'][k]
                            break
                current_combo_score += score
        
        if current_combo_score < best_score_4:
            best_score_4 = current_combo_score
            best_combo_4 = combo

    results['pick_combo'] = best_combo_4
    results['remaining_opponents'] = remaining_opponents
    
    # --- 3. 风险评估 (Worst Case) ---
    if best_combo_4:
        worst_case_score = float('-inf')
        worst_case_banned = None
        
        for banned_player in best_combo_4:
            remaining_3 = [p for p in best_combo_4 if p != banned_player]
            score_3 = 0
            for player_name in remaining_3:
                player_data = next(p for p in team_data if p['player'] == player_name)
                for opp_deck in remaining_opponents:
                    clean_opp = opp_deck.strip()
                    score = player_data['matchups'].get(clean_opp, 3.0)
                    if clean_opp not in player_data['matchups']:
                        for k in player_data['matchups'].keys():
                            if clean_opp in k or k in clean_opp:
                                score = player_data['matchups'][k]
                                break
                    score_3 += score
            
            if score_3 > worst_case_score:
                worst_case_score = score_3
                worst_case_banned = banned_player
        
        results['risk_analysis'] = {
            'if_ban': worst_case_banned,
            'remaining_score': worst_case_score
        }

    return results

# ==========================================
# 5. 界面渲染
# ==========================================

st.title("🛡️ PTCG 3v3 战队助手 (Pro 4人版)")
st.caption("策略：Ban 1 选 4，防止对方 Ban 人导致崩盘")

# 侧边栏
with st.sidebar:
    st.header("📂 数据源")
    uploaded_file = st.file_uploader("上传 CSV 表格 (可选)", type="csv")
    
    current_team_data = DEFAULT_DATA
    data_source_info = "使用内置默认数据"
    
    if uploaded_file is not None:
        parsed_data, msg = parse_uploaded_csv(uploaded_file)
        if parsed_data:
            current_team_data = parsed_data
            data_source_info = f"✅ {msg}"
            st.success(msg)
        else:
            st.error(f"❌ 读取失败: {msg}")
    else:
        st.info("💡 当前使用代码内嵌的默认数据 (含龟龟完整数据)")

    # 显示人数，用于自检是否读到了幽灵行
    st.caption(f"当前数据人数: {len(current_team_data)} 人")

    st.markdown("---")
    st.header("⚙️ 对局设置")
    
    # 提取所有对手
    all_possible_opponents = set()
    for member in current_team_data:
        all_possible_opponents.update(member['matchups'].keys())
    sorted_opponents = sorted([x for x in all_possible_opponents if x != "其它"])
    
    selected_opponents = []
    default_values = ["沙奈朵", "鬼龙", "密勒顿", "赛富豪", "(无)", "(无)"]
    
    for i in range(6):
        options = ["(无)"] + sorted_opponents
        def_index = 0
        if i < len(default_values) and default_values[i] in options:
             def_index = options.index(default_values[i])
        
        deck = st.selectbox(f"对手卡组 #{i+1}", options=options, index=def_index, key=f"deck_select_{i}")
        if deck != "(无)":
            selected_opponents.append(deck)
            
    st.markdown("---")
    st.write(f"当前已选: {len(selected_opponents)} 套")

# 主区域
if not selected_opponents:
    st.info("👈 请选择对手卡组")
else:
    # --- 调试/自检区域 ---
    with st.expander("🔍 数据自检 (点此查看程序读到的分数)", expanded=False):
        debug_rows = []
        for m in current_team_data:
            r = {"队员": m['player']}
            r.update(m['matchups'])
            debug_rows.append(r)
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True)
        st.caption("检查方法：核对这里的分数是否与你 Excel 中的一致。如果这里全是 3 或名字是 nan，说明 CSV 格式有误。")

    st.markdown("---")

    # 表格
    st.subheader("📊 优劣势速览 (越绿越好)")
    table_data = []
    for member in current_team_data:
        row = {"队员": f"{member['player']} ({member['deck']})"}
        for idx, opp in enumerate(selected_opponents):
            col_name = f"{opp} (#{idx+1})"
            
            # 匹配逻辑复用
            clean_opp = opp.strip()
            rating = member['matchups'].get(clean_opp, 3.0)
            if clean_opp not in member['matchups']:
                for k in member['matchups'].keys():
                    if clean_opp in k or k in clean_opp:
                        rating = member['matchups'][k]
                        break
            
            row[col_name] = rating
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    df.set_index("队员", inplace=True)
    st.dataframe(df.style.map(get_color_style), use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 AI 战术建议")
    
    analysis = calculate_ban_pick(current_team_data, selected_opponents)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔴 建议 Ban")
        if analysis['ban_target']:
            st.error(f"**{analysis['ban_target']}**")
            st.write(f"威胁指数: **{analysis['ban_score']}**")
            st.write("理由：这是对方所有卡组中，对我方全体威胁最大的。")
        else:
            st.info("数据不足")

    with col2:
        st.markdown("### 🟢 建议 4 人名单")
        if analysis.get('pick_combo'):
            # 格式化输出 4 人名单
            combo = analysis['pick_combo']
            st.success("**" + " + ".join(combo) + "**")
            
            st.markdown("#### 🛡️ 抗压分析")
            risk = analysis.get('risk_analysis')
            if risk:
                st.write(f"如果对方 Ban 掉了 **{risk['if_ban']}** (最坏情况):")
                st.write(f"剩下的 3 人组合风险值为: **{risk['remaining_score']}**")
                st.caption("注：推荐这 4 人是因为即使被 Ban 掉核心，剩下的阵容依然是所有组合中最稳的。")
                
            if analysis['remaining_opponents']:
                 st.markdown("---")
                 st.caption(f"剩余需应对的对手: {', '.join(analysis['remaining_opponents'])}")
        else:
            st.info("请选择对手")


