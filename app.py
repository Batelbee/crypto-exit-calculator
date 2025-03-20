import pandas as pd
import streamlit as st

def calculate_exit(prices, amounts, multiplier, stages):
    """Рассчитывает точку фиксации вложенных средств и лимитные ордера"""
    total_cost = sum(p * a for p, a in zip(prices, amounts))  # Общая сумма вложений
    total_tokens = sum(amounts)  # Общее количество токенов
    
    target_value = total_cost * multiplier  # Целевая стоимость актива
    sell_price = target_value / total_tokens  # Цена фиксации
    amount_to_sell = total_cost / sell_price  # Количество токенов для продажи
    remaining_tokens = total_tokens - amount_to_sell  # Оставшиеся токены
    
    # Обновленные коэффициенты для расчета лимитных ордеров
    stage_multipliers_dict = {
        2: [1.5, 2.0],
        3: [1.33, 1.66, 2.0],
        4: [1.25, 1.5, 1.75, 2.0]
    }
    stage_multipliers = stage_multipliers_dict.get(stages, [2.0])
    
    # Расчет цен для лимитных ордеров
    stage_prices = [sell_price * multiplier for multiplier in stage_multipliers]
    
    # Равномерное распределение оставшихся токенов на этапы
    stage_amounts = [remaining_tokens / stages] * stages
    
    return total_cost, target_value, amount_to_sell, sell_price, remaining_tokens, stage_prices, stage_amounts

# Интерфейс приложения
st.markdown("""
    <h1 style='text-align: center; font-size: 36px;'>Калькулятор точек выхода из рынка</h1>
    """, unsafe_allow_html=True)

# Ввод данных
st.markdown("""
    <h3 style='font-size: 22px;'>Количество покупок</h3>
    """, unsafe_allow_html=True)
num_entries = st.slider("Выберите количество покупок", min_value=1, max_value=10, value=3, key="num_entries_slider")
prices = []
amounts = []
for i in range(num_entries):
    st.markdown(f"""
        <h3 style='font-size: 22px;'>Покупка №{i+1}</h3>
        """, unsafe_allow_html=True)
    price = st.number_input(f"Цена за токен ($)", min_value=0.0, step=0.01, format="%.10f", key=f"price_{i}")
    amount = st.number_input(f"Количество токенов", min_value=0.0, step=0.000000001, format="%.10f", key=f"amount_{i}")
    prices.append(price)
    amounts.append(amount)

st.markdown("""
    <h3 style='font-size: 22px;'>Минимальный X для фиксации</h3>
    """, unsafe_allow_html=True)
multiplier = st.slider("Выберите X", min_value=2, max_value=4, value=3, key="multiplier_slider")

st.markdown("""
    <h3 style='font-size: 22px;'>Количество этапов выхода для лимитных ордеров</h3>
    """, unsafe_allow_html=True)
stages = st.slider("Выберите количество этапов", min_value=2, max_value=4, value=3, key="stages_slider")

# Расчет и вывод результатов
if st.button("Рассчитать"):
    if any(p == 0 or a == 0 for p, a in zip(prices, amounts)):
        st.error("Введите корректные данные о покупке.")
    else:
        total_cost, target_value, amount_to_sell, sell_price, remaining_tokens, stage_prices, stage_amounts = calculate_exit(prices, amounts, multiplier, stages)
        
        results = pd.DataFrame({
            "Параметр": ["Общая сумма вложений", "Стоимость при фиксации", "Кол-во для продажи", "Цена продажи", "Оставшиеся токены"],
            "Значение": [total_cost, target_value, amount_to_sell, sell_price, remaining_tokens]
        })
        st.dataframe(results)
        
        st.markdown("""
            <h2 style='font-size: 24px;'>Лимитные ордера</h2>
            """, unsafe_allow_html=True)
        stage_df = pd.DataFrame({
            "Этап": [f"Этап {i+1}" for i in range(len(stage_prices))],
            "Цена ордера": stage_prices,
            "Кол-во токенов": stage_amounts
        })
        st.dataframe(stage_df)

