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


@st.cache_data
def build_insights_df(desires, metadata):
    """Merge worker desires and metadata for advanced analysis."""
    # Filter for IT occupations
    d = desires[desires["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)].copy()
    m = metadata[metadata["Occupation (O*NET-SOC Title)"].isin(IT_OCCUPATIONS)].copy()

    # Clean up the Unicode right single quotation mark (U+2019) in Education
    m["Education"] = m["Education"].str.replace("\u2019", "'", regex=False)  # Smart quote → ASCII apostrophe

    # Merge
    merged = pd.merge(d, m, on=["User ID", "Occupation (O*NET-SOC Title)"], how="inner")
    return merged


# ─────────────────────────────────────────────────────────────
# PAGE RENDERERS
# ─────────────────────────────────────────────────────────────

def page_landscape(landscape_df, selected_occ):
    """Prompt 1: Desire-Capability Landscape Scatter Plot."""
    st.markdown("### 📊 Cảnh quan Tự động hóa — Desire vs Capability")
    st.markdown(
        "Biểu đồ phân tán chia 4 vùng so sánh **mong muốn tự động hóa của người lao động** (trục Y) "
        "với **khả năng AI được chuyên gia đánh giá** (trục X) cho các tác vụ IT. Ngưỡng phân chia: 3.0."
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

    st.markdown("---")
    st.markdown("### 💡 Ý nghĩa các phân vùng chiến lược:")
    
    col_desc1, col_desc2 = st.columns(2)
    with col_desc1:
        st.markdown(
            "🟢 **Green Light:** Cả khả năng của AI (>3.0) và mong muốn của worker (>3.0) đều cao. "
            "Đây là vùng **đồng thuận cao**, cực kỳ phù hợp để tự động hóa bằng AI Agent ngay lập tức."
        )
        st.markdown(
            "🔴 **Red Light:** Khả năng AI cao (>3.0) nhưng worker không muốn tự động hóa (<=3.0). "
            "Đây là vùng **xung đột**, cần đặc biệt cẩn trọng vì có thể làm mất đi ý nghĩa công việc hoặc gây e ngại cho người lao động."
        )
    with col_desc2:
        st.markdown(
            "🟠 **R&D Opportunity:** Worker muốn tự động hóa (>3.0) nhưng khả năng của AI thấp (<=3.0). "
            "Đây là cơ hội tốt cho các hoạt động **nghiên cứu & phát triển (R&D)** nhằm giải quyết nhu cầu thực tế."
        )
        st.markdown(
            "⬜ **Low Priority:** Cả khả năng AI và mong muốn của worker đều thấp (<=3.0). "
            "Đây là vùng **ưu tiên thấp**, không nên tập trung nguồn lực đầu tư."
        )


def page_mismatch(landscape_df, selected_occ):
    """Prompt 2: Task distribution bar chart across quadrants."""
    st.markdown("### 📉 Phân bố Tác vụ theo Vùng Cảnh quan — Phân tích Bất cân đối")
    st.markdown(
        "Biểu đồ cột so sánh số lượng tác vụ IT rơi vào từng vùng cảnh quan, "
        "giúp nhận diện sự **bất cân đối** trong nỗ lực tự động hóa."
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


def page_has_spectrum(has_df, selected_occ):
    """Prompt 3: HAS Spectrum — Worker vs Expert comparison."""
    st.markdown("### 📈 Thang đo Tác nhân Con người (HAS) — Worker vs Expert")
    st.markdown(
        "So sánh phân phối đánh giá **mức độ cần thiết của con người** (Human Agency Scale, 1-5) "
        "giữa góc nhìn **người lao động** (Worker) và **chuyên gia AI** (Expert) cho từng ngành nghề IT."
    )

    if selected_occ == "✨ Tất cả":
        st.warning("⚠️ Vui lòng chọn một ngành nghề CNTT cụ thể ở thanh bên (sidebar) để xem biểu đồ so sánh HAS.")
        return

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
    
    api_key = get_groq_api_key()
            
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


@st.cache_resource
def get_global_paper_retriever(json_path):
    return PaperRetriever(json_path)


def get_groq_api_key():
    import os
    from pathlib import Path
    api_key = ""
    
    # Check if streamlit secrets file exists before accessing st.secrets
    # to avoid the red warning box
    has_secrets_file = False
    try:
        if Path(".streamlit/secrets.toml").exists() or (Path.home() / ".streamlit" / "secrets.toml").exists():
            has_secrets_file = True
    except Exception:
        pass
        
    if has_secrets_file:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
            
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
        
    if not api_key:
        try:
            with open("api_key.txt", "r") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            pass
    return api_key


def generate_ai_insight_stream(prompt_context, query, system_instruction):
    from groq import Groq
    api_key = get_groq_api_key()
    if not api_key:
        st.warning("⚠️ Không tìm thấy Groq API Key. Vui lòng thiết lập biến môi trường `GROQ_API_KEY` hoặc tạo tệp `api_key.txt` cục bộ.")
        return
        
    model_name = "llama-3.3-70b-versatile"
    json_path = DATA_DIR / "paper_text.json"
    
    retrieved_context = ""
    if json_path.exists():
        try:
            retriever = get_global_paper_retriever(json_path)
            retrieved_pages = retriever.retrieve(query, top_k=3)
            retrieved_context = "\n\n".join([f"--- PAGE {p['page']} ---\n{p['text']}" for p in retrieved_pages])
        except Exception as e:
            pass

    full_system_prompt = f"""
{system_instruction}

BỐI CẢNH NẰM TRONG BÀI BÁO KHOA HỌC GỐC (WORKBank paper, arXiv:2506.06576):
{retrieved_context}

DỮ LIỆU ĐANG ĐƯỢC LỌC VÀ HIỂN THỊ TRÊN BIỂU ĐỒ (DỮ LIỆU THỰC TẾ):
{prompt_context}
"""

    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": f"Dựa trên dữ liệu thực tế và bối cảnh bài báo, hãy phân tích và đưa ra khuyến nghị chi tiết cho: {query}"}
    ]
    
    try:
        client = Groq(api_key=api_key)
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.3,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Đã xảy ra lỗi khi gọi Groq API: {str(e)}"


def page_advanced_insights(desires_df, metadata_df, selected_occ, demographic_var):
    """Trang ✨ Nghiên Cứu Độc Lập (New Insights)"""
    st.markdown("### ✨ Nghiên Cứu Độc Lập & Phát Kiến Mới")
    st.markdown(
        "Khai thác chuyên sâu bộ dữ liệu khảo sát thô để tìm ra các mối tương quan về nhân khẩu học, "
        "tâm lý lao động và trải nghiệm công nghệ thực tế của nhân sự IT mà bài báo gốc chưa đề cập."
    )

    # Load and merge data
    merged_df = build_insights_df(desires_df, metadata_df)

    if selected_occ != "✨ Tất cả":
        merged_df = merged_df[merged_df["Occupation (O*NET-SOC Title)"] == selected_occ]

    tab1 = st.container()
    with tab1:
        # ── 💡 Đề Xuất Nghiên Cứu ──
        with st.expander("💡 **Đề Xuất Nghiên Cứu (Research Proposal):** Tại sao cần phân tích này?", expanded=False):
            st.markdown(
                "**Hạn chế của bài báo gốc** (*WORKBank*, arXiv:2506.06576):\n\n"
                "Bài báo thu thập dữ liệu nhân khẩu học nhưng **chỉ dùng làm biến kiểm soát** trong mô hình hồi quy "
                "(Appendix B, Table 1), không trực quan hóa hay diễn giải theo nhóm. Chỉ số *Job Security* chỉ được nhắc "
                "**1 câu duy nhất** (*\"ρ = −0.22\"*, Section 3.2). Lý do muốn tự động hóa (Figure 4b) chỉ phân tích ở mức **toàn mẫu**.\n\n"
                "**3 phát kiến mới của phân tích này:**\n\n"
                "1. 📊 **So sánh Desire vs. Job Security theo nhóm** — Bài báo gốc coi lực lượng lao động là khối đồng nhất\n"
                "2. 🎯 **Ma Trận Sẵn Sàng Nhân Sự** — Áp dụng triết lý 4 phân vùng (vốn cho *tác vụ*) sang **con người**, "
                "giải quyết bài toán *\"Ai cần gì khi deploy AI?\"*\n"
                "3. 📢 **Phân Tích Động Cơ theo nhóm** — Chia lý do muốn tự động hóa theo nhóm nhân khẩu để "
                "*cá nhân hóa truyền thông nội bộ*\n\n"
                "**Cơ sở lý thuyết:** Prosci ADKAR Model (Quản trị thay đổi), Self-Determination Theory — Deci & Ryan, "
                "OECD 2024 (*AI and the Future of Skills*), ILO 2024 (*Generative AI and Jobs*)."
            )

        st.markdown("#### 📊 Ảnh hưởng của Nhân khẩu học đến Mong muốn & An ninh việc làm")
        st.markdown(
            "Phân tích này đối chiếu các biến nhân khẩu học của người lao động IT để xem các nhóm tuổi, giới tính, "
            "trình độ học vấn hoặc kinh nghiệm khác nhau phản ứng như thế nào đối với AI và Tự động hóa."
        )

        df_plot = merged_df.copy()
        if demographic_var == "Nhóm tuổi (Age Group)":
            bins = [0, 25, 35, 45, 55, 100]
            labels = ["Dưới 25 tuổi", "25-34 tuổi", "35-44 tuổi", "45-54 tuổi", "Trên 55 tuổi"]
            df_plot["Age Group"] = pd.cut(df_plot["Age"], bins=bins, labels=labels)
            group_col = "Age Group"
        elif demographic_var == "Giới tính (Gender)":
            group_col = "Gender"
        elif demographic_var == "Trình độ học vấn (Education)":
            group_col = "Education"
        else:
            group_col = "Experience"

        # Group and calculate means
        stats = df_plot.groupby(group_col, observed=False)[["Automation Desire Rating", "Job Security Rating"]].mean().reset_index()

        # Sort values for logical display
        if group_col == "Experience":
            exp_order = ['Less than 1 year', '1-2 year', '3-5 years', '6-10 years', 'More than 10 years']
            stats[group_col] = pd.Categorical(stats[group_col], categories=exp_order, ordered=True)
            stats = stats.sort_values(group_col)
        elif group_col == "Education":
            edu_order = ['High School', 'Some College, No Degree', 'Associate Degree', "Bachelor's Degree", "Master's Degree", 'Doctorate (e.g., PhD)', 'Professional Degree (e.g., MD, JD)', 'Prefer not to say']
            stats[group_col] = pd.Categorical(stats[group_col], categories=edu_order, ordered=True)
            stats = stats.sort_values(group_col)

        fig = go.Figure(data=[
            go.Bar(
                name='Mong muốn Tự động hóa (Automation Desire)',
                x=stats[group_col],
                y=stats["Automation Desire Rating"],
                marker_color='#2ecc71'
            ),
            go.Bar(
                name='Lo ngại An ninh việc làm (Job Security Concern)',
                x=stats[group_col],
                y=stats["Job Security Rating"],
                marker_color='#e74c3c'
            )
        ])
        fig.update_layout(
            barmode='group',
            title=f"Trung bình Mong muốn Tự động hóa và Lo ngại An ninh theo {demographic_var}",
            xaxis_title=demographic_var,
            yaxis_title="Điểm số đánh giá (Thang 1-5)",
            yaxis=dict(range=[1, 5]),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 💡 Khám phá quan trọng:")

        # Dynamically compute insight text from actual data
        if group_col == "Education":
            max_desire_idx = stats["Automation Desire Rating"].idxmax()
            max_security_idx = stats["Job Security Rating"].idxmax()
            min_security_idx = stats["Job Security Rating"].idxmin()
            
            max_desire_group = stats.loc[max_desire_idx, group_col]
            max_desire_val = stats.loc[max_desire_idx, "Automation Desire Rating"]
            
            max_security_group = stats.loc[max_security_idx, group_col]
            max_security_val = stats.loc[max_security_idx, "Job Security Rating"]
            
            min_security_group = stats.loc[min_security_idx, group_col]
            min_security_val = stats.loc[min_security_idx, "Job Security Rating"]
            
            if max_desire_group == max_security_group:
                st.markdown(
                    f"*   **Nhóm có học vị {max_desire_group}** vừa có mong muốn tự động hóa công việc cao nhất (~{max_desire_val:.2f}) "
                    f"vừa có mức độ lo ngại về an ninh việc làm cao nhất (~{max_security_val:.2f}). Điều này chỉ ra rằng nhóm có trình độ này "
                    f"nhận thức rất rõ tiềm năng của AI và muốn áp dụng nó để nâng cao năng suất, nhưng cũng đồng thời cảm thấy áp lực lớn nhất về tính ổn định công việc."
                )
            else:
                st.markdown(
                    f"*   **Mong muốn tự động hóa:** Nhóm có trình độ học vấn **{max_desire_group}** có mong muốn tự động hóa cao nhất (~{max_desire_val:.2f}). "
                    f"Trong khi đó, nhóm **{max_security_group}** lại có mức độ lo ngại về an ninh việc làm cao nhất (~{max_security_val:.2f}) "
                    f"và nhóm **{min_security_group}** lo ngại ít nhất (~{min_security_val:.2f}). Điều này phản ánh sự phân hóa trong nhận thức và tâm lý của nhân sự đối với làn sóng AI tùy theo trình độ học vấn."
                )
        elif group_col == "Gender":
            male = stats[stats[group_col] == "Male"]
            female = stats[stats[group_col] == "Female"]
            if not male.empty and not female.empty:
                m_desire = male["Automation Desire Rating"].values[0]
                f_desire = female["Automation Desire Rating"].values[0]
                m_security = male["Job Security Rating"].values[0]
                f_security = female["Job Security Rating"].values[0]
                
                if m_desire > f_desire:
                    desire_narrative = f"**Nam giới (Male)** có điểm mong muốn tự động hóa cao hơn (**Nam**: ~{m_desire:.2f} so với **Nữ**: ~{f_desire:.2f})"
                else:
                    desire_narrative = f"**Nữ giới (Female)** có điểm mong muốn tự động hóa cao hơn (**Nữ**: ~{f_desire:.2f} so với **Nam**: ~{m_desire:.2f})"
                    
                if f_security > m_security:
                    security_narrative = f"**Nữ giới (Female)** lo ngại về an ninh việc làm cao hơn (**Nữ**: ~{f_security:.2f} so với **Nam**: ~{m_security:.2f})"
                else:
                    security_narrative = f"**Nam giới (Male)** lo ngại về an ninh việc làm cao hơn (**Nam**: ~{m_security:.2f} so với **Nữ**: ~{f_security:.2f})"
                
                st.markdown(
                    f"*   Theo số liệu thực tế: {desire_narrative}, đồng thời {security_narrative}. "
                    "Sự chênh lệch này chỉ ra thái độ tiếp cận công nghệ và nhu cầu đảm bảo an toàn việc làm khác nhau giữa các giới tính, "
                    "đòi hỏi chính sách đổi mới sáng tạo cần đi đôi với sự đồng hành và hỗ trợ phù hợp."
                )
            else:
                st.info("Không đủ dữ liệu giới tính trong bộ lọc hiện tại.")
        elif group_col == "Experience":
            max_security_row = stats.loc[stats["Job Security Rating"].idxmax()]
            min_security_row = stats.loc[stats["Job Security Rating"].idxmin()]
            st.markdown(
                f"*   Nhóm có kinh nghiệm **{max_security_row[group_col]}** lo ngại về an ninh việc làm nhiều nhất (~{max_security_row['Job Security Rating']:.2f}), trong khi nhóm "
                f"**{min_security_row[group_col]}** có mức độ lo ngại thấp nhất (~{min_security_row['Job Security Rating']:.2f}). "
                "Sự khác biệt này phản ánh thâm niên và mức độ nhạy cảm của các tác vụ đối với khả năng thay thế của công nghệ ở các nhóm thâm niên khác nhau."
            )
        else:
            max_desire_row = stats.loc[stats["Automation Desire Rating"].idxmax()]
            st.markdown(
                f"*   Nhóm tuổi **{max_desire_row[group_col]}** thể hiện mong muốn tự động hóa cao nhất (~{max_desire_row['Automation Desire Rating']:.2f}) "
                "để giải phóng sức lao động, tiết kiệm thời gian khỏi các thủ tục lặp đi lặp lại."
            )

        # 🤖 AI Phân Tích 1: Số liệu & Thái độ
        st.markdown("<br>", unsafe_allow_html=True)
        part1_stats_str = "\n".join([
            f"- Nhóm {row[group_col]}: Mong muốn tự động hóa (Desire) = {row['Automation Desire Rating']:.2f}/5, Lo ngại an ninh việc làm (Job Security) = {row['Job Security Rating']:.2f}/5"
            for _, row in stats.iterrows()
        ])
        part1_prompt = f"Ngành nghề lọc: {selected_occ}\nBiến nhân khẩu học đang chọn: {demographic_var}\n\nDỮ LIỆU THỰC TẾ TRÊN BIỂU ĐỒ:\n{part1_stats_str}"
        part1_system = """
Bạn là một chuyên gia phân tích dữ liệu nhân sự ngành CNTT. Hãy phân tích các con số thực tế trên và trả lời bằng tiếng Việt (dưới 200 từ).
Bố cục bắt buộc:
1. **Phát hiện quan trọng (Key Finding)**: Chỉ ra nhóm nào có Desire cao nhất/thấp nhất, nhóm nào lo lắng Job Security nhất/ít nhất. Sử dụng số liệu chính xác để so sánh.
2. **Kiến giải thực tế (Insight)**: Giải thích lý do cụ thể tại sao nhóm nhân khẩu học đó lại có thái độ như vậy (Ví dụ: tại sao người kinh nghiệm ít lại lo sợ hơn, hoặc tại sao học vị cao lại muốn tự động hóa nhiều hơn).
3. **Khuyến nghị tuyển dụng/quản lý (Actionable Advice)**: Đưa ra 1-2 hành động cụ thể cho HR manager đối với các nhóm cụ thể.
Không viết chung chung hay nói lý thuyết suông. Hãy bám sát các số liệu đã cung cấp.
"""
        if st.button("✨ AI phân tích Số liệu & Thái độ theo nhóm", key="btn_ai_part1"):
            with st.chat_message("assistant"):
                st.write_stream(generate_ai_insight_stream(part1_prompt, f"Phân tích thái độ AI theo {demographic_var} trong ngành {selected_occ}.", part1_system))



        # ─────────────────────────────────────────────────────────────
        # 📊 PHÂN TÍCH ĐỘNG CƠ TỰ ĐỘNG HÓA (Motivation Breakdown)
        # ─────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📊 Phân Tích Động Cơ Tự Động Hóa theo Nhóm (Motivation Breakdown)")
        st.markdown(
            "Bài báo gốc phân tích lý do muốn tự động hóa ở mức **toàn mẫu** (Figure 4b: 69% chọn 'Free Time'). "
            "Phân tích này chia theo **nhóm nhân khẩu** → phát hiện động cơ khác biệt → truyền thông cá nhân hóa."
        )

        _reason_map = {
            "Reasons for Automation Desire - Free Time": "Giải phóng thời gian",
            "Reasons for Automation Desire - Repetitive": "Việc lặp lại",
            "Reasons for Automation Desire - Human Error": "Giảm lỗi người",
            "Reasons for Automation Desire - Stress": "Giảm căng thẳng",
            "Reasons for Automation Desire - Difficulty": "Việc quá khó",
            "Reasons for Automation Desire - Scale": "Mở rộng quy mô",
        }
        _avail_reasons = {k: v for k, v in _reason_map.items() if k in df_plot.columns}

        _motivation_ctx = ""
        if _avail_reasons:
            _reason_records = []
            for grp_name, grp_df in df_plot.groupby(group_col, observed=False):
                if len(grp_df) == 0:
                    continue
                for col, label in _avail_reasons.items():
                    _tc = grp_df[col].apply(lambda x: x is True or str(x).strip().lower() == 'true').sum()
                    _pct = (_tc / len(grp_df) * 100)
                    _reason_records.append({"Nhóm": str(grp_name), "Lý do": label, "Tỷ lệ (%)": round(_pct, 1)})

            _reason_df = pd.DataFrame(_reason_records)

            fig_motiv = px.bar(
                _reason_df, x="Nhóm", y="Tỷ lệ (%)", color="Lý do", barmode="group",
                color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"],
            )
            fig_motiv.update_layout(
                template="plotly_white", height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_title=demographic_var, yaxis_title="Tỷ lệ chọn lý do (%)",
            )
            st.plotly_chart(fig_motiv, use_container_width=True, key="bar_motivation_breakdown")

            st.markdown("##### 💡 Khám phá quan trọng:")
            _pivot_r = _reason_df.pivot(index="Nhóm", columns="Lý do", values="Tỷ lệ (%)")
            if not _pivot_r.empty and len(_pivot_r) > 1:
                _rv = _pivot_r.var()
                _most_varied = _rv.idxmax()
                st.markdown(
                    f"*   **Lý do có sự khác biệt lớn nhất giữa các nhóm:** \"{_most_varied}\" "
                    f"(phương sai = {_rv[_most_varied]:.1f}). Các nhóm nhân khẩu có "
                    f"**động cơ tự động hóa khác nhau rõ rệt** → cần thiết kế truyền thông riêng."
                )
                if "Giải phóng thời gian" in _pivot_r.columns:
                    _mx = _pivot_r["Giải phóng thời gian"].idxmax()
                    _mx_v = _pivot_r["Giải phóng thời gian"].max()
                    _mn = _pivot_r["Giải phóng thời gian"].idxmin()
                    _mn_v = _pivot_r["Giải phóng thời gian"].min()
                    st.markdown(
                        f"*   Nhóm **{_mx}** chọn \"Giải phóng thời gian\" nhiều nhất ({_mx_v:.1f}%), "
                        f"nhóm **{_mn}** chỉ {_mn_v:.1f}%. "
                        f"Bài báo gốc báo cáo 69% toàn mẫu — con số thực tế **khác biệt đáng kể** giữa các nhóm."
                    )

            _motivation_ctx = "\n".join([
                f"- {row['Nhóm']} → {row['Lý do']}: {row['Tỷ lệ (%)']:.1f}%"
                for _, row in _reason_df.iterrows()
            ])
        else:
            st.info("Không tìm thấy cột dữ liệu lý do tự động hóa trong bộ dữ liệu hiện tại.")

        # 🤖 AI Phân Tích 3: Động cơ tự động hóa
        st.markdown("<br>", unsafe_allow_html=True)
        part3_prompt = f"Ngành nghề lọc: {selected_occ}\nBiến nhân khẩu học đang chọn: {demographic_var}\n\nTỶ LỆ CHỌN LÝ DO MUỐN TỰ ĐỘNG HÓA CỦA CÁC NHÓM (%):\n{_motivation_ctx if _motivation_ctx else 'Không có dữ liệu.'}"
        part3_system = """
Bạn là một chuyên gia tâm lý học hành vi tổ chức. Hãy phân tích động cơ muốn tự động hóa của các nhóm lao động và trả lời bằng tiếng Việt (dưới 200 từ).
Bố cục bắt buộc:
1. **Phát hiện động cơ (Motivation Patterns)**: Chỉ ra sự khác biệt lớn nhất về lý do muốn tự động hóa giữa các nhóm (ví dụ: nhóm nào ưu tiên giải phóng thời gian nhất, nhóm nào muốn giảm căng thẳng/sai sót). Dùng số phần trăm cụ thể.
2. **Kiến giải tâm lý (Self-Determination Theory)**: Liên hệ hành vi này với nhu cầu Autonomy (Tự chủ - giải phóng thời gian), Competence (Năng lực - giảm sai sót/độ khó) hoặc Relatedness (Kết nối - giảm stress).
3. **Cá nhân hóa truyền thông (Communication Strategy)**: Khuyến nghị 1-2 cách truyền thông nội bộ khác nhau cho các nhóm để họ đồng thuận khi giới thiệu công cụ AI mới.
Hãy bám sát các số liệu tỷ lệ phần trăm được cung cấp.
"""
        if _avail_reasons:
            if st.button("✨ AI phân tích Động cơ & Chiến lược truyền thông", key="btn_ai_part3"):
                with st.chat_message("assistant"):
                    st.write_stream(generate_ai_insight_stream(part3_prompt, f"Phân tích động cơ muốn tự động hóa theo {demographic_var} trong ngành {selected_occ}.", part3_system))

        # ─── 📚 Khung Lý Thuyết ───
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📚 Khung Lý Thuyết & Tài Liệu Tham Khảo", expanded=False):
            st.markdown(
                "**1. Prosci ADKAR® Model** (Quản trị thay đổi):\n"
                "- **A**wareness → **D**esire → **K**nowledge → **A**bility → **R**einforcement\n"
                "- Mỗi Profile trong Ma Trận Sẵn Sàng tương ứng với giai đoạn ADKAR mà nhóm đó đang thiếu\n\n"
                "**2. Self-Determination Theory** — Deci & Ryan (1985):\n"
                "- 3 nhu cầu nội tại: Autonomy, Competence, Relatedness\n"
                "- 'Free Time' → Autonomy | 'Difficulty/Error' → Competence | 'Stress' → Relatedness\n\n"
                "**3. Tài liệu tham khảo:**\n"
                "- OECD (2024): *AI and the Future of Skills* — AI tác động khác biệt theo tuổi, giới, học vấn\n"
                "- ILO (2024): *Generative AI and Jobs* — Phụ nữ tập trung ở vai trò dễ bị tự động hóa\n"
                "- Polsl.pl (2024): Trình độ học vấn cao giúp giảm AI anxiety\n"
                "- Prosci Research: Dự án có quản trị thay đổi → tỷ lệ thành công cao hơn 6 lần"
            )




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
            "✨ Nghiên Cứu Độc Lập (New Insights)",
        ],
        index=0,
        key="nav_radio",
    )

    st.sidebar.markdown("---")
    
    # Global filters in sidebar
    selected_occ = "✨ Tất cả"
    demographic_var = "Trình độ học vấn (Education)"
    
    if not (page.startswith("4") or page.startswith("💬") or "Chatbot" in page):
        st.sidebar.markdown("### 🔍 Bộ lọc toàn cục (Global Filters)")
        selected_occ = st.sidebar.selectbox(
            "🔽 Chọn ngành nghề cần lọc:",
            ["✨ Tất cả"] + IT_OCCUPATIONS,
            index=0,
            key="global_occ_filter"
        )
        
        if page.startswith("✨") or "Nghiên Cứu" in page:
            demographic_var = st.sidebar.selectbox(
                "🔽 Chọn biến nhân khẩu học:",
                [
                    "Trình độ học vấn (Education)",
                    "Giới tính (Gender)",
                    "Kinh nghiệm làm việc (Experience)",
                    "Nhóm tuổi (Age Group)"
                ],
                index=0,
                key="global_demo_filter"
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
        page_landscape(landscape_df, selected_occ)

    elif page.startswith("2"):
        landscape_df = build_landscape_df(desires, expert)
        page_mismatch(landscape_df, selected_occ)

    elif page.startswith("3"):
        has_df = build_has_data(desires, expert)
        page_has_spectrum(has_df, selected_occ)

    elif page.startswith("4"):
        skill_df = build_skill_shift_data(tasks, expert)
        page_skill_shift(skill_df)

    elif page.startswith("💬") or "Chatbot" in page:
        page_chatbot()

    elif page.startswith("✨") or "Nghiên Cứu" in page:
        page_advanced_insights(desires, metadata, selected_occ, demographic_var)


if __name__ == "__main__":
    main()
