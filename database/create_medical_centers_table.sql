-- =====================================================
-- TẠO BẢNG MEDICAL_CENTERS
-- Table lưu thông tin các trung tâm y tế hỗ trợ sức khỏe tâm thần
-- =====================================================

CREATE TABLE IF NOT EXISTS medical_centers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(255),
    services TEXT[] DEFAULT ARRAY[]::TEXT[],
    opening_hours JSONB DEFAULT '{}'::jsonb,
    description TEXT,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TẠO INDEXES ĐỂ TỐI ƯU TÌM KIẾM
-- =====================================================

-- Index cho tìm kiếm theo tọa độ (spatial search)
CREATE INDEX IF NOT EXISTS idx_medical_centers_location 
ON medical_centers (latitude, longitude);

-- Index cho tìm kiếm theo services
CREATE INDEX IF NOT EXISTS idx_medical_centers_services 
ON medical_centers USING GIN(services);

-- Index cho tìm kiếm theo tên
CREATE INDEX IF NOT EXISTS idx_medical_centers_name 
ON medical_centers (name);

-- =====================================================
-- INSERT SAMPLE DATA - TP.HỒ CHÍ MINH
-- =====================================================

INSERT INTO medical_centers (name, address, latitude, longitude, phone, email, website, services, opening_hours, description) VALUES

-- 1. Bệnh viện Tâm thần TP.HCM
(
    'Bệnh viện Tâm thần Thành phố Hồ Chí Minh',
    '766 Võ Văn Kiệt, Phường 1, Quận 5, TP. Hồ Chí Minh',
    10.7544,
    106.6605,
    '028.3855.4269',
    'info@tamthan-tphcm.com.vn',
    'http://www.tamthan-tphcm.com.vn',
    ARRAY['Khám Tâm thần', 'Điều trị Nội trú', 'Tư vấn Tâm lý', 'Trị liệu Tâm lý', 'Điều trị Nghiện'],
    '{
        "monday": "07:00-16:30",
        "tuesday": "07:00-16:30", 
        "wednesday": "07:00-16:30",
        "thursday": "07:00-16:30",
        "friday": "07:00-16:30",
        "saturday": "07:00-11:30",
        "sunday": "Closed"
    }'::jsonb,
    'Bệnh viện chuyên khoa tâm thần hàng đầu TP.HCM, có đội ngũ bác sĩ giỏi và trang thiết bị hiện đại'
),

-- 2. Trung tâm Tư vấn Tâm lý UMC
(
    'Trung tâm Tư vấn Tâm lý UMC',
    '203 Nguyễn Văn Thủ, Phường Đa Kao, Quận 1, TP. Hồ Chí Minh',
    10.7879,
    106.6947,
    '028.3824.3757',
    'contact@umc.edu.vn',
    'https://umc.edu.vn',
    ARRAY['Tư vấn Tâm lý', 'Trị liệu Nhóm', 'Đánh giá Tâm lý', 'Coaching'],
    '{
        "monday": "08:00-20:00",
        "tuesday": "08:00-20:00",
        "wednesday": "08:00-20:00",
        "thursday": "08:00-20:00",
        "friday": "08:00-20:00",
        "saturday": "08:00-17:00",
        "sunday": "08:00-12:00"
    }'::jsonb,
    'Trung tâm tư vấn tâm lý chuyên nghiệp, phù hợp với sinh viên và người trẻ'
),

-- 3. Phòng khám Tâm thần - Bệnh viện Đại học Y Dược
(
    'Phòng khám Tâm thần - Bệnh viện Đại học Y Dược TP.HCM',
    '215 Hồng Bàng, Phường 11, Quận 5, TP. Hồ Chí Minh',
    10.7567,
    106.6533,
    '028.3855.4269',
    'info@bvdaihoc.com.vn',
    'http://benhviendaihoc.vn',
    ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Ngoại trú'],
    '{
        "monday": "07:00-17:00",
        "tuesday": "07:00-17:00",
        "wednesday": "07:00-17:00",
        "thursday": "07:00-17:00",
        "friday": "07:00-17:00",
        "saturday": "07:00-12:00",
        "sunday": "Closed"
    }'::jsonb,
    'Phòng khám tại bệnh viện uy tín, có đội ngũ giảng viên và bác sĩ giàu kinh nghiệm'
),

-- 4. Trung tâm Tâm lý Trị liệu Mindfulness
(
    'Trung tâm Tâm lý Trị liệu Mindfulness',
    '20 Nguyễn Thị Minh Khai, Phường Đa Kao, Quận 1, TP. Hồ Chí Minh',
    10.7905,
    106.6949,
    '028.3824.8888',
    'hello@mindfulness.vn',
    'https://mindfulness.vn',
    ARRAY['Tư vấn Tâm lý', 'Thiền định', 'Quản lý Căng thẳng', 'Yoga trị liệu'],
    '{
        "monday": "09:00-21:00",
        "tuesday": "09:00-21:00",
        "wednesday": "09:00-21:00",
        "thursday": "09:00-21:00",
        "friday": "09:00-21:00",
        "saturday": "09:00-18:00",
        "sunday": "09:00-18:00"
    }'::jsonb,
    'Trung tâm chuyên về mindfulness và quản lý căng thẳng cho sinh viên và người đi làm'
),

