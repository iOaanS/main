import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lab2')))
from lab2 import vhi_df # Імпорт даних VHI з модуля lab2

# Визначаємо мінімальний та максимальний рік
min_year, max_year = int(vhi_df["Year"].min()), int(vhi_df["Year"].max())

# Ініціалізація стану Streamlit
if "selected_index" not in st.session_state:
    st.session_state.selected_index = "VHI"
if "selected_area" not in st.session_state:
    st.session_state.selected_area = vhi_df["Province_name"].unique()[0]
if "week_range" not in st.session_state:
    st.session_state.week_range = (1, 52)
if "year_range" not in st.session_state:
    st.session_state.year_range = (min_year, max_year)
if "sort_ascending" not in st.session_state:
    st.session_state.sort_ascending = False
if "sort_descending" not in st.session_state:
    st.session_state.sort_descending = False

# Розподіл інтерфейсу на дві колонки
col1, col2 = st.columns([1, 2])

# Колонка 1
with col1:
    st.header("Фільтри")

    # Вибір індексу для аналізу: VCI, TCI або VHI
    st.selectbox(
        "Оберіть індекс для аналізу",
        options=["VCI", "TCI", "VHI"],
        key="selected_index",
    )

    # Вибір області
    areas = sorted(vhi_df["Province_name"].unique())
    st.selectbox(
        "Оберіть область",
        options=areas,
        key="selected_area"
    )

    # Вибір інтервалу тижнів
    st.slider(
        "Виберіть інтервал тижнів",
        min_value=1,
        max_value=52,
        step=1,
        key="week_range"
    )

    # Вибір інтервалу років
    st.slider(
        "Виберіть інтервал років",
        min_value=min_year,
        max_value=max_year,
        step=1,
        key="year_range",
    )

    # Прапорці для сортування
    sort_asc = st.checkbox("Сортувати за зростанням", key="sort_ascending")
    sort_desc = st.checkbox("Сортувати за спаданням", key="sort_descending")

    # Попередження, якщо обрано обидва типи сортування одночасно
    if sort_asc and sort_desc:
        st.warning(
            "Оберіть тільки один тип сортування або зніміть обидва для перегляду без сортування."
        )

    st.markdown("---")
    # Кнопка скидання фільтрів
    if st.button("Скинути фільтри"):
        for key in [
            "selected_index",
            "selected_area",
            "week_range",
            "year_range",
            "sort_ascending",
            "sort_descending",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Фільтрація даних
filtered_df = vhi_df[
    (vhi_df["Province_name"] == st.session_state.selected_area)
    & (vhi_df["Week"] >= st.session_state.week_range[0])
    & (vhi_df["Week"] <= st.session_state.week_range[1])
    & (vhi_df["Year"] >= st.session_state.year_range[0])
    & (vhi_df["Year"] <= st.session_state.year_range[1])
]

# Сортування
if sort_asc and not sort_desc:
    filtered_df = filtered_df.sort_values(
        by=st.session_state.selected_index, ascending=True
    )
elif sort_desc and not sort_asc:
    filtered_df = filtered_df.sort_values(
        by=st.session_state.selected_index, ascending=False
    )

# Колонка 2 - таблиця, графік, порівняння областей
with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння областей"])

    # Таблиця
    with tab1:
        st.header("Відфільтровані дані")
        st.dataframe(
            filtered_df[["Year", "Week", "Province_name", "VCI", "TCI", "VHI"]]
        )

    # Графік часовий ряд
    with tab2:
        st.header(
            f"Графік {st.session_state.selected_index} для області {st.session_state.selected_area}"
        )
        area_df = filtered_df.sort_values(by=["Year", "Week"])

        if not area_df.empty:
            area_df["Date"] = pd.to_datetime(
                area_df["Year"].astype(str) + area_df["Week"].astype(str) + "1",
                format="%G%V%u",
            )

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(
                area_df["Date"],
                area_df[st.session_state.selected_index],
                marker="o",
                linestyle="-",
            )
            ax.set_xlabel("Рік")
            ax.set_ylabel(st.session_state.selected_index)
            ax.set_title(f"Часовий ряд {st.session_state.selected_index} по тижнях")

            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
            for label in ax.get_xticklabels():
                label.set_rotation(45)

            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("Немає даних для цієї області за вказаний період.")

    # Порівняння областей
    with tab3:
        st.header(f"Порівняння областей за {st.session_state.selected_index}")

        comp_df = (
            vhi_df[
                (vhi_df["Week"] >= st.session_state.week_range[0])
                & (vhi_df["Week"] <= st.session_state.week_range[1])
                & (vhi_df["Year"] >= st.session_state.year_range[0])
                & (vhi_df["Year"] <= st.session_state.year_range[1])
            ]
            .groupby("Province_name")[st.session_state.selected_index]
            .mean()
            .reset_index()
        )

        if sort_asc and not sort_desc:
            comp_df = comp_df.sort_values(
                by=st.session_state.selected_index, ascending=True
            )
        elif sort_desc and not sort_asc:
            comp_df = comp_df.sort_values(
                by=st.session_state.selected_index, ascending=False
            )

        if not area_df.empty:
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            x = range(len(comp_df))
            ax2.bar(x, comp_df[st.session_state.selected_index], color="skyblue")
            ax2.set_xticks(x)
            ax2.set_xticklabels(comp_df["Province_name"], rotation=45, ha="right")
            ax2.set_xlabel("Область")
            ax2.set_ylabel(f"Середній {st.session_state.selected_index}")
            ax2.set_title(
                f"Порівняння середніх значень {st.session_state.selected_index} по областях"
            )

            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.warning("Немає даних для побудови порівняння.")
