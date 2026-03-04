export const SAMPLE_DATA = {
  teachers: [
    { id: 'T1', name: 'Dr. Sharma', subjects: ['S1', 'S2'] },
    { id: 'T2', name: 'Prof. Kumar', subjects: ['S3', 'S4'] },
    { id: 'T3', name: 'Dr. Verma', subjects: ['S5', 'S1'] },
    { id: 'T4', name: 'Prof. Singh', subjects: ['S2', 'S6'] },
    { id: 'T5', name: 'Dr. Patel', subjects: ['S3', 'S5'] },
  ],
  rooms: [
    { id: 'R1', name: 'Room 101', capacity: 60, type: 'lecture_hall' },
    { id: 'R2', name: 'Room 102', capacity: 60, type: 'lecture_hall' },
    { id: 'R3', name: 'Lab A', capacity: 60, type: 'lab' },
    { id: 'R4', name: 'Lab B', capacity: 60, type: 'lab' },
  ],
  subjects: [
    { id: 'S1', name: 'Data Structures', code: 'CS301', lectures_per_week: 4, requires_lab: true, lab_hours: 1 },
    { id: 'S2', name: 'DBMS', code: 'CS302', lectures_per_week: 3, requires_lab: true, lab_hours: 1 },
    { id: 'S3', name: 'Operating Systems', code: 'CS303', lectures_per_week: 4, requires_lab: false, lab_hours: 0 },
    { id: 'S4', name: 'Computer Networks', code: 'CS304', lectures_per_week: 3, requires_lab: true, lab_hours: 1 },
    { id: 'S5', name: 'Mathematics III', code: 'MA301', lectures_per_week: 4, requires_lab: false, lab_hours: 0 },
    { id: 'S6', name: 'Technical English', code: 'HU301', lectures_per_week: 2, requires_lab: false, lab_hours: 0 },
  ],
  student_groups: [
    { id: 'G1', name: 'CSE-3A', strength: 55, subjects: ['S1', 'S2', 'S3', 'S5', 'S6'] },
    { id: 'G2', name: 'CSE-3B', strength: 50, subjects: ['S1', 'S3', 'S4', 'S5', 'S6'] },
  ],
  working_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  periods_per_day: 6,
  constraints: {
    teacher_preferences: {},
    max_classes_per_day_per_teacher: 4,
    max_classes_per_day_per_group: 5,
    lunch_break_after_period: 3,
  },
  timeout: 30,
};

export const EXAM_SAMPLE_DATA = {
  teachers: [
    { id: 'T1', name: 'Dr. Sharma (Invigilator)', subjects: ['S1', 'S2', 'S3'] },
    { id: 'T2', name: 'Prof. Kumar (Invigilator)', subjects: ['S4', 'S5'] },
  ],
  rooms: [
    { id: 'R1', name: 'Exam Hall A', capacity: 120, type: 'lecture_hall' },
    { id: 'R2', name: 'Exam Hall B', capacity: 120, type: 'lecture_hall' },
    { id: 'R3', name: 'Exam Hall C', capacity: 80, type: 'lecture_hall' },
  ],
  subjects: [
    { id: 'S1', name: 'Data Structures', code: 'CS301', lectures_per_week: 1, requires_lab: false, lab_hours: 0 },
    { id: 'S2', name: 'DBMS', code: 'CS302', lectures_per_week: 1, requires_lab: false, lab_hours: 0 },
    { id: 'S3', name: 'Operating Systems', code: 'CS303', lectures_per_week: 1, requires_lab: false, lab_hours: 0 },
    { id: 'S4', name: 'Computer Networks', code: 'CS304', lectures_per_week: 1, requires_lab: false, lab_hours: 0 },
    { id: 'S5', name: 'Mathematics III', code: 'MA301', lectures_per_week: 1, requires_lab: false, lab_hours: 0 },
  ],
  student_groups: [
    { id: 'G1', name: 'CSE-3A', strength: 55, subjects: ['S1', 'S2', 'S3', 'S5'] },
    { id: 'G2', name: 'CSE-3B', strength: 50, subjects: ['S1', 'S3', 'S4', 'S5'] },
  ],
  working_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  periods_per_day: 3,
  constraints: {
    teacher_preferences: {},
    max_classes_per_day_per_teacher: 2,
    max_classes_per_day_per_group: 1,
    lunch_break_after_period: 2,
  },
  timeout: 30,
};
