"""Presentation figures (16:9 PNG) in results/figures/.

  1_auroc_controles.png   AUROC with 95% CI, all patients vs the Nov-Dec 2016 window
  2_indice_vs_updrs.png   main model index vs UPDRS inside PD
  3_diales.png            5 dials: control vs clinical group medians
  4_seguimiento_90d.png   SIMULATED 90-day tracking with baseline band and alert
  5_validacion_externa.png  NeuroVoz-trained models on MDVR-KCL (English, same room for all)
Palette validated with the dataviz validator: HC #2F9BCB, clinical #E8552A.
"""
import json
import logging

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from confound_analysis import shared_window_ids  # noqa: E402
from dataset import ML_DIR, RESULTS_DIR, build_index, load_patient_meta  # noqa: E402
from evaluate import age_matched_ids, auroc_ci, cross_val_patient_scores  # noqa: E402
from rank_dials import partial_spearman  # noqa: E402
from train_baseline import make_logreg  # noqa: E402

FIG_DIR = RESULTS_DIR / "figures"
EXPORT_DIR = ML_DIR / "export"
HC, PD_COLOR, NAVY, GRAY, INK, MUTED = "#2F9BCB", "#E8552A", "#092634", "#A7B1B7", "#092634", "#5B6F7A"
BENCHMARK_SENTENCES = 0.77
SCORES = RESULTS_DIR / "scores"
MODELS = [  # (label, csv, kind)
    ("Solo edad + sexo", None, "control"),
    ("Solo canal (sala/micro)", "confound_channel_only.csv", "control"),
    ("Solo silencio", "egemaps_silence_sentences_pataka_logreg.csv", "control"),
    ("eGeMAPS", "confound_egemaps_all.csv", "voice"),
    ("eGeMAPS, canal descontado", "confound_egemaps_all_resid.csv", "voice"),
    ("WavLM", "ssl_wavlm-base-plus_layer_avg.csv", "voice"),
    ("WavLM, canal descontado", "ssl_wavlm-base-plus_layer_avg_channel_resid.csv", "main"),
    ("WavLM Large, canal descontado", "improve_wavlm-large_resid.csv", "voice"),
    ("Whisper large-v3, canal descontado", "improve_whisper-large-v3_resid.csv", "voice"),
    ("WavLM fine-tuned (SupCon)", "finetuned_wavlm-base-plus.csv", "voice"),
    ("HuBERT fine-tuned (SupCon)", "finetuned_hubert-base-ls960.csv", "voice"),
    ("DA-DSQA frases (sin reentrenar)", "dadsqa_sentences.csv", "voice"),
]
log = logging.getLogger("figures")


def style() -> None:
    plt.rcParams.update({
        "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 11, "axes.edgecolor": MUTED,
        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": "#E3EBEF", "grid.linewidth": 0.8, "figure.dpi": 200, "savefig.bbox": "tight",
        "figure.facecolor": "white", "axes.facecolor": "white",
    })


def labelled(scores: pd.DataFrame) -> pd.DataFrame:
    return scores.assign(label=lambda d: d["patient_id"].str.startswith("PD").astype(int))


def age_only_scores() -> pd.DataFrame:
    meta = build_index()[["patient_id", "label", "fold"]].drop_duplicates().merge(load_patient_meta(), on="patient_id")
    meta = meta.dropna(subset=["age"]).assign(sex=lambda d: d["sex"].fillna(0.5))
    return cross_val_patient_scores(meta, ["age", "sex"], make_logreg)[["patient_id", "score"]]


