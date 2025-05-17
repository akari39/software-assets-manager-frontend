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

  static fromArray(dataArray) {
    return dataArray.map(data => new SoftwareInfo(data));
  }
}
