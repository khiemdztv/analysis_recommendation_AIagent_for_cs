# Hướng Dẫn Ôn Tập & Đề Thi Mẫu Môn Trực Quan Hóa Dữ Liệu (Paper Coding Test)

Môn học **Trực quan hóa dữ liệu (Data Visualization)** khi thi viết trên giấy thường yêu cầu kết hợp:
1. **Pandas**: Xử lý, làm sạch và gom nhóm dữ liệu.
2. **Plotly Express (`px`)**: Vẽ các loại biểu đồ chuyên dụng (Cột, Hộp, Phân tán, Phân phối, Nhiệt, Đường).
3. **Streamlit (`st`)**: Hiển thị biểu đồ lên giao diện web, phân chia bố cục và tạo bộ lọc tương tác.

Dưới đây là các câu hỏi thi mẫu từ cơ bản đến nâng cao được chia theo chủ đề giúp bạn ôn tập toàn diện nhất.

---

## 1. Các Hàm Vẽ Biểu Đồ Plotly Express (`px`) Cần Nhớ

| Loại biểu đồ | Cú pháp Plotly Express | Trường hợp sử dụng |
| :--- | :--- | :--- |
| **Histogram (Phân phối)** | `px.histogram(df, x="cot_x", color="cot_nhom", title="...")` | Xem phân phối tần suất (ví dụ: phân phối tuổi). |
| **Bar (Biểu đồ cột)** | `px.bar(df, x="cot_x", y="cot_y", title="...")` | So sánh giá trị giữa các nhóm (thường đi sau GroupBy). |
| **Scatter (Phân tán)** | `px.scatter(df, x="cot_x", y="cot_y", color="cot_nhom", title="...")` | Tìm mối tương quan giữa 2 biến số liên tục. |
| **Box (Biểu đồ hộp)** | `px.box(df, x="cot_nhom", y="cot_gia_tri", title="...")` | So sánh phân phối, biên độ và các giá trị ngoại lai (outliers). |
| **Pie (Biểu đồ tròn)** | `px.pie(df, names="cot_nhom", values="cot_gia_tri", title="...")` | Xem tỷ lệ phần trăm đóng góp của các nhóm. |
| **Line (Biểu đồ đường)** | `px.line(df, x="cot_x", y="cot_y", title="...")` | Trực quan hóa xu hướng thay đổi theo thời gian. |
| **Heatmap (Bản đồ nhiệt)** | `px.imshow(ma_tran_tuong_quan, title="...")` | Trực quan hóa mức độ tương quan giữa các biến số. |
| **Violin (Biểu đồ vĩ cầm)**| `px.violin(df, x="cot_nhom", y="cot_y", box=True, title="...")` | So sánh phân bổ mật độ dữ liệu chi tiết hơn Box Plot. |

---

## 2. Các Hàm Streamlit (`st`) Hiển Thị Giao Diện Cần Nhớ

- `st.title("Tiêu đề trang")`
- `st.write("Đoạn văn bản mô tả")`
- `st.plotly_chart(fig)`: Hiển thị đối tượng biểu đồ Plotly `fig` lên giao diện.
- `st.selectbox("Nhãn", options=danh_sach)`: Bộ chọn thả xuống (chọn duy nhất một giá trị).
- `st.multiselect("Nhãn", options=danh_sach)`: Bộ lọc cho phép chọn nhiều giá trị cùng lúc.
- `st.slider("Nhãn", min_val, max_val, (val_dau, val_cuoi))`: Thanh trượt chọn giá trị số hoặc chọn khoảng (range).
- `col1, col2 = st.columns(2)`: Chia không gian hiển thị thành các cột dọc bên cạnh nhau.

---

## 3. Các Bài Tập Thực Hành Viết Tay (Đề Thi Mẫu)

### Câu 1: Biểu Đồ Phân Phối Tần Suất (Histogram với Plotly & Streamlit)
**Đề bài:** Hãy viết ứng dụng Streamlit đọc tệp `domain_worker_metadata.csv` và vẽ biểu đồ Histogram thể hiện phân phối độ tuổi (`Age`) của người lao động, phân nhóm màu sắc (color) theo giới tính (`Gender`).

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

# Tiêu đề giao diện Streamlit
st.title("Phân Phối Độ Tuổi Người Lao Động")

# Đọc dữ liệu
df_meta = pd.read_csv("domain_worker_metadata.csv")

