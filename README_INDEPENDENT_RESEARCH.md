# Hướng Dẫn Phát Kiến Nghiên Cứu Độc Lập (Independent Research README)

Tài liệu này giải thích chi tiết **ý tưởng hình thành**, **cơ sở lý thuyết/triết lý thiết kế**, và **cách thức vận hành** của trang **✨ Nghiên Cứu Độc Lập (New Insights)** (Trang số 6) trong ứng dụng web WORKBank.

---

## 1. Ý Tưởng Hình Thành & Động Lực Nghiên Cứu (Motivation & Inspiration)

### Hạn chế của bài báo gốc (WORKBank paper, arXiv:2506.06576)
Bài báo gốc của nhóm nghiên cứu MIT/Harvard tập trung phân tích khả năng của AI (expert-rated) và mong muốn tự động hóa của người lao động ở cấp độ **tác vụ chung** cho toàn thị trường lao động Mỹ. Tuy nhiên, nghiên cứu này coi toàn bộ lực lượng lao động là một **khối đồng nhất (homogeneous group)**. 
Bài báo bỏ qua một thực tế quan trọng: **Sự tiếp nhận công nghệ phụ thuộc rất lớn vào các yếu tố cá nhân của người lao động** như trình độ học vấn, kinh nghiệm làm việc, giới tính, mức độ tiếp xúc thực tế với AI và động lực nội tại đối với công việc.

### Phát kiến mới của dự án
Trong thực tế quản trị doanh nghiệp, việc chuyển đổi số và triển khai AI Agent thành công hay thất bại phụ thuộc lớn vào **Tâm lý học lao động (Occupational Psychology)** và **Hành vi tổ chức (Organizational Behavior)** nhằm giảm thiểu sự kháng cự công nghệ (Change Resistance).

Trang **Nghiên Cứu Độc Lập** được hình thành nhằm giải quyết bài toán: **Làm sao để thiết kế một lộ trình triển khai AI Agent lấy con người làm trung tâm (Worker-Centric AI Deployment)?** 
Chúng tôi kết hợp dữ liệu đánh giá tác vụ thô với dữ liệu nhân khẩu học cá nhân của từng worker để tìm ra các quy luật tâm lý và đề xuất giải pháp HR thực chiến.

---

## 2. Thiết Kế Ý Tưởng Dựa Trên Các Khung Lý Thuyết (Conceptual Frameworks)

Ý tưởng nghiên cứu được cấu thành từ 3 phân hệ (Tabs) tương ứng với 3 lý thuyết quản trị và hành vi:

```text
Ý TƯỞNG NGHIÊN CỨU ĐỘC LẬP
 ├── Tab 1: Nhân khẩu học & An ninh việc làm ──► Khung Quản trị thay đổi & Quản trị rủi ro HR
 ├── Tab 2: Enjoyment vs. Tự động hóa         ──► Thuyết tự quyết (Self-Determination Theory - SDT)
 └── Tab 3: Trải nghiệm LLM vs. Kiểm soát     ──► Mô hình Chấp nhận Công nghệ (TAM Model)
```

### Phân hệ 1: Nhân khẩu học & An ninh việc làm (Demographics & Job Security)
*   **Ý tưởng hình thành:** Đánh giá mức độ tổn thương và e ngại của các nhóm nhân sự khác nhau. Nhóm học vị cao (PhD) hay nhóm ít kinh nghiệm phản ứng thế nào trước AI?
*   **Ứng dụng thực tế:** Phát hiện nhóm nhân viên chịu áp lực tâm lý lớn nhất để thiết kế các chính sách bảo đảm an ninh việc làm, tái đào tạo (upskilling) phù hợp, tránh gây khủng hoảng truyền thông nội bộ.

### Phân hệ 2: Enjoyment vs. Tự động hóa (Tâm lý học Thuyết Tự Quyết - SDT)
*   **Ý tưởng hình thành:** Theo *Thuyết tự quyết (Self-Determination Theory)*, con người có nhu cầu nội tại về quyền tự chủ (autonomy) và sự gắn kết với công việc mang lại niềm vui (Enjoyment). Nếu doanh nghiệp cố tình dùng AI để tự động hóa phần việc nhân viên đang vô cùng yêu thích, họ sẽ phản kháng quyết liệt vì bị tước đoạt động lực làm việc.
*   **Kiểm chứng dữ liệu:** Phân tích chỉ ra hệ số tương quan âm rõ rệt ($r = -0.22$). Người lao động mong muốn tự động hóa rất cao đối với việc tẻ nhạt, lặp đi lặp lại (Enjoyment thấp) nhưng muốn giữ lại quyền tự làm đối với các tác vụ họ đam mê (Enjoyment cao).

