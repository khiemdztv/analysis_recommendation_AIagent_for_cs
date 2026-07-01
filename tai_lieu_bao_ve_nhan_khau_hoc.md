# 📘 TÀI LIỆU HƯỚNG DẪN BẢO VỆ & THUYẾT TRÌNH CHUYÊN SÂU
## Đề tài: Ảnh Hưởng Của Nhân Khoảg Học Đến Mong Muốn & An Ninh Việc Làm Trong Ngành IT

Tài liệu này được biên soạn để giúp bạn trình bày với giảng viên hướng dẫn (thầy cô) và các bạn cùng lớp một cách mạch lạc, nêu bật được **tính mới (novelty)**, **cơ sở khoa học (theoretical frameworks)** và **giá trị ứng dụng thực tiễn** của phân hệ này.

---

## 🛠️ PHẦN 1: TẠI SAO LẠI CÓ Ý TƯỞNG NÀY? (KHOẢNG TRỐNG NGHIÊN CỨU)

Khi đọc bài báo gốc **WORKBank (arXiv:2506.06576)**, chúng ta phát hiện ra **3 hạn chế cốt lõi** mà tác giả bài báo chưa giải quyết (đây chính là "khoảng trống nghiên cứu" để bạn ghi điểm với thầy cô):

1. **Nhân khẩu học bị "bỏ quên" trong phân tích trực quan**: 
   - Bài báo gốc thu thập đầy đủ tuổi, giới tính, học vấn, kinh nghiệm của người lao động nhưng **chỉ dùng làm biến kiểm soát (control variables)** trong mô hình hồi quy (Appendix B, Table 1). Tác giả coi lực lượng lao động là một khối đồng nhất và không hề trực quan hóa sự khác biệt giữa các nhóm.
2. **Chỉ số An ninh việc làm (Job Security) bị coi nhẹ**:
   - Tác giả chỉ viết đúng **1 câu duy nhất** trong toàn bộ bài báo về Job Security: *"correlation between automation desire and job security is negative (ρ = −0.22)"* (Section 3.2). Họ không hề phân tích nhóm người nào đang lo sợ nhất và tại sao họ lại sợ.
3. **Động cơ tự động hóa chỉ được phân tích ở mức toàn mẫu**:
   - Biểu đồ lý do muốn tự động hóa trong bài báo (Figure 4b) gộp chung tất cả mọi người lại (ví dụ: 69% chọn Giải phóng thời gian). Thực tế, lập trình viên lâu năm muốn tự động hóa vì lý do hoàn toàn khác với nhân viên support mới vào nghề.

👉 **Phát kiến của bạn**: Đưa **Con người (Worker-centric)** vào trung tâm của phân tích công nghệ. Chuyển đổi góc nhìn từ *"Tác vụ nào bị tự động hóa?"* sang *"Người lao động nào cần được hỗ trợ và hỗ trợ như thế nào?"*.

---

## 📈 PHẦN 2: LÀM RÕ 3 PHÁT KIẾN MỚI TRÊN BIỂU ĐỒ

### 1. Sự lệch pha giữa Mong muốn (Desire) và Lo ngại An ninh (Job Security)
*   **Cách phát hiện**: Gom nhóm dữ liệu IT theo từng biến nhân khẩu học và tính điểm trung bình (Thang đo 1-5).
*   **Hiện tượng thực tế**:
    *   *Theo Giới tính*: Nam giới muốn tự động hóa cao hơn Nữ, nhưng Nữ lại lo sợ mất việc hơn Nam.
    *   *Theo Học vị*: Người có trình độ Doctorate/PhD có mong muốn tự động hóa rất cao nhưng cũng lo sợ an ninh việc làm cao nhất.
*   **Giải thích khoa học**: Người có học vị cao nhận thức rất rõ sức mạnh của AI nên muốn dùng nó để giải phóng sức lao động (Desire cao), nhưng cũng chính vì hiểu rõ khả năng của AI nên họ ý thức được tính chất thay thế của công nghệ đối với các công việc phức tạp (Job Security thấp).

