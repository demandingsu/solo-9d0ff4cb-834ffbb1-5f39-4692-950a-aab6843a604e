"""公告链分析逻辑测试。"""

from analysis import (
    STATUS_ACTIVE,
    STATUS_CANCELLED,
    STATUS_PENDING,
    build_projects,
    find_anomalies,
)
from scraper import Announcement


def ann(project, notice, ntype, pub, deadline=None, target=None):
    return Announcement(
        project_no=project,
        notice_no=notice,
        notice_type=ntype,
        publish_time=pub,
        deadline=deadline,
        target_notice_no=target,
        title=notice,
        url=f"http://example.com/detail/{notice}.html",
    )


def test_correction_updates_deadline():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="N1"),
    ]
    (p,) = build_projects(anns)
    assert p["status"] == STATUS_ACTIVE
    assert p["deadline"] == "2026-11-25 17:00"
    assert len(p["chain"]) == 2
    assert p["anomalies"] == []
    # 链上说明须记录“旧值 → 新值”，不能在生成说明前就覆盖旧截标时间
    assert "2026-11-20 17:00 → 2026-11-25 17:00" in p["chain"][1]["note"]


def test_cancellation_marks_stopped():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "cancellation", "2026-11-06 14:00", target="N1"),
    ]
    (p,) = build_projects(anns)
    assert p["status"] == STATUS_CANCELLED


def test_chain_sorted_by_publish_time_not_input_order():
    anns = [
        ann("P1", "N3", "correction", "2026-11-09 16:00", deadline="2026-11-28 10:00", target="N2"),
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="N1"),
    ]
    (p,) = build_projects(anns)
    assert [c["notice_no"] for c in p["chain"]] == ["N1", "N2", "N3"]
    assert p["deadline"] == "2026-11-28 10:00"


def test_correction_then_cancellation():
    anns = [
        ann("P1", "N1", "tender", "2026-11-08 09:00", deadline="2026-11-30 17:00"),
        ann("P1", "N2", "correction", "2026-11-10 11:00", deadline="2026-12-02 17:00", target="N1"),
        ann("P1", "N3", "cancellation", "2026-11-11 09:00", target="N1"),
    ]
    (p,) = build_projects(anns)
    assert p["status"] == STATUS_CANCELLED
    assert p["deadline"] == "2026-12-02 17:00"  # 保留最后一次更正后的截标时间供参考


def test_projects_grouped_independently():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P2", "N2", "tender", "2026-11-02 09:00", deadline="2026-11-22 12:00"),
        ann("P2", "N3", "cancellation", "2026-11-06 14:00", target="N2"),
    ]
    projects = {p["project_no"]: p for p in build_projects(anns)}
    assert projects["P1"]["status"] == STATUS_ACTIVE
    assert projects["P1"]["deadline"] == "2026-11-20 17:00"
    assert projects["P2"]["status"] == STATUS_CANCELLED


# ---------- 引用核对：断链、跨项目、时间倒挂、异常传递 ----------


def test_correction_target_missing_is_anomaly():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="NOPE"),
    ]
    anomalies = find_anomalies(anns)
    assert "N2" in anomalies
    assert "不存在" in anomalies["N2"]

    (p,) = build_projects(anns)
    assert p["status"] == STATUS_PENDING
    assert p["deadline"] is None  # 不得采信异常更正里的截标时间
    assert [a["notice_no"] for a in p["anomalies"]] == ["N2"]
    assert p["anomalies"][0]["url"] == "http://example.com/detail/N2.html"
    chain = {c["notice_no"]: c for c in p["chain"]}
    assert chain["N1"]["anomaly"] is False
    assert chain["N2"]["anomaly"] is True


def test_cancellation_target_missing_does_not_stop_project():
    # 指向不存在公告的撤销不能算作停办
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "cancellation", "2026-11-06 14:00", target="GHOST"),
    ]
    (p,) = build_projects(anns)
    assert p["status"] == STATUS_PENDING
    assert p["deadline"] is None
    assert [a["notice_no"] for a in p["anomalies"]] == ["N2"]
    assert "不存在" in p["anomalies"][0]["reason"]


