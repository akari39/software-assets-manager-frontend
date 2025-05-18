export const SOFTWARE_INFO_STATUS = {
  0: "操作系统",
  1: "办公",
  2: "开发",
  3: "设计",
  4: "流媒体访问许可",
  5: "其他",
};
export default class SoftwareInfo {
  constructor(data) {
    this.softwareInfoName = data.SoftwareInfoName;
    this.softwareInfoType = data.SoftwareInfoType;
    this.softwareInfoMatchRule = data.SoftwareInfoMatchRule;
    this.softwareInfoID = data.SoftwareInfoID;
  }

  toJson() {
    return {
      SoftwareInfoName: this.softwareInfoName,
      SoftwareInfoType: this.softwareInfoType,
      SoftwareInfoMatchRule: this.softwareInfoMatchRule,
      SoftwareInfoID: this.softwareInfoID,
    };
  }

    get displaySoftwareInfoType() {
    const typeMap = SOFTWARE_INFO_STATUS;
    return typeMap[this.softwareInfoType] || "未知";
  }

  static fromArray(dataArray) {
    return dataArray.map(data => new SoftwareInfo(data));
  }
}
