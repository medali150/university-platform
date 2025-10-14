'use client';

import React from 'react';
import DepartmentHeadScheduleCreator from '@/components/department-head/schedule-creator';

const DepartmentHeadSchedulePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <DepartmentHeadScheduleCreator />
    </div>
  );
};

export default DepartmentHeadSchedulePage;