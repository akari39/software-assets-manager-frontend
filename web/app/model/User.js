import Employee from "@/app/model/Employee";
export default class User {
  constructor(data) {
    this.employee_id = data.employee_id;
    this.permissions = data.permissions;
    this.status = data.status;
    this.user_id = data.user_id;
    this.employee = data.employee ? new Employee(data.employee) : null;
  }

  toJson() {
    return {
      employee_id: this.employee_id,
      permissions: this.permissions,
      status: this.status,
      user_id: this.user_id,
      employee: this.employee ? this.employee.toJson() : null,
    };
  }

  /**
   * 将原始数组转换为 User 实例数组
   * @param {Array} dataArray
   * @returns {User[]}
   */
  static fromArray(dataArray) {
    return dataArray.map(item => new User(item));
  }
}
