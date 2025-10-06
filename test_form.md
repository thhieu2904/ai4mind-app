## 📝 **Thiết kế Bảng hỏi Đánh giá Ứng dụng AI4Mind**

### **Tiêu đề:** Khảo sát Trải nghiệm Ứng dụng Hỗ trợ Sức khỏe Tinh thần AI4Mind

**Mô tả:**
_Cảm ơn bạn đã dành thời gian trải nghiệm AI4Mind! Những đóng góp của bạn sẽ giúp chúng tôi cải thiện và phát triển ứng dụng tốt hơn. Vui lòng trả lời các câu hỏi dưới đây một cách khách quan nhất._

---

### **Phần 1: Thông tin chung**

Phần này giúp chúng tôi hiểu rõ hơn về người dùng. Mọi thông tin đều được bảo mật.

1. **Bạn biết đến AI4Mind qua kênh nào?**
   - [ ] Bạn bè giới thiệu
   - [ ] Mạng xã hội (Facebook, TikTok,...)
   - [ ] Trường học/Giảng viên
   - [ ] Tìm kiếm trên Google/App Store
   - [ ] Khác: (Vui lòng ghi rõ)
2. **Bạn đã sử dụng ứng dụng trong bao lâu?**
   - [ ] Mới dùng thử hôm nay
   - [ ] Vài ngày
   - [ ] Hơn 1 tuần
   - [ ] Hơn 1 tháng
3. **Tần suất sử dụng của bạn?**
   - [ ] Hàng ngày
   - [ ] Vài lần một tuần
   - [ ] Mỗi tuần một lần
   - [ ] Hiếm khi

---

### **Phần 2: Trải nghiệm và Giao diện người dùng (UI/UX)**

Đánh giá theo thang điểm từ 1 (Rất không hài lòng) đến 5 (Rất hài lòng).

| Tiêu chí                                                               | 1   | 2   | 3   | 4   | 5   |
| ---------------------------------------------------------------------- | --- | --- | --- | --- | --- |
| **Giao diện**của ứng dụng có dễ nhìn và thân thiện không?              | ⚫  | ⚫  | ⚫  | ⚫  | ⚫  |
| **Bố cục**các tính năng có dễ tìm và dễ sử dụng không?                 | ⚫  | ⚫  | ⚫  | ⚫  | ⚫  |
| **Tốc độ phản hồi**của ứng dụng có nhanh không?                        | ⚫  | ⚫  | ⚫  | ⚫  | ⚫  |
| **Màu sắc và hình ảnh**trong ứng dụng có tạo cảm giác thoải mái không? | ⚫  | ⚫  | ⚫  | ⚫  | ⚫  |

Xuất sang Trang tính

---

### **Phần 3: Đánh giá các Tính năng chính**

Dựa trên các tính năng cốt lõi được thể hiện trong `README.md` và mã nguồn frontend.

#### **3.1. Tính năng "Trắc nghiệm Sức khỏe" (GAD-7)**

1. **Bạn có thấy bộ câu hỏi GAD-7 dễ hiểu không?**
   - [ ] Rất dễ hiểu
   - [ ] Dễ hiểu
   - [ ] Bình thường
   - [ ] Khó hiểu
   - [ ] Rất khó hiểu
2. **Kết quả và giải thích sau bài trắc nghiệm có hữu ích cho bạn không?**
   - (Thang điểm 1-5: Hoàn toàn không hữu ích -> Rất hữu ích)
3. **Các khuyến nghị mà AI đưa ra sau bài trắc nghiệm có phù hợp và thiết thực không?**
   - (Thang điểm 1-5: Hoàn toàn không phù hợp -> Rất phù hợp)

#### **3.2. Tính năng "Ghi âm & Phân tích Giọng nói"**

1. **Hướng dẫn ghi âm và các câu hỏi gợi ý có giúp bạn dễ dàng chia sẻ hơn không?**
   - [ ] Rất hữu ích
   - [ ] Hữu ích
   - [ ] Không ảnh hưởng nhiều
   - [ ] Không hữu ích
2. **Bạn có tin tưởng vào kết quả phân tích cảm xúc qua giọng nói không?**
   - (Thang điểm 1-5: Hoàn toàn không tin tưởng -> Rất tin tưởng)
3. **Bạn có lo ngại về quyền riêng tư khi sử dụng tính năng này không?**
   - [ ] Có, tôi rất lo ngại
   - [ ] Có một chút lo ngại
   - [ ] Không, tôi tin tưởng ứng dụng

#### **3.3. Tính năng "Thống kê Sức khỏe"**

1. **Các biểu đồ (Xu hướng điểm, Phân bố mức độ) có trực quan và dễ hiểu không?** (Tham khảo `ScoreTrendChart.tsx` và `SeverityDistributionChart.tsx`)
   - [ ] Có, rất trực quan
   - [ ] Tương đối dễ hiểu
   - [ ] Hơi khó hiểu, cần cải thiện
2. **Thông tin về "Điểm trung bình", "Điểm gần nhất" và "Xu hướng" có hữu ích cho việc theo dõi sức khỏe tinh thần của bạn không?**
   - (Thang điểm 1-5: Hoàn toàn không hữu ích -> Rất hữu ích)

#### **3.4. Tính năng "Tìm kiếm Hỗ trợ"**

1. **Bạn đã thử tính năng nào trong mục "Tìm kiếm hỗ trợ"? (chọn nhiều)**
   - [ ] Trò chuyện với AI
   - [ ] Tìm kiếm chuyên gia tâm lý
   - [ ] Tìm trung tâm y tế gần nhất
   - [ ] Tôi chưa thử tính năng nào
2. **(Nếu đã dùng) Đánh giá mức độ hữu ích của tính năng "Trò chuyện với AI":**
   - (Thang điểm 1-5)
3. **(Nếu đã dùng) Bản đồ các trung tâm y tế có dễ sử dụng và thông tin có chính xác không?**
   - (Thang điểm 1-5)

---

### **Phần 4: Đóng góp & Ý kiến khác**

1. **Tính năng nào bạn thích nhất ở AI4Mind và tại sao?**
   - (Câu trả lời tự luận)
2. **Theo bạn, AI4Mind cần cải thiện điều gì nhất?**
   - (Câu trả lời tự luận)
3. **Bạn có muốn đề xuất thêm tính năng nào mới cho ứng dụng không?**
   - (Câu trả lời tự luận)
4. **Bạn có sẵn sàng giới thiệu AI4Mind cho bạn bè hoặc người thân không?**
   - (Thang điểm 1-10: Chắc chắn không -> Chắc chắn có)

**Lời cảm ơn:**
_Một lần nữa, chúng tôi chân thành cảm ơn những đóng góp quý giá của bạn!_
