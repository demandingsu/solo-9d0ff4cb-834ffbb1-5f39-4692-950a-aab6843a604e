"""公告链分析：把同一项目的公告按发布时间串起来，推导最终状态。

规则：
- 招标公告：确立（或重新确立）项目的截标时间，状态置为“进行中”；
- 更正公告：仅当引用合法时才更新项目当前截标时间；
- 撤销公告：仅当引用合法时才将项目标记为“停办”。

引用合法性（按公告编号核对，三条同时满足才算合法）：
1. 被引用的公告编号在本轮抓取到的公告中**存在**（断链即异常）；
2. 被引用公告与本公告属于**同一项目**（跨项目引用即异常）；
3. 被引用公告的**发布时间更早**（引用尚未发布或同时发布的公告即异常）。

异常具有传递性：引用了异常公告的后续公告同样不可信，一并标记为异常。
任何项目只要包含异常公告，就不得形成确定结论——状态显示“待核实”，
并列出全部异常来源；其余项目照常给出结果。
每条公告都作为依据保留在链上，页面可点击查看来源链接。
"""

from __future__ import annotations

from typing import Iterable

from scraper import TYPE_LABELS, Announcement

STATUS_ACTIVE = "进行中"
STATUS_CANCELLED = "停办"
STATUS_PENDING = "待核实"


def _base_note(a: Announcement, deadline: str | None) -> str:
    """公告未被判为异常时的链上说明（保持原有口径）。"""
    if a.notice_type == "tender":
        return f"发布招标，截标时间 {a.deadline or '未注明'}"
    if a.notice_type == "correction":
        if a.deadline:
            return f"更正 {a.target_notice_no}：截标时间 {deadline or '未定'} → {a.deadline}"
        return f"更正 {a.target_notice_no}（未涉及截标时间）"
    if a.notice_type == "cancellation":
        return f"撤销 {a.target_notice_no}：项目停止办理"
    return "未知类型公告"


def _invalid_reason(a: Announcement, index: dict[str, Announcement]) -> str | None:
    """核对单条更正/撤销公告的引用，返回异常原因；合法则返回 None。"""
    target = index.get(a.target_notice_no or "")
    if target is None:
        return f"引用的公告 {a.target_notice_no} 不存在（断链），更正/撤销不能成立"
    if target.project_no != a.project_no:
        return (
            f"引用的公告 {target.notice_no} 属于其他项目（{target.project_no}），"
            f"不能用于本项目（{a.project_no}）"
        )
    if target.publish_time >= a.publish_time:
        return (
            f"引用的公告 {target.notice_no} 发布时间（{target.publish_time}）"
            f"不早于本公告（{a.publish_time}），引用关系不成立"
        )
    return None


def find_anomalies(announcements: Iterable[Announcement]) -> dict[str, str]:
    """核对全部更正/撤销公告的引用，返回 {异常公告编号: 异常原因}。

    异常可传递：引用异常公告的后续公告也标记为异常（引用链不可信）。
    """
    items = list(announcements)

    # 公告编号全局索引；同一编号出现多次本身即数据异常，全部标记
    index: dict[str, Announcement] = {}
    duplicate_nos: set[str] = set()
    for a in items:
        if a.notice_no in index:
            duplicate_nos.add(a.notice_no)
        else:
            index[a.notice_no] = a

    anomalies: dict[str, str] = {}
    for no in duplicate_nos:
        anomalies[no] = f"公告编号 {no} 重复出现，数据来源不可信"

    # 按发布时间、公告编号排序后逐条核对：被引用公告发布更早，
    # 因此处理到本公告时其引用目标的异常状态已经确定
    ordered = sorted(items, key=lambda a: (a.publish_time, a.notice_no))
    for a in ordered:
        if a.notice_type not in ("correction", "cancellation"):
            continue
        reason = _invalid_reason(a, index)
        if reason is not None:
            anomalies.setdefault(a.notice_no, reason)
            continue
        target = index[a.target_notice_no]
        if target.notice_no in anomalies:
            anomalies.setdefault(
                a.notice_no,
                f"引用的公告 {target.notice_no} 已被标记为异常，本公告的更正/撤销不可采信",
            )
    return anomalies


def build_projects(announcements: Iterable[Announcement]) -> list[dict]:
    anomalies = find_anomalies(announcements)

    by_project: dict[str, list[Announcement]] = {}
    for a in announcements:
        by_project.setdefault(a.project_no, []).append(a)

    projects = []
    for project_no, items in by_project.items():
        # 按发布时间串链，时间相同按公告编号稳定排序
        items.sort(key=lambda a: (a.publish_time, a.notice_no))
        status = STATUS_ACTIVE
        deadline = None
        chain = []
        project_anomalies: list[dict] = []
        tainted = False

        for a in items:
            reason = anomalies.get(a.notice_no)
            if reason is None:
                # 先依据当前（旧）截标时间生成链上说明，再应用公告的结论
                note = _base_note(a, deadline)
                # 引用合法的公告才允许改变项目结论
                if a.notice_type == "tender":
                    status = STATUS_ACTIVE
                    deadline = a.deadline
                elif a.notice_type == "correction":
                    if a.deadline:
                        deadline = a.deadline
                elif a.notice_type == "cancellation":
                    status = STATUS_CANCELLED
            else:
                # 异常公告不参与状态推导，避免形成确定结论
                tainted = True
                note = f"{_base_note(a, deadline)}；⚠ 异常：{reason}"
                project_anomalies.append(
                    {
                        "notice_no": a.notice_no,
                        "type_label": TYPE_LABELS.get(a.notice_type, a.notice_type),
                        "publish_time": a.publish_time,
                        "reason": reason,
                        "url": a.url,
                    }
                )
            chain.append(
                {
                    "notice_no": a.notice_no,
                    "type_label": TYPE_LABELS.get(a.notice_type, a.notice_type),
                    "publish_time": a.publish_time,
                    "note": note,
                    "url": a.url,
                    "anomaly": reason is not None,
                }
            )

        if tainted:
            # 存在异常来源：不输出确定的状态/截标时间结论
            projects.append(
                {
                    "project_no": project_no,
                    "status": STATUS_PENDING,
                    "deadline": None,
                    "chain": chain,
                    "anomalies": project_anomalies,
                }
            )
        else:
            projects.append(
                {
                    "project_no": project_no,
                    "status": status,
                    "deadline": deadline,
                    "chain": chain,
                    "anomalies": [],
                }
            )

    projects.sort(key=lambda p: p["project_no"])
    return projects