def auroc_rows() -> pd.DataFrame:
    window = shared_window_ids()
    meta = load_patient_meta().assign(label=lambda d: d["patient_id"].str.startswith("PD").astype(int))
    matched = age_matched_ids(meta)
    channel = pd.read_csv(SCORES / "confound_channel_only.csv").rename(columns={"score": "channel"})
    rows = []
    for name, csv, kind in MODELS:
        if csv is None:
            scores = age_only_scores()
        elif (SCORES / csv).exists():
            scores = pd.read_csv(SCORES / csv)
        else:
            continue
        s = labelled(scores)
        w = s[s["patient_id"].isin(window)]
        m = s[s["patient_id"].isin(matched)]
        auc, lo, hi = auroc_ci(s["label"], s["score"])
        mauc, mlo, mhi = auroc_ci(m["label"], m["score"])
        wauc, wlo, whi = auroc_ci(w["label"], w["score"])
        both = s.merge(channel, on="patient_id")
        rows.append({"model": name, "kind": kind, "auc": auc, "lo": lo, "hi": hi,
                     "mauc": mauc, "mlo": mlo, "mhi": mhi, "wauc": wauc, "wlo": wlo, "whi": whi,
                     "rho_with_channel_only": stats.spearmanr(both["score"], both["channel"])[0]})
    return pd.DataFrame(rows)


def fig_auroc(df: pd.DataFrame) -> None:
    colors = df["kind"].map({"control": GRAY, "voice": HC, "main": NAVY})
    y = np.arange(len(df))[::-1]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.4), sharey=True)
    panels = [("auc", "lo", "hi", "Todos los pacientes (n = 107)"),
              ("mauc", "mlo", "mhi", "Emparejados por edad (±3 años)\n→ quita el efecto edad"),
              ("wauc", "wlo", "whi", "Misma época de grabación (nov-dic 2016)\n→ quita el efecto sala (7 PD / 25 HC)")]
    for ax, (c, lo, hi, title) in zip(axes, panels):
        ax.barh(y, df[c] - 0.5, left=0.5, height=0.6, color=colors)
        ax.errorbar(df[c], y, xerr=[df[c] - df[lo], df[hi] - df[c]], fmt="none", ecolor=INK, elinewidth=1, capsize=2)
        for yi, v in zip(y, df[c]):
            ax.text(max(v, 0.5) + 0.01, yi + 0.3, f"{v:.2f}".replace(".", ","), fontsize=9, color=INK)
        ax.axvline(0.5, color=MUTED, linewidth=1)
        ax.set_xlim(0.0, 1.05)
        ax.set_title(title, fontsize=11, loc="left", color=INK)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("AUROC (0,5 = azar)")
    axes[0].axvline(BENCHMARK_SENTENCES, color=PD_COLOR, linestyle="--", linewidth=1.2)
    axes[0].text(BENCHMARK_SENTENCES - 0.01, y.min() - 0.45, "benchmark externo\nfrases 0,77", color=INK,
                 fontsize=8, ha="right", va="top")
    axes[0].set_ylim(y.min() - 1.1, y.max() + 0.6)
    axes[0].set_yticks(y, df["model"])
    fig.suptitle("La sala y la edad predicen Parkinson en NeuroVoz; la voz sigue separando cuando se quitan",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, -0.03, "Gris: controles sin voz. Azul: modelos de voz. Navy: modelo principal (WavLM congelado, "
             "canal descontado). IC 95 % por bootstrap de pacientes; validación cruzada por paciente (folds.csv). "
             "Los modelos con fine-tuning puntúan alto pero su score correlaciona con el del modelo «solo canal».",
             fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "1_auroc_controles.png")
    plt.close(fig)