# Vẽ biểu đồ Histogram bằng Plotly Express
fig = px.histogram(
    df_meta, 
    x="Age", 
    color="Gender", 
    title="Phân phối tuổi theo Giới tính",
    nbins=20  # Chia thành 20 cột khoảng tuổi
)

# Hiển thị biểu đồ lên giao diện Streamlit
st.plotly_chart(fig)
```

---

### Câu 2: Phân Tích Thống Kê & Vẽ Biểu Đồ Cột (GroupBy & Bar Chart)
**Đề bài:** Viết ứng dụng Streamlit đọc dữ liệu từ `domain_worker_desires.csv`. Hãy gom nhóm dữ liệu theo cột `Self-reported Expertise` (Mức độ tự đánh giá năng lực) để tính điểm trung bình mong muốn tự động hóa (`Automation Desire Rating`) của từng nhóm. Vẽ biểu đồ cột biểu diễn kết quả này.

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Mong Muốn Tự Động Hóa Theo Trình Độ")

# Đọc dữ liệu
df_desire = pd.read_csv("domain_worker_desires.csv")

# Groupby tính điểm trung bình và reset_index để đưa kết quả về dạng DataFrame phẳng
df_grouped = df_desire.groupby("Self-reported Expertise")["Automation Desire Rating"].mean().reset_index()

# Vẽ biểu đồ cột
fig = px.bar(
    df_grouped,
    x="Self-reported Expertise",
    y="Automation Desire Rating",
    title="Điểm Mong Muốn Tự Động Hóa Trung Bình",
    labels={"Automation Desire Rating": "Điểm trung bình (1-5)"}
)

# Hiển thị lên giao diện
st.plotly_chart(fig)
```

---

### Câu 3: Khảo Sát Mối Tương Quan (Scatter Plot)
**Đề bài:** Đọc tệp `task_statement_with_metadata.csv`. Loại bỏ các dòng bị thiếu lương (`Occupation Mean Annual Wage`). Viết code Streamlit vẽ biểu đồ phân tán (Scatter Plot) để trực quan hóa mối tương quan giữa:
- Trục X: Độ quan trọng của nhiệm vụ (`Importance`).
- Trục Y: Mức lương trung bình năm của ngành nghề (`Occupation Mean Annual Wage`).
- Màu sắc (Color): Phân loại nhiệm vụ (`Task Type`).

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Tương Quan Giữa Độ Quan Trọng Nhiệm Vụ Và Lương")

# Đọc dữ liệu
df_task = pd.read_csv("task_statement_with_metadata.csv")

# Loại bỏ giá trị null ở cột lương
df_clean = df_task.dropna(subset=["Occupation Mean Annual Wage"])

# Vẽ biểu đồ phân tán Scatter Plot
fig = px.scatter(
    df_clean,
    x="Importance",
    y="Occupation Mean Annual Wage",
    color="Task Type",
    title="Độ Quan Trọng Nhiệm Vụ vs Mức Lương",
    opacity=0.7
)

# Hiển thị biểu đồ
st.plotly_chart(fig)
```

---

### Câu 4: Phân Tích Biên Độ & Giá Trị Ngoại Lai (Box Plot sau khi Merge)
**Đề bài:** Hãy ghép bảng `domain_worker_desires.csv` và bảng `domain_worker_metadata.csv` dựa trên `User ID`. Vẽ biểu đồ hộp (Box Plot) thể hiện phân phối điểm mong muốn tự động hóa (`Automation Desire Rating`) tương ứng với từng nhóm trình độ học vấn (`Education`).

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Phân Phối Mong Muốn Tự Động Hóa Theo Học Vấn")

# Đọc dữ liệu
df_meta = pd.read_csv("domain_worker_metadata.csv")
df_desire = pd.read_csv("domain_worker_desires.csv")

# Ghép hai bảng
df_merged = pd.merge(df_desire, df_meta[["User ID", "Education"]], on="User ID")

# Vẽ biểu đồ Box Plot để so sánh phân phối các nhóm học vấn
fig = px.box(
    df_merged,
    x="Education",
    y="Automation Desire Rating",
    title="Biểu đồ hộp phân phối Automation Desire theo Trình độ học vấn",
    color="Education"
)

# Hiển thị lên Streamlit
st.plotly_chart(fig)
```

---