-- 5. Bệnh viện Nhi đồng 1 - Khoa Tâm lý
(
    'Bệnh viện Nhi đồng 1 - Khoa Tâm lý',
    '341 Sư Vạn Hạnh, Phường 12, Quận 10, TP. Hồ Chí Minh',
    10.7731,
    106.6646,
    '028.3865.2562',
    'bvnd1@hcm.vnn.vn',
    'https://benhviennhidong1.org.vn',
    ARRAY['Tư vấn Tâm lý trẻ em', 'Đánh giá Phát triển', 'Trị liệu Hành vi'],
    '{
        "monday": "07:00-16:00",
        "tuesday": "07:00-16:00",
        "wednesday": "07:00-16:00",
        "thursday": "07:00-16:00",
        "friday": "07:00-16:00",
        "saturday": "07:00-11:00",
        "sunday": "Closed"
    }'::jsonb,
    'Chuyên về tâm lý trẻ em và thanh thiếu niên, phù hợp với sinh viên năm nhất'
);

-- =====================================================
-- INSERT SAMPLE DATA - TRÀ VINH
-- =====================================================

INSERT INTO medical_centers (name, address, latitude, longitude, phone, email, services, opening_hours, description) VALUES

-- 6. Bệnh viện Đa khoa Trà Vinh
(
    'Bệnh viện Đa khoa Trà Vinh',
    'Số 1, Đường Nguyễn Đáng, Phường 4, TP. Trà Vinh',
    9.9345,
    106.3420,
    '0294.3862.901',
    'bvdktravinh@travinh.gov.vn',
    ARRAY['Khoa Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Nội trú', 'Khám Ngoại trú'],
    '{
        "monday": "07:00-17:00",
        "tuesday": "07:00-17:00",
        "wednesday": "07:00-17:00",
        "thursday": "07:00-17:00",
        "friday": "07:00-17:00",
        "saturday": "07:00-12:00",
        "sunday": "Cấp cứu 24/7"
    }'::jsonb,
    'Bệnh viện đa khoa tỉnh có khoa tâm thần, phục vụ người dân Trà Vinh và các tỉnh lân cận'
);

-- =====================================================
-- THÊM DỮ LIỆU CÁC TỈNH KHÁC (OPTIONAL - ĐỂ SCALE)
-- =====================================================

INSERT INTO medical_centers (name, address, latitude, longitude, phone, services, opening_hours, description) VALUES

-- 7. Cần Thơ
(
    'Bệnh viện Tâm thần Cần Thơ',
    'Số 8, Đường 3 Tháng 2, Quận Ninh Kiều, TP. Cần Thơ',
    10.0344,
    105.7720,
    '0292.3822.076',
    ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Nội trú', 'Điều trị Ngoại trú'],
    '{
        "monday": "07:00-16:30",
        "tuesday": "07:00-16:30",
        "wednesday": "07:00-16:30",
        "thursday": "07:00-16:30",
        "friday": "07:00-16:30",
        "saturday": "07:00-11:30",
        "sunday": "Closed"
    }'::jsonb,
    'Bệnh viện chuyên khoa tâm thần khu vực Đồng bằng Sông Cửu Long'
),

-- 8. Đà Nẵng
(
    'Bệnh viện Tâm thần Đà Nẵng',
    '193 Điện Biên Phủ, Quận Thanh Khê, TP. Đà Nẵng',
    16.0672,
    108.1974,
    '0236.3821.135',
    ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Nội trú', 'Cộng đồng'],
    '{
        "monday": "07:00-16:30",
        "tuesday": "07:00-16:30",
        "wednesday": "07:00-16:30",
        "thursday": "07:00-16:30",
        "friday": "07:00-16:30",
        "saturday": "07:00-11:30",
        "sunday": "Closed"
    }'::jsonb,
    'Bệnh viện tâm thần miền Trung, phục vụ Đà Nẵng và các tỉnh lân cận'
),

-- 9. Vũng Tàu
(
    'Bệnh viện Tâm thần Bà Rịa - Vũng Tàu',
    'Số 88, Đường 30 Tháng 4, Phường Thắng Tam, TP. Vũng Tàu',
    10.3460,
    107.0843,
    '0254.3836.248',
    ARRAY['Khám Tâm thần', 'Tư vấn Tâm lý', 'Điều trị Nội trú', 'Điều trị Nghiện'],
    '{
        "monday": "07:00-16:30",
        "tuesday": "07:00-16:30",
        "wednesday": "07:00-16:30",
        "thursday": "07:00-16:30",
        "friday": "07:00-16:30",
        "saturday": "07:00-11:30",
        "sunday": "Closed"
    }'::jsonb,
    'Bệnh viện chuyên khoa tâm thần tỉnh Bà Rịa - Vũng Tàu'
),

-- 10. Long An
(
    'Bệnh viện Đa khoa Long An - Khoa Tâm thần',
    'Số 1, Đường Hùng Vương, Phường 2, TP. Tân An, Long An',
    10.5359,
    106.4104,
    '0272.3852.469',
    ARRAY['Khoa Tâm thần', 'Tư vấn Tâm lý', 'Khám Ngoại trú'],
    '{
        "monday": "07:00-17:00",
        "tuesday": "07:00-17:00",
        "wednesday": "07:00-17:00",
        "thursday": "07:00-17:00",
        "friday": "07:00-17:00",
        "saturday": "07:00-12:00",
        "sunday": "Cấp cứu 24/7"
    }'::jsonb,
    'Khoa tâm thần tại bệnh viện đa khoa tỉnh Long An, gần TP.HCM'
);

-- =====================================================
-- THÊM TRIGGER TỰ ĐỘNG CẬP NHẬT updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_medical_centers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_medical_centers_updated_at
    BEFORE UPDATE ON medical_centers
    FOR EACH ROW
    EXECUTE FUNCTION update_medical_centers_updated_at();

-- =====================================================
-- KẾT THÚC MIGRATION
-- =====================================================

-- Verify data
SELECT COUNT(*) as total_centers FROM medical_centers;
SELECT name, address FROM medical_centers ORDER BY name;
