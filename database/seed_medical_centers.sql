-- Seed data: Trung tâm y tế / bệnh viện hỗ trợ sức khỏe tâm thần tại Việt Nam
-- Bao gồm các thành phố lớn: Hà Nội, TP.HCM, Đà Nẵng, Cần Thơ, Huế

INSERT INTO medical_centers (id, name, address, description, latitude, longitude, phone, email, website, services, opening_hours, image_url)
VALUES

-- ===================== HÀ NỘI =====================


-- ===================== TP. HỒ CHÍ MINH =====================

(gen_random_uuid(),
 'Bệnh viện Tâm thần TP. Hồ Chí Minh',
 '766 Võ Văn Kiệt, Phường 1, Quận 5, TP. Hồ Chí Minh',
 'Bệnh viện tâm thần lớn nhất khu vực phía Nam, chuyên điều trị các rối loạn tâm thần nặng, cai nghiện và phục hồi chức năng tâm thần.',
 10.75690000, 106.66330000,
 '028 3835 5171', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Cai nghiện Ma túy', 'Phục hồi Chức năng', 'Điều trị Trầm cảm', 'Tư vấn Tâm lý'],
 '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:30","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Viện Tâm lý & Tâm thần Thực hành - BV Chợ Rẫy',
 '201B Nguyễn Chí Thanh, Quận 5, TP. Hồ Chí Minh',
 'Đơn vị tâm thần của Bệnh viện Chợ Rẫy, một trong những bệnh viện lớn nhất Việt Nam, cung cấp dịch vụ khám và tư vấn sức khỏe tâm thần toàn diện.',
 10.75690000, 106.65880000,
 '028 3855 4137', NULL, 'http://choray.vn',
 ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Lo âu', 'Điều trị Trầm cảm', 'Rối loạn Stress Sau Chấn thương (PTSD)'],
 '{"monday":"07:00-17:00","tuesday":"07:00-17:00","wednesday":"07:00-17:00","thursday":"07:00-17:00","friday":"07:00-17:00","saturday":"07:00-12:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Trung tâm Sức khỏe Tâm thần Sài Gòn',
 '116 Nguyễn Đình Chiểu, Quận 3, TP. Hồ Chí Minh',
 'Trung tâm chuyên sâu về sức khỏe tâm thần tại TP.HCM, cung cấp dịch vụ tư vấn, trị liệu tâm lý cá nhân và nhóm cho mọi lứa tuổi.',
 10.78540000, 106.68830000,
 '028 3930 5678', 'info@saigonmentalhealth.vn', NULL,
 ARRAY['Tư vấn Tâm lý', 'Liệu pháp Nhận thức Hành vi (CBT)', 'Tư vấn Trẻ em & Thiếu niên', 'Tư vấn Cặp đôi', 'Trị liệu Nhóm', 'Thiền & Mindfulness'],
 '{"monday":"08:00-20:00","tuesday":"08:00-20:00","wednesday":"08:00-20:00","thursday":"08:00-20:00","friday":"08:00-20:00","saturday":"08:00-17:00","sunday":"09:00-15:00"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'BV Đại học Y Dược TP.HCM - Khoa Tâm thần Kinh',
 '215 Hồng Bàng, Quận 5, TP. Hồ Chí Minh',
 'Khoa Tâm thần Kinh của Bệnh viện Đại học Y Dược TP.HCM, kết hợp điều trị tâm thần và thần kinh với đội ngũ chuyên gia đầu ngành.',
 10.75410000, 106.66280000,
 '028 3855 4269', NULL, 'http://bvdaihocyduoc.com.vn',
 ARRAY['Khám Tâm thần', 'Khám Thần kinh', 'Tư vấn Tâm lý', 'Điều trị Mất ngủ', 'Rối loạn Lo âu', 'Điều trị Trầm cảm'],
 '{"monday":"07:00-17:00","tuesday":"07:00-17:00","wednesday":"07:00-17:00","thursday":"07:00-17:00","friday":"07:00-17:00","saturday":"07:00-12:00","sunday":"Đóng cửa"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Phòng khám Tâm lý Mindcare',
 '95 Trần Quốc Thảo, Quận 3, TP. Hồ Chí Minh',
 'Phòng khám tâm lý hiện đại, thân thiện tại trung tâm TP.HCM. Đội ngũ chuyên gia tâm lý được đào tạo quốc tế, tập trung vào sức khỏe tâm thần thanh niên.',
 10.78280000, 106.69030000,
 '028 7308 5566', 'hello@mindcare.vn', 'https://mindcare.vn',
 ARRAY['Tư vấn Tâm lý', 'Liệu pháp CBT', 'Tư vấn Online', 'Tư vấn Học đường', 'Quản lý Stress', 'Hỗ trợ Sức khỏe Tâm thần Thanh niên'],
 '{"monday":"09:00-21:00","tuesday":"09:00-21:00","wednesday":"09:00-21:00","thursday":"09:00-21:00","friday":"09:00-21:00","saturday":"09:00-18:00","sunday":"10:00-16:00"}'::jsonb,
 NULL),

