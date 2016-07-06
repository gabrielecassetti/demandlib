# -*- coding: utf-8 -*-
"""
Implementation of the bdew standard load profiles for electric power.


"""
import pandas as pd
from datetime import time as settime
from .tools import add_weekdays2df


class IndustrialLoadProfile():
    'Generate an industrial heat or electric load profile.'
    def __init__(self, dt_index, **kwargs):
        """
        """
        self.dataframe = pd.DataFrame(index=dt_index)
        self.dataframe = add_weekdays2df(self.dataframe, holiday_is_sunday=True,
                                         holidays=kwargs.get('holidays'))
        self.dataframe['hour'] = dt_index.hour + 1


    def simple_profile(self, annual_demand, **kwargs):
        """
        Create industrial load profile

        Parameters
        ----------

        am : datetime.time
            beginning of workday
        pm : datetime.time
            end of workday
        week : list
            list of weekdays
        weekend : list
            list of weekend days
        profile_factors : dictionary
            dictionary with scaling factors for night and day of weekdays and
            weekend days
        """

        # Day(am to pm), night (pm to am), week day (week),
        # weekend day (weekend)
        am = kwargs.get('am', settime(7, 0, 0))
        pm = kwargs.get('pm', settime(23, 30, 0))

        week = kwargs.get('week', [1, 2, 3, 4, 5])
        weekend = kwargs.get('weekend', [0, 6, 7])

        profile_factors = kwargs.get('profile_factors',
            {'week': {'day': 0.8, 'night': 0.6},
             'weekend': {'day': 0.9, 'night': 0.7}})

        self.dataframe['ind'] = 0

        self.dataframe['ind'].mask(
            self.dataframe['weekday'].between_time(am, pm).isin(week),
            profile_factors['week']['day'], True)
        self.dataframe['ind'].mask(
            self.dataframe['weekday'].between_time(pm, am).isin(week),
            profile_factors['week']['night'], True)
        self.dataframe['ind'].mask(
            self.dataframe['weekday'].between_time(am, pm).isin(weekend),
            profile_factors['weekend']['day'], True)
        self.dataframe['ind'].mask(
            self.dataframe['weekday'].between_time(pm, am).isin(weekend),
            profile_factors['weekend']['night'], True)

        if self.dataframe['ind'].isnull().any(axis=0):
            logging.error('NAN value found in industrial load profile')

        return (self.dataframe['ind'] / self.dataframe['ind'].sum()
                * annual_demand)