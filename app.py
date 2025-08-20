from datetime import date
from typing import Optional
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import func, case
from dotenv import load_dotenv
load_dotenv()
from models import db, Category, Transaction   # ambil model dari models.py


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

# SQLite file
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///finance.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# init db
db.init_app(app)


# ========== HELPERS ==========
def ensure_category(name: Optional[str], kind: str) -> None:
    """Buat kategori otomatis jika belum ada. Abaikan jika kosong."""
    if not name:
        return
    nm = name.strip()
    if not nm:
        return
    existing = Category.query.filter_by(name=nm).first()
    if not existing:
        c = Category()
        c.name = nm
        c.kind = kind
        c.monthly_budget = None
        db.session.add(c)
        db.session.commit()


def month_year_lists():
    months_raw = db.session.query(func.strftime("%m", Transaction.tx_date)).distinct().all()
    years_raw = db.session.query(func.strftime("%Y", Transaction.tx_date)).distinct().all()
    months_list = sorted({int(m[0]) for m in months_raw}) if months_raw else [int(date.today().strftime("%m"))]
    years_list = sorted({int(y[0]) for y in years_raw}) if years_raw else [int(date.today().strftime("%Y"))]
    return months_list, years_list


# ========== ROUTES ==========
@app.route("/")
def dashboard():
    # Ringkasan global
    all_tx = Transaction.query.all()
    income = sum(t.amount for t in all_tx if t.type == "INCOME")
    expense = sum(t.amount for t in all_tx if t.type == "EXPENSE")
    balance = income - expense

    # Grafik: filter opsional per tahun
    sel_year = request.args.get("year", type=int)
    q = db.session.query(
        func.strftime("%Y-%m", Transaction.tx_date).label("ym"),
        func.sum(case((Transaction.type == "INCOME", Transaction.amount), else_=0)).label("inc"),
        func.sum(case((Transaction.type == "EXPENSE", Transaction.amount), else_=0)).label("exp"),
    )
    if sel_year:
        q = q.filter(func.strftime("%Y", Transaction.tx_date) == str(sel_year))
    rows = q.group_by("ym").order_by("ym").all()

    chart_labels = [r.ym for r in rows]
    chart_income = [float(r.inc or 0) for r in rows]
    chart_expense = [float(r.exp or 0) for r in rows]

    # Donut: expense by category bulan berjalan
    now_m = int(date.today().strftime("%m"))
    now_y = int(date.today().strftime("%Y"))
    cat_rows = db.session.query(
        Transaction.category, func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "EXPENSE",
        func.strftime("%m", Transaction.tx_date) == f"{now_m:02d}",
        func.strftime("%Y", Transaction.tx_date) == str(now_y),
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    cat_labels = [c[0] for c in cat_rows]
    cat_values = [float(c[1] or 0) for c in cat_rows]

    # Dropdown tahun
    _, years_list = month_year_lists()

    # 5 transaksi terakhir
    last_tx = Transaction.query.order_by(Transaction.tx_date.desc(), Transaction.id.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        income=income,
        expense=expense,
        balance=balance,
        chart_labels=chart_labels,
        chart_income=chart_income,
        chart_expense=chart_expense,
        cat_labels=cat_labels,
        cat_values=cat_values,
        now_m=now_m,
        now_y=now_y,
        sel_year=sel_year,
        years_list=years_list,
        last_tx=last_tx,
    )


@app.route("/transactions")
def transactions():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    q = Transaction.query
    if month:
        q = q.filter(func.strftime("%m", Transaction.tx_date) == f"{month:02d}")
    if year:
        q = q.filter(func.strftime("%Y", Transaction.tx_date) == str(year))
    txs = q.order_by(Transaction.tx_date.desc(), Transaction.id.desc()).all()

    inc = sum(t.amount for t in txs if t.type == "INCOME")
    exp = sum(t.amount for t in txs if t.type == "EXPENSE")
    bal = inc - exp

    months_list, years_list = month_year_lists()

    return render_template(
        "transactions.html",
        transactions=txs,
        income=inc,
        expense=exp,
        balance=bal,
        months_list=months_list,
        years_list=years_list,
        sel_month=month,
        sel_year=year,
    )


@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        tx_type = (request.form.get("type") or "").strip()
        category = (request.form.get("category") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        note = (request.form.get("note") or "").strip()
        tx_date_s = (request.form.get("tx_date") or "").strip()

        if not tx_type or not category or not amount_raw:
            flash("Lengkapi semua field wajib!", "danger")
            return redirect(url_for("add_transaction"))

        try:
            amount = float(amount_raw)
        except ValueError:
            flash("Nominal harus angka!", "danger")
            return redirect(url_for("add_transaction"))
        if amount <= 0:
            flash("Nominal harus > 0!", "danger")
            return redirect(url_for("add_transaction"))

        if tx_type not in {"INCOME", "EXPENSE"}:
            flash("Jenis transaksi tidak valid!", "danger")
            return redirect(url_for("add_transaction"))

        tx_date_val = date.fromisoformat(tx_date_s) if tx_date_s else date.today()

        ensure_category(category, tx_type)

        tx = Transaction()
        tx.type = tx_type
        tx.category = category
        tx.amount = amount
        tx.note = note
        tx.tx_date = tx_date_val

        db.session.add(tx)
        db.session.commit()

        flash("Transaksi berhasil ditambahkan ✅", "success")
        return redirect(url_for("transactions"))

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("add_transaction.html", categories=categories)


@app.route("/transactions/<int:tx_id>/edit", methods=["GET", "POST"])
def edit_transaction(tx_id: int):
    t = Transaction.query.get_or_404(tx_id)
    if request.method == "POST":
        tx_type = (request.form.get("type") or "").strip()
        category = (request.form.get("category") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        note = (request.form.get("note") or "").strip()
        tx_date_s = (request.form.get("tx_date") or "").strip()

        try:
            amount = float(amount_raw)
        except ValueError:
            flash("Nominal tidak valid.", "danger")
            return redirect(url_for("edit_transaction", tx_id=tx_id))

        if amount <= 0 or tx_type not in {"INCOME", "EXPENSE"}:
            flash("Data tidak valid.", "danger")
            return redirect(url_for("edit_transaction", tx_id=tx_id))

        ensure_category(category, tx_type)

        t.type = tx_type
        t.category = category
        t.amount = amount
        t.note = note
        t.tx_date = date.fromisoformat(tx_date_s) if tx_date_s else t.tx_date
        db.session.commit()

        flash("Transaksi diperbarui ✏️", "success")
        return redirect(url_for("transactions"))

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("edit_transaction.html", t=t, categories=categories)


@app.route("/transactions/<int:tx_id>/delete", methods=["POST"])
def delete_transaction(tx_id: int):
    t = Transaction.query.get_or_404(tx_id)
    db.session.delete(t)
    db.session.commit()
    flash("Transaksi dihapus 🗑️", "warning")
    return redirect(url_for("transactions"))


@app.route("/budget", methods=["GET", "POST"])
def budget():
    sel_month = request.args.get("month", type=int)
    sel_year = request.args.get("year", type=int)
    today_m = int(date.today().strftime("%m"))
    today_y = int(date.today().strftime("%Y"))
    view_m = sel_month or today_m
    view_y = sel_year or today_y

    if request.method == "POST":
        for cat in Category.query.filter_by(kind="EXPENSE").all():
            key = f"budget_{cat.id}"
            val_s = (request.form.get(key) or "").strip()
            cat.monthly_budget = float(val_s) if val_s else None
        db.session.commit()
        flash("Budget diperbarui ✅", "success")
        return redirect(url_for("budget", month=view_m, year=view_y))

    cats = Category.query.filter_by(kind="EXPENSE").order_by(Category.name.asc()).all()

    spent_rows = db.session.query(
        Transaction.category, func.sum(Transaction.amount).label("spent")
    ).filter(
        Transaction.type == "EXPENSE",
        func.strftime("%m", Transaction.tx_date) == f"{view_m:02d}",
        func.strftime("%Y", Transaction.tx_date) == str(view_y),
    ).group_by(Transaction.category).all()
    spent_map = {n: float(s or 0) for n, s in spent_rows}

    items = []
    for c in cats:
        spent = spent_map.get(c.name, 0.0)
        budget_val = c.monthly_budget
        pct = None if not budget_val else min(100.0, (spent / budget_val) * 100.0)
        remain = None if budget_val is None else (budget_val - spent)
        items.append(
            {"cat": c, "spent": spent, "budget": budget_val, "pct": pct, "remain": remain}
        )

    months_list, years_list = month_year_lists()
    if today_m not in months_list:
        months_list = sorted(set(months_list) | {today_m})
    if today_y not in years_list:
        years_list = sorted(set(years_list) | {today_y})

    return render_template(
        "budget.html",
        items=items,
        month=view_m,
        year=view_y,
        months_list=months_list,
        years_list=years_list,
        sel_month=view_m,
        sel_year=view_y,
    )


# ========== INIT ==========
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
