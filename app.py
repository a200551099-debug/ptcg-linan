import streamlit as st
import pandas as pd
import itertools

# ==========================================
# 1. 核心数据与配置
# ==========================================

# 评分映射字典 (核心算法权重)
SCORE_MAP = {
    "优": 2, "小优": 1, "均": 0, "平": 0, "小劣": -1, "劣": -2, "我不想打": -100
}

# 颜色映射 (用于表格显示)
COLOR_MAP = {
    "优": "background-color: #d4edda; color: #155724",
    "小优": "background-color: #e2e6ea; color: #155724",
    "均": "background-color: #cce5ff; color: #004085",
    "平": "background-color: #cce5ff; color: #004085",
    "小劣": "background-color: #fff3cd; color: #856404",
    "劣": "background-color: #f8d7da; color: #721c24",
    "我不想打": "background-color: #343a40; color: #ffffff"
}

# 原始数据
RAW_DATA = {
  "team_data": [
    { "player": "三毛九鬼龙", "deck": "鬼龙", "matchups": { "比雕恶喷": "优", "尾狸恶喷": "优", "沙奈朵": "劣", "鬼龙": "均", "轰鬼": "均", "密勒顿": "优", "勾喷": "劣", "LTB": "均", "纯恶月": "平", "水恶月": "小劣", "汇流梦幻": "劣", "双无梦幻": "我不想打", "水熊": "小劣", "铁武者": "优", "古剑豹": "优", "赛富豪": "优", "其它": "优" } },
    { "player": "土豆", "deck": "鬼龙", "matchups": { "比雕恶喷": "优", "尾狸恶喷": "小优", "沙奈朵": "小劣", "鬼龙": "小优", "轰鬼": "小优", "密勒顿": "小优", "勾喷": "小劣", "LTB": "均", "纯恶月": "平", "水恶月": "平", "汇流梦幻": "小优", "双无梦幻": "平", "水熊": "平", "铁武者": "优", "古剑豹": "小优", "赛富豪": "优", "其它": "优" } },
    { "player": "语申", "deck": "尾狸恶喷", "matchups": { "比雕恶喷": "平", "尾狸恶喷": "平", "沙奈朵": "劣", "鬼龙": "小劣", "轰鬼": "小劣", "密勒顿": "优", "勾喷": "小劣", "LTB": "劣", "纯恶月": "优", "水恶月": "优", "汇流梦幻": "优", "双无梦幻": "优", "水熊": "劣", "铁武者": "平", "古剑豹": "平", "赛富豪": "平", "其它": "优" } },
    { "player": "ZZ", "deck": "沙奈朵", "matchups": { "比雕恶喷": "优", "尾狸恶喷": "优", "沙奈朵": "平", "鬼龙": "优", "轰鬼": "优", "密勒顿": "平", "勾喷": "优", "LTB": "优", "纯恶月": "优", "水恶月": "优", "汇流梦幻": "优", "双无梦幻": "优", "水熊": "我不想打", "铁武者": "我不想打", "古剑豹": "优", "赛富豪": "优", "其它": "优" } },
    { "player": "乐子人", "deck": "lostK喷", "matchups": { "比雕恶喷": "优", "尾狸恶喷": "优", "沙奈朵": "劣", "鬼龙": "优", "轰鬼": "优", "密勒顿": "平", "勾喷": "平", "LTB": "平", "纯恶月": "优", "水恶月": "优", "汇流梦幻": "我不想打", "双无梦幻": "我不想打", "水熊": "劣", "铁武者": "劣", "古剑豹": "优", "赛富豪": "优", "其它": "劣" } },
    { "player": "龟龟", "deck": "涡轮梦幻", "matchups": { "比雕恶喷": "小劣", "尾狸恶喷": "劣", "沙奈朵": "劣", "鬼龙": "平", "轰鬼": "劣", "密勒顿": "优", "勾喷": "我不想打", "LTB": "优", "纯恶月": "优", "水恶月": "优", "汇流梦幻": "小劣", "双无梦幻": "平", "水熊": "优", "铁武者": "优", "古剑豹": "优", "赛富豪": "优", "其它": "优" } }
  ]
}

# ==========================================
# 2. 辅助函数
# ==========================================

