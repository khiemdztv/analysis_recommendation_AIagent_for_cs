import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ast
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIG & DATA LOADING
# ─────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent

IT_OCCUPATIONS = [
    "Computer Programmers",
    "Web Developers",
    "Computer and Information Systems Managers",
    "Computer Systems Analysts",
    "Information Technology Project Managers",
    "Computer and Information Research Scientists",
    "Computer User Support Specialists",
    "Information Security Analysts",
    "Software Quality Assurance Analysts and Testers",
    "Database Administrators",
    "Network and Computer Systems Administrators",
    "Computer Systems Engineers/Architects",
    "Computer Network Support Specialists",
    "Web Administrators",
]

QUADRANT_COLORS = {
    "Green Light": "#2ecc71",
    "Red Light": "#e74c3c",
    "R&D Opportunity": "#f39c12",
    "Low Priority": "#95a5a6",
}

QUADRANT_BG = {
    "Green Light": "rgba(46,204,113,0.10)",
    "Red Light": "rgba(231,76,60,0.10)",
    "R&D Opportunity": "rgba(243,156,18,0.10)",
    "Low Priority": "rgba(149,165,166,0.10)",
}


@st.cache_data
def load_data():
    desires = pd.read_csv(DATA_DIR / "domain_worker_desires.csv")
    expert = pd.read_csv(DATA_DIR / "expert_rated_technological_capability.csv")
    tasks = pd.read_csv(DATA_DIR / "task_statement_with_metadata.csv")
    metadata = pd.read_csv(DATA_DIR / "domain_worker_metadata.csv")
    return desires, expert, tasks, metadata