def fig_updrs() -> None:
    scores = pd.read_csv(SCORES / "ssl_wavlm-base-plus_layer_avg_channel_resid.csv")
    meta = load_patient_meta().merge(scores, on="patient_id")
    pdm = meta[meta["patient_id"].str.startswith("PD")].dropna(subset=["updrs", "age"])
    pdm = pdm.assign(sex=lambda d: d["sex"].fillna(0.5), index=lambda d: 100 * d["score"])
    rho, p = partial_spearman(pdm["index"].to_numpy(), pdm["updrs"].to_numpy(), pdm[["age", "sex"]].to_numpy())
    raw_rho = stats.spearmanr(pdm["index"], pdm["updrs"])[0]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(pdm["updrs"], pdm["index"], s=42, color=PD_COLOR, edgecolor="white", linewidth=1.2, zorder=3)
    slope, intercept = np.polyfit(pdm["updrs"], pdm["index"], 1)
    xs = np.linspace(pdm["updrs"].min(), pdm["updrs"].max(), 50)
    ax.plot(xs, slope * xs + intercept, color=NAVY, linewidth=2)
    ax.set_xlabel("UPDRS (gravedad motora, mayor = peor)")
    ax.set_ylabel("Índice vocal VoxWave (0-100)")
    ax.set_title(f"El índice vocal sube con la gravedad: ρ = {raw_rho:.2f}; ρ parcial (edad, sexo) = {rho:.2f}, "
                 f"p = {p:.4f}".replace(".", ","), loc="left", fontsize=11)
    fig.text(0.01, -0.03, f"{len(pdm)} pacientes con Parkinson de NeuroVoz. Predicción fuera de fold del modelo "
             "WavLM con el canal descontado.", fontsize=8, color=MUTED)
    fig.savefig(FIG_DIR / "2_indice_vs_updrs.png")
    plt.close(fig)