-- ===================== ĐÀ NẴNG =====================


-- ===================== CẦN THƠ =====================

(gen_random_uuid(),
 'Bệnh viện Tâm thần Cần Thơ',
 '1 Nguyễn Văn Cừ, Ninh Kiều, Cần Thơ',
 'Bệnh viện tâm thần khu vực đồng bằng sông Cửu Long, phục vụ nhu cầu khám và điều trị bệnh tâm thần của hơn 20 triệu dân miền Tây Nam Bộ.',
 10.03720000, 105.78380000,
 '0292 3831 058', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Phục hồi Chức năng', 'Điều trị Trầm cảm', 'Cai nghiện'],
 '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

-- ===================== HẢI PHÒNG =====================

(gen_random_uuid(),
 'Bệnh viện Tâm thần Hải Phòng',
 '135 Lê Lai, Ngô Quyền, Hải Phòng',
 'Bệnh viện tâm thần tuyến tỉnh/thành phố tại Hải Phòng, cung cấp đầy đủ các dịch vụ khám, chữa bệnh tâm thần cho người dân vùng duyên hải Bắc Bộ.',
 20.85380000, 106.68380000,
 '0225 3842 271', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Phục hồi Chức năng', 'Điều trị Trầm cảm'],
 '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

-- ===================== TRÀ VINH =====================

(gen_random_uuid(),
 'Bệnh viện Tâm thần Trà Vinh',
 '6 Nguyễn Đáng, Phường 1, TP. Trà Vinh, Trà Vinh',
 'Bệnh viện tâm thần tỉnh Trà Vinh, cung cấp dịch vụ khám chữa bệnh tâm thần cho người dân tỉnh Trà Vinh và các vùng lân cận đồng bằng sông Cửu Long.',
 9.93480000, 106.34490000,
 '0294 3858 016', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Phục hồi Chức năng', 'Điều trị Trầm cảm', 'Cai nghiện'],
 '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Bệnh viện Đa khoa Trà Vinh',
 '399 Đ. Nguyễn Đáng, Khóm 10, Trà Vinh, Vietnam',
 'Bệnh viện đa khoa tỉnh Trà Vinh, cung cấp dịch vụ khám và điều trị đa chuyên khoa cho người dân địa phương.',
 9.93383610, 106.32385900,
 '0294 3862 553', NULL, 'http://benhvientravinh.com.vn',
 ARRAY['Khám Tổng quát', 'Khám Nội', 'Khám Ngoại', 'Cấp cứu 24/7', 'Khám Tâm thần', 'Khám Thần kinh'],
 '{"monday":"07:00-17:00","tuesday":"07:00-17:00","wednesday":"07:00-17:00","thursday":"07:00-17:00","friday":"07:00-17:00","saturday":"07:00-12:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Bệnh Viện Đa Khoa Minh Tâm',
 '36 Đ. Nguyễn Đáng, Phường 9, Trà Vinh, Vietnam',
 'Bệnh viện đa khoa Minh Tâm tại Trà Vinh, cung cấp dịch vụ khám chữa bệnh đa chuyên khoa.',
 9.92418240, 106.33753340,
 '0294 3850 665', NULL, 'http://minhtamhospital.com/',
 ARRAY['Khám Tổng quát', 'Khám Nội', 'Khám Ngoại', 'Cấp cứu 24/7', 'Khám Tâm thần', 'Tư vấn Tâm lý'],
 '{"monday":"00:00-23:59","tuesday":"00:00-23:59","wednesday":"00:00-23:59","thursday":"00:00-23:59","friday":"00:00-23:59","saturday":"00:00-23:59","sunday":"00:00-23:59"}'::jsonb,
 NULL),

-- ===================== VĨNH LONG =====================

(gen_random_uuid(),
 'Bệnh viện Tâm thần Vĩnh Long',
 '28 Phạm Thái Bường, Phường 4, TP. Vĩnh Long, Vĩnh Long',
 'Bệnh viện tâm thần tỉnh Vĩnh Long, là cơ sở điều trị tâm thần tuyến tỉnh phục vụ hơn 1 triệu dân Vĩnh Long và hỗ trợ các tỉnh lân cận khu vực đồng bằng.',
 10.25430000, 105.97280000,
 '0270 3823 016', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Phục hồi Chức năng', 'Điều trị Trầm cảm', 'Cai nghiện'],
 '{"monday":"07:00-16:30","tuesday":"07:00-16:30","wednesday":"07:00-16:30","thursday":"07:00-16:30","friday":"07:00-16:30","saturday":"07:00-11:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Bệnh viện Đa khoa Vĩnh Long - Khoa Thần kinh Tâm thần',
 '4 Hùng Vương, Phường 2, TP. Vĩnh Long, Vĩnh Long',
 'Khoa Thần kinh Tâm thần của Bệnh viện Đa khoa tỉnh Vĩnh Long, cung cấp dịch vụ chẩn đoán và điều trị chuyên khoa tâm thần - thần kinh chất lượng tại tỉnh.',
 10.25620000, 105.97130000,
 '0270 3822 494', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Khám Thần kinh', 'Tư vấn Tâm lý', 'Điều trị Trầm cảm', 'Rối loạn Lo âu', 'Rối loạn Giấc ngủ'],
 '{"monday":"07:00-17:00","tuesday":"07:00-17:00","wednesday":"07:00-17:00","thursday":"07:00-17:00","friday":"07:00-17:00","saturday":"07:00-12:00","sunday":"Cấp cứu 24/7"}'::jsonb,
 NULL),

(gen_random_uuid(),
 'Trung tâm Tư vấn Sức khỏe Tâm thần Vĩnh Long',
 '15 Trưng Nữ Vương, Phường 1, TP. Vĩnh Long, Vĩnh Long',
 'Trung tâm tư vấn sức khỏe tâm thần tại Vĩnh Long, chuyên hỗ trợ các vấn đề tâm lý cho thanh niên, sinh viên Đại học Cửu Long và người dân địa phương.',
 10.25180000, 105.97450000,
 '0270 3825 678', NULL, NULL,
 ARRAY['Tư vấn Tâm lý', 'Tư vấn Học đường', 'Tư vấn Gia đình', 'Quản lý Stress', 'Sức khỏe Tâm thần Cộng đồng'],
 '{"monday":"08:00-17:00","tuesday":"08:00-17:00","wednesday":"08:00-17:00","thursday":"08:00-17:00","friday":"08:00-17:00","saturday":"08:00-11:30","sunday":"Đóng cửa"}'::jsonb,
 NULL),

-- ===================== BÌNH DƯƠNG =====================

(gen_random_uuid(),
 'Trung tâm Sức khỏe Tâm thần Bình Dương',
 '552 Đại lộ Bình Dương, Thuận An, Bình Dương',
 'Trung tâm sức khỏe tâm thần hiện đại tại Bình Dương, phục vụ nhu cầu chăm sóc sức khỏe tâm thần cho người lao động và cư dân khu công nghiệp.',
 10.90580000, 106.72680000,
 '0274 3855 789', NULL, NULL,
 ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Tư vấn Stress Công việc', 'Điều trị Trầm cảm', 'Rối loạn Lo âu'],
 '{"monday":"07:30-17:00","tuesday":"07:30-17:00","wednesday":"07:30-17:00","thursday":"07:30-17:00","friday":"07:30-17:00","saturday":"07:30-12:00","sunday":"Đóng cửa"}'::jsonb,
 NULL)
ON CONFLICT DO NOTHING;