@st.cache_data
def build_landscape_df(desires, expert):
    """Merge worker desire and expert capability per task for IT occupations."""
    d = desires[desires["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)]
    e = expert[expert["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)]

    worker_avg = (
        d.groupby(["Task ID", "Task", "Occupation (O*NET-SOC Title)"])["Automation Desire Rating"]
        .mean()
        .reset_index()
        .rename(columns={
            "Automation Desire Rating": "Worker_Automation_Desire",
            "Task": "Task_Name",
            "Occupation (O*NET-SOC Title)": "Occupation",
        })
    )

    expert_avg = (
        e.groupby("Task ID")["Automation Capacity Rating"]
        .mean()
        .reset_index()
        .rename(columns={"Automation Capacity Rating": "AI_Expert_Capability"})
    )

    merged = pd.merge(worker_avg, expert_avg, on="Task ID", how="inner")

    def assign_quadrant(row):
        x, y = row["AI_Expert_Capability"], row["Worker_Automation_Desire"]
        if x > 3 and y > 3:
            return "Green Light"
        elif x > 3 and y <= 3:
            return "Red Light"
        elif x <= 3 and y > 3:
            return "R&D Opportunity"
        else:
            return "Low Priority"

    merged["Quadrant"] = merged.apply(assign_quadrant, axis=1)
    return merged


@st.cache_data
def build_has_data(desires, expert):
    """Build HAS distribution data for each IT occupation (worker vs expert)."""
    d = desires[desires["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)]
    e = expert[expert["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)]

    results = []
    for occ in IT_OCCUPATIONS:
        for level in range(1, 6):
            w_occ = d[d["Occupation (O*NET-SOC Title)"] == occ]
            e_occ = e[e["Occupation (O*NET-SOC Title)"] == occ]

            w_total = len(w_occ)
            e_total = len(e_occ)

            w_count = len(w_occ[w_occ["Human Agency Scale Rating"] == level])
            e_count = len(e_occ[e_occ["Human Agency Scale Rating"] == level])

            results.append({
                "Occupation": occ,
                "HAS_Level": level,
                "Worker_Desired_Score": (w_count / w_total * 100) if w_total > 0 else 0,
                "Expert_Assessed_Score": (e_count / e_total * 100) if e_total > 0 else 0,
            })

    return pd.DataFrame(results)


@st.cache_data
def build_skill_shift_data(tasks_df, expert_df):
    """Build skill shift data: rank by wage vs rank by HAS."""
    def parse_skills(s):
        try:
            val = ast.literal_eval(s)
            return val if isinstance(val, list) else [s]
        except Exception:
            return [s.strip("[]'\"")]

    tasks_df = tasks_df.copy()
    tasks_df["Skills_List"] = tasks_df["Skill (O*NET Work Activity)"].apply(parse_skills)
    exploded = tasks_df.explode("Skills_List")

    expert_has = expert_df.groupby("Task ID")["Human Agency Scale Rating"].mean().reset_index()
    merged = pd.merge(exploded, expert_has, on="Task ID", how="inner")

    target_skills = [
        "Analyzing Data or Information",
        "Processing Information",
        "Organizing, Planning, and Prioritizing Work",
        "Communicating with Supervisors, Peers, or Subordinates",
    ]

    skill_stats = (
        merged[merged["Skills_List"].isin(target_skills)]
        .groupby("Skills_List")
        .agg(
            Avg_Wage=("Occupation Mean Annual Wage", "mean"),
            Avg_HAS=("Human Agency Scale Rating", "mean"),
        )
        .reset_index()
    )

    skill_stats["Wage_Rank"] = skill_stats["Avg_Wage"].rank(ascending=False).astype(int)
    skill_stats["HAS_Rank"] = skill_stats["Avg_HAS"].rank(ascending=False).astype(int)

    short_names = {
        "Analyzing Data or Information": "Analyzing Data",
        "Processing Information": "Processing Info",
        "Organizing, Planning, and Prioritizing Work": "Organizing & Planning",
        "Communicating with Supervisors, Peers, or Subordinates": "Interpersonal Comm.",
    }
    skill_stats["Short_Name"] = skill_stats["Skills_List"].map(short_names)

    return skill_stats


# ─────────────────────────────────────────────────────────────
# PAGE RENDERERS
# ─────────────────────────────────────────────────────────────

def page_landscape(landscape_df):
    """Prompt 1: Desire-Capability Landscape Scatter Plot."""
    st.markdown("### 📊 Cảnh quan Tự động hóa — Desire vs Capability")
    st.markdown(
        "Biểu đồ phân tán chia 4 vùng so sánh **mong muốn tự động hóa của người lao động** (trục Y) "
        "với **khả năng AI được chuyên gia đánh giá** (trục X) cho các tác vụ IT. Ngưỡng phân chia: 3.0."
    )

    selected_occ = st.selectbox(
        "🔽 Chọn ngành nghề cần lọc (Mặc định: Tất cả):",
        ["✨ Tất cả"] + IT_OCCUPATIONS,
        index=0,
        key="landscape_occ_filter"
    )
    if selected_occ != "✨ Tất cả":
        landscape_df = landscape_df[landscape_df["Occupation"] == selected_occ]

    fig = go.Figure()

    # Background quadrant rectangles
    shapes = [
        # Green Light (top-right)
        dict(type="rect", x0=3, x1=5.5, y0=3, y1=5.5,
             fillcolor=QUADRANT_BG["Green Light"], line=dict(width=0), layer="below"),
        # Red Light (bottom-right)
        dict(type="rect", x0=3, x1=5.5, y0=0.5, y1=3,
             fillcolor=QUADRANT_BG["Red Light"], line=dict(width=0), layer="below"),
        # R&D Opportunity (top-left)
        dict(type="rect", x0=0.5, x1=3, y0=3, y1=5.5,
             fillcolor=QUADRANT_BG["R&D Opportunity"], line=dict(width=0), layer="below"),
        # Low Priority (bottom-left)
        dict(type="rect", x0=0.5, x1=3, y0=0.5, y1=3,
             fillcolor=QUADRANT_BG["Low Priority"], line=dict(width=0), layer="below"),
    ]

    # Quadrant labels
    annotations = [
        dict(x=4.25, y=5.3, text="🟢 Green Light", showarrow=False,
             font=dict(size=13, color="#27ae60", family="Inter"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=4.25, y=0.7, text="🔴 Red Light", showarrow=False,
             font=dict(size=13, color="#c0392b", family="Inter"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=1.75, y=5.3, text="🟠 R&D Opportunity", showarrow=False,
             font=dict(size=13, color="#e67e22", family="Inter"), bgcolor="rgba(255,255,255,0.7)"),
        dict(x=1.75, y=0.7, text="⬜ Low Priority", showarrow=False,
             font=dict(size=13, color="#7f8c8d", family="Inter"), bgcolor="rgba(255,255,255,0.7)"),
    ]

    # Scatter points grouped by quadrant
    for quad, color in QUADRANT_COLORS.items():
        subset = landscape_df[landscape_df["Quadrant"] == quad]
        fig.add_trace(go.Scatter(
            x=subset["AI_Expert_Capability"],
            y=subset["Worker_Automation_Desire"],
            mode="markers",
            name=quad,
            marker=dict(size=9, color=color, opacity=0.85, line=dict(width=1, color="white")),
            customdata=np.stack([subset["Task_Name"], subset["Occupation"]], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Ngành: %{customdata[1]}<br>"
                "AI Capability: %{x:.2f}<br>"
                "Worker Desire: %{y:.2f}<extra></extra>"
            ),
        ))

    # Threshold lines
    fig.add_hline(y=3, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)
    fig.add_vline(x=3, line_dash="dot", line_color="rgba(0,0,0,0.25)", line_width=1)

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(title="AI Expert Capability (1-5)", range=[0.5, 5.5], dtick=1, gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(title="Worker Automation Desire (1-5)", range=[0.5, 5.5], dtick=1, gridcolor="rgba(0,0,0,0.06)"),
        template="plotly_white",
        height=620,
        margin=dict(t=30, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
    )

    st.plotly_chart(fig, use_container_width=True, key="scatter_landscape")

    # Summary metrics
    total = len(landscape_df)
    cols = st.columns(4)
    for i, (quad, color) in enumerate(QUADRANT_COLORS.items()):
        count = len(landscape_df[landscape_df["Quadrant"] == quad])
        pct = count / total * 100 if total > 0 else 0
        cols[i].metric(label=quad, value=f"{count} tác vụ", delta=f"{pct:.1f}%")


def page_mismatch(landscape_df):
    """Prompt 2: Task distribution bar chart across quadrants."""
    st.markdown("### 📉 Phân bố Tác vụ theo Vùng Cảnh quan — Phân tích Bất cân đối")
    st.markdown(
        "Biểu đồ cột so sánh số lượng tác vụ IT rơi vào từng vùng cảnh quan, "
        "giúp nhận diện sự **bất cân đối** trong nỗ lực tự động hóa."
    )

    selected_occ = st.selectbox(
        "🔽 Chọn ngành nghề cần lọc (Mặc định: Tất cả):",
        ["✨ Tất cả"] + IT_OCCUPATIONS,
        index=0,
        key="mismatch_occ_filter"
    )
    if selected_occ != "✨ Tất cả":
        landscape_df = landscape_df[landscape_df["Occupation"] == selected_occ]

    order = ["Green Light", "R&D Opportunity", "Red Light", "Low Priority"]
    quad_counts_dict = {q: 0 for q in order}
    for q, val in landscape_df["Quadrant"].value_counts().items():
        quad_counts_dict[q] = val
        
    quad_counts = pd.DataFrame([
        {"Quadrant": q, "Task_Count": count} for q, count in quad_counts_dict.items()
    ])

    total = quad_counts["Task_Count"].sum()
    quad_counts["Percentage"] = (quad_counts["Task_Count"] / total * 100).round(1) if total > 0 else 0

    # Highlight colors: warning for Red Light & Low Priority
    bar_colors = []
    for q in quad_counts["Quadrant"]:
        if q in ("Red Light", "Low Priority"):
            bar_colors.append(QUADRANT_COLORS[q])
        else:
            bar_colors.append("rgba(149,165,166,0.45)" if q == "R&D Opportunity" else "rgba(46,204,113,0.45)")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quad_counts["Quadrant"],
        y=quad_counts["Task_Count"],
        marker_color=bar_colors,
        marker_line=dict(width=2, color=[QUADRANT_COLORS[q] for q in quad_counts["Quadrant"]]),
        text=[f"{c} ({p}%)" for c, p in zip(quad_counts["Task_Count"], quad_counts["Percentage"])],
        textposition="outside",
        textfont=dict(size=14, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Số tác vụ: %{y}<extra></extra>",
    ))

    # Highlight annotation for Red + Low
    red_count = quad_counts.loc[quad_counts["Quadrant"] == "Red Light", "Task_Count"].values[0]
    low_count = quad_counts.loc[quad_counts["Quadrant"] == "Low Priority", "Task_Count"].values[0]
    mismatch_pct = (red_count + low_count) / total * 100 if total > 0 else 0

    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis=dict(title="Số lượng tác vụ", gridcolor="rgba(0,0,0,0.06)"),
        xaxis=dict(title=""),
        margin=dict(t=40, b=40),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, key="bar_mismatch")

    # Detailed analysis markdown
    red_tasks = landscape_df[landscape_df["Quadrant"] == "Red Light"].sort_values(
        "AI_Expert_Capability", ascending=False
    ).head(5)

    green_tasks = landscape_df[landscape_df["Quadrant"] == "Green Light"].sort_values(
        "Worker_Automation_Desire", ascending=False
    ).head(5)

    st.markdown("---")
    st.markdown(
        f"### 🔍 Phân tích Bất cân đối\n\n"
        f"**{mismatch_pct:.1f}%** tổng số tác vụ IT ({red_count + low_count}/{total}) nằm trong vùng "
        f"**Đèn Đỏ** và **Ưu tiên Thấp** — nơi hoặc AI có khả năng nhưng worker từ chối tự động hóa, "
        f"hoặc cả hai đều đánh giá thấp.\n\n"
        f"Điều này cho thấy nỗ lực tự động hóa hiện tại đang tập trung vào các tác vụ có **xung đột** "
        f"giữa khả năng công nghệ và mong muốn của người lao động, trong khi vùng **Đèn Xanh** — nơi "
        f"cả worker lẫn AI đều đồng thuận — cần được ưu tiên nguồn lực hơn."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔴 Top tác vụ vùng Đèn Đỏ (Red Light)")
        st.markdown("*AI có khả năng cao nhưng worker không muốn tự động hóa:*")
        for _, row in red_tasks.iterrows():
            st.markdown(
                f"- **{row['Occupation']}**: {row['Task_Name'][:80]}… "
                f"(AI={row['AI_Expert_Capability']:.1f}, Desire={row['Worker_Automation_Desire']:.1f})"
            )

    with col2:
        st.markdown("#### 🟢 Top tác vụ vùng Đèn Xanh (Green Light)")
        st.markdown("*Cả worker lẫn AI đều đồng thuận cần tự động hóa:*")
        for _, row in green_tasks.iterrows():
            st.markdown(
                f"- **{row['Occupation']}**: {row['Task_Name'][:80]}… "
                f"(AI={row['AI_Expert_Capability']:.1f}, Desire={row['Worker_Automation_Desire']:.1f})"
            )

    st.markdown(
        "\n---\n"
        "#### 💡 Khuyến nghị\n"
        "1. **Ưu tiên đầu tư vào vùng Green Light**: Đây là nơi có sự đồng thuận cao nhất — triển khai AI agent sẽ được worker chấp nhận.\n"
        "2. **Nghiên cứu sâu vùng R&D Opportunity**: Worker muốn tự động hóa nhưng AI chưa đủ khả năng — đây là cơ hội phát triển công nghệ mới.\n"
        "3. **Cẩn trọng với vùng Red Light**: Cần tìm hiểu lý do worker từ chối trước khi ép triển khai AI — có thể liên quan đến an ninh nghề nghiệp hoặc chất lượng công việc.\n"
    )


def page_has_spectrum(has_df):
    """Prompt 3: HAS Spectrum — Worker vs Expert comparison."""
    st.markdown("### 📈 Thang đo Tác nhân Con người (HAS) — Worker vs Expert")
    st.markdown(
        "So sánh phân phối đánh giá **mức độ cần thiết của con người** (Human Agency Scale, 1-5) "
        "giữa góc nhìn **người lao động** (Worker) và **chuyên gia AI** (Expert) cho từng ngành nghề IT."
    )

    selected_occ = st.selectbox(
        "🔽 Chọn ngành nghề IT:",
        IT_OCCUPATIONS,
        index=0,
        key="has_selectbox",
    )

    occ_data = has_df[has_df["Occupation"] == selected_occ].sort_values("HAS_Level")

    if occ_data.empty:
        st.warning(f"Không có dữ liệu HAS cho ngành: {selected_occ}")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=occ_data["HAS_Level"],
        y=occ_data["Worker_Desired_Score"],
        mode="lines+markers",
        name="👷 Worker (Mong muốn)",
        line=dict(color="#3498db", width=3, shape="spline"),
        marker=dict(size=10, symbol="circle"),
        hovertemplate="HAS Level %{x}<br>Worker: %{y:.1f}%<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=occ_data["HAS_Level"],
        y=occ_data["Expert_Assessed_Score"],
        mode="lines+markers",
        name="🤖 Expert (Đánh giá)",
        line=dict(color="#e74c3c", width=3, shape="spline"),
        marker=dict(size=10, symbol="diamond"),
        hovertemplate="HAS Level %{x}<br>Expert: %{y:.1f}%<extra></extra>",
    ))

    # Fill area between the two lines to highlight disagreement
    fig.add_trace(go.Scatter(
        x=list(occ_data["HAS_Level"]) + list(occ_data["HAS_Level"])[::-1],
        y=list(occ_data["Worker_Desired_Score"]) + list(occ_data["Expert_Assessed_Score"])[::-1],
        fill="toself",
        fillcolor="rgba(0,0,0,0.04)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis=dict(
            title="Mức Human Agency Scale (HAS)",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["H1\n(Tự động hoàn toàn)", "H2", "H3\n(Hợp tác)", "H4", "H5\n(Con người kiểm soát)"],
            gridcolor="rgba(0,0,0,0.06)",
        ),
        yaxis=dict(title="Tỷ lệ (%)", gridcolor="rgba(0,0,0,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=30, b=80),
    )

    st.plotly_chart(fig, use_container_width=True, key="line_has")

    # Interpretation
    worker_peak = occ_data.loc[occ_data["Worker_Desired_Score"].idxmax()]
    expert_peak = occ_data.loc[occ_data["Expert_Assessed_Score"].idxmax()]

    gap = abs(worker_peak["HAS_Level"] - expert_peak["HAS_Level"])

    st.markdown("---")
    st.markdown(f"#### 🔍 Phân tích cho **{selected_occ}**")
    st.markdown(
        f"- **Worker** đánh giá tập trung ở mức **H{int(worker_peak['HAS_Level'])}** "
        f"({worker_peak['Worker_Desired_Score']:.1f}%)\n"
        f"- **Expert** đánh giá tập trung ở mức **H{int(expert_peak['HAS_Level'])}** "
        f"({expert_peak['Expert_Assessed_Score']:.1f}%)\n"
        f"- Khoảng cách bất đồng: **{gap} mức HAS**"
    )

    if gap >= 2:
        st.error(
            "⚠️ **Bất đồng lớn!** Worker và Expert có góc nhìn rất khác nhau. "
            "Worker muốn giữ quyền kiểm soát cao hơn so với đánh giá khả năng của AI. "
            "Cần đối thoại và thử nghiệm thí điểm trước khi triển khai."
        )
    elif gap == 1:
        st.warning(
            "⚡ **Bất đồng trung bình.** Có sự khác biệt nhưng không quá lớn. "
            "Có thể triển khai AI agent với mô hình hợp tác (human-in-the-loop)."
        )
    else:
        st.success(
            "✅ **Đồng thuận!** Worker và Expert có cùng đánh giá. "
            "Triển khai AI agent theo mức HAS này sẽ được chấp nhận rộng rãi."
        )


def page_skill_shift(skill_df):
    """Prompt 4: Skill Shift Slope Chart."""
    st.markdown("### 📐 Dịch chuyển Kỹ năng IT — Wage Rank vs HAS Rank")
    st.markdown(
        "Biểu đồ dốc minh họa sự **dịch chuyển thứ hạng** của các kỹ năng IT: "
        "bên trái là xếp hạng theo **mức lương trung bình** (hiện tại), "
        "bên phải là xếp hạng theo **mức độ cần thiết của con người** (tương lai). "
        "Đường đỏ = kỹ năng giảm giá trị, Đường xanh = kỹ năng lên ngôi."
    )

    if skill_df.empty:
        st.warning("Không đủ dữ liệu kỹ năng để vẽ biểu đồ.")
        return

    fig = go.Figure()

    for _, row in skill_df.iterrows():
        wage_rank = row["Wage_Rank"]
        has_rank = row["HAS_Rank"]
        name = row["Short_Name"]
        skill_full = row["Skills_List"]

        # Direction: if rank goes up (numerically higher = worse), color red; if goes down, color green
        if has_rank > wage_rank:
            color = "#e74c3c"  # red — skill declining
            direction = "📉 Giảm"
        elif has_rank < wage_rank:
            color = "#2ecc71"  # green — skill rising
            direction = "📈 Tăng"
        else:
            color = "#f1c40f"  # yellow — stable
            direction = "➡️ Ổn định"

        # Line connecting wage rank to HAS rank
        fig.add_trace(go.Scatter(
            x=["Xếp hạng theo Lương\n(Hiện tại)", "Xếp hạng theo HAS\n(Tương lai)"],
            y=[wage_rank, has_rank],
            mode="lines+markers+text",
            line=dict(color=color, width=4),
            marker=dict(size=14, color=color, line=dict(width=2, color="white")),
            text=[name, f"{name} {direction}"],
            textposition=["middle left", "middle right"],
            textfont=dict(size=12, color=color, family="Inter"),
            name=f"{name} ({direction})",
            hovertemplate=(
                f"<b>{name}</b><br>"
                f"Kỹ năng: {skill_full}<br>"
                f"Wage Rank: {int(wage_rank)}<br>"
                f"HAS Rank: {int(has_rank)}<br>"
                f"Xu hướng: {direction}<extra></extra>"
            ),
        ))

    fig.update_layout(
        template="plotly_white",
        height=550,
        yaxis=dict(
            title="Thứ hạng (1 = cao nhất)",
            autorange="reversed",  # Rank 1 at top
            dtick=1,
            gridcolor="rgba(0,0,0,0.06)",
            range=[0.3, len(skill_df) + 0.7],
        ),
        xaxis=dict(
            title="",
            gridcolor="rgba(0,0,0,0.06)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        margin=dict(t=30, b=80, l=200, r=220),
    )

    st.plotly_chart(fig, use_container_width=True, key="slope_skills")

    # Insight table
    st.markdown("---")
    st.markdown("#### 📋 Bảng chi tiết Dịch chuyển Kỹ năng")

    display_df = skill_df[["Short_Name", "Skills_List", "Avg_Wage", "Avg_HAS", "Wage_Rank", "HAS_Rank"]].copy()
    display_df.columns = ["Tên ngắn", "Kỹ năng (O*NET)", "Lương TB ($)", "HAS TB", "Rank Lương", "Rank HAS"]
    display_df["Lương TB ($)"] = display_df["Lương TB ($)"].apply(lambda x: f"${x:,.0f}")
    display_df["HAS TB"] = display_df["HAS TB"].apply(lambda x: f"{x:.2f}")
    display_df = display_df.sort_values("Rank Lương")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown(
        "\n#### 💡 Diễn giải\n"
        "- **Kỹ năng xử lý thông tin/phân tích dữ liệu** (đường đỏ): Hiện có mức lương cao nhưng mức cần thiết "
        "của con người thấp → AI có thể thay thế phần lớn → **giảm giá trị** trong tương lai.\n"
        "- **Kỹ năng tổ chức, lập kế hoạch, giao tiếp** (đường xanh): Hiện lương thấp hơn nhưng đòi hỏi "
        "sự can thiệp của con người cao → khó tự động hóa → **tăng giá trị** trong kỷ nguyên AI.\n\n"
        "**Khuyến nghị**: Các chuyên gia IT nên đầu tư phát triển kỹ năng mềm (tổ chức, giao tiếp, "
        "lãnh đạo) song song với kỹ năng kỹ thuật để tăng tính cạnh tranh trong thời đại AI."
    )


# ─────────────────────────────────────────────────────────────
# CHATBOT HELPER & PAGE
# ─────────────────────────────────────────────────────────────

class PaperRetriever:
    def __init__(self, json_path):
        import json
        import re
        from collections import Counter
        
        with open(json_path, "r", encoding="utf-8") as f:
            self.pages = json.load(f)
        
        self.doc_term_counts = []
        self.df = Counter()
        self.num_docs = len(self.pages)
        
        for p in self.pages:
            tokens = self._tokenize(p["text"])
            self.doc_term_counts.append(Counter(tokens))
            for t in set(tokens):
                self.df[t] += 1
                
    def _tokenize(self, text):
        import re
        return re.findall(r'\w+', text.lower())
        
    def retrieve(self, query, top_k=5):
        import math
        query_expanded = self._expand_query(query)
        query_tokens = self._tokenize(query_expanded)
        
        scores = []
        for i, p in enumerate(self.pages):
            score = 0
            tc = self.doc_term_counts[i]
            doc_len = sum(tc.values())
            if doc_len == 0:
                continue
            for t in query_tokens:
                if t in tc:
                    tf = tc[t] / doc_len
                    idf = math.log((self.num_docs + 1) / (self.df[t] + 1)) + 1
                    score += tf * idf
            scores.append((score, p))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scores if item[0] > 0]
        if not results:
            results = self.pages[:top_k]
        return results[:top_k]

    def _expand_query(self, query):
        query_lower = query.lower()
        expanded = [query_lower]
        mappings = {
            "thang đo": "human agency scale has level",
            "has": "human agency scale has level",
            "đèn đỏ": "red light zone conflict worker desire",
            "đèn xanh": "green light zone alignment worker desire",
            "đèn vàng": "r&d opportunity zone",
            "cơ hội r&d": "r&d opportunity zone",
            "ưu tiên thấp": "low priority zone",
            "dịch chuyển kỹ năng": "skill shift wage rank correlation",
            "kỹ năng": "skill work activity occupation",
            "lương": "wage annual mean salary",
            "chuyên gia": "expert capability rating",
            "người lao động": "worker desire automation rating",
            "bất cân đối": "mismatch conflict disagreement",
            "tác nhân": "agency autonomous agent",
        }
        for key, val in mappings.items():
            if key in query_lower:
                expanded.append(val)
        return " ".join(expanded)


def page_chatbot():
    import streamlit as st
    from groq import Groq
    
    st.markdown("### 💬 Chatbot WORKBank AI")
    st.markdown(
        "Chatbot này sử dụng Groq API và được cung cấp toàn bộ ngữ cảnh từ bài báo khoa học "
        "**WORKBank** (*arXiv:2506.06576v3*) để trả lời các câu hỏi của bạn về định nghĩa, thuật ngữ và kết quả phân tích."
    )
    
    json_path = DATA_DIR / "paper_text.json"
    if not json_path.exists():
        st.error("Không tìm thấy tệp dữ liệu trích xuất văn bản paper_text.json. Vui lòng kiểm tra lại.")
        return
        
    @st.cache_resource
    def get_retriever():
        return PaperRetriever(json_path)
        
    retriever = get_retriever()
    
    import os
    # Load Groq API Key from Streamlit secrets or environment variables
    api_key = st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    
    # Fallback to local file for development
    if not api_key:
        try:
            with open("api_key.txt", "r") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            pass
            
    model_name = "llama-3.3-70b-versatile"
    
    if not api_key:
        st.warning("⚠️ Không tìm thấy Groq API Key. Vui lòng thiết lập biến môi trường `GROQ_API_KEY` hoặc tạo tệp `api_key.txt` cục bộ.")
        return
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 Xem nguồn tài liệu tham khảo"):
                    for src in msg["sources"]:
                        st.markdown(f"**Trang {src['page']}:**\n>{src['text'][:400]}...")
                        
    if prompt := st.chat_input("Hỏi tôi về thang đo HAS, các phân vùng cảnh quan, dịch chuyển kỹ năng..."):
        with st.chat_message("user"):
            st.markdown(prompt)
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        retrieved_pages = retriever.retrieve(prompt, top_k=4)
        context_str = "\n\n".join([f"--- PAGE {p['page']} ---\n{p['text']}" for p in retrieved_pages])
        
        system_prompt = f"""
You are an expert AI assistant specialized in the research paper: "Future of Work with AI Agents: Auditing Automation and Augmentation Potential across the U.S. Workforce" (WORKBank paper, arXiv:2506.06576).
You will answer user questions about this paper based on the provided retrieved text chunks and the core definitions below.

CORE DEFINITIONS:
1. Human Agency Scale (HAS) Levels:
- H1 (Full Automation): AI operates completely autonomously without human intervention.
- H2 (AI-led, human oversight): AI performs the task; human can override or handles minor interventions.
- H3 (Collaborative): Human and AI collaborate as equal partners.
- H4 (Human-led, AI support): Human performs the task; AI assists.
- H5 (Human only / Full Human Control): AI cannot function without human input, or task is completely manual.

2. Deployment Zones (Landscape Quadrants):
- Green Light Zone: High AI Technical Capability (rating > 3) and High Worker Automation Desire (rating > 3). Recommended for automation.
- Red Light Zone: High AI Technical Capability (rating > 3) but Low Worker Automation Desire (rating <= 3). Caution is needed (threat to job meaning, quality, security).
- R&D Opportunity Zone: Low AI Technical Capability (rating <= 3) but High Worker Automation Desire (rating > 3). Technology gap, needs R&D.
- Low Priority Zone: Low AI Technical Capability (rating <= 3) and Low Worker Automation Desire (rating <= 3). Not suitable for automation now.

3. Key Findings:
- Workers generally prefer to automate administrative tasks but keep control over tasks involving judgment, creativity, and human-centric roles.
- Skill premium shifts from information processing to interpersonal coordination and leadership as AI agents are adopted.

INSTRUCTIONS:
- Answer in the same language as the user's question (Vietnamese or English).
- Be precise, accurate, and professional.
- Refer to the retrieved text when explaining paper specifics. If the retrieved text doesn't contain the answer and you cannot find it, state that the retrieved pages do not contain specific information, but provide general knowledge based on the paper's core concepts.
- Cite the source pages (e.g., "theo Trang X của bài báo...") when using retrieved context.

RETIREVED TEXT CHUNKS FROM PAPER:
{context_str}
"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in st.session_state.messages[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                client = Groq(api_key=api_key)
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                with st.expander("📚 Xem nguồn tài liệu tham khảo"):
                    for src in retrieved_pages:
                        st.markdown(f"**Trang {src['page']}:**\n>{src['text'][:400]}...")
                        
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "sources": [{"page": p["page"], "text": p["text"]} for p in retrieved_pages]
                })
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi gọi Groq API: {str(e)}")


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="WORKBank — AI Agent Analysis",
        page_icon="🤖",
        layout="wide",
    )

    # Custom CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #ffffff;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid #e2e8f0;
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #0f172a !important;
        }

        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {
            color: #334155 !important;
        }

        .stMetric {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
            font-weight: 600;
            color: #0f172a;
        }
    </style>
    """, unsafe_allow_html=True)

    # Load data
    desires, expert, tasks, metadata = load_data()

    # Sidebar navigation
    st.sidebar.markdown("# 🤖 WORKBank")
    st.sidebar.markdown("**Phân tích AI Agent trong ngành Khoa học Máy tính**")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "📑 Chọn trang phân tích:",
        [
            "1️⃣ Cảnh quan Tự động hóa",
            "2️⃣ Phân bố & Bất cân đối",
            "3️⃣ Thang đo HAS — Worker vs Expert",
            "4️⃣ Dịch chuyển Kỹ năng",
            "💬 Chatbot WORKBank AI",
        ],
        index=0,
        key="nav_radio",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"📊 **Dữ liệu:**\n"
        f"- Workers: {len(desires):,} records\n"
        f"- Expert: {len(expert):,} records\n"
        f"- Tasks: {len(tasks):,} records\n"
        f"- Metadata: {len(metadata):,} records\n"
    )
    st.sidebar.markdown(f"🎯 **14 ngành IT** được phân tích")

    # Title
    st.markdown("## 🤖 WORKBank — Phân tích & Khuyến nghị Ứng dụng AI Agent")
    st.markdown("*Nhóm ngành Khoa học Máy tính & Toán học (Computer and Mathematical)*")
    st.markdown("---")

    # Route pages
    if page.startswith("1"):
        landscape_df = build_landscape_df(desires, expert)
        page_landscape(landscape_df)

    elif page.startswith("2"):
        landscape_df = build_landscape_df(desires, expert)
        page_mismatch(landscape_df)

    elif page.startswith("3"):
        has_df = build_has_data(desires, expert)
        page_has_spectrum(has_df)

    elif page.startswith("4"):
        skill_df = build_skill_shift_data(tasks, expert)
        page_skill_shift(skill_df)

    elif page.startswith("💬") or "Chatbot" in page:
        page_chatbot()


if __name__ == "__main__":
    main()
