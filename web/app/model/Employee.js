export default class Employee {
  constructor(data) {
    this.name = data.name;
    this.gender = data.gender;
    this.department = data.department;
    this.level = data.level;
    this.status = data.status;
    this.employee_id = data.employee_id;
  }

  toJson() {
    return {
      name: this.name,
      gender: this.gender,
      department: this.department,
      level: this.level,
      status: this.status,
      employee_id: this.employee_id,
    };
  }
}