def fig_dials() -> None:
    ref = pd.read_csv(EXPORT_DIR / "dials_reference.csv")
    ref = ref.reindex(ref["d_pd_vs_hc_age_sex_adjusted"].abs().sort_values().index)
    y = np.arange(len(ref))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hlines(y, ref["hc_median_z"], ref["pd_median_z"], color="#C9D3D8", linewidth=3, zorder=1)
    ax.scatter(ref["hc_median_z"], y, s=80, color=HC, edgecolor="white", linewidth=1.5, zorder=3, label="Voces de control")
    ax.scatter(ref["pd_median_z"], y, s=80, color=PD_COLOR, edgecolor="white", linewidth=1.5, zorder=3, label="Grupo clínico (Parkinson)")
    for yi, d in zip(y, ref["d_pd_vs_hc_age_sex_adjusted"]):
        ax.text(0.62, yi, f"d = {d:+.2f}".replace(".", ","), va="center", fontsize=9, color=MUTED)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.set_yticks(y, ref["name_es"])
    ax.set_xlim(-0.6, 0.8)
    ax.set_xlabel("Mediana por grupo (desviaciones estándar respecto a todas las frases)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, frameon=False, fontsize=9)
    ax.set_title("Los diales de la voz: entonación más plana, ritmo más rápido y pausas más cortas",
                 loc="left", fontsize=11)
    fig.text(0.01, -0.1, "d = diferencia ajustada por edad y sexo. 53 PD / 55 HC de NeuroVoz, frases + pa-ta-ka.",
             fontsize=8, color=MUTED)
    fig.savefig(FIG_DIR / "3_diales.png")
    plt.close(fig)


def fig_dial_drift(ax: plt.Axes, tl: dict) -> None:
    """Lower panel: weekly drift of the dials (z vs own baseline, positive = clinical direction)."""
    dd = tl["dial_drift"]
    daily = pd.DataFrame(dd["daily"])
    start = tl["tracking_rule"]["baseline_days"]
    after = daily[daily["day"] >= start].assign(week=lambda d: (d["day"] - start) // 7)
    weekly = after.groupby("week").median()
    x = start + 7 * weekly.index + 3
    names = tl["dials"]
    top = dd["alert"]["top_dials"] if dd["alert"] else []
    top_cols = [c for c in names if names[c] in top]
    for col, color in zip(top_cols, (HC, GRAY)):
        ax.plot(x, weekly[col], color=color, linewidth=1.5)
        ax.text(x[-1] + 0.8, weekly[col].iloc[-1], names[col], color=INK, fontsize=9, va="center")
    ax.plot(x, weekly["score"], color=NAVY, linewidth=2.5, marker="o", markersize=4)
    ax.text(x[-1] + 0.8, weekly["score"].iloc[-1], "Deriva de los diales\n(media ponderada)", color=INK,
            fontsize=9, va="center", fontweight="bold")
    ax.axhline(tl["tracking_rule"]["z_alert"], color=MUTED, linestyle="--", linewidth=1)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    if dd["alert"]:
        ax.axvline(dd["alert"]["day"], color=PD_COLOR, linewidth=2)
    ax.set_xlim(0, 91)
    ax.set_ylabel("Cambio frente a tu\nreferencia (z, hacia el\npatrón clínico)")
    ax.set_xlabel("Día")
    ax.set_title("Qué parámetros cambian: rango tonal y variación de entonación lideran la deriva",
                 loc="left", fontsize=11)


def fig_tracking() -> None:
    tl = json.loads((EXPORT_DIR / "timeline_90d.json").read_text(encoding="utf-8"))
    s = pd.DataFrame(tl["sessions"])
    w = pd.DataFrame(tl["weekly"])
    c, sp, z = tl["baseline"]["centre"], tl["baseline"]["spread"], tl["tracking_rule"]["z_alert"]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    ax.axvspan(0, tl["tracking_rule"]["baseline_days"], color=HC, alpha=0.08, lw=0)
    ax.axhspan(max(0, c - z * sp), c + z * sp, color=HC, alpha=0.14, lw=0)
    ax.axhline(c, color=HC, linestyle="--", linewidth=1)
    ok, off = s[~s["wear_off"]], s[s["wear_off"]]
    ax.scatter(ok["day"], ok["score"], s=22, color=HC, alpha=0.9, label="Sesión diaria", zorder=3)
    ax.scatter(off["day"], off["score"], s=22, facecolor="white", edgecolor=MUTED, linewidth=1,
               label="Fin de dosis (no cuenta)", zorder=3)
    ax.plot(w["start_day"] + 3, w["value"], color=NAVY, linewidth=2.5, marker="o", markersize=4,
            label="Mediana semanal", zorder=4)
    if tl["alert"]:
        ax.axvline(tl["alert"]["day"], color=PD_COLOR, linewidth=2)
        ax.text(tl["alert"]["day"] - 1, 97, f"Aviso, día {tl['alert']['day']}", color=INK, ha="right",
                va="top", fontsize=10, fontweight="bold")
    ax.text(1, 97, "Referencia personal\n(14 días)", color=INK, fontsize=9, va="top")
    ax.set_xlim(0, 91)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Índice vocal (0-100)")
    ax.legend(loc="center right", frameon=False, fontsize=9)
    ax.set_title("Seguimiento frente a la propia referencia (SIMULADO): avisa solo cuando la deriva se sostiene "
                 "3 semanas", loc="left", fontsize=11)
    fig_dial_drift(ax2, tl)
    fig.text(0.01, -0.02, "Timeline simulado con grabaciones reales de dos pacientes de NeuroVoz (UPDRS 10 → 43). "
             "Solo cuentan sesiones en ON y sin discinesias. No es un seguimiento real.", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "4_seguimiento_90d.png")
    plt.close(fig)


EXTERNAL_ROWS = [  # (row id, label, kind)
    ("channel", "Control: solo sala (entrenado en ese dataset)", "control"),
    ("raw", "WavLM sin corregir canal", "voice"),
    ("egemaps", "eGeMAPS, canal descontado", "voice"),
    ("large", "WavLM Large, canal descontado", "voice"),
    ("main", "WavLM, canal descontado (principal)", "main"),
    ("ceiling", "Techo: WavLM entrenado en ese dataset", "control"),
]
MDVR_KEYS = {"channel": "p_in_mdvr_channel", "raw": "p_wavlm_raw", "egemaps": "p_egemaps_resid",
             "large": "p_wavlm_large_resid", "main": "p_main", "ceiling": "p_in_mdvr_wavlm"}
ITALIAN_KEYS = {"channel": "p_in_dataset_channel", "raw": "p_wavlm_raw", "egemaps": "p_egemaps_resid",
                "large": "p_wavlm_large_resid", "main": "p_main", "ceiling": "p_in_dataset_wavlm"}


def external_panels() -> list[tuple[str, dict]]:
    """[(title, {row id: (auc, lo, hi, rho_speech or None)})]"""
    panels = []
    mdvr_path, ita_path = RESULTS_DIR / "external_mdvr.json", RESULTS_DIR / "external_italian.json"
    if mdvr_path.exists():
        for task, r in json.loads(mdvr_path.read_text()).items():
            rows = {k: (r[v]["auroc"], *r[v]["ci"], r[v]["rho_updrs_iii18"][0]) for k, v in MDVR_KEYS.items()}
            label = {"dialogo": "diálogo"}.get(task, task)
            panels.append((f"Londres, {label} en inglés\n{r['n_pd']} PD / {r['n_hc']} HC, misma sala y móvil", rows))
    if ita_path.exists():
        r = json.loads(ita_path.read_text())["habla_todo"]["PD_vs_EHC"]
        rows = {k: (*r[v], None) for k, v in ITALIAN_KEYS.items()}
        panels.append((f"Italia, habla en italiano\n{r['n_pos']} PD / {r['n_neg']} controles de su edad", rows))
    return panels


def fig_external() -> None:
    panels = external_panels()
    if not panels:
        return
    y = np.arange(len(EXTERNAL_ROWS))[::-1]
    colors = [{"control": GRAY, "voice": HC, "main": NAVY}[k] for _, _, k in EXTERNAL_ROWS]
    fig, axes = plt.subplots(1, len(panels), figsize=(5 * len(panels) + 3, 5), sharey=True)
    for ax, (title, rows) in zip(np.atleast_1d(axes), panels):
        auc = np.array([rows[r][0] for r, _, _ in EXTERNAL_ROWS])
        lo = np.array([rows[r][1] for r, _, _ in EXTERNAL_ROWS])
        hi = np.array([rows[r][2] for r, _, _ in EXTERNAL_ROWS])
        ax.barh(y, auc - 0.5, left=0.5, height=0.6, color=colors)
        ax.errorbar(auc, y, xerr=[auc - lo, hi - auc], fmt="none", ecolor=INK, elinewidth=1, capsize=2)
        for yi, (r, _, _), v in zip(y, EXTERNAL_ROWS, auc):
            rho = rows[r][3]
            txt = f"{v:.2f}" + (f"  ρ habla {rho:+.2f}" if rho is not None else "")
            ax.text(max(v, 0.5) + 0.01, yi + 0.3, txt.replace(".", ","), fontsize=8, color=INK)
        ax.axvline(0.5, color=MUTED, linewidth=1)
        ax.set_xlim(0.0, 1.2)
        ax.grid(axis="y", visible=False)
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_xlabel("AUROC (0,5 = azar)")
    np.atleast_1d(axes)[0].set_yticks(y, [label for _, label, _ in EXTERNAL_ROWS])
    fig.suptitle("Validación externa: el modelo entrenado solo con voces españolas reconoce el Parkinson en "
                 "inglés e italiano, sin reentrenar", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.01, -0.05, "Londres (MDVR-KCL): todos grabados en la misma sala y con el mismo móvil; la sala no separa "
             "(control < 0,5 = sin señal). ρ habla = Spearman con UPDRS III-18 valorado por el neurólogo.\nItalia "
             "(ItalianPVS): la sala sí separa los grupos (0,90); aun así el índice principal aporta por encima de ella "
             "(p = 3·10⁻⁷). Filas grises: entrenadas dentro de cada dataset dejando una persona fuera.",
             fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "5_validacion_externa.png")
    plt.close(fig)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    style()
    df = auroc_rows()
    df.to_csv(FIG_DIR / "auroc_table.csv", index=False, float_format="%.3f")
    fig_auroc(df)
    fig_updrs()
    fig_dials()
    fig_tracking()
    fig_external()
    log.info("\n%s", df.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
