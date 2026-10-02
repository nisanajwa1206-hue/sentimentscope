import re
from collections import Counter
from google_play_scraper import Sort, reviews
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from wordcloud import WordCloud

# ================== KONFIGURASI HALAMAN & THEME ==================
st.set_page_config(
    page_title="DataScraper and Analysis App di Play Store",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS untuk Dark Mode Modern & Card UI (lebih menarik)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Dark Theme Container dengan gradasi halus */
    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #12203a 0%, transparent 60%),
                    radial-gradient(900px 500px at 100% 0%, #1b1233 0%, transparent 55%),
                    #0b0e14;
        color: #e6edf3;
    }

    /* Header Custom dengan efek glassmorphism & glow */
    .main-header {
        background: linear-gradient(120deg, rgba(31,111,235,0.18) 0%, rgba(88,166,255,0.05) 60%, rgba(255,255,255,0.02) 100%);
        padding: 24px 28px;
        border-radius: 16px;
        border: 1px solid rgba(88,166,255,0.35);
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(31,111,235,0.15);
        backdrop-filter: blur(8px);
    }
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #a371f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #9fb3c8;
        margin-top: 6px;
    }

    /* Custom Card Style dengan hover glow */
    .kpi-card {
        background: linear-gradient(160deg, #161b22 0%, #10151d 100%);
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        transition: all 0.25s ease;
    }
    .kpi-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 0 18px rgba(88,166,255,0.35);
        transform: translateY(-3px);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #58a6ff;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Metric cards Streamlit */
    [data-testid="stMetric"] {
        background: linear-gradient(160deg, #161b22 0%, #10151d 100%);
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #a371f7;
        box-shadow: 0 0 16px rgba(163,113,247,0.25);
    }
    [data-testid="stMetricValue"] {
        color: #58a6ff;
        font-weight: 800;
    }

    /* Custom 5W1H Cards */
    .card-5w1h {
        background: linear-gradient(90deg, rgba(31,111,235,0.10) 0%, #161b22 70%);
        border-left: 4px solid #58a6ff;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
        transition: all 0.25s ease;
    }
    .card-5w1h:hover {
        border-left-color: #a371f7;
        box-shadow: 0 0 16px rgba(88,166,255,0.2);
        transform: translateX(4px);
    }
    .badge-5w1h {
        background: linear-gradient(90deg, #1f6feb, #a371f7);
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-right: 8px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #10151d 100%);
        border-right: 1px solid #21262d;
    }

    /* Tombol */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(31,111,235,0.35);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ================== SIDEBAR NAVIGASI ==================
with st.sidebar:
    st.caption("BBDM 26D - FK UNDIP")
    st.markdown("## 📊 DataScraper and\n### Analysis App")
    st.markdown("**di Google Play Store**")
    st.markdown("---")

    st.markdown("### 🧭 NAVIGASI")
    halaman = st.radio(
        "Pilih Halaman:",
        [
            "📊 Ringkasan & KPI",
            "📈 Visualisasi Data",
            "📋 Tabel Ulasan",
            "🔍 Analisis 5W1H & Temuan",
            "💡 Rekomendasi & Keterbatasan",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### ⚙️ PENGATURAN SCRAPPER")
    app_id = st.text_input(
        "App ID Play Store",
        value="com.dafturn.mypertamina",
        help="Masukkan App ID target (contoh: com.dafturn.mypertamina)",
    )
    jumlah = st.slider("Jumlah Ulasan Ditarik", 50, 500, 150, 10)
    btn_scrape = st.button("🚀 Tarik & Analisis Data", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### ℹ️ INFO PENELITIAN")
    st.caption(
        "Studi Sentimen Ulasan Pengguna aplikasi di Google Play Store (Periode Dinamis) dengan analisis sentimen hybrid (rating + leksikon teks)."
    )


# ================== ANALISIS SENTIMEN HYBRID (LEBIH SENSITIF) ==================
KATA_POSITIF = {
    "bagus", "mantap", "keren", "suka", "nyaman", "mudah", "lancar", "cepat",
    "puas", "membantu", "rekomendasi", "recommended", "terbaik", "aman", "gratis",
    "praktis", "baik", "oke", "ok", "hebat", "top", "memudahkan", "lengkap",
    "responsif", "efisien", "senang", "terima kasih", "thanks", "sukses", "berhasil",
}

KATA_NEGATIF = {
    "buruk", "jelek", "error", "gagal", "kecewa", "lambat", "lemot", "crash",
    "macet", "ribet", "susah", "sulit", "bermasalah", "masalah", "keluhan",
    "kesal", "marah", "benci", "parah", "kacau", "tidak bisa", "tiba-tiba",
    "penipuan", "boros", "lelet", "hang", "force close", "tidak berguna",
    "kentang", "pelit", "lemot banget", "maintenance", "gangguan", "down",
}

KATA_NEGASI = {"tidak", "tak", "gak", "nggak", "ga", "ngga", "bukan", "jangan", "belum"}
KATA_INTENSIFIER = {"sangat", "banget", "sekali", "amat", "paling", "terlalu", "begitu", "beneran"}


def skor_teks_sentimen(teks):
    """Skor sentimen teks berbasis leksikon dengan penanganan negasi & intensifier."""
    if not isinstance(teks, str) or not teks.strip():
        return 0
    kata = re.findall(r"[a-z']+", teks.lower())
    skor = 0
    for i, k in enumerate(kata):
        val = 0
        if k in KATA_POSITIF:
            val = 1
        elif k in KATA_NEGATIF:
            val = -1
        if val:
            konteks = kata[max(0, i - 2):i]
            if any(n in konteks for n in KATA_NEGASI):
                val = -val  # negasi membalik sentimen
            if any(it in konteks for it in KATA_INTENSIFIER):
                val *= 1.5  # intensifier memperkuat
            skor += val
    return skor


def tentukan_sentimen(skor_rating, teks=""):
    """Klasifikasi hybrid: bobot rating + sinyal teks (lebih sensitif dari rating murni)."""
    s_teks = skor_teks_sentimen(teks)
    s_rating = skor_rating - 3  # rating 1->-2 ... 5->+2
    sinyal_teks = np.sign(s_teks) * min(abs(s_teks), 3) * 0.7 if s_teks != 0 else 0
    total = s_rating + sinyal_teks
    if total > 0.5:
        return "Positif"
    elif total < -0.5:
        return "Negatif"
    else:
        return "Netral"


@st.cache_data(ttl=600)
def load_data(app_id_param, count_param):
    hasil = reviews(
        app_id_param.strip(),
        lang="id",
        country="id",
        sort=Sort.NEWEST,
        count=count_param,
    )
    data = hasil[0] if isinstance(hasil, tuple) else hasil
    if not data:
        return None
    df = pd.DataFrame(data)
    df["at"] = pd.to_datetime(df["at"])
    df["sentiment"] = df.apply(lambda r: tentukan_sentimen(r["score"], r.get("content", "")), axis=1)
    df["skor_sentimen"] = df.apply(
        lambda r: (r["score"] - 3) + (np.sign(skor_teks_sentimen(r.get("content", ""))) * min(abs(skor_teks_sentimen(r.get("content", ""))), 3) * 0.7 if skor_teks_sentimen(r.get("content", "")) != 0 else 0),
        axis=1,
    )
    return df


if "df_data" not in st.session_state:
    st.session_state.df_data = None

if btn_scrape or st.session_state.df_data is None:
    with st.spinner("Sedang melakukan scraping data ulasan dari Google Play Store..."):
        try:
            st.session_state.df_data = load_data(app_id, jumlah)
        except Exception as e:
            st.error(f"Gagal menarik data dari Google Play Store: {e}")

df = st.session_state.df_data

# ================== HALAMAN UTAMA ==================

if df is None:
    st.warning("⚠️ Data ulasan tidak ditemukan. Pastikan App ID tepat dan periksa koneksi internet Anda.")
else:
    # ------------------ 1. RINGKASAN & KPI ------------------
    if halaman == "📊 Ringkasan & KPI":
        st.markdown(
            f"""
            <div class="main-header">
                <h1 class="main-title">📊 Ringkasan & Indikator Kinerja Utama (KPI)</h1>
                <div class="sub-title">Ringkasan performa ulasan dan persepsi publik aplikasi <b>{app_id}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        total_ulasan = len(df)
        rata_rating = df["score"].mean()
        sentiment_counts = df["sentiment"].value_counts()
        sentiment_mayoritas = sentiment_counts.idxmax()
        pct_negatif = (df["sentiment"] == "Negatif").mean() * 100
        pct_positif = (df["sentiment"] == "Positif").mean() * 100

        # KPI Metrics Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Sampel Ulasan", f"{total_ulasan} Data")
        k2.metric("Rata-Rata Rating", f"{rata_rating:.2f} / 5.0")
        k3.metric("Sentimen Dominan", sentiment_mayoritas)
        k4.metric("Tingkat Keluhan (Negatif)", f"{pct_negatif:.1f}%")

        st.divider()

        st.subheader("📌 Ringkasan Eksekutif")
        st.info(
            f"Berdasarkan penarikan **{total_ulasan} ulasan terbaru**, aplikasi mendapatkan skor rerata **{rata_rating:.2f}** dari skala 5.0. "
            f"Hasil klasifikasi sentimen hybrid (rating + analisis teks) menunjukkan **{pct_positif:.1f}%** ulasan ber-sentimen Positif, "
            f"sementara **{pct_negatif:.1f}%** menyuarakan keluhan (Negatif). "
            f"Sentimen dominan publik saat ini berada pada kategori **{sentiment_mayoritas}**."
        )

        st.subheader("📉 Gambaran Tren Ulasan Harian")
        df_daily = df.groupby(df["at"].dt.date)["score"].agg(["count", "mean"]).reset_index()
        fig_trend = px.area(
            df_daily,
            x="at",
            y="count",
            title="Frekuensi Ulasan Pengguna Per Hari",
            labels={"at": "Tanggal", "count": "Jumlah Ulasan"},
            template="plotly_dark",
        )
        fig_trend.update_traces(line_color="#58a6ff", fillcolor="rgba(88,166,255,0.25)")
        fig_trend.update_layout(title_font_color="#e6edf3", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------ 2. VISUALISASI DATA ------------------
    elif halaman == "📈 Visualisasi Data":
        st.markdown(
            """
            <div class="main-header">
                <h1 class="main-title">📈 Visualisasi Data Sentimen & Teks</h1>
                <div class="sub-title">Grafik interaktif, sebaran rating, dan analisis kata kunci terbanyak (Word Cloud)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Distribusi Sentimen")
            ringkasan = df["sentiment"].value_counts().reindex(["Positif", "Netral", "Negatif"]).fillna(0)
            fig_pie = px.pie(
                values=ringkasan.values,
                names=ringkasan.index,
                hole=0.45,
                color=ringkasan.index,
                color_discrete_map={"Positif": "#3fb950", "Netral": "#d29922", "Negatif": "#f85149"},
                template="plotly_dark",
            )
            fig_pie.update_traces(textinfo="percent+label", pull=[0.03, 0, 0.03])
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("⭐ Distribusi Rating (1-5 Bintang)")
            rating_counts = df["score"].value_counts().sort_index().reset_index()
            rating_counts.columns = ["Rating", "Jumlah"]
            fig_bar = px.bar(
                rating_counts,
                x="Rating",
                y="Jumlah",
                color="Jumlah",
                color_continuous_scale=["#1f6feb", "#a371f7"],
                template="plotly_dark",
                text="Jumlah",
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        st.subheader("☁️ Word Cloud (Kata Paling Sering Muncul)")
        stopwords = set(
            [
                "yang", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "dengan",
                "saya", "aplikasi", "app", "ada", "tidak", "tak", "gak", "nggak",
                "sudah", "belum", "juga", "karena", "kalo", "kalau", "sangat",
                "bisa", "atau", "jadi", "pada", "lebih", "saat", "akan", "banyak",
                "tolong", "bintang", "nya", "mau", "biar", "lagi", "selalu"
            ]
        )
        semua_teks = " ".join(df["content"].dropna().astype(str)).lower()
        kata_kata = re.sub(r"[^a-zA-Z\s]", " ", semua_teks)

        if kata_kata.strip():
            wordcloud = WordCloud(
                width=1000,
                height=400,
                background_color="#0d1117",
                stopwords=stopwords,
                colormap="cool",
                collocations=False,
            ).generate(kata_kata)

            fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
            fig_wc.patch.set_facecolor("#0d1117")
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
            plt.close(fig_wc)

    # ------------------ 3. TABEL ULASAN ------------------
    elif halaman == "📋 Tabel Ulasan":
        st.markdown(
            """
            <div class="main-header">
                <h1 class="main-title">📋 Dataset Ulasan Pengguna</h1>
                <div class="sub-title">Filter, cari, dan unduh data mentah ulasan pengguna Google Play Store</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Filters
        c_filter1, c_filter2 = st.columns([1, 2])
        with c_filter1:
            pilihan_sentimen = st.multiselect(
                "Filter Sentimen:",
                ["Positif", "Netral", "Negatif"],
                default=["Positif", "Netral", "Negatif"],
            )
        with c_filter2:
            search_query = st.text_input("🔍 Cari Kata Kunci pada Ulasan:", placeholder="Contoh: login, qr, error, transaksi")

        df_filtered = df[df["sentiment"].isin(pilihan_sentimen)]
        if search_query:
            df_filtered = df_filtered[df_filtered["content"].str.contains(search_query, case=False, na=False)]

        st.dataframe(
            df_filtered[["userName", "content", "score", "sentiment", "skor_sentimen", "at"]],
            use_container_width=True,
            height=450,
        )

        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Dataset Filtered (CSV)",
            data=csv_data,
            file_name=f"dataset_ulasan_{app_id}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ------------------ 4. ANALISIS 5W1H & TEMUAN ------------------
    elif halaman == "🔍 Analisis 5W1H & Temuan":
        st.markdown(
            """
            <div class="main-header">
                <h1 class="main-title">🔍 Analisis 5W + 1H & Temuan Utama</h1>
                <div class="sub-title">Ekstraksi wawasan otomatis berdasarkan pengolahan kata dan statistik sentimen</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Keyword Extraction 5W1H
        stopwords = {
            "yang", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "dengan",
            "saya", "aplikasi", "app", "ada", "tidak", "tak", "gak", "nggak",
            "sudah", "belum", "juga", "karena", "kalo", "kalau", "sangat",
            "bisa", "atau", "jadi", "pada", "lebih", "saat", "akan", "banyak",
            "tolong", "bintang", "nya", "biar", "mau"
        }
        semua_teks = " ".join(df["content"].dropna().astype(str)).lower()
        kata_kata = re.sub(r"[^a-zA-Z\s]", " ", semua_teks).split()
        kata_filter = [k for k in kata_kata if len(k) > 3 and k not in stopwords]
        top5 = Counter(kata_filter).most_common(5)
        what = ", ".join([f"<b>'{k}'</b> ({v}x)" for k, v in top5]) if top5 else "Tidak cukup kata unik"

        # Kata kunci keluhan utama dari ulasan negatif (lebih sensitif utk analisis WHY)
        teks_negatif = " ".join(df[df["sentiment"] == "Negatif"]["content"].dropna().astype(str)).lower()
        kata_neg = re.sub(r"[^a-zA-Z\s]", " ", teks_negatif).split()
        kata_neg_filter = [k for k in kata_neg if len(k) > 3 and k not in stopwords]
        keluhan_utama = Counter(kata_neg_filter).most_common(3)
        keluhan_str = ", ".join([f"<b>'{k}'</b> ({v}x)" for k, v in keluhan_utama]) if keluhan_utama else "tidak ditemukan keluhan dominan"

        tgl_awal = df["at"].min().strftime("%d %B %Y")
        tgl_akhir = df["at"].max().strftime("%d %B %Y")

        persen = df["sentiment"].value_counts(normalize=True) * 100
        pct_pos = persen.get("Positif", 0)
        pct_net = persen.get("Netral", 0)
        pct_neg = persen.get("Negatif", 0)

        if pct_neg >= 50:
            why = f"Pengguna mendominasi keluhan pada topik: {keluhan_str}. Keluhan umumnya berkaitan dengan error sistem, kendala verifikasi akun, kegagalan transaksi, atau performa lambat."
            how = f"Status kinerja memerlukan <b>PERBAIKAN KRITIS</b> ({pct_pos:.1f}% Positif, {pct_net:.1f}% Netral, {pct_neg:.1f}% Negatif)."
        else:
            why = f"Pengguna merespons relatif positif, namun topik keluhan yang masih muncul: {keluhan_str}."
            how = f"Status kinerja berada dalam tingkat <b>STABIL / CUKUP BAIK</b> ({pct_pos:.1f}% Positif, {pct_net:.1f}% Netral, {pct_neg:.1f}% Negatif)."

        items_5w1h = [
            ("WHAT (Topik Utama)", f"Kata kunci terbanyak yang menjadi pusat perbincangan: {what}."),
            ("WHO (Objek Responden)", f"Responden ulasan adalah pengguna aktif aplikasi <b>{app_id}</b>."),
            ("WHERE (Lokasi/Sumber Data)", "Data diperoleh secara transparan dari platform publik <b>Google Play Store</b>."),
            ("WHEN (Rentang Waktu)", f"Data mencakup transaksi ulasan mulai dari <b>{tgl_awal}</b> sampai <b>{tgl_akhir}</b>."),
            ("WHY (Faktor Penyebab)", why),
            ("HOW (Evaluasi Status)", how),
        ]

        for title, desc in items_5w1h:
            st.markdown(
                f"""
                <div class="card-5w1h">
                    <span class="badge-5w1h">{title}</span>
                    <div style="margin-top: 10px; color: #c9d1d9; font-size: 0.95rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ------------------ 5. REKOMENDASI & KETERBATASAN ------------------
    elif halaman == "💡 Rekomendasi & Keterbatasan":
        st.markdown(
            """
            <div class="main-header">
                <h1 class="main-title">💡 Rekomendasi Strategic & Keterbatasan Studi</h1>
                <div class="sub-title">Langkah tindak lanjut perbaikan sistem dan batasan metodologi penarikan data</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_rec, col_lim = st.columns(2)

        with col_rec:
            st.subheader("🚀 Rekomendasi Perbaikan")
            st.markdown(
                """
                - **Optimasi Server & API Response:** Memperkuat infrastruktur *backend* untuk menangani beban trafik tinggi saat jam operasional.
                - **Penyederhanaan Alur Verifikasi (UX):** Mengurangi tahapan rumit saat pendaftaran akun dan verifikasi plat kendaraan/QR Code.
                - **Manajemen Ulasan Aktif (Customer Care):** Merespons ulasan bintang 1 & 2 di Play Store secara cepat untuk memberikan *troubleshooting* langsung.
                - **Pemberitahuan Pemeliharaan System:** Memberikan info *maintenance* yang transparan di dalam aplikasi agar pengguna tidak memberikan keluhan buruk.
                """
            )

        with col_lim:
            st.subheader("⚠️ Keterbatasan Penelitian")
            st.markdown(
                """
                - **Ukuran Sampel Scraped:** Penarikan terbatas pada kuota sampel ulasan terbaru yang tersedia melalui API Google Play Store.
                - **Pembersihan Teks (Stopwords):** Pengolahan kata menggunakan filter berbasis aturan baku yang mungkin melewatkan kata-kata gaul atau *typo*.
                - **Cakupan Leksikon:** Analisis sentimen hybrid berbasis kamus kata, sehingga sarkasme dan konteks kalimat yang sangat kompleks belum dapat terdeteksi sepenuhnya.
                """
            )