---

### 2. Ma Trận Sẵn Sàng Nhân Sự (Worker Readiness Matrix)
*   **Nguồn gốc ý tưởng**: Bài báo gốc có biểu đồ 4 phân vùng cho **tác vụ** (Task Readiness Matrix). Chúng ta áp dụng triết lý đó để phân loại **con người** bằng cách vẽ đồ thị Scatter 2 chiều: Trục X (Desire) và Trục Y (Job Security), lấy ngưỡng **3.0** (trung điểm thang đo) làm vạch chia 4 góc phần tư:

```
                  Lo ngại An ninh việc làm (Job Security Rating)
                                     5.0
                                      |
             🔴 Threatened Resistors   |   🟡 Anxious Innovators
             (Kháng cự — Cần hỗ trợ)  |   (Muốn nhưng sợ mất việc)
                                      |
  [Desire < 3.0] ---------------------+--------------------- [Desire >= 3.0]
  [Security >= 3.0]                   |                     [Security >= 3.0]
                                      |
             ⚪ Passive Observers      |   🟢 Ready Adopters
             (Thờ ơ — Cần training)   |   (Deploy ngay — Đại sứ AI)
                                      |
                                     1.0 ------------------- 5.0
                                              Mong muốn Tự động hóa (Desire)
```

*   **Ứng dụng Khung Lý Thuyết Quản trị thay đổi Prosci ADKAR®**:
    *   🟢 **Ready Adopters** (Desire ≥ 3, Security < 3): Đã vượt qua bước **A**wareness (Nhận thức) và **D**esire (Mong muốn). Tổ chức cần tập trung vào **K**nowledge (Đào tạo công cụ) và **A**bility (Cung cấp tài nguyên) để họ làm đại sứ AI dẫn dắt đội ngũ.
    *   🟡 **Anxious Innovators** (Desire ≥ 3, Security ≥ 3): Đã có **D**esire nhưng bị nghẽn ở bước hành động vì sợ mất việc. Ban lãnh đạo cần thực hiện **R**einforcement (Cam kết an toàn việc làm, không sa thải khi ứng dụng AI).
    *   ⚪ **Passive Observers** (Desire < 3, Security < 3): Bị nghẽn ngay từ bước **A**wareness. Cần tổ chức các buổi demo, workshop để họ thấy giá trị thực tế của AI.
    *   🔴 **Threatened Resistors** (Desire < 3, Security ≥ 3): Nhóm kháng cự mạnh nhất vì thiếu cả **A**, **D** và lo sợ mất sinh kế. Đây là nhóm cần ưu tiên hỗ trợ tâm lý, tái đào tạo chuyển đổi vai trò (Reskilling) nhiều nhất.

---

### 3. Phân Tích Động Cơ Tự Động Hóa theo Nhóm (Motivation Breakdown)
*   **Cách phát hiện**: Bóc tách 6 lý do muốn tự động hóa (Free Time, Repetitive, Human Error, Stress, Difficulty, Scale) theo từng nhóm nhân khẩu học.
*   **Ứng dụng Thuyết Tự Quyết (Self-Determination Theory - Deci & Ryan)**:
    Con người có 3 nhu cầu nội tại cơ bản:
    1.  **Autonomy (Sự tự chủ)**: Thể hiện qua lý do *Free Time (Giải phóng thời gian)* để tự quyết định công việc sáng tạo hơn.
    2.  **Competence (Tự tin vào năng lực)**: Thể hiện qua lý do *Giảm sai sót (Human Error)* hoặc *Việc quá khó (Difficulty)*.
    3.  **Relatedness (Mối quan hệ/Giảm áp lực)**: Thể hiện qua lý do *Giảm căng thẳng (Stress)*.