### Câu 5: Tạo Bộ Lọc Tương Tác Trên Giao Diện (Interactive Dashboard với Pie Chart)
**Đề bài:** Hãy thiết kế một bảng điều khiển Streamlit tương tác đơn giản cho phép:
1. Người dùng chọn một Nghề nghiệp từ menu thả xuống (`st.selectbox`). Danh sách nghề nghiệp lấy từ cột `Occupation (O*NET-SOC Title)` trong file `domain_worker_metadata.csv`.
2. Sau khi người dùng chọn nghề nghiệp, hãy lọc dữ liệu và vẽ biểu đồ tròn (Pie Chart) thể hiện tỷ lệ cơ cấu trình độ học vấn (`Education`) của những người làm nghề đó.

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Khảo Sát Học Vấn Theo Nghề Nghiệp")

# Đọc dữ liệu
df_meta = pd.read_csv("domain_worker_metadata.csv")

# 1. Lấy danh sách nghề nghiệp duy nhất để làm lựa chọn cho selectbox
occupations = df_meta["Occupation (O*NET-SOC Title)"].unique()

# Tạo selectbox tương tác
selected_occ = st.selectbox("Chọn một nghề nghiệp để xem:", options=occupations)

# 2. Lọc dữ liệu theo nghề nghiệp đã chọn
df_filtered = df_meta[df_meta["Occupation (O*NET-SOC Title)"] == selected_occ]

# Đếm tần suất học vấn trong nhóm nghề nghiệp này để vẽ Pie Chart
df_pie_data = df_filtered["Education"].value_counts().reset_index()

# Vẽ biểu đồ tròn
fig = px.pie(
    df_pie_data,
    names="Education",
    values="count",
    title=f"Tỷ lệ học vấn của ngành: {selected_occ}"
)

# Hiển thị biểu đồ tương tác
st.plotly_chart(fig)
```

---

### Câu 6: Biểu Đồ Đường Xu Thế Thời Gian (Line Chart - phân tích xu hướng)
**Đề bài:** Đọc tệp `domain_worker_desires.csv`. Hãy chuẩn hóa cột ngày tháng (`Date`) về dạng dữ liệu thời gian trong Pandas, đếm số lượng bản ghi khảo sát phát sinh theo từng ngày, sau đó vẽ biểu đồ đường (Line Chart) biểu diễn số lượng khảo sát qua các ngày.

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Xu Hướng Số Lượng Khảo Sát Theo Thời Gian")

# Đọc dữ liệu
df_desire = pd.read_csv("domain_worker_desires.csv")

# 1. Chuyển đổi cột Date từ chuỗi sang kiểu Datetime
df_desire["Date"] = pd.to_datetime(df_desire["Date"])

# 2. Đếm số lượng khảo sát theo từng ngày và reset_index
df_trend = df_desire.groupby("Date").size().reset_index(name="Survey Count")

# 3. Sắp xếp tăng dần theo thời gian để đường vẽ chạy đúng trình tự
df_trend = df_trend.sort_values("Date")

# Vẽ biểu đồ đường
fig = px.line(
    df_trend,
    x="Date",
    y="Survey Count",
    title="Số lượng khảo sát thực hiện mỗi ngày"
)

# Hiển thị lên giao diện
st.plotly_chart(fig)
```

---

### Câu 7: Trực Quan Hóa Hệ Số Tương Quan (Correlation Heatmap)
**Đề bài:** Đọc tệp `domain_worker_desires.csv`. Hãy viết code tính toán ma trận hệ số tương quan Pearson giữa các thuộc tính số sau:
`Automation Desire Rating`, `Enjoyment Rating`, `Job Security Rating`, `Involved Uncertainty`, `Domain Expertise Requirement`. 
Trực quan hóa ma trận tương quan này bằng biểu đồ Heatmap (Bản đồ nhiệt) sử dụng hàm `px.imshow()`.

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Ma Trận Tương Quan Hệ Số Đánh Giá")

# Đọc dữ liệu
df_desire = pd.read_csv("domain_worker_desires.csv")

# 1. Danh sách các cột thuộc tính số cần tính tương quan
cols = [
    "Automation Desire Rating", 
    "Enjoyment Rating", 
    "Job Security Rating", 
    "Involved Uncertainty", 
    "Domain Expertise Requirement"
]

# 2. Tính ma trận tương quan Pearson
corr_matrix = df_desire[cols].corr()

