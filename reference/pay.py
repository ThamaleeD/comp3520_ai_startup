def pay_summary(role, hours, rate, salary, holidays, month_pay, month_days_worked):
    role = role.strip().lower()
    if role not in ("staff", "manager", "owner"): raise ValueError("role")
    if len(hours) != 5 or any(h < 0 or h > 24 for h in hours): raise ValueError("hours")
    if role != "staff":
        if salary is None or salary <= 0: raise ValueError("salary")
        return {"regular_hours": 0, "overtime_hours": 0, "double_time_hours": 0,
                "stat_days": 0, "stat_pay": 0, "total_pay": round(salary / 52, 2)}
    if rate is None or rate <= 0: raise ValueError("rate")
    if any(hours[i] != 0 for i in holidays): raise ValueError("holiday hours")
    capped = sum(min(h, 12) for i, h in enumerate(hours) if i not in holidays)
    dt = sum(max(0, h - 12) for i, h in enumerate(hours) if i not in holidays)
    reg, ot = min(capped, 40), max(0, capped - 40)
    per = month_pay / month_days_worked if month_days_worked else 0
    sp = len(holidays) * per
    total = round(reg * rate + ot * 1.5 * rate + dt * 2 * rate + sp, 2)
    return {"regular_hours": reg, "overtime_hours": ot, "double_time_hours": dt,
            "stat_days": len(holidays), "stat_pay": round(sp, 2), "total_pay": total}
