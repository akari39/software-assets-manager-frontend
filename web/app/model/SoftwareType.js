export default class SoftwareType {
  static TYPE_MAP = {
    0: '操作系统授权',
    1: '办公类软件',
    2: '开发类软件',
    3: '设计类软件',
    4: '流媒体访问许可',
    5: '其他',
  };

  static getName(type) {
    const key = Number(type);
    return SoftwareType.TYPE_MAP.hasOwnProperty(key)
      ? SoftwareType.TYPE_MAP[key]
      : '未知';
  }

  toString() {
    return this.name;
  }
}