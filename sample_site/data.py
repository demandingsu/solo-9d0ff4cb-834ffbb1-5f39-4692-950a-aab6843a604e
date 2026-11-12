"""示例公告站的公告数据。

字段与采集端约定的页面结构一一对应：
- notice_no    公告编号
- project_no   项目编号
- type         公告类型：tender 招标公告 / correction 更正公告 / cancellation 撤销公告
- title        公告标题
- publish_time 发布时间（YYYY-MM-DD HH:MM）
- deadline     截标时间（撤销公告无）
- target       更正 / 撤销所指的公告编号（招标公告无）
- body         正文

数据场景（用于演示引用核对）：
- PRJ-2026-001 ~ 005：引用合法的正常公告链（含更正、撤销、连续更正）；
- PRJ-2026-006：正常对照组（招标 + 合法更正）；
- PRJ-2026-007：跨项目引用——更正/撤销指向其他项目的公告，引用不成立；
- PRJ-2026-008：断链——撤销指向不存在的公告编号，不能据此判定停办；
- PRJ-2026-009：时间倒挂——更正指向发布时间更晚的公告，引用不成立；
- PRJ-2026-010：异常传递——后续更正引用了异常公告，连带不可采信。
"""

TYPE_LABELS = {
    "tender": "招标公告",
    "correction": "更正公告",
    "cancellation": "撤销公告",
}

