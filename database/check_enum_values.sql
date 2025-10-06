-- Kiểm tra enum userrole trong PostgreSQL có những giá trị nào

SELECT 
    e.enumlabel as enum_value,
    e.enumsortorder as sort_order
FROM pg_enum e
JOIN pg_type t ON e.enumtypid = t.oid
WHERE t.typname = 'userrole'
ORDER BY e.enumsortorder;

-- This will show all valid values for userrole enum