*   **Ý nghĩa thực tiễn**: Dữ liệu chứng minh các nhóm nhân khẩu học có động cơ khác nhau (Ví dụ: Nhóm tuổi trẻ muốn giải phóng thời gian để sáng tạo, trong khi nhóm lớn tuổi muốn giảm áp lực/stress công việc). Do đó, doanh nghiệp không thể dùng chung 1 thông điệp truyền thông khi áp dụng công nghệ mới.

---

## 🎯 PHẦN 3: KỊCH BẢN THUYẾT TRÌNH & BẢO VỆ TRƯỚC HỘI ĐỒNG (QUY TRÌNH 3 BƯỚC)

Khi thầy cô yêu cầu trình bày phần này, bạn có thể nói theo mạch sau:

### Bước 1: Đặt vấn đề & Nêu tính mới (Mở đầu cuốn hút)
> *"Thưa Thầy/Cô, trong bài báo gốc WORKBank, tác giả tập trung rất nhiều vào việc phân loại tác vụ (Tasks) xem tác vụ nào dễ bị tự động hóa. Tuy nhiên, họ bỏ qua một yếu tố vô cùng quan trọng: **Con người (Workers) - những người trực tiếp vận hành các tác vụ đó**. Do đó, em đã phát triển phân hệ nghiên cứu độc lập này để deep-dive vào khía cạnh nhân khẩu học và an ninh việc làm, nhằm giải quyết bài toán: **Làm sao để doanh nghiệp triển khai AI mà không gặp sự kháng cự từ nhân viên?**"*

### Bước 2: Trình bày dữ liệu trực quan & 3 phát kiến khoa học (Core)
*   **Bật biểu đồ Bar 1**: Chỉ ra sự lệch pha (Desire cao nhưng Security thấp ở một số nhóm như Doctorate hoặc Nữ giới).
*   **Bật biểu đồ Scatter Matrix**: Giải thích cách chia 4 vùng dựa trên điểm số thực tế. Nhấn mạnh việc chuyển đổi từ ma trận tác vụ của bài báo sang ma trận con người. Liên kết trực tiếp với mô hình quản trị thay đổi **ADKAR**.
*   **Bật biểu đồ Bar Động cơ**: Chứng minh động cơ của các nhóm có sự khác biệt rõ rệt (phương sai cao nhất nằm ở lý do nào) và đối chiếu với **Self-Determination Theory**.

### Bước 3: Đưa ra thông điệp kết luận (Take-away message)
> *"Kết luận lại, phân tích này giúp các nhà quản trị nhân sự (HR) không còn nhìn lực lượng lao động như một khối chung chung. Dựa vào Ma trận Sẵn sàng và Phân tích động cơ, doanh nghiệp có thể đưa ra **chương trình đào tạo và truyền thông cá nhân hóa** cho từng nhóm tuổi, trình độ học vấn hay giới tính. Đây là đóng góp thực tiễn vượt ra ngoài phạm vi học thuật của bài báo gốc."*

---

## 📚 TÀI LIỆU THAM KHẢO ACADEMIC (Để ghi vào slide/báo cáo)
1.  **Dữ liệu nguồn**: Bài báo khoa học *WORKBank: A Benchmark for Assessing the Impact of AI on IT Tasks* (arXiv:2506.06576).
2.  **Khung quản trị thay đổi**: Hiệp hội Quản trị Thay đổi Chuyên nghiệp (Prosci) - Mô hình ADKAR®.
3.  **Tâm lý học hành vi**: Deci, E. L., & Ryan, R. M. (1985). *Self-determination theory and active self-regulation*.
4.  **Báo cáo quốc tế**:
    *   **OECD (2024)**: *AI and the Future of Skills Volume 1* (Tác động bất cân xứng của AI lên các nhóm học vấn khác nhau).
    *   **ILO (2024)**: *Generative AI and Jobs: A global analysis of potential effects on job quantity and quality* (Sự ảnh hưởng đặc thù về giới tính đối với tự động hóa văn phòng và hỗ trợ).
