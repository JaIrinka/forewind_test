from typing import Any

import numpy as np
import pandas as pd

class Processor:

    PROFIT_FIELD_NAME: str = "Прибыль (убыток) от продажи, RUB"
    AGE_FIELD_NAME: str = "Возраст компании, years"
    PROFIT_COMPONENT_FIELD_NAMES: tuple[str, ...] = (
        "Выручка, RUB",
        "Себестоимость продаж, RUB",
        "Управленческие расходы, RUB",
        "Коммерческие расходы, RUB",
    )
    REGISTRATION_DATE_FIELD_NAME: str = "Дата регистрации"

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

    def _lookup_value(self, data_row: pd.DataFrame, column_name: str) -> float | None:
        if column_name not in data_row.columns:
            return None
        if data_row.empty:
            return None
        return self._to_numeric(data_row[column_name].iloc[0])

    def _to_numeric(self, value: Any) -> float:
        if value is None:
            return np.nan
        if isinstance(value, str):
            try:
                return float(value.replace(' ', ''))
            except ValueError:
                return np.nan
        return value

    def _lookup_last_available_value(self, data_row: pd.DataFrame, target_year: int, field_name: str, last_available: int) -> float:
        for offset in range(1, last_available + 1):
            candidate_year = target_year - offset
            column_name = self._resolve_column_name(candidate_year, field_name)
            value = self._lookup_value(data_row, column_name)
            if pd.notna(value):
                return value
        return np.nan

    def _compute_profit(self, data_row: pd.DataFrame, target_year: int) -> float:
        revenue, cost, management, commercial = (
            self._lookup_value(data_row, self._resolve_column_name(target_year, name))
            for name in self.PROFIT_COMPONENT_FIELD_NAMES
        )
        if any(pd.isna(v) for v in (revenue, cost, management, commercial)):
            return np.nan
        return revenue - cost - management - commercial

    def _compute_age(self, data_row: pd.DataFrame, application_year: int) -> int | float:
        if data_row.empty:
            return np.nan
        registration_date = data_row[self.REGISTRATION_DATE_FIELD_NAME].iloc[0]
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
            data_row = data.loc[data['_id'] == application['_id']]
            row = {'_id': application['_id']}
            for request_entry in request:
                field_name = request_entry['field_name']
                target_year = self._resolve_target_year(application['year'], request_entry)
                if field_name == self.PROFIT_FIELD_NAME:
                    value = self._compute_profit(data_row, target_year)
                elif field_name == self.AGE_FIELD_NAME:
                    value = self._compute_age(data_row, application['year'])
                else:
                    column_name = self._resolve_column_name(target_year, field_name)
                    value = self._lookup_value(data_row, column_name)
                    if 'last_available' in request_entry and pd.isna(value):
                        value = self._lookup_last_available_value(
                            data_row, target_year, field_name, request_entry['last_available']
                        )
                output_field_name = self._resolve_output_field_name(field_name, request_entry)
                if output_field_name in row:
                    raise ValueError(
                        f'Duplicate output field "{output_field_name}" for application _id={application["_id"]}: '
                        f'request entry {request_entry!r} collides with an earlier entry that produced the same name'
                    )
                row[output_field_name] = value
            rows.append(row)

        return pd.DataFrame(rows)