import numpy as np
import pandas as pd

class Processor:

    PROFIT_FIELD_NAME = "Прибыль (убыток) от продажи, RUB"
    AGE_FIELD_NAME = "Возраст компании, years"
    PROFIT_COMPONENT_FIELD_NAMES = (
        "Выручка, RUB",
        "Себестоимость продаж, RUB",
        "Управленческие расходы, RUB",
        "Коммерческие расходы, RUB",
    )
    REGISTRATION_DATE_FIELD_NAME = "Дата регистрации"

    # can be omitted
    def __init__(self, *args, **kwargs):
        pass

    # ----------------------------------------------------------------------
    # Private methods

    def _resolve_target_year(self, year: int, request_entry: dict) -> int:
        return year - request_entry.get('prev', 0)

    def _resolve_column_name(self, target_year: int, field_name: str) -> str:
        return f"{target_year}, {field_name}"

    def _resolve_output_field_name(self, field_name: str, request_entry: dict) -> str:
        prev = request_entry.get('prev', 0)
        if prev > 0:
            name = f"{field_name} {'Prev'*prev}"
        elif prev < 0:
            name = f"{field_name} {'Next'*(-prev)}"
        else:
            name = field_name
        if 'last_available' in request_entry:
            name = f"{name} LA{request_entry['last_available']}"
        return name

    def _lookup_value(self, data: pd.DataFrame, _id, column_name: str):
        if column_name not in data.columns:
            return None
        row = data.loc[data['_id'] == _id]
        if row.empty:
            return None
        return self._to_numeric(row[column_name].iloc[0])

    def _to_numeric(self, value):
        if value is None:
            return np.nan
        if isinstance(value, str):
            try:
                return float(value.replace(' ', ''))
            except ValueError:
                return np.nan
        return value

    def _lookup_last_available_value(self, data: pd.DataFrame, _id, target_year: int, field_name: str, last_available: int):
        for offset in range(1, last_available + 1):
            candidate_year = target_year - offset
            column_name = self._resolve_column_name(candidate_year, field_name)
            value = self._lookup_value(data, _id, column_name)
            if pd.notna(value):
                return value
        return np.nan

    def _compute_profit(self, data: pd.DataFrame, _id, target_year: int):
        revenue, cost, management, commercial = (
            self._lookup_value(data, _id, self._resolve_column_name(target_year, name))
            for name in self.PROFIT_COMPONENT_FIELD_NAMES
        )
        if any(pd.isna(v) for v in (revenue, cost, management, commercial)):
            return np.nan
        return revenue - cost - management - commercial

    def _compute_age(self, data: pd.DataFrame, _id, application_year: int):
        row = data.loc[data['_id'] == _id]
        if row.empty:
            return np.nan
        registration_date = row[self.REGISTRATION_DATE_FIELD_NAME].iloc[0]
        if pd.isna(registration_date) or registration_date.year > application_year:
            return np.nan
        return application_year - registration_date.year

    # ----------------------------------------------------------------------
    # Main Public Method

    def get_data(
            self,
            data: pd.DataFrame,
            applications: pd.DataFrame,
            request: list
    ) -> pd.DataFrame:

        rows = []
        for _, application in applications.iterrows():
            row = {'_id': application['_id']}
            for request_entry in request:
                field_name = request_entry['field_name']
                target_year = self._resolve_target_year(application['year'], request_entry)
                if field_name == self.PROFIT_FIELD_NAME:
                    value = self._compute_profit(data, application['_id'], target_year)
                elif field_name == self.AGE_FIELD_NAME:
                    value = self._compute_age(data, application['_id'], application['year'])
                else:
                    column_name = self._resolve_column_name(target_year, field_name)
                    value = self._lookup_value(data, application['_id'], column_name)
                    if 'last_available' in request_entry and pd.isna(value):
                        value = self._lookup_last_available_value(
                            data, application['_id'], target_year, field_name, request_entry['last_available']
                        )
                row[self._resolve_output_field_name(field_name, request_entry)] = value
            rows.append(row)

        return pd.DataFrame(rows)