def test_cross_project_correction_is_anomaly():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P2", "N2", "tender", "2026-11-02 09:00", deadline="2026-11-22 12:00"),
        # P2 的更正却引用 P1 的招标公告
        ann("P2", "N3", "correction", "2026-11-05 10:00", deadline="2026-12-01 17:00", target="N1"),
    ]
    anomalies = find_anomalies(anns)
    assert set(anomalies) == {"N3"}
    assert "其他项目" in anomalies["N3"]

    projects = {p["project_no"]: p for p in build_projects(anns)}
    # 被引用的 P1 不受影响，照常给出结果
    assert projects["P1"]["status"] == STATUS_ACTIVE
    assert projects["P1"]["deadline"] == "2026-11-20 17:00"
    # 发起异常引用的 P2 待核实，且不采信异常更正的截标时间
    assert projects["P2"]["status"] == STATUS_PENDING
    assert projects["P2"]["deadline"] is None


def test_cross_project_cancellation_does_not_stop_either_project():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P2", "N2", "tender", "2026-11-02 09:00", deadline="2026-11-22 12:00"),
        # P2 的撤销却指向 P1 的公告
        ann("P2", "N3", "cancellation", "2026-11-06 14:00", target="N1"),
    ]
    projects = {p["project_no"]: p for p in build_projects(anns)}
    assert projects["P1"]["status"] == STATUS_ACTIVE
    assert projects["P2"]["status"] == STATUS_PENDING
    assert [a["notice_no"] for a in projects["P2"]["anomalies"]] == ["N3"]


def test_target_published_later_is_anomaly():
    # 时间倒挂：更正指向发布时间更晚（或相同）的公告
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="N3"),
        ann("P1", "N3", "correction", "2026-11-09 16:00", deadline="2026-11-28 10:00", target="N1"),
    ]
    anomalies = find_anomalies(anns)
    assert "N2" in anomalies
    assert "发布时间" in anomalies["N2"]
    # N3 本身引用合法，不应被标记
    assert "N3" not in anomalies

    (p,) = build_projects(anns)
    assert p["status"] == STATUS_PENDING
    assert {a["notice_no"] for a in p["anomalies"]} == {"N2"}


def test_anomaly_propagates_through_reference_chain():
    # N2 断链为异常；N3 引用 N2，连带异常；招标 N1 不受影响
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="GHOST"),
        ann("P1", "N3", "correction", "2026-11-07 10:00", deadline="2026-11-27 17:00", target="N2"),
        ann("P1", "N4", "cancellation", "2026-11-09 10:00", target="N3"),
    ]
    anomalies = find_anomalies(anns)
    assert set(anomalies) == {"N2", "N3", "N4"}

    (p,) = build_projects(anns)
    assert p["status"] == STATUS_PENDING
    assert p["deadline"] is None
    assert {a["notice_no"] for a in p["anomalies"]} == {"N2", "N3", "N4"}
    # 撤销为异常时不得标记停办
    assert all(c["anomaly"] for c in p["chain"] if c["notice_no"] in ("N2", "N3", "N4"))
    assert not next(c for c in p["chain"] if c["notice_no"] == "N1")["anomaly"]


def test_valid_projects_unaffected_alongside_anomalous_ones():
    anns = [
        # 正常项目：招标 + 合法更正
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N2", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="N1"),
        # 异常项目：断链撤销
        ann("P2", "N3", "tender", "2026-11-02 09:00", deadline="2026-11-22 12:00"),
        ann("P2", "N4", "cancellation", "2026-11-06 14:00", target="GHOST"),
    ]
    projects = {p["project_no"]: p for p in build_projects(anns)}
    assert projects["P1"]["status"] == STATUS_ACTIVE
    assert projects["P1"]["deadline"] == "2026-11-25 17:00"
    assert projects["P1"]["anomalies"] == []
    assert projects["P2"]["status"] == STATUS_PENDING


def test_duplicate_notice_no_is_anomaly():
    anns = [
        ann("P1", "N1", "tender", "2026-11-01 09:00", deadline="2026-11-20 17:00"),
        ann("P1", "N1", "correction", "2026-11-05 10:00", deadline="2026-11-25 17:00", target="N1"),
    ]
    anomalies = find_anomalies(anns)
    assert "N1" in anomalies
    assert "重复" in anomalies["N1"]
    (p,) = build_projects(anns)
    assert p["status"] == STATUS_PENDING