### Phân hệ 3: Trải nghiệm LLM & Quyền kiểm soát (Mô hình Chấp nhận Công nghệ - TAM)
*   **Ý tưởng hình thành:** Theo *Mô hình Chấp nhận Công nghệ (Technology Acceptance Model)*, nhận thức về tính hữu ích (perceived usefulness) tăng lên khi có trải nghiệm thực tế sử dụng hệ thống. Những người dùng LLM hàng ngày sẽ hiểu rõ giới hạn và năng lực của công cụ, từ đó cởi mở hơn trong việc chuyển giao tác vụ cho AI.
*   **Ứng dụng thực tế:** Chứng minh tầm quan trọng của việc tổ chức các buổi đào tạo, hackathon và cấp tài khoản LLM cho nhân viên trải nghiệm sớm nhằm "bình thường hóa" công nghệ và xóa tan nỗi sợ e dè mơ hồ.

---

## 3. Cách Thức Vận Hành & Kiến Trúc Dữ Liệu (Data Pipeline)

Để hiện thực hóa ý tưởng trên thành biểu đồ trực quan, mã nguồn [streamlit_app.py](file:///d:/Documents/Data%20Visualization/workbank/streamlit_app.py) thực hiện luồng vận hành kỹ thuật sau:

### Bước 1: Tích hợp dữ liệu (Data Join)
Hàm [build_insights_df](file:///d:/Documents/Data%20Visualization/workbank/streamlit_app.py#L174-L185) thực hiện kết nối:
- Bảng khảo sát tác vụ [domain_worker_desires.csv](file:///d:/Documents/Data%20Visualization/workbank/domain_worker_desires.csv) chứa điểm mong muốn (`Automation Desire Rating`), độ yêu thích (`Enjoyment Rating`).
- Bảng thông tin cá nhân [domain_worker_metadata.csv](file:///d:/Documents/Data%20Visualization/workbank/domain_worker_metadata.csv) chứa các thuộc tính nhân khẩu học và tần suất sử dụng LLM.
- **Thuật toán ghép:** Sử dụng `pd.merge` trên khóa chính kép `["User ID", "Occupation (O*NET-SOC Title)"]` để đảm bảo dữ liệu ghép chính xác theo từng cá nhân người khảo sát.

### Bước 2: Gom nhóm & Tính toán thống kê (Aggregation)
Khi người dùng chọn bộ lọc, hệ thống thực thi các phép toán:
- **GroupBy**: `.groupby()` theo các nhóm nhân khẩu học hoặc nhóm sử dụng LLM để tính toán giá trị trung bình (`.mean()`).
- **Correlation**: Gọi hàm `.corr()` để tính toán hệ số tương quan Pearson giữa mức độ yêu thích và mong muốn tự động hóa.
- **Categorical Order**: Ép thứ tự hiển thị của dữ liệu phân loại thứ bậc (như tần suất dùng LLM) theo trình tự logic bằng cách định nghĩa `pd.Categorical`.

### Bước 3: Trực quan hóa tương tác (Visualization Engine)
Dữ liệu sau khi xử lý được nạp vào Plotly để render các loại biểu đồ tương tác cao:
- Biểu đồ cột đôi (`go.Bar`) so sánh đồng thời điểm Mong muốn và An ninh việc làm.
- Biểu đồ phân tán (`px.scatter`) đi kèm đường xu thế hồi quy OLS màu đỏ thể hiện độ dốc tương quan.

---

## 4. Cơ Chế Sinh Nhận Định Tự Động (AI Insights Engine)

Để đưa ra các khuyến nghị quản trị thiết thực, trang Nghiên Cứu Độc Lập tích hợp một hệ thống suy luận AI thời gian thực:

1.  **Thu thập dữ liệu giao diện (State Capture):** Chương trình đọc các giá trị thống kê thực tế hiện hiển thị trên biểu đồ đang được lọc và chuyển đổi thành một văn bản ngữ cảnh (Prompt Context).
2.  **Truy xuất bài báo khoa học (RAG):** Hệ thống tìm kiếm top 3 trang tài liệu liên quan nhất trong tệp `paper_text.json` bằng công cụ TF-IDF dựa trên truy vấn lọc.
3.  **Kêu gọi mô hình ngôn ngữ lớn (LLM Call):** Gửi toàn bộ dữ liệu thực tế + lý thuyết bài báo sang **Groq API** (`llama-3.3-70b-versatile`) đi kèm system prompt đóng vai trò chuyên gia nhân sự.
4.  **Sinh khuyến nghị (Streaming Response):** AI trả về các khuyến nghị chiến lược và giải pháp tổ chức cụ thể dưới dạng dòng chảy chữ mượt mà ngay trên giao diện Streamlit.