ANNOUNCEMENTS = [
    # ---------- 正常公告链（原有 5 个项目） ----------
    {
        "notice_no": "NT-2026-0001",
        "project_no": "PRJ-2026-001",
        "type": "tender",
        "title": "市政道路改造工程施工招标",
        "publish_time": "2026-11-01 09:00",
        "deadline": "2026-11-20 17:00",
        "target": None,
        "body": "现就市政道路改造工程进行公开招标，欢迎符合条件的投标人参加投标。",
    },
    {
        "notice_no": "NT-2026-0003",
        "project_no": "PRJ-2026-002",
        "type": "tender",
        "title": "办公楼物业服务采购",
        "publish_time": "2026-11-02 09:00",
        "deadline": "2026-11-22 12:00",
        "target": None,
        "body": "现就办公楼物业服务进行公开招标，服务期一年。",
    },
    {
        "notice_no": "NT-2026-0005",
        "project_no": "PRJ-2026-003",
        "type": "tender",
        "title": "智慧园区网络设备采购",
        "publish_time": "2026-11-03 09:00",
        "deadline": "2026-11-24 17:00",
        "target": None,
        "body": "现就智慧园区网络设备采购进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0008",
        "project_no": "PRJ-2026-004",
        "type": "tender",
        "title": "职工食堂食材配送服务",
        "publish_time": "2026-11-04 09:00",
        "deadline": "2026-11-21 17:00",
        "target": None,
        "body": "现就职工食堂食材配送服务进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0002",
        "project_no": "PRJ-2026-001",
        "type": "correction",
        "title": "市政道路改造工程施工招标更正公告",
        "publish_time": "2026-11-05 10:00",
        "deadline": "2026-11-25 17:00",
        "target": "NT-2026-0001",
        "body": "因工程量清单调整，现将截标时间由 2026-11-20 17:00 更正为 2026-11-25 17:00，其余内容不变。",
    },
    {
        "notice_no": "NT-2026-0004",
        "project_no": "PRJ-2026-002",
        "type": "cancellation",
        "title": "办公楼物业服务采购撤销公告",
        "publish_time": "2026-11-06 14:00",
        "deadline": None,
        "target": "NT-2026-0003",
        "body": "因采购计划调整，现撤销办公楼物业服务采购招标公告，本项目停止办理。",
    },
    {
        "notice_no": "NT-2026-0006",
        "project_no": "PRJ-2026-003",
        "type": "correction",
        "title": "智慧园区网络设备采购更正公告（一）",
        "publish_time": "2026-11-07 09:30",
        "deadline": "2026-11-26 10:00",
        "target": "NT-2026-0005",
        "body": "现将截标时间由 2026-11-24 17:00 更正为 2026-11-26 10:00。",
    },
    {
        "notice_no": "NT-2026-0009",
        "project_no": "PRJ-2026-005",
        "type": "tender",
        "title": "医疗设备采购项目",
        "publish_time": "2026-11-08 09:00",
        "deadline": "2026-11-30 17:00",
        "target": None,
        "body": "现就医疗设备采购项目进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0007",
        "project_no": "PRJ-2026-003",
        "type": "correction",
        "title": "智慧园区网络设备采购更正公告（二）",
        "publish_time": "2026-11-09 16:00",
        "deadline": "2026-11-28 10:00",
        "target": "NT-2026-0006",
        "body": "现将截标时间由 2026-11-26 10:00 更正为 2026-11-28 10:00。",
    },
    {
        "notice_no": "NT-2026-0010",
        "project_no": "PRJ-2026-005",
        "type": "correction",
        "title": "医疗设备采购项目更正公告",
        "publish_time": "2026-11-10 11:00",
        "deadline": "2026-12-02 17:00",
        "target": "NT-2026-0009",
        "body": "现将截标时间由 2026-11-30 17:00 更正为 2026-12-02 17:00。",
    },
    {
        "notice_no": "NT-2026-0011",
        "project_no": "PRJ-2026-005",
        "type": "cancellation",
        "title": "医疗设备采购项目撤销公告",
        "publish_time": "2026-11-11 09:00",
        "deadline": None,
        "target": "NT-2026-0009",
        "body": "因技术参数重大调整，现撤销医疗设备采购项目招标公告，本项目停止办理。",
    },
    # ---------- 正常对照组：招标 + 合法更正 ----------
    {
        "notice_no": "NT-2026-0012",
        "project_no": "PRJ-2026-006",
        "type": "tender",
        "title": "绿化养护服务采购",
        "publish_time": "2026-11-12 09:00",
        "deadline": "2026-12-05 17:00",
        "target": None,
        "body": "现就绿化养护服务进行公开招标，服务期两年。",
    },
    {
        "notice_no": "NT-2026-0013",
        "project_no": "PRJ-2026-006",
        "type": "correction",
        "title": "绿化养护服务采购更正公告",
        "publish_time": "2026-11-13 10:00",
        "deadline": "2026-12-08 17:00",
        "target": "NT-2026-0012",
        "body": "因评审安排调整，现将截标时间由 2026-12-05 17:00 更正为 2026-12-08 17:00。",
    },
    # ---------- 跨项目引用：指向其他项目的公告 ----------
    {
        "notice_no": "NT-2026-0014",
        "project_no": "PRJ-2026-007",
        "type": "tender",
        "title": "机房空调采购项目",
        "publish_time": "2026-11-14 09:00",
        "deadline": "2026-12-10 17:00",
        "target": None,
        "body": "现就机房空调采购项目进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0015",
        "project_no": "PRJ-2026-007",
        "type": "correction",
        "title": "机房空调采购项目更正公告（引用了其他项目公告）",
        "publish_time": "2026-11-15 10:00",
        "deadline": "2026-12-12 17:00",
        # NT-2026-0012 属于 PRJ-2026-006，跨项目引用不成立
        "target": "NT-2026-0012",
        "body": "本公告误引其他项目的招标公告 NT-2026-0012 作为更正对象，属于异常数据，仅供演示。",
    },
    {
        "notice_no": "NT-2026-0016",
        "project_no": "PRJ-2026-007",
        "type": "cancellation",
        "title": "机房空调采购项目撤销公告（引用了其他项目公告）",
        "publish_time": "2026-11-16 10:00",
        "deadline": None,
        # NT-2026-0003 属于 PRJ-2026-002，跨项目撤销不成立，项目不得判定为停办
        "target": "NT-2026-0003",
        "body": "本公告误引其他项目的招标公告 NT-2026-0003 作为撤销对象，属于异常数据，仅供演示。",
    },
    # ---------- 断链：撤销指向不存在的公告编号 ----------
    {
        "notice_no": "NT-2026-0017",
        "project_no": "PRJ-2026-008",
        "type": "tender",
        "title": "档案数字化加工服务采购",
        "publish_time": "2026-11-17 09:00",
        "deadline": "2026-12-15 17:00",
        "target": None,
        "body": "现就档案数字化加工服务进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0018",
        "project_no": "PRJ-2026-008",
        "type": "cancellation",
        "title": "档案数字化加工服务采购撤销公告（断链）",
        "publish_time": "2026-11-18 10:00",
        "deadline": None,
        # NT-2026-9999 在本站不存在，详情页返回 404，撤销不能成立
        "target": "NT-2026-9999",
        "body": "本公告所指公告 NT-2026-9999 在本站不存在（断链），属于异常数据，仅供演示。",
    },
    # ---------- 时间倒挂：更正指向发布时间更晚的公告 ----------
    {
        "notice_no": "NT-2026-0019",
        "project_no": "PRJ-2026-009",
        "type": "tender",
        "title": "电梯维保服务采购",
        "publish_time": "2026-11-19 09:00",
        "deadline": "2026-12-18 17:00",
        "target": None,
        "body": "现就电梯维保服务进行公开招标，服务期三年。",
    },
    {
        "notice_no": "NT-2026-0020",
        "project_no": "PRJ-2026-009",
        "type": "correction",
        "title": "电梯维保服务采购更正公告（时间倒挂）",
        "publish_time": "2026-11-20 09:00",
        "deadline": "2026-12-20 17:00",
        # 指向同项目、但发布时间更晚（2026-11-22）的公告，引用不成立
        "target": "NT-2026-0021",
        "body": "本公告引用了尚未发布的公告 NT-2026-0021 作为更正对象，时间倒挂，属于异常数据。",
    },
    {
        "notice_no": "NT-2026-0021",
        "project_no": "PRJ-2026-009",
        "type": "correction",
        "title": "电梯维保服务采购更正公告（二）",
        "publish_time": "2026-11-22 09:00",
        "deadline": "2026-12-22 17:00",
        "target": "NT-2026-0019",
        "body": "现将截标时间由 2026-12-18 17:00 更正为 2026-12-22 17:00。",
    },
    # ---------- 异常传递：后续公告引用了异常公告 ----------
    {
        "notice_no": "NT-2026-0022",
        "project_no": "PRJ-2026-010",
        "type": "tender",
        "title": "消防设施检测服务采购",
        "publish_time": "2026-11-23 09:00",
        "deadline": "2026-12-25 17:00",
        "target": None,
        "body": "现就消防设施检测服务进行公开招标。",
    },
    {
        "notice_no": "NT-2026-0023",
        "project_no": "PRJ-2026-010",
        "type": "correction",
        "title": "消防设施检测服务采购更正公告（一，断链）",
        "publish_time": "2026-11-24 09:00",
        "deadline": "2026-12-27 17:00",
        # 指向不存在的公告，本条为异常公告
        "target": "NT-2026-8888",
        "body": "本公告所指公告 NT-2026-8888 在本站不存在（断链），属于异常数据，仅供演示。",
    },
    {
        "notice_no": "NT-2026-0024",
        "project_no": "PRJ-2026-010",
        "type": "correction",
        "title": "消防设施检测服务采购更正公告（二，引用异常公告）",
        "publish_time": "2026-11-25 09:00",
        "deadline": "2026-12-29 17:00",
        # 引用了上一条异常公告，连带不可采信
        "target": "NT-2026-0023",
        "body": "本公告以异常更正 NT-2026-0023 为依据，异常沿引用链传递，属于演示数据。",
    },
]

PAGE_SIZE = 5


def sorted_announcements():
    """列表页按发布时间倒序展示。"""
    return sorted(ANNOUNCEMENTS, key=lambda a: (a["publish_time"], a["notice_no"]), reverse=True)


def get_by_notice_no(notice_no):
    for a in ANNOUNCEMENTS:
        if a["notice_no"] == notice_no:
            return a
    return None
