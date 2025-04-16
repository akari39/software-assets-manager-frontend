export class SoftwareInfo {
  constructor(data) {
    this.softwareInfoName = data.SoftwareInfoName;
    this.softwareInfoType = data.SoftwareInfoType;
    this.softwareInfoMatchRule = data.SoftwareInfoMatchRule;
    this.softwareInfoID = data.SoftwareInfoID;
  }
}

export const LICENSE_STATUS = {
  0: "已领用",
  1: "未领用",
};

// Main class for SoftwareLicense
export default class SoftwareLicense {
  constructor(data) {
    this.softwareInfoID = data.SoftwareInfoID;
    this.licenseType = data.LicenseType;
    this.licenseStatus = data.LicenseStatus;
    this.licenseKey = data.LicenseKey;
    this.licenseExpiredDate = data.LicenseExpiredDate;
    this.lvLimit = data.LvLimit;
    this.remark = data.Remark;
    this.licenseID = data.LicenseID;
    this.createTime = data.CreateTime;
    this.lastUpdateTime = data.LastUpdateTime;
    this.softwareInfo = data.software_info ? new SoftwareInfo(data.software_info) : null;
  }

  // Getter: format the license expired date as a human-readable string
  get formattedLicenseExpiredDate() {
    if (!this.licenseExpiredDate) return "未设置";
    const date = new Date(this.licenseExpiredDate);
    return date.toLocaleString();
  }

  // Getter: format the last update time as a human-readable string
  get formattedLastUpdateTime() {
    if (!this.lastUpdateTime) return "未设置";
    const date = new Date(this.lastUpdateTime);
    return date.toLocaleString();
  }

  // Getter: map numeric license status to human-readable text
  get displayLicenseStatus() {
    const statusMap = LICENSE_STATUS;
    return statusMap[this.licenseStatus] || "未知";
  }

  // Factory method for converting an array of raw license objects into SoftwareLicense instances
  static fromArray(dataArray) {
    return dataArray.map(data => new SoftwareLicense(data));
  }
}