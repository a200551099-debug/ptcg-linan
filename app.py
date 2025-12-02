import streamlit as st
import pandas as pd
import itertools

# ==========================================
# 1. 核心配置
# ==========================================

st.set_page_config(page_title="PTCG 战队 BP 助手", page_icon="🃏", layout="wide")

# 评分权重 ("我不想打" 已改为 -2)
SCORE_MAP = {
    "优": 2,
    "小优": 1,
    "均": 0,
    "平": 0,
    "小劣": -1,
    "劣": -2,
    "我不想打": -2
}

# 颜色样式
COLOR_MAP = {
    "优": "background-color: #d4edda; color: #155724",
    "小优": "background-color: #e2e6ea; color: #155724",
    "均": "background-color: #cce5ff; color: #004085",
    "平": "background-color: #cce5ff; color: #004085",
    "小劣": "background-color: #fff3cd; color: #856404",
    "劣": "background-color: #f8d7da; color: #721c24",
    "我不想打": "background-color: #343a40; color: #ffffff"
}

# 队员数据
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
# 2. 逻辑函数
# ==========================================

def get_score(rating_text):
    return SCORE_MAP.get(rating_text, 0)

def style_dataframe(val):
    return COLOR_MAP.get(val, "")

def calculate_ban_pick(team_data, selected_opponents):
    results = {}
    
    # 1. Ban 计算
    unique_opponents = list(set(selected_opponents))
    opponent_scores = {} 
    
    for opp_deck in unique_opponents:
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

    # 2. Pick 计算
    remaining_opponents = selected_opponents.copy()
    if ban_target and ban_target in remaining_opponents:
        remaining_opponents.remove(ban_target)

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
# 3. 界面渲染
# ==========================================

st.title("🏆 PTCG 3v3 战队赛 BP 助手")

# 准备选项
all_possible_opponents = set()
for member in RAW_DATA['team_data']:
    all_possible_opponents.update(member['matchups'].keys())
sorted_opponents = sorted([x for x in all_possible_opponents if x != "其它"])
if "其它" in all_possible_opponents:
    sorted_opponents.append("其它")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 对局设置")
    selected_opponents = []
    default_values = ["沙奈朵", "鬼龙", "密勒顿", "赛富豪", "(无)", "(无)"]
    
    for i in range(6):
        options = ["(无)"] + sorted_opponents
        def_index = options.index(default_values[i]) if default_values[i] in options else 0
        deck = st.selectbox(f"对手卡组 #{i+1}", options=options, index=def_index, key=f"deck_select_{i}")
        if deck != "(无)":
            selected_opponents.append(deck)
    st.write(f"当前已选: {len(selected_opponents)} 套")

# 主区域
if not selected_opponents:
    st.warning("👈 请在左侧选择对手的卡组")
else:
    # 表格
    st.subheader("📊 优劣势速览表")
    table_data = []
    for member in RAW_DATA['team_data']:
        row = {"队员": f"{member['player']} ({member['deck']})"}
        for idx, opp in enumerate(selected_opponents):
            col_name = f"{opp} (#{idx+1})"
            rating = member['matchups'].get(opp, member['matchups'].get("其它", "平"))
            row[col_name] = rating
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    df.set_index("队员", inplace=True)
    st.dataframe(df.style.map(style_dataframe), use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 AI 战术建议")
    
    analysis = calculate_ban_pick(RAW_DATA['team_data'], selected_opponents)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔴 建议 Ban")
        if analysis['ban_target']:
            st.error(f"**{analysis['ban_target']}**")
            st.write(f"威胁评分: {analysis['ban_score']}")
            st.write("如果不Ban这套，我方总劣势最大。")
        else:
            st.info("数据不足")

    with col2:
        st.markdown("### 🟢 建议 Pick")
        if analysis['pick_combo']:
            st.success(f"**{' + '.join(analysis['pick_combo'])}**")
            st.write("面对剩余对手，这三人胜算最高。")
        else:
            st.info("请选择对手")