def get_score(rating_text):
    return SCORE_MAP.get(rating_text, 0)

def style_dataframe(val):
    return COLOR_MAP.get(val, "")

def calculate_ban_pick(team_data, selected_opponents):
    results = {}
    opponent_scores = {}
    for opp_deck in selected_opponents:
        total_score = 0
        for member in team_data:
            rating = member['matchups'].get(opp_deck, member['matchups'].get("其它", "平"))
            total_score += get_score(rating)
        opponent_scores[opp_deck] = total_score
    
    if opponent_scores:
        ban_target = min(opponent_scores, key=opponent_scores.get)
        ban_reason_score = opponent_scores[ban_target]
    else:
        ban_target = None
        ban_reason_score = 0

    results['ban_target'] = ban_target
    results['ban_score'] = ban_reason_score
    results['opponent_scores'] = opponent_scores

    if ban_target:
        remaining_opponents = [d for d in selected_opponents if d != ban_target]
    else:
        remaining_opponents = selected_opponents

    if not remaining_opponents:
        results['pick_combo'] = []
        results['pick_score'] = 0
        return results

    all_members = [m['player'] for m in team_data]
    combos = list(itertools.combinations(all_members, 3))
    
    best_combo = None
    best_score = -float('inf')

    for combo in combos:
        current_combo_score = 0
        for player_name in combo:
            player_data = next(p for p in team_data if p['player'] == player_name)
            for opp_deck in remaining_opponents:
                rating = player_data['matchups'].get(opp_deck, player_data['matchups'].get("其它", "平"))
                current_combo_score += get_score(rating)
        
        if current_combo_score > best_score:
            best_score = current_combo_score
            best_combo = combo

    results['pick_combo'] = best_combo
    results['pick_score'] = best_score
    results['remaining_opponents'] = remaining_opponents
    return results

# ==========================================
# 3. Streamlit UI 界面
# ==========================================

st.set_page_config(page_title="PTCG 战队 BP 助手", page_icon="🃏", layout="wide")
st.title("🏆 PTCG 3v3 战队赛 BP 助手")

# 提取所有可能的对手卡组
all_possible_opponents = set()
for member in RAW_DATA['team_data']:
    all_possible_opponents.update(member['matchups'].keys())
sorted_opponents = sorted([x for x in all_possible_opponents if x != "其它"])
if "其它" in all_possible_opponents:
    sorted_opponents.append("其它")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 对局设置")
    default_selection = ["沙奈朵", "鬼龙", "密勒顿", "赛富豪"]
    valid_defaults = [x for x in default_selection if x in sorted_opponents]
    selected_opponents = st.multiselect("对手携带了哪些卡组？", options=sorted_opponents, default=valid_defaults)

# 主界面
if not selected_opponents:
    st.warning("👈 请在左侧选择对手的卡组以开始分析。")
else:
    st.subheader("📊 优劣势速览表")
    table_data = []
    for member in RAW_DATA['team_data']:
        row = {"队员": f"{member['player']} ({member['deck']})"}
        for opp in selected_opponents:
            rating = member['matchups'].get(opp, member['matchups'].get("其它", "平"))
            row[opp] = rating
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    df.set_index("队员", inplace=True)
    st.dataframe(df.style.map(style_dataframe), use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 AI 战术建议")
    
    analysis = calculate_ban_pick(RAW_DATA['team_data'], selected_opponents)
    
    st.markdown("### 🔴 建议 Ban")
    ban_target = analysis['ban_target']
    if ban_target:
        st.error(f"**{ban_target}**")
        st.write(f"如果不 Ban {ban_target}，我方全员对阵它的总期望收益最低 (威胁分: {analysis['ban_score']})。")
        if analysis['ban_score'] <= -50:
            st.caption("⚠️ 警告：因为有队员对此卡组是「不想打」，所以必须 Ban。")
    
    st.markdown("### 🟢 建议 Pick (出战阵容)")
    pick_combo = analysis['pick_combo']
    if pick_combo:
        combo_str = " + ".join(pick_combo)
        st.success(f"**{combo_str}**")
        rem_opps = ", ".join(analysis['remaining_opponents'])
        st.write(f"在 Ban 掉 {analysis['ban_target']} 后，面对 {rem_opps}，这三位胜算最高。")

