# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import math

from openerp import models, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def increase_date_to(self):
        """For running sick days not yet APPROVED increase date_to to today"""
        _logger.debug('ONESTEiN hr_holidays increase_date_to')
        sick_day_ids = self.search(
            [('holiday_status_id.absenteeism_control', '=', True),
             ('state', '=', 'confirm'),
             ('type', '=', 'remove')])

        for sick_day in sick_day_ids:
            date_from = sick_day.date_from
            date_to = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if date_from:
                # The following is based on addons/hr_holidays/hr_holidays.py
                # date_to has to be greater than date_from
                if (date_from and date_to) and (date_from > date_to):
                    _logger.warning('The start date must be anterior to the end date.')
                    raise Warning(_('The start date must be anterior to the end date.'))

                # Compute and update the number of days
                if (date_to and date_from) and (date_from <= date_to):
                    from_dt = datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)
                    to_dt = datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                    timedelta = to_dt - from_dt
                    diff_day = timedelta.days + float(timedelta.seconds) / 86400

                    number_of_days_temp = round(math.floor(diff_day))+1
                else:
                    number_of_days_temp = 0

                    sick_day.write({'date_to': date_to,
                                    'number_of_days_temp': number_of_days_temp})
            else:
                _logger.warning('ONESTEiN hr_holidays increase_date_to no date_from set')

    def _compute_notify_date(self, notification, holiday):
        notify_date = datetime.strptime(holiday.date_from, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
            days=notification.interval)
        return notify_date

    @api.model
    def create(self, vals):
        # Create the related hr_absenteeism_dates
        holiday = super(hr_holidays, self).create(vals)
        if holiday.date_from:
            for notification in holiday.holiday_status_id.notification_ids:
                notify_date = self._compute_notify_date(notification, holiday)
                absent_vals = {
                    'name': notification.name,
                    'holiday_id': holiday.id,
                    'absent_notify_date': notify_date,
                    'notification_id': notification.id
                }
                self.env['hr.absenteeism.dates'].create(absent_vals)
        return holiday

    @api.multi
    def _validate_fields(self, field_names):
        ### monkey patch hr_holidays constraints
        self._constraints = [t for t in self._constraints if t[1] != 'You can not have 2 leaves that overlaps on same day!']
        return super(hr_holidays, self)._validate_fields(field_names)