# 3. Vẽ bản đồ nhiệt Heatmap
fig = px.imshow(
    corr_matrix,
    text_auto=True, # Hiển thị trực tiếp hệ số tương quan lên từng ô màu
    title="Bản Đồ Nhiệt Tương Quan Giữa Các Thuộc Tính Đánh Giá",
    color_continuous_scale="RdBu" # Thang màu đỏ-xanh đối xứng
)

# Hiển thị lên giao diện
st.plotly_chart(fig)
```

---

### Câu 8: Phân Chia Bố Cục Đa Cột Trên Dashboard (Streamlit Columns & Violin Plot)
**Đề bài:** Hãy viết ứng dụng Streamlit đọc tệp `domain_worker_metadata.csv`. Chia giao diện hiển thị thành 2 cột dọc có kích thước bằng nhau:
- **Cột 1:** Vẽ biểu đồ Histogram phân phối tuổi (`Age`) của người lao động.
- **Cột 2:** Vẽ biểu đồ vĩ cầm (Violin Plot) phân tích mức phân bổ độ tuổi (`Age`) theo từng trình độ học vấn (`Education`).

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Phân Tích Bố Cục Đa Cột & Phân Bố Tuổi")

# Đọc dữ liệu
df_meta = pd.read_csv("domain_worker_metadata.csv")

# 1. Chia giao diện thành 2 cột
col1, col2 = st.columns(2)

# 2. Code xử lý hiển thị cho Cột 1
with col1:
    st.subheader("Phân Phối Tuổi Tần Suất")
    fig_hist = px.histogram(df_meta, x="Age", title="Tần suất theo độ tuổi")
    st.plotly_chart(fig_hist, use_container_width=True) # Điều chỉnh vừa khung cột

# 3. Code xử lý hiển thị cho Cột 2
with col2:
    st.subheader("Phân Phối Tuổi Theo Học Vấn")
    fig_violin = px.violin(
        df_meta, 
        x="Education", 
        y="Age", 
        box=True, # Tích hợp một hộp box plot nhỏ bên trong vĩ cầm
        title="Biểu đồ vĩ cầm độ tuổi theo học vấn"
    )
    st.plotly_chart(fig_violin, use_container_width=True)
```

---

### Câu 9: Bộ Lọc Tương Tác Nâng Cao (Streamlit Slider & Multiselect)
**Đề bài:** Đọc tệp `domain_worker_metadata.csv`. Hãy thiết kế giao diện Streamlit chứa:
1. Một thanh kéo chọn khoảng tuổi (`st.slider`) từ 18 tuổi đến 70 tuổi.
2. Một hộp chọn nhiều giá trị (`st.multiselect`) cho phép chọn một hoặc nhiều Nhóm giới tính (`Gender`).
Hãy lọc dữ liệu dựa trên cả 2 bộ lọc này và vẽ biểu đồ tròn (Pie Chart) biểu diễn cơ cấu chủng tộc (`Race`) của tập người lao động sau khi lọc.

#### Lời giải viết trên giấy:
```python
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Bộ Lọc Phân Tích Chủng Tộc Tương Tác")

# Đọc dữ liệu
df_meta = pd.read_csv("domain_worker_metadata.csv")

# 1. Tạo thanh trượt chọn khoảng tuổi (tuổi nhỏ nhất, tuổi lớn nhất)
age_range = st.slider(
    "Chọn khoảng tuổi nghiên cứu:",
    min_value=18,
    max_value=70,
    value=(25, 45) # Giá trị mặc định khi mở app
)

# 2. Tạo hộp chọn nhiều Giới tính
gender_options = df_meta["Gender"].unique()
selected_genders = st.multiselect(
    "Chọn các giới tính cần lọc:",
    options=gender_options,
    default=list(gender_options) # Mặc định chọn tất cả
)

# 3. Áp dụng các điều kiện lọc vào DataFrame
df_filtered = df_meta[
    (df_meta["Age"] >= age_range[0]) &
    (df_meta["Age"] <= age_range[1]) &
    (df_meta["Gender"].isin(selected_genders))
]

# 4. Trực quan hóa cấu trúc Chủng tộc (Race) của nhóm sau lọc
if not df_filtered.empty:
    df_race = df_filtered["Race"].value_counts().reset_index()
    fig = px.pie(
        df_race,
        names="Race",
        values="count",
        title="Tỷ lệ phân bổ Chủng tộc sau lọc"
    )
    st.plotly_chart(fig)
else:
    st.warning("Không có dữ liệu thỏa mãn bộ lọc đã chọn!")
```
