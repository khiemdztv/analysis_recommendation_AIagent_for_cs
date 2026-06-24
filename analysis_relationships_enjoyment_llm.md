# NGHIÊN CỨU CHUYÊN SÂU: SỰ YÊU THÍCH (ENJOYMENT), TRẢI NGHIỆM LLM VÀ MONG MUỐN TỰ ĐỘNG HÓA

Tài liệu này giải thích chi tiết cơ sở khoa học, ý nghĩa các con số/nhãn (labels), và giá trị nghiên cứu của hai mối quan hệ cốt lõi trong phần **Nghiên Cứu Độc Lập (New Insights)** tại [streamlit_app.py](file:///d:/Documents/Data%20Visualization/workbank/streamlit_app.py). Đây là tài liệu hướng dẫn giúp bạn bảo vệ và giải thích thuyết phục trước Hội đồng/Thầy cô hướng dẫn về lý do tại sao các phân tích này là cần thiết trong một đề tài về AI Agent.

---

## 1. TỔNG QUAN BỐI CẢNH (RESEARCH CONTEXT)

Thông thường, khi nghiên cứu về việc tích hợp AI Agent vào doanh nghiệp, người ta chỉ tập trung vào khía cạnh kỹ thuật: **AI có khả năng làm được việc đó không? (Capability)**. 
Tuy nhiên, dự án của chúng ta tiếp cận theo hướng **Worker-Centric (Lấy người lao động làm trung tâm)**. Hai phân tích dưới đây đại diện cho khía cạnh **Tâm lý học lao động (Occupational Psychology)** và **Hành vi tổ chức (Organizational Behavior)**:
1. **Sự yêu thích công việc (Enjoyment)**: Phản ánh động lực nội tại (intrinsic motivation) của con người.
2. **Trải nghiệm sử dụng AI thực tế (LLM Experience/Usage)**: Phản ánh nhận thức thực tế của con người về công nghệ qua mô hình chấp nhận công nghệ (TAM - Technology Acceptance Model).

---

## 2. MỐI QUAN HỆ 1: SỰ YÊU THÍCH (ENJOYMENT) VS. MONG MUỐN TỰ ĐỘNG HÓA

### A. Tại sao lại phân tích mối quan hệ này? (Cơ sở khoa học)
* **Quy luật tâm lý và Động lực nội tại**: Theo thuyết tự quyết (Self-Determination Theory), con người có xu hướng muốn giữ lại những công việc mang lại niềm vui, sự tự chủ, cảm giác thử thách và sáng tạo (Enjoyment cao). Họ chỉ muốn đẩy những phần việc tẻ nhạt, lặp đi lặp lại hoặc gây căng thẳng (Enjoyment thấp) cho máy móc.
* **Ngăn ngừa sự kháng cự công nghệ (Change Resistance)**: Nếu doanh nghiệp áp dụng AI Agent để tự động hóa cả những việc nhân viên yêu thích, họ sẽ cảm thấy bị mất đi ý nghĩa công việc (job meaning), dẫn đến việc chống đối ngầm hoặc giảm hiệu suất. Do đó, việc đo lường mối tương quan này giúp xác định **chiến lược lộ trình tự động hóa tối ưu**.

### B. Giải thích ý nghĩa các con số & Nhãn (Labels)
* **Enjoyment Rating (Thang đo Yêu thích: 1 - 5)**:
  * **1 (Thấp nhất)**: Tác vụ gây nhàm chán, mệt mỏi, tẻ nhạt, hoặc có tính lặp đi lặp lại cao (ví dụ: nhập dữ liệu, gửi email cảm ơn định kỳ).
  * **3 (Trung bình)**: Tác vụ mang tính trung hòa về cảm xúc.
  * **5 (Cao nhất)**: Tác vụ mang tính sáng tạo cao, đòi hỏi tư duy sâu hoặc tạo ra nhiều giá trị tự hào cá nhân (ví dụ: thiết kế kiến trúc hệ thống, viết kịch bản sáng tạo).
* **Automation Desire Rating (Thang đo Mong muốn tự động hóa: 1 - 5)**:
  * **1**: Hoàn toàn muốn tự làm thủ công, không muốn AI chạm vào.
  * **5**: Cực kỳ muốn giao trọn gói công việc này cho AI tự động hóa hoàn toàn.
* **Hệ số tương quan ($r$)**:
  * Thường đạt giá trị khoảng **$-0.28$** đến **$-0.30$** (Tương quan âm rõ rệt).
  * **Ý nghĩa toán học**: Khi điểm Yêu thích (Enjoyment) tăng lên 1 đơn vị, điểm Mong muốn tự động hóa (Automation Desire) sẽ giảm xuống tương ứng theo hệ số góc của đường xu hướng.
  * **Dữ liệu thực tế**: Khi Enjoyment = 1, điểm mong muốn tự động hóa trung bình đạt rất cao (~4.00+). Khi Enjoyment = 5, điểm mong muốn tự động hóa giảm mạnh xuống mức thấp (~2.50 - 2.80).

### C. Cách trả lời và giải thích với Thầy (Talking Points)
> *"Thưa thầy, biểu đồ tương quan này chứng minh một nghịch lý thực tế: **Người lao động không ghét AI, họ chỉ ghét việc AI cướp đi những phần việc thú vị của họ**. Số liệu cho thấy tương quan âm rõ rệt ($r \approx -0.28$). Từ đó, em đưa ra khuyến nghị chiến lược cho doanh nghiệp: Khi triển khai AI Agent, bước đi đầu tiên phải là tự động hóa các tác vụ có Enjoyment từ 1 đến 2. Việc này vừa giúp giải phóng sức lao động, vừa tạo ra sự đồng thuận tối đa của nhân viên, giúp dự án chuyển đổi số dễ dàng thành công hơn."*

---

## 3. MỐI QUAN HỆ 2: TRẢI NGHIỆM LLM THỰC TẾ VS. MONG MUỐN TỰ ĐỘNG HÓA

### A. Tại sao lại phân tích mối quan hệ này? (Cơ sở khoa học)
* **Mô hình Chấp nhận Công nghệ (TAM - Technology Acceptance Model)**: TAM chỉ ra rằng thái độ chấp nhận công nghệ phụ thuộc vào **Nhận thức về tính hữu ích (Perceived Usefulness)** và **Nhận thức về tính dễ sử dụng (Perceived Ease of Use)**. 
* **Sự khác biệt giữa Lý thuyết và Thực hành**: Những người chưa từng sử dụng LLM thường đánh giá AI dựa trên các tin đồn, truyền thông thổi phồng hoặc nỗi sợ hãi mơ hồ (sợ mất việc). Những người đã dùng thực tế sẽ đánh giá AI dựa trên **năng lực thực tế của công cụ**, giúp họ có cái nhìn thực tế và chính xác hơn.

### B. Giải thích ý nghĩa các con số & Nhãn (Labels)
* **Biến 1: Tần suất sử dụng LLM trong công việc (LLM Use in Work)**:
  * *No, I've never heard of them*: Chưa bao giờ nghe nói đến LLM.
  * *No, I have not used them...*: Đã nghe nói nhưng chưa bao giờ dùng cho công việc.
  * *Yes, occasionally...*: Đã dùng thỉnh thoảng cho một số tác vụ cụ thể.
  * *Yes, every week...*: Sử dụng hàng tuần.
  * *Yes, every day...*: Sử dụng hàng ngày trong công việc.
* **Biến 2: Mức độ quen thuộc với LLM (LLM Familiarity)**:
  * Phân cấp từ *Chưa từng nghe* $\rightarrow$ *Nghe sơ qua* $\rightarrow$ *Có một số kinh nghiệm* $\rightarrow$ *Sử dụng thường xuyên*.
* **Kết quả phân tích từ dữ liệu**:
  * Cột biểu đồ của nhóm **"Sử dụng hàng ngày (Every day)"** hoặc **"Sử dụng thường xuyên (Regularly)"** luôn có điểm số Mong muốn tự động hóa cao nhất (gần mức 4.0).
  * Cột biểu đồ của nhóm **"Chưa từng nghe/Chưa từng sử dụng"** có điểm số Mong muốn tự động hóa thấp nhất (dưới mức trung bình 3.0).

### C. Cách trả lời và giải thích với Thầy (Talking Points)
> *"Thưa thầy, phân tích này giúp giải quyết bài toán: **Làm sao để nhân viên sẵn sàng phối hợp với AI Agent?** Kết quả dữ liệu chỉ ra rằng: Càng sử dụng AI thường xuyên (hàng ngày/hàng tuần), người lao động càng muốn ứng dụng tự động hóa sâu hơn. Điều này chứng minh nỗi sợ bị AI thay thế sẽ giảm dần khi người lao động trực tiếp tương tác và thấy được giá trị của AI trong việc hỗ trợ họ. 
> Khuyến nghị của em là: Doanh nghiệp không nên áp đặt AI ngay lập tức dưới dạng tự động hóa bắt buộc, mà trước tiên cần tổ chức các buổi đào tạo, cấp tài khoản dùng thử để nhân viên nâng cao mức độ quen thuộc (Familiarity) và tần suất sử dụng (Usage). Khi rào cản e ngại công nghệ bị phá vỡ, việc triển khai AI Agent ở các cấp độ tự chủ cao hơn (như HAS H4, H5) sẽ diễn ra vô cùng thuận lợi."*

---

## 4. TÓM TẮT GIÁ TRỊ HỌC THUẬT CHO TOÀN BỘ ĐỀ TÀI

Việc đưa hai chỉ số này vào đề tài giúp nâng tầm sản phẩm từ một ứng dụng thống kê thông thường thành một nghiên cứu mang tính khoa học liên ngành (Kết hợp giữa **Computer Science**, **Data Science** và **Behavioral Science**):
* **Tính mới (Novelty)**: Không đi theo lối mòn chỉ đánh giá xem AI "khôn" đến mức nào, mà đánh giá mức độ **"Sẵn sàng thích ứng" (Readiness & Outlook)** của hệ sinh thái con người xung quanh AI.
* **Tính thực tiễn (Practicality)**: Cung cấp cho các nhà quản trị doanh nghiệp và kỹ sư hệ thống một bộ tiêu chí cụ thể để thiết kế công việc (Job Design) và quản trị thay đổi (Change Management) khi tích hợp AI vào quy trình sản xuất thực tế